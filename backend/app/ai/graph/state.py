"""LangGraph Typed State Definitions for PS-21 Insurance Workflows."""
from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class BaseAgentState(TypedDict):
    """
    Universal state shared across all LangGraph insurance workflow nodes.
    Maintains conversation messages, routing status, business data context, and audit metrics.
    """
    # Conversation and thread identifiers
    thread_id: str
    session_id: str
    customer_id: Optional[str]
    prospect_id: Optional[str]
    user_role: str

    # Conversation history with LangGraph message reducer
    messages: Annotated[List[BaseMessage], add_messages]

    # Control flow & Routing
    current_agent: str
    next_step: Optional[str]
    is_completed: bool
    requires_human_review: bool
    human_review_reason: Optional[str]
    interrupted_at_node: Optional[str]

    # Domain Business Context (read/written through deterministic tools)
    customer_profile: Dict[str, Any]
    prospect_signals: Dict[str, Any]
    lead_score: Optional[int]
    needs_profile: Dict[str, Any]
    qualification_data: Dict[str, Any]
    structured_risk: Dict[str, Any]
    active_quote_id: Optional[str]
    active_application_id: Optional[str]
    risk_flags: List[str]
    underwriting_decision: Optional[Dict[str, Any]]
    compliance_flags: List[str]
    dropoff_status: Optional[Dict[str, Any]]
    followup_status: Optional[Dict[str, Any]]
    support_output: Optional[Dict[str, Any]]
    analytics_summary: Optional[Dict[str, Any]]

    # Execution telemetry & Observability
    total_tokens_consumed: int
    execution_steps_count: int
    errors: List[str]


def create_initial_agent_state(
    thread_id: str,
    session_id: str,
    user_role: str = "Customer",
    customer_id: Optional[str] = None,
    prospect_id: Optional[str] = None,
    initial_messages: Optional[List[BaseMessage]] = None,
    customer_profile: Optional[Dict[str, Any]] = None,
) -> BaseAgentState:
    """Helper factory for initializing a fresh agent state graph."""
    return {
        "thread_id": thread_id,
        "session_id": session_id,
        "customer_id": customer_id,
        "prospect_id": prospect_id,
        "user_role": user_role,
        "messages": initial_messages or [],
        "current_agent": "WorkflowOrchestrator",
        "next_step": None,
        "is_completed": False,
        "requires_human_review": False,
        "human_review_reason": None,
        "interrupted_at_node": None,
        "customer_profile": customer_profile or {},
        "prospect_signals": {},
        "lead_score": None,
        "needs_profile": {},
        "qualification_data": {},
        "structured_risk": {},
        "active_quote_id": None,
        "active_application_id": None,
        "risk_flags": [],
        "underwriting_decision": None,
        "compliance_flags": [],
        "dropoff_status": None,
        "followup_status": None,
        "support_output": None,
        "analytics_summary": None,
        "total_tokens_consumed": 0,
        "execution_steps_count": 0,
        "errors": [],
    }
