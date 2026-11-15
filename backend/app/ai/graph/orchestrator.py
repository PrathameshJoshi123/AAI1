"""LangGraph Multi-Agent Monolith Workflow Orchestrator for Phase 10."""
import time
from typing import Any, Dict, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from app.ai.agents.registry import agent_registry
from app.ai.agents.definitions.prospect_intelligence_agent import ProspectSignalInput
from app.ai.agents.definitions.lead_qualification_agent import LeadQualificationInput
from app.ai.agents.definitions.needs_assessment_agent import NeedsAssessmentInput
from app.ai.agents.definitions.risk_information_analysis_agent import RiskInformationInput
from app.ai.agents.definitions.recommendation_agent import RecommendationAgentInput
from app.ai.agents.definitions.dropoff_detection_agent import DropOffDetectionInput
from app.ai.agents.definitions.followup_coordination_agent import FollowUpCoordinationInput
from app.ai.agents.definitions.compliance_monitoring_agent import ComplianceAuditInput
from app.ai.agents.definitions.customer_support_agent import SupportQueryInput
from app.ai.agents.definitions.conversion_analytics_agent import ConversionAnalyticsInput
from app.ai.client.mistral_client import mistral_client
from app.ai.config import ai_config
from app.ai.graph.checkpointer import checkpoint_manager
from app.ai.graph.interrupts import trigger_human_review_interruption
from app.ai.graph.routing import route_after_risk_check, route_by_master_intent
from app.ai.graph.state import BaseAgentState, create_initial_agent_state
from app.ai.observability.audit_recorder import ai_recorder
from app.ai.tools.base import ToolExecutionContext
from app.ai.tools.system_tools import CalculateDeterministicQuoteTool
from app.core.logging import logger


# Node Definitions

async def intake_node(state: BaseAgentState) -> Dict[str, Any]:
    """Intake node: registers input messages and increments step telemetry."""
    steps = state.get("execution_steps_count", 0) + 1
    return {
        "execution_steps_count": steps,
        "current_agent": "WorkflowOrchestrator",
    }


async def intent_router_node(state: BaseAgentState) -> Dict[str, Any]:
    """Classifies user intent into a structured path within the monolith graph."""
    messages = state.get("messages", [])
    last_text = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage) or getattr(msg, "type", "") == "human":
            last_text = msg.content if isinstance(msg.content, str) else str(msg.content)
            break

    last_lower = last_text.lower()

    if any(k in last_lower for k in ["quote", "price", "premium", "cost", "how much", "rate"]):
        next_step = "quote_coordination"
    elif any(k in last_lower for k in ["advisor", "human", "agent", "talk to someone", "representative"]):
        next_step = "advisor_handoff"
    elif any(k in last_lower for k in ["claim", "cancel", "refund", "grace", "faq", "help", "support"]):
        next_step = "customer_support"
    elif any(k in last_lower for k in ["apply", "proposal", "onboard", "kyc", "form"]):
        next_step = "onboarding"
    elif any(k in last_lower for k in ["document", "upload", "proof", "salary slip", "aadhaar", "pan"]):
        next_step = "document_review"
    elif any(k in last_lower for k in ["recommend", "suggest", "which plan", "best plan", "compare"]):
        next_step = "recommendation"
    elif any(k in last_lower for k in ["need", "cover", "coverage", "family", "dependents", "liabilities"]):
        next_step = "needs_assessment"
    elif any(k in last_lower for k in ["medical", "health", "smoke", "tobacco", "disease", "history", "risk"]):
        next_step = "risk_analysis"
    elif any(k in last_lower for k in ["prospect", "traffic", "utm", "channel"]):
        next_step = "prospect_intel"
    elif any(k in last_lower for k in ["qualify", "score", "lead"]):
        next_step = "lead_qual"
    elif any(k in last_lower for k in ["stalled", "drop", "friction"]):
        next_step = "dropoff_detection"
    elif any(k in last_lower for k in ["follow up", "remind", "nudge"]):
        next_step = "followup"
    elif any(k in last_lower for k in ["compliance", "audit", "disclose"]):
        next_step = "compliance"
    elif any(k in last_lower for k in ["funnel", "analytics", "conversion"]):
        next_step = "conversion_analytics"
    else:
        next_step = "conversational_engagement"

    return {
        "next_step": next_step,
        "current_agent": "IntentRouter",
    }


