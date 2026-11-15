"""Base Agent Specification adhering strictly to Section 13 of AGENTS.md."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from app.ai.client.mistral_client import mistral_client
from app.ai.tools.base import BaseTool
from app.core.logging import logger


class BaseAgent(ABC):
    """
    Standardized AI Agent interface.
    Every agent must define its identifier, purpose, schemas, permissions, and tools.
    """
    id: str
    name: str
    description: str
    purpose: str
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    required_permissions: List[str] = []
    registered_tools: List[BaseTool] = []
    model_name: str = "mistral-large-latest"
    temperature: float = 0.2

    def __init__(self):
        self.client = mistral_client

    def get_metadata(self) -> Dict[str, Any]:
        """Returns JSON-serializable agent configuration for Admin oversight."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "purpose": self.purpose,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "required_permissions": self.required_permissions,
            "tools": [t.name for t in self.registered_tools],
            "input_schema": self.input_schema.model_json_schema(),
            "output_schema": self.output_schema.model_json_schema(),
        }

    @abstractmethod
    async def run(self, input_data: BaseModel, context: Dict[str, Any]) -> BaseModel:
        """Executes a single reasoned agent task."""
        pass

