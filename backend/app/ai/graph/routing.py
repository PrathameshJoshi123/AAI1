"""Conditional Edge Routing Logic for LangGraph Multi-Agent Workflows."""
from typing import Literal
from app.ai.graph.state import BaseAgentState
from app.core.logging import logger


def route_by_master_intent(state: BaseAgentState) -> str:
    """Routes customer workflow to the appropriate specialized node in the monolith graph."""
    next_step = state.get("next_step") or "conversational_engagement"
    logger.info(f"Master Monolith Routing. Target next_step={next_step}")

    valid_targets = {
        "prospect_intel": "prospect_intelligence_node",
        "lead_qual": "lead_qualification_node",
        "conversational_engagement": "conversational_engagement_node",
        "needs_assessment": "needs_assessment_node",
        "risk_analysis": "risk_information_analysis_node",
        "recommendation": "recommendation_node",
        "quote_coordination": "quote_coordination_node",
        "onboarding": "onboarding_node",
        "document_review": "document_review_node",
        "underwriting_escalation": "underwriting_escalation_node",
        "dropoff_detection": "dropoff_detection_node",
        "followup": "followup_coordination_node",
        "compliance": "compliance_monitoring_node",
        "customer_support": "customer_support_node",
        "conversion_analytics": "conversion_analytics_node",
        "advisor_handoff": "advisor_handoff_node",
    }

    return valid_targets.get(next_step, "conversational_engagement_node")


def route_after_risk_check(state: BaseAgentState) -> str:
    """Routes after risk evaluation completes (or resumes after interruption)."""
    if state.get("requires_human_review"):
        return "underwriting_escalation_node"
    return "compliance_monitoring_node"


def route_by_intent(state: BaseAgentState) -> Literal["needs_analysis", "quote_coordination", "advisor_handoff", "output"]:
    """Backwards-compatible legacy route by intent."""
    next_step = state.get("next_step")
    if next_step == "needs_discovery":
        return "needs_analysis"
    elif next_step == "get_quote":
        return "quote_coordination"
    elif next_step == "speak_to_human":
        return "advisor_handoff"
    return "output"