# 1. Prospect Intelligence Node
async def prospect_intelligence_node(state: BaseAgentState) -> Dict[str, Any]:
    agent = agent_registry.get("prospect-intelligence-agent")
    if agent and not await agent_registry.is_agent_active(agent.id):
        return {"current_agent": agent.id, "errors": [f"{agent.name} is paused by administrator."]}

    if agent:
        res = await agent.run(
            ProspectSignalInput(prospect_id=state.get("prospect_id") or "prospect-anon"),
            context={"tool_context": None},
        )
        return {
            "prospect_signals": res.model_dump(),
            "current_agent": agent.id,
        }
    return {"current_agent": "ProspectIntelligenceAgent"}


# 2. Lead Qualification Node
async def lead_qualification_node(state: BaseAgentState) -> Dict[str, Any]:
    agent = agent_registry.get("lead-qualification-agent")
    if agent and not await agent_registry.is_agent_active(agent.id):
        return {"current_agent": agent.id, "errors": [f"{agent.name} is paused by administrator."]}

    if agent:
        res = await agent.run(
            LeadQualificationInput(prospect_id=state.get("prospect_id") or "prospect-anon"),
            context={"tool_context": None},
        )
        return {
            "lead_score": res.qualification_score,
            "qualification_data": res.model_dump(),
            "current_agent": agent.id,
        }
    return {"current_agent": "LeadQualificationAgent"}


