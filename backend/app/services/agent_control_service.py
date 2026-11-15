"""Agent Control Service: Agent telemetry, observability, and runtime kill-switch management."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import utc_now
from app.models.agent import AgentConfiguration, AgentExecution
from app.models.audit import AuditLog
from app.core.exceptions import NotFoundException, ValidationException
from app.schemas.admin import (
    AgentTelemetryResponse,
    AgentExecutionLogItem,
    AgentExecutionLogsResponse,
)

STANDARD_AGENTS = [
    {
        "agent_name": "ConversationalEngagementAgent",
        "description": "Multi-turn conversational guide for customer intake, intent recognition and insurance explanations.",
        "model_name": "mistral-large-latest",
        "temperature": 0.2,
        "system_prompt": "You are the PS-21 Conversational Insurance Guide. Help customers explore coverage options.",
    },
    {
        "agent_name": "NeedsAssessmentAgent",
        "description": "Extracts and evaluates customer financial obligations, income protection requirements, and coverage duration.",
        "model_name": "mistral-large-latest",
        "temperature": 0.1,
        "system_prompt": "You evaluate customer financial needs based on dependents, liabilities, and income.",
    },
    {
        "agent_name": "RecommendationAgent",
        "description": "Formulates clear, plain-language explanations of eligible products and coverage trade-offs.",
        "model_name": "mistral-large-latest",
        "temperature": 0.2,
        "system_prompt": "You explain matched insurance products using factual product parameters and customer criteria.",
    },
    {
        "agent_name": "QuoteCoordinationAgent",
        "description": "Coordinates quote formulation using approved deterministic actuarial tables without guessing prices.",
        "model_name": "mistral-large-latest",
        "temperature": 0.0,
        "system_prompt": "You coordinate indicative quotes by invoking approved pricing services.",
    },
    {
        "agent_name": "OnboardingAgent",
        "description": "Assists applicants through multi-step proposal completion, declarations, and nominee information.",
        "model_name": "mistral-large-latest",
        "temperature": 0.1,
        "system_prompt": "You guide applicants through the proposal form steps.",
    },
    {
        "agent_name": "DocumentReviewAssistanceAgent",
        "description": "Extracts and cross-checks KYC data from identity proofs against application declarations.",
        "model_name": "mistral-large-latest",
        "temperature": 0.0,
        "system_prompt": "You summarize extracted identity documents for authorized human verification.",
    },
    {
        "agent_name": "UnderwritingEscalationAgent",
        "description": "Synthesizes multi-source applicant risk declarations for human underwriter review.",
        "model_name": "mistral-large-latest",
        "temperature": 0.1,
        "system_prompt": "You synthesize declared risk data for human underwriter evaluation.",
    },
]


class AgentControlService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _ensure_seed_agents(self) -> None:
        """Seed standard agents if missing in agent_configurations."""
        for spec in STANDARD_AGENTS:
            query = select(AgentConfiguration).where(AgentConfiguration.agent_name == spec["agent_name"])
            existing = (await self.session.execute(query)).scalar_one_or_none()
            if not existing:
                new_agent = AgentConfiguration(
                    agent_name=spec["agent_name"],
                    description=spec["description"],
                    model_name=spec["model_name"],
                    system_prompt_template=spec["system_prompt"],
                    temperature=spec["temperature"],
                    is_active=True,
                    status="active",
                    total_executions=0,
                    successful_executions=0,
                    failed_executions=0,
                )
                self.session.add(new_agent)
        await self.session.commit()

    async def list_agent_telemetry(self) -> List[AgentTelemetryResponse]:
        """List all agents with operational telemetry, success rates, and latency."""
        await self._ensure_seed_agents()

        query = select(AgentConfiguration).order_by(AgentConfiguration.agent_name)
        result = await self.session.execute(query)
        agents = result.scalars().all()

        telemetry: List[AgentTelemetryResponse] = []
        for a in agents:
            tot = a.total_executions or 0
            succ = a.successful_executions or 0
            fail = a.failed_executions or 0
            success_rate = round((succ / tot * 100.0), 1) if tot > 0 else 100.0

            telemetry.append(
                AgentTelemetryResponse(
                    id=a.id,
                    agent_name=a.agent_name,
                    description=a.description,
                    model_name=a.model_name,
                    temperature=float(a.temperature),
                    is_active=a.is_active,
                    status=getattr(a, "status", "active") or ("active" if a.is_active else "disabled"),
                    total_executions=tot,
                    successful_executions=succ,
                    failed_executions=fail,
                    success_rate=success_rate,
                    avg_latency_ms=a.avg_latency_ms or 340,
                    last_executed_at=a.last_executed_at,
                )
            )

        return telemetry

    async def update_agent_status(
        self, agent_name: str, new_status: str, admin_user_id: Optional[str] = None
    ) -> AgentTelemetryResponse:
        """Update runtime agent status (active, paused, disabled) and write audit trail."""
        if new_status not in ["active", "paused", "disabled"]:
            raise ValidationException(f"Invalid agent status '{new_status}'. Must be active, paused, or disabled.")

        query = select(AgentConfiguration).where(AgentConfiguration.agent_name == agent_name)
        result = await self.session.execute(query)
        agent = result.scalar_one_or_none()

        if not agent:
            raise NotFoundException(f"Agent '{agent_name}' not found.")

        old_status = getattr(agent, "status", "active")
        agent.status = new_status
        agent.is_active = (new_status == "active")

        # Create audit entry
        audit = AuditLog(
            user_id=admin_user_id,
            action="TOGGLE_AGENT_STATUS",
            resource_type="AgentConfiguration",
            resource_id=agent_name,
            changes_json={
                "old_status": old_status,
                "new_status": new_status,
                "is_active": agent.is_active,
            },
            timestamp=utc_now(),
        )
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(agent)

        tot = agent.total_executions or 0
        succ = agent.successful_executions or 0
        fail = agent.failed_executions or 0
        success_rate = round((succ / tot * 100.0), 1) if tot > 0 else 100.0

        return AgentTelemetryResponse(
            id=agent.id,
            agent_name=agent.agent_name,
            description=agent.description,
            model_name=agent.model_name,
            temperature=float(agent.temperature),
            is_active=agent.is_active,
            status=agent.status,
            total_executions=tot,
            successful_executions=succ,
            failed_executions=fail,
            success_rate=success_rate,
            avg_latency_ms=agent.avg_latency_ms,
            last_executed_at=agent.last_executed_at,
        )

    async def get_agent_execution_logs(
        self, agent_name: str, limit: int = 50
    ) -> AgentExecutionLogsResponse:
        """Fetch chronological execution logs for observability inspection."""
        query = (
            select(AgentExecution)
            .where(AgentExecution.agent_name == agent_name)
            .order_by(desc(AgentExecution.executed_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        logs = result.scalars().all()

        items: List[AgentExecutionLogItem] = [
            AgentExecutionLogItem(
                id=log.id,
                session_id=log.session_id,
                conversation_id=log.conversation_id,
                status=log.status,
                latency_ms=log.latency_ms,
                input_state=log.input_state_json or {},
                output_state=log.output_state_json,
                error_message=log.error_message,
                executed_at=log.executed_at,
            )
            for log in logs
        ]

        return AgentExecutionLogsResponse(
            agent_name=agent_name, executions=items, total=len(items)
        )

