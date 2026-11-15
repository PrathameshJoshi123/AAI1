"""AI Execution Observability & Database Audit Recorder."""
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.models.agent import AgentExecution
from app.models.audit import AuditLog


class AIAuditRecorder:
    """Persists agent executions, token usage, latency, and compliance audit events."""

    @staticmethod
    async def record_execution(
        agent_name: str,
        session_id: str,
        input_state: Dict[str, Any],
        output_state: Optional[Dict[str, Any]] = None,
        status: str = "success",
        latency_ms: Optional[int] = None,
        token_usage: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> str:
        """Saves an agent execution trace to the database."""
        try:
            async with AsyncSessionLocal() as session:
                execution = AgentExecution(
                    agent_name=agent_name,
                    session_id=session_id,
                    conversation_id=conversation_id,
                    input_state_json=input_state,
                    output_state_json=output_state,
                    status=status,
                    latency_ms=latency_ms,
                    token_usage_json=token_usage,
                    error_message=error_message,
                    executed_at=datetime.now(timezone.utc),
                )
                session.add(execution)
                await session.commit()
                await session.refresh(execution)
                logger.info(
                    f"Recorded agent execution {execution.id} [{agent_name}] status: {status} "
                    f"latency: {latency_ms}ms"
                )
                return execution.id
        except Exception as e:
            logger.error(f"Failed to record agent execution to database: {e}\n{traceback.format_exc()}")
            return ""

    @staticmethod
    async def record_ai_compliance_log(
        user_id: Optional[str],
        action: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Records sensitive AI decisions or escalations into AuditLog."""
        try:
            async with AsyncSessionLocal() as session:
                log = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource_type="AIAgent",
                    resource_id=resource_id,
                    payload_json=details,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to record AI compliance log: {e}")


ai_recorder = AIAuditRecorder()