# 3. Conversational Engagement Node
async def conversational_engagement_node(state: BaseAgentState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    last_text = messages[-1].content if messages else "Hello"
    agent = agent_registry.get("conversational-engagement-agent") or agent_registry.get("conversational_advisor_agent")

    if agent and not await agent_registry.is_agent_active(agent.id):
        return {
            "requires_human_review": True,
            "human_review_reason": "AI Advisor is temporarily offline for maintenance.",
            "current_agent": agent.id,
        }

    return {
        "current_agent": "ConversationalEngagementAgent",
    }


# 4. Needs Assessment Node
async def needs_assessment_node(state: BaseAgentState) -> Dict[str, Any]:
    agent = agent_registry.get("needs-assessment-agent")
    if agent and not await agent_registry.is_agent_active(agent.id):
        return {"current_agent": agent.id, "errors": [f"{agent.name} is paused by administrator."]}

    if agent:
        res = await agent.run(
            NeedsAssessmentInput(customer_id=state.get("customer_id") or "cust-anon"),
            context={"tool_context": None},
        )
        return {
            "needs_profile": res.model_dump(),
            "current_agent": agent.id,
        }
    return {"current_agent": "NeedsAssessmentAgent"}


# 5. Risk Information Analysis Node
async def risk_information_analysis_node(state: BaseAgentState) -> Dict[str, Any]:
    agent = agent_registry.get("risk-information-analysis-agent")
    if agent and not await agent_registry.is_agent_active(agent.id):
        return {"current_agent": agent.id, "errors": [f"{agent.name} is paused by administrator."]}

    if agent:
        qualification = state.get("qualification_data", {})
        res = await agent.run(
            RiskInformationInput(
                customer_id=state.get("customer_id") or "cust-anon",
                requested_coverage=qualification.get("desired_coverage", 250000.0),
            ),
            context={"tool_context": None},
        )
        flags = state.get("risk_flags", []).copy()
        flags.extend(res.flagged_conditions)
        return {
            "structured_risk": res.model_dump(),
            "risk_flags": flags,
            "requires_human_review": not res.straight_through_processing,
            "current_agent": agent.id,
        }
    return {"current_agent": "RiskInformationAnalysisAgent"}


# 6. Recommendation Node
async def recommendation_node(state: BaseAgentState) -> Dict[str, Any]:
    agent = agent_registry.get("recommendation-agent")
    if agent and not await agent_registry.is_agent_active(agent.id):
        return {"current_agent": agent.id, "errors": [f"{agent.name} is paused by administrator."]}

    if agent:
        try:
            res = await agent.run(
                RecommendationAgentInput(
                    product_name="Term Secure Plus",
                    product_category="Term Life",
                    match_score=94.5,
                    recommended_sum_assured=500000.0,
                    recommended_term_years=25,
                    match_factors={"income_ratio": "12x", "tenure_fit": "Exact"},
                ),
                context={"tool_context": None},
            )
            return {
                "active_recommendation_id": "REC-TERM-PLUS",
                "current_agent": agent.id,
            }
        except Exception as e:
            logger.warning(f"Recommendation execution: {e}")
    return {"current_agent": "RecommendationAgent"}


# 7. Quote Coordination Node
async def quote_coordination_node(state: BaseAgentState) -> Dict[str, Any]:
    context = ToolExecutionContext(
        user_id=state.get("customer_id") or "anonymous",
        email="customer@system.local",
        roles=[state.get("user_role", "Customer")],
        permissions=[],
    )
    quote_tool = CalculateDeterministicQuoteTool()
    quote_data = await quote_tool.execute(
        context,
        product_code="TERM_SECURE_PLUS",
        coverage_amount=250000.0,
        term_years=20,
        age=30,
        is_smoker=False,
    )
    return {
        "active_quote_id": quote_data.get("quote_id"),
        "current_agent": "QuoteCoordinationAgent",
    }


# 8. Onboarding Node
async def onboarding_node(state: BaseAgentState) -> Dict[str, Any]:
    return {
        "active_application_id": state.get("active_application_id") or "APP-DRAFT-2026",
        "current_agent": "OnboardingAgent",
    }


# 9. Document Review Node
async def document_review_node(state: BaseAgentState) -> Dict[str, Any]:
    return {
        "current_agent": "DocumentReviewAssistanceAgent",
    }


# 10. Underwriting Escalation Node (HITL)
async def underwriting_escalation_node(state: BaseAgentState) -> Dict[str, Any]:
    risk_flags = state.get("risk_flags", [])
    if not risk_flags:
        risk_flags.append("UNDERWRITING_REVIEW_REQUESTED")

    logger.info(f"Underwriting escalation triggered for flags: {risk_flags}")
    decision = trigger_human_review_interruption(
        reason="UNDERWRITING_ESCALATION_REQUIRED",
        case_id=state.get("active_application_id"),
        risk_flags=risk_flags,
        data={"state": state.get("qualification_data")},
    )
    return {
        "risk_flags": risk_flags,
        "requires_human_review": False,
        "underwriting_decision": decision,
        "current_agent": "UnderwritingEscalationAgent",
    }


# 11. Drop-off Detection Node
async def dropoff_detection_node(state: BaseAgentState) -> Dict[str, Any]:
    agent = agent_registry.get("drop-off-detection-agent")
    if agent:
        res = await agent.run(
            DropOffDetectionInput(
                session_id=state.get("session_id", "s-1"),
                customer_id=state.get("customer_id", "c-1"),
            ),
            context={"tool_context": None},
        )
        return {
            "dropoff_status": res.model_dump(),
            "current_agent": agent.id,
        }
    return {"current_agent": "DropOffDetectionAgent"}


# 12. Follow-up Coordination Node
async def followup_coordination_node(state: BaseAgentState) -> Dict[str, Any]:
    agent = agent_registry.get("follow-up-coordination-agent")
    if agent:
        res = await agent.run(
            FollowUpCoordinationInput(customer_id=state.get("customer_id", "c-1")),
            context={"tool_context": None},
        )
        return {
            "followup_status": res.model_dump(),
            "current_agent": agent.id,
        }
    return {"current_agent": "FollowUpCoordinationAgent"}


# 13. Customer Support Node
async def customer_support_node(state: BaseAgentState) -> Dict[str, Any]:
    agent = agent_registry.get("customer-support-agent")
    messages = state.get("messages", [])
    last_text = messages[-1].content if messages else "Help inquiry"

    if agent:
        res = await agent.run(
            SupportQueryInput(
                customer_id=state.get("customer_id", "c-1"),
                question=last_text if isinstance(last_text, str) else str(last_text),
            ),
            context={"tool_context": None},
        )
        return {
            "support_output": res.model_dump(),
            "current_agent": agent.id,
        }
    return {"current_agent": "CustomerSupportAgent"}


# 14. Conversion Analytics Node
async def conversion_analytics_node(state: BaseAgentState) -> Dict[str, Any]:
    agent = agent_registry.get("conversion-analytics-agent")
    if agent:
        res = await agent.run(
            ConversionAnalyticsInput(reporting_window_days=30),
            context={"tool_context": None},
        )
        return {
            "analytics_summary": res.model_dump(),
            "current_agent": agent.id,
        }
    return {"current_agent": "ConversionAnalyticsAgent"}


# 15. Compliance Monitoring Node
async def compliance_monitoring_node(state: BaseAgentState) -> Dict[str, Any]:
    agent = agent_registry.get("compliance-monitoring-agent")
    messages = state.get("messages", [])
    last_text = str(messages[-1].content) if messages else ""

    if agent:
        try:
            res = await agent.run(
                ComplianceAuditInput(
                    session_id=state.get("session_id", "s-1"),
                    workflow_step="turn_synthesis",
                    messages_text=last_text,
                    quote_presented=state.get("active_quote_id") is not None,
                    disclaimer_present=True,
                ),
                context={"tool_context": None},
            )
            flags = state.get("compliance_flags", []).copy()
            if not res.is_compliant:
                flags.extend(res.missing_disclosures)
            return {
                "compliance_flags": flags,
                "current_agent": agent.id,
            }
        except Exception as e:
            logger.warning(f"Compliance check warning: {e}")
    return {"current_agent": "ComplianceMonitoringAgent"}


# 16. Advisor Handoff Node
async def advisor_handoff_node(state: BaseAgentState) -> Dict[str, Any]:
    return {
        "requires_human_review": True,
        "human_review_reason": state.get("human_review_reason") or "Customer requested human advisor consultation",
        "current_agent": "AdvisorHandoffAgent",
    }


# Output Synthesis Node
async def output_node(state: BaseAgentState) -> Dict[str, Any]:
    current_agent = state.get("current_agent", "WorkflowOrchestrator")
    active_quote_id = state.get("active_quote_id")
    underwriting_decision = state.get("underwriting_decision")
    support_output = state.get("support_output")
    analytics_summary = state.get("analytics_summary")

    if support_output:
        content = support_output.get("answer", "Here is information regarding your inquiry.")
    elif active_quote_id:
        content = (
            f"I have coordinated an indicative quote for Term Secure Plus (ID: {active_quote_id}). "
            "Please note this quote is indicative and subject to medical declarations and authorized underwriting approval."
        )
    elif underwriting_decision:
        content = (
            f"Your application has been reviewed by our underwriting team with outcome: "
            f"'{underwriting_decision.get('decision', 'Approved')}'. Notes: {underwriting_decision.get('notes', 'None')}."
        )
    elif analytics_summary:
        content = (
            f"Conversion Funnel Report ({analytics_summary.get('reporting_window_days')} days): "
            f"Conversion rate is {analytics_summary.get('overall_conversion_rate')}%. "
            f"Primary bottleneck: {analytics_summary.get('primary_bottleneck')}."
        )
    elif state.get("requires_human_review"):
        content = (
            "I have escalated your request to an accredited insurance advisor who will review your case "
            "and assist you shortly."
        )
    else:
        content = (
            "Welcome to PS-21 Conversational Insurance. I can assist you with needs analysis, "
            "indicative quotes, policy explanations, or connect you with a licensed advisor. How can I help you today?"
        )

    ai_msg = AIMessage(content=content)
    return {
        "messages": [ai_msg],
        "is_completed": True,
        "current_agent": current_agent,
    }


# Monolith Graph Builder & Orchestrator

class InsuranceWorkflowOrchestrator:
    """Builder and runtime manager for the PS-21 multi-agent monolith graph."""

    def __init__(self):
        self._graph = None
        self._compiled_graph = None

    def build_graph(self) -> StateGraph:
        """Constructs the unified monolithic multi-agent state graph."""
        builder = StateGraph(BaseAgentState)

        # Register nodes
        builder.add_node("intake", intake_node)
        builder.add_node("intent_router", intent_router_node)
        builder.add_node("prospect_intelligence_node", prospect_intelligence_node)
        builder.add_node("lead_qualification_node", lead_qualification_node)
        builder.add_node("conversational_engagement_node", conversational_engagement_node)
        builder.add_node("needs_assessment_node", needs_assessment_node)
        builder.add_node("risk_information_analysis_node", risk_information_analysis_node)
        builder.add_node("recommendation_node", recommendation_node)
        builder.add_node("quote_coordination_node", quote_coordination_node)
        builder.add_node("onboarding_node", onboarding_node)
        builder.add_node("document_review_node", document_review_node)
        builder.add_node("underwriting_escalation_node", underwriting_escalation_node)
        builder.add_node("dropoff_detection_node", dropoff_detection_node)
        builder.add_node("followup_coordination_node", followup_coordination_node)
        builder.add_node("customer_support_node", customer_support_node)
        builder.add_node("conversion_analytics_node", conversion_analytics_node)
        builder.add_node("compliance_monitoring_node", compliance_monitoring_node)
        builder.add_node("advisor_handoff_node", advisor_handoff_node)
        builder.add_node("output_node", output_node)

        # Wire entry and router
        builder.add_edge(START, "intake")
        builder.add_edge("intake", "intent_router")

        # Intent router conditional branching
        builder.add_conditional_edges(
            "intent_router",
            route_by_master_intent,
            {
                "prospect_intelligence_node": "prospect_intelligence_node",
                "lead_qualification_node": "lead_qualification_node",
                "conversational_engagement_node": "conversational_engagement_node",
                "needs_assessment_node": "needs_assessment_node",
                "risk_information_analysis_node": "risk_information_analysis_node",
                "recommendation_node": "recommendation_node",
                "quote_coordination_node": "quote_coordination_node",
                "onboarding_node": "onboarding_node",
                "document_review_node": "document_review_node",
                "underwriting_escalation_node": "underwriting_escalation_node",
                "dropoff_detection_node": "dropoff_detection_node",
                "followup_coordination_node": "followup_coordination_node",
                "customer_support_node": "customer_support_node",
                "conversion_analytics_node": "conversion_analytics_node",
                "advisor_handoff_node": "advisor_handoff_node",
            },
        )

        # Sequential transitions
        builder.add_edge("prospect_intelligence_node", "lead_qualification_node")
        builder.add_edge("lead_qualification_node", "conversational_engagement_node")
        builder.add_edge("conversational_engagement_node", "compliance_monitoring_node")

        builder.add_edge("needs_assessment_node", "risk_information_analysis_node")
        builder.add_conditional_edges(
            "risk_information_analysis_node",
            route_after_risk_check,
            {
                "underwriting_escalation_node": "underwriting_escalation_node",
                "compliance_monitoring_node": "compliance_monitoring_node",
            },
        )

        builder.add_edge("recommendation_node", "compliance_monitoring_node")
        builder.add_edge("quote_coordination_node", "compliance_monitoring_node")
        builder.add_edge("onboarding_node", "compliance_monitoring_node")
        builder.add_edge("document_review_node", "compliance_monitoring_node")
        builder.add_edge("dropoff_detection_node", "followup_coordination_node")
        builder.add_edge("followup_coordination_node", "compliance_monitoring_node")
        builder.add_edge("customer_support_node", "compliance_monitoring_node")
        builder.add_edge("conversion_analytics_node", "output_node")
        builder.add_edge("underwriting_escalation_node", "compliance_monitoring_node")
        builder.add_edge("advisor_handoff_node", "compliance_monitoring_node")

        # Compliance flows to output
        builder.add_edge("compliance_monitoring_node", "output_node")
        builder.add_edge("output_node", END)

        return builder

    def get_compiled_graph(self):
        """Compiles monolithic graph with persistent SQLite checkpointer."""
        if self._compiled_graph is None:
            builder = self.build_graph()
            checkpointer = checkpoint_manager.get_saver()
            self._compiled_graph = builder.compile(checkpointer=checkpointer)
            logger.info("LangGraph monolith workflow compiled successfully with SQLite persistence.")
        return self._compiled_graph

    async def execute_turn(
        self,
        thread_id: str,
        session_id: str,
        user_message: str,
        user_role: str = "Customer",
        customer_id: Optional[str] = None,
        prospect_id: Optional[str] = None,
        qualification_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Runs a turn in the monolith workflow graph, recording metrics and traces."""
        start_time = time.perf_counter()
        graph = self.get_compiled_graph()
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": ai_config.GRAPH_MAX_RECURSION_LIMIT,
        }

        existing = graph.get_state(config)
        if not existing or not existing.values:
            input_state = create_initial_agent_state(
                thread_id=thread_id,
                session_id=session_id,
                user_role=user_role,
                customer_id=customer_id,
                prospect_id=prospect_id,
                initial_messages=[HumanMessage(content=user_message)],
            )
        else:
            input_state = {"messages": [HumanMessage(content=user_message)]}

        if qualification_override:
            input_state["qualification_data"] = qualification_override

        try:
            output_state = await graph.ainvoke(input_state, config=config)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            await ai_recorder.record_execution(
                agent_name="InsuranceWorkflowOrchestrator",
                session_id=session_id,
                input_state={"thread_id": thread_id, "message": user_message},
                output_state={
                    "is_completed": output_state.get("is_completed"),
                    "current_agent": output_state.get("current_agent"),
                    "requires_human_review": output_state.get("requires_human_review"),
                },
                status="success",
                latency_ms=elapsed_ms,
                token_usage={"total_tokens": output_state.get("total_tokens_consumed", 0)},
            )
            return output_state

        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            await ai_recorder.record_execution(
                agent_name="InsuranceWorkflowOrchestrator",
                session_id=session_id,
                input_state={"thread_id": thread_id, "message": user_message},
                output_state=None,
                status="failed",
                latency_ms=elapsed_ms,
                error_message=str(e),
            )
            raise

    async def resume_workflow(self, thread_id: str, human_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Resumes an interrupted workflow with human reviewer input."""
        graph = self.get_compiled_graph()
        config = {"configurable": {"thread_id": thread_id}}
        logger.info(f"Resuming thread {thread_id} with human decision: {human_decision}")

        command = Command(resume=human_decision)
        output_state = await graph.ainvoke(command, config=config)
        return output_state


workflow_orchestrator = InsuranceWorkflowOrchestrator()
