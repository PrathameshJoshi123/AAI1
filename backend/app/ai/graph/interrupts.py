"""Human-in-the-Loop Interruption and Resumption Primitives."""
from typing import Any, Dict, Optional
from langgraph.types import interrupt
from app.ai.client.exceptions import HumanReviewInterruption
from app.core.logging import logger


def trigger_human_review_interruption(
    reason: str,
    case_id: Optional[str] = None,
    risk_flags: Optional[list] = None,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Invokes LangGraph's native interrupt primitive to pause workflow execution
    and wait for human advisor/underwriter sign-off.
    
    When resumed via graph.invoke(Command(resume=...)), this returns the resume value.
    """
    logger.info(f"Triggering LangGraph Human-in-the-Loop interruption. Reason: {reason} | Case: {case_id}")
    
    payload = {
        "reason": reason,
        "case_id": case_id,
        "risk_flags": risk_flags or [],
        "data": data or {},
        "status": "awaiting_human_review",
    }
    
    # LangGraph interrupt pauses execution here
    decision = interrupt(payload)
    logger.info(f"Human-in-the-loop workflow resumed with decision: {decision}")
    return decision

