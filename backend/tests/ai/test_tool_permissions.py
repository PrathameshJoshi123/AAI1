"""Tests for Declarative Tool Registry and Permission Verification."""
import pytest
from app.ai.client.exceptions import ToolExecutionError
from app.ai.tools.base import BaseTool, ToolExecutionContext
from app.ai.tools.registry import ToolRegistry
from app.core.exceptions import PermissionDeniedException
from pydantic import BaseModel, Field


class SampleToolArgs(BaseModel):
    query: str = Field(description="Search parameter")


class SamplePrivilegedTool(BaseTool):
    name = "privileged_search_tool"
    description = "Searches sensitive records. Requires permissions."
    required_permissions = ["cases:review"]
    args_schema = SampleToolArgs

    async def _run(self, context: ToolExecutionContext, args: SampleToolArgs):
        return f"Searched: {args.query}"


@pytest.mark.asyncio
async def test_tool_execution_allowed_with_permission(dummy_tool_context):
    """User possessing required permission successfully executes tool."""
    tool = SamplePrivilegedTool()
    result = await tool.execute(dummy_tool_context, query="Medical Records")
    assert result == "Searched: Medical Records"


@pytest.mark.asyncio
async def test_tool_execution_blocked_without_permission(customer_tool_context):
    """User lacking required permission triggers PermissionDeniedException."""
    tool = SamplePrivilegedTool()
    with pytest.raises(PermissionDeniedException):
        await tool.execute(customer_tool_context, query="Medical Records")


@pytest.mark.asyncio
async def test_tool_registry_dispatch(dummy_tool_context):
    """Tool registry correctly registers, looks up, and dispatches tool execution."""
    registry = ToolRegistry()
    registry.register(SamplePrivilegedTool())

    result = await registry.dispatch(
        "privileged_search_tool",
        dummy_tool_context,
        {"query": "Test Case"},
    )
    assert result == "Searched: Test Case"


@pytest.mark.asyncio
async def test_tool_registry_nonexistent_tool(dummy_tool_context):
    """Dispatching unknown tool name raises ToolExecutionError."""
    registry = ToolRegistry()
    with pytest.raises(ToolExecutionError):
        await registry.dispatch("nonexistent_tool", dummy_tool_context, {})

