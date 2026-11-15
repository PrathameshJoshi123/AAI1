"""Pytest fixtures for Phase 3 AI infrastructure testing."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.ai.client.mistral_client import LLMUsageMetrics, MistralClientWrapper
from app.ai.tools.base import ToolExecutionContext


@pytest.fixture
def dummy_tool_context():
    return ToolExecutionContext(
        user_id="user-test-uuid-1",
        email="advisor@ps21-insurance.com",
        roles=["Advisor"],
        permissions=["cases:read", "cases:review"],
    )


@pytest.fixture
def customer_tool_context():
    return ToolExecutionContext(
        user_id="cust-test-uuid-2",
        email="customer@ps21-insurance.com",
        roles=["Customer"],
        permissions=[],
    )


@pytest.fixture
def mock_mistral_client():
    client = MistralClientWrapper(api_key="mock-api-key")
    mock_sdk = MagicMock()
    mock_complete = AsyncMock()
    mock_sdk.chat.complete_async = mock_complete
    client._client = mock_sdk
    return client, mock_complete

