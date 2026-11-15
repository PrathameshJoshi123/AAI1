"""Agent Interceptor: Runtime status verification for LangGraph nodes and AI dispatchers."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent import AgentConfiguration
from app.core.exceptions import BusinessRuleViolationException


class AgentDisabledException(BusinessRuleViolationException):
    """Raised when an agent invocation is blocked because it was disabled by an administrator."""
    pass


class AgentPausedException(BusinessRuleViolationException):
    """Raised when an agent invocation is suspended because it is currently paused."""
    pass


async def verify_agent_execution_allowed(agent_name: str, session: AsyncSession) -> None:
    """Check AgentConfiguration status before executing any agent logic or LangGraph node.
    
    Raises:
        AgentDisabledException: If agent status is 'disabled' or is_active is False.
        AgentPausedException: If agent status is 'paused'.
    """
    query = select(AgentConfiguration).where(AgentConfiguration.agent_name == agent_name)
    result = await session.execute(query)
    agent_cfg = result.scalar_one_or_none()

    if not agent_cfg:
        # If no config entry exists yet, assume active
        return

    status = getattr(agent_cfg, "status", "active")
    if not agent_cfg.is_active or status == "disabled":
        raise AgentDisabledException(
            f"Agent '{agent_name}' execution blocked: This agent has been disabled in the Admin Control Centre."
        )

    if status == "paused":
        raise AgentPausedException(
            f"Agent '{agent_name}' execution paused: This agent has been paused by an administrator."
        )

