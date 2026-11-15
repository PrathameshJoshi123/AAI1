"""AI Diagnostic, Multi-Agent Orchestration, and Thread Inspection Endpoints."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.agents.registry import agent_registry
from app.ai.client.exceptions import AIConfigurationError
from app.ai.config import ai_config
from app.ai.graph.checkpointer import checkpoint_manager
from app.ai.graph.orchestrator import workflow_orchestrator
from app.ai.tools.registry import tool_registry
from app.api.deps import get_current_user, get_db, require_roles
from app.models.agent import AgentConfiguration, AgentExecution
from app.models.auth import User
from app.schemas.common import APIResponse

router = APIRouter(prefix="/ai", tags=["AI & Agents"])


class ChatTurnRequest(BaseModel):
    message: str = Field(min_length=1, description="Customer or user prompt")
    thread_id: str = Field(description="Conversation or workflow thread identifier")
    session_id: str = Field(default="default-session", description="Client session identifier")
    prospect_id: Optional[str] = Field(default=None, description="Optional prospect identifier")
    qualification_data: Optional[Dict[str, Any]] = Field(default=None, description="Optional qualification overrides")


class ResumeWorkflowRequest(BaseModel):
    decision: str = Field(description="Underwriting or review decision (e.g. Approved, Declined, MoreInfo)")
    notes: Optional[str] = Field(default=None, description="Reviewer notes or comments")
    loading_percentage: Optional[float] = Field(default=0.0, description="Optional premium loading percentage")


@router.get("/health", response_model=APIResponse[Dict[str, Any]])
async def ai_health_check(
    current_user: User = Depends(get_current_user),
):
    """
    Verifies Mistral AI configuration and connectivity.
    Does not incur heavy generation cost.
    """
    has_key = bool(ai_config.MISTRAL_API_KEY and ai_config.MISTRAL_API_KEY.strip() != "")
    return APIResponse(
        data={
            "provider": "Mistral AI",
            "is_configured": has_key,
            "default_model": ai_config.MISTRAL_DEFAULT_MODEL,
            "fast_model": ai_config.MISTRAL_FAST_MODEL,
            "temperature": ai_config.MISTRAL_TEMPERATURE,
            "checkpoints_db": ai_config.CHECKPOINTS_DB_PATH,
            "status": "ready" if has_key else "missing_credentials",
        },
        message="AI infrastructure diagnostic check completed.",
    )


@router.post("/chat", response_model=APIResponse[Dict[str, Any]])
async def execute_chat_turn(
    request: ChatTurnRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Executes a multi-agent conversational turn using LangGraph monolith with persistent SQLite checkpointing.
    """
    roles = [r.name for r in current_user.roles]
    output_state = await workflow_orchestrator.execute_turn(
        thread_id=request.thread_id,
        session_id=request.session_id,
        user_message=request.message,
        user_role=roles[0] if roles else "Customer",
        customer_id=current_user.id,
        prospect_id=request.prospect_id,
        qualification_override=request.qualification_data,
    )

    last_msg = ""
    messages = output_state.get("messages", [])
    if messages:
        msg = messages[-1]
        last_msg = msg.content if isinstance(msg.content, str) else str(msg.content)

    return APIResponse(
        data={
            "thread_id": request.thread_id,
            "response": last_msg,
            "is_completed": output_state.get("is_completed", False),
            "current_agent": output_state.get("current_agent"),
            "active_quote_id": output_state.get("active_quote_id"),
            "requires_human_review": output_state.get("requires_human_review", False),
            "risk_flags": output_state.get("risk_flags", []),
            "compliance_flags": output_state.get("compliance_flags", []),
            "needs_profile": output_state.get("needs_profile"),
            "support_output": output_state.get("support_output"),
            "analytics_summary": output_state.get("analytics_summary"),
        },
        message="Monolith agent workflow executed successfully.",
    )


@router.get("/threads/{thread_id}/state", response_model=APIResponse[Dict[str, Any]])
async def get_thread_state(
    thread_id: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieves current state snapshot and checkpoint status for a thread."""
    graph = workflow_orchestrator.get_compiled_graph()
    snapshot = checkpoint_manager.get_thread_state(graph, thread_id)
    if not snapshot:
        return APIResponse(
            data={"thread_id": thread_id, "exists": False},
            message=f"No persisted checkpoint found for thread '{thread_id}'.",
        )
    return APIResponse(
        data={"thread_id": thread_id, "exists": True, "state": snapshot},
        message="Thread state retrieved from SQLite checkpointer.",
    )


@router.post("/threads/{thread_id}/resume", response_model=APIResponse[Dict[str, Any]])
async def resume_interrupted_thread(
    thread_id: str,
    request: ResumeWorkflowRequest,
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
):
    """
    Resumes an interrupted workflow following human advisor or underwriter review.
    """
    human_decision = {
        "reviewer_id": current_user.id,
        "reviewer_email": current_user.email,
        "decision": request.decision,
        "notes": request.notes or "",
        "loading_percentage": request.loading_percentage or 0.0,
    }

    output_state = await workflow_orchestrator.resume_workflow(thread_id, human_decision)

    last_msg = ""
    messages = output_state.get("messages", [])
    if messages:
        msg = messages[-1]
        last_msg = msg.content if isinstance(msg.content, str) else str(msg.content)

    return APIResponse(
        data={
            "thread_id": thread_id,
            "response": last_msg,
            "is_completed": output_state.get("is_completed", False),
            "underwriting_decision": output_state.get("underwriting_decision"),
        },
        message="Workflow resumed successfully with human review input.",
    )


@router.get("/executions", response_model=APIResponse[List[Dict[str, Any]]])
async def list_agent_executions(
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
):
    """Returns recent agent execution traces with latency and token metrics."""
    stmt = select(AgentExecution).order_by(desc(AgentExecution.executed_at)).limit(limit)
    res = await session.execute(stmt)
    executions = res.scalars().all()

    return APIResponse(
        data=[
            {
                "id": e.id,
                "agent_name": e.agent_name,
                "session_id": e.session_id,
                "status": e.status,
                "latency_ms": e.latency_ms,
                "token_usage": e.token_usage_json,
                "error_message": e.error_message,
                "executed_at": e.executed_at.isoformat() if e.executed_at else None,
            }
            for e in executions
        ],
        message="Recent agent executions retrieved.",
    )


@router.get("/agents/config", response_model=APIResponse[List[Dict[str, Any]]])
async def list_agent_configurations(
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
):
    """Lists registered agents, models, and tool declarations."""
    return APIResponse(
        data=agent_registry.list_all(),
        message="Registered agents retrieved.",
    )


@router.post("/agents/sync", response_model=APIResponse[Dict[str, Any]])
async def sync_agents_with_db(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
):
    """Synchronizes all in-memory registered agents with the agent_configurations database table."""
    await agent_registry.sync_with_database(session)
    return APIResponse(
        data={"synced_agent_count": len(agent_registry.list_all())},
        message="Agents successfully synchronized with database configuration.",
    )


@router.get("/tools", response_model=APIResponse[List[Dict[str, Any]]])
async def list_tools(
    current_user: User = Depends(get_current_user),
):
    """Lists available tools and schemas."""
    tools = tool_registry.list_all()
    return APIResponse(
        data=[
            {
                "name": t.name,
                "description": t.description,
                "required_permissions": t.required_permissions,
                "schema": t.args_schema.model_json_schema(),
            }
            for t in tools
        ],
        message="Available tools retrieved.",
    )
