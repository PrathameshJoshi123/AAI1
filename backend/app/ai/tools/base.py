"""Base Tool Abstraction & Permission Verification Engine."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from app.core.exceptions import PermissionDeniedException
from app.core.logging import logger


class ToolExecutionContext:
    """User and authorization context passed into each tool execution."""
    def __init__(self, user_id: str, email: str, roles: List[str], permissions: List[str]):
        self.user_id = user_id
        self.email = email
        self.roles = roles
        self.permissions = permissions

    def has_permission(self, perm: str) -> bool:
        if "Owner" in self.roles or "Admin" in self.roles:
            return True
        return perm in self.permissions

    def has_all_permissions(self, required_perms: List[str]) -> bool:
        return all(self.has_permission(p) for p in required_perms)


class BaseTool(ABC):
    """
    Abstract base class for all registered tools.
    Enforces RBAC validation, argument schema parsing, and execution telemetry.
    """
    name: str
    description: str
    required_permissions: List[str] = []
    args_schema: Type[BaseModel]

    def get_tool_declaration(self) -> Dict[str, Any]:
        """Returns JSON schema specification for Mistral tool declaration."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_json_schema(),
            },
        }

    async def execute(self, context: ToolExecutionContext, **kwargs) -> Any:
        """
        Validates caller permissions and Pydantic arguments before calling _run().
        """
        # 1. Authorization check
        if self.required_permissions:
            if not context.has_all_permissions(self.required_permissions):
                logger.warning(
                    f"Tool '{self.name}' invocation blocked: User '{context.email}' lacks {self.required_permissions}"
                )
                raise PermissionDeniedException(
                    f"Permission denied: Missing required permission for tool '{self.name}'"
                )

        # 2. Argument schema validation
        validated_args = self.args_schema.model_validate(kwargs)

        # 3. Execution
        logger.info(f"Executing tool '{self.name}' for user '{context.email}'")
        return await self._run(context, validated_args)

    @abstractmethod
    async def _run(self, context: ToolExecutionContext, args: Any) -> Any:
        """Concrete execution logic implemented by each tool."""
        pass

