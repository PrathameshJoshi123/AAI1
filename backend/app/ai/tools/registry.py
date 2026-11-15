"""Central Tool Registry and Invocation Dispatcher."""
from typing import Any, Dict, List, Optional
from app.ai.client.exceptions import ToolExecutionError
from app.ai.tools.base import BaseTool, ToolExecutionContext
from app.core.logging import logger


class ToolRegistry:
    """Registry managing available tools and dispatching execution."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """Registers a tool instance."""
        if tool.name in self._tools:
            logger.warning(f"Overwriting previously registered tool '{tool.name}'")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: '{tool.name}'")

    def get(self, tool_name: str) -> Optional[BaseTool]:
        return self._tools.get(tool_name)

    def list_all(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get_declarations(self, context: Optional[ToolExecutionContext] = None) -> List[Dict[str, Any]]:
        """Returns JSON declarations for all tools that context has permission to use."""
        declarations = []
        for tool in self._tools.values():
            if context is None or context.has_all_permissions(tool.required_permissions):
                declarations.append(tool.get_tool_declaration())
        return declarations

    async def dispatch(self, tool_name: str, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        """Executes a named tool with context and arguments."""
        tool = self.get(tool_name)
        if not tool:
            raise ToolExecutionError(tool_name, f"Tool '{tool_name}' not found in registry.")

        try:
            return await tool.execute(context, **arguments)
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            raise


tool_registry = ToolRegistry()

