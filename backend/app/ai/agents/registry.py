"""Agent Discovery, Dynamic Configuration, and Lifecycle Manager."""
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.agents.base import BaseAgent
from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.models.agent import AgentConfiguration


class AgentRegistry:
    """Manages active agents and synchronizes configuration with the database."""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """Registers an agent implementation."""
        self._agents[agent.id] = agent
        logger.info(f"Registered agent: '{agent.name}' (id: {agent.id})")

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        return self._agents.get(agent_id)

    def list_all(self) -> List[Dict[str, Any]]:
        return [agent.get_metadata() for agent in self._agents.values()]

    async def is_agent_active(self, agent_id: str) -> bool:
        """Checks if agent is allowed to run based on Admin Control Centre configuration."""
        async with AsyncSessionLocal() as session:
            stmt = select(AgentConfiguration).where(AgentConfiguration.agent_name == agent_id)
            result = await session.execute(stmt)
            config = result.scalar_one_or_none()
            if not config:
                return True  # Default to active if configuration record not yet created
            return config.is_active and config.status == "active"

    async def sync_with_database(self, session: AsyncSession) -> None:
        """Synchronizes all registered in-memory agents with the database configuration table."""
        for agent_id, agent in self._agents.items():
            stmt = select(AgentConfiguration).where(AgentConfiguration.agent_name == agent_id)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                new_config = AgentConfiguration(
                    agent_name=agent_id,
                    description=agent.description,
                    model_name=agent.model_name,
                    system_prompt_template=getattr(agent, "purpose", "AI Insurance Specialist"),
                    temperature=agent.temperature,
                    is_active=True,
                    status="active",
                    registered_tools_json={"tools": [t.name for t in agent.registered_tools]},
                )
                session.add(new_config)
        await session.commit()
        logger.info(f"Synchronized {len(self._agents)} agents with agent_configurations table.")


agent_registry = AgentRegistry()
