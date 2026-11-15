"""Tests for Mistral Client: configuration, bounded retries, token & latency tracking."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.ai.client.exceptions import (
    AIConfigurationError,
    MistralAuthenticationError,
    MistralRateLimitError,
)
from app.ai.client.mistral_client import MistralClientWrapper


@pytest.mark.asyncio
async def test_missing_api_key_raises_configuration_error():
    """Client with empty API key must immediately raise AIConfigurationError."""
    client = MistralClientWrapper(api_key="")
    with pytest.raises(AIConfigurationError) as exc_info:
        await client.generate([{"role": "user", "content": "Hello"}])
    assert "MISTRAL_API_KEY is not configured" in str(exc_info.value)


@pytest.mark.asyncio
async def test_successful_mistral_call_tracks_metrics(mock_mistral_client):
    """Successful LLM generation captures tokens and latency metrics."""
    client, mock_complete = mock_mistral_client

    mock_resp = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "I recommend Term Life Insurance."
    mock_resp.choices = [mock_choice]
    mock_resp.usage.prompt_tokens = 45
    mock_resp.usage.completion_tokens = 12
    mock_resp.usage.total_tokens = 57
    mock_complete.return_value = mock_resp

    content, metrics = await client.generate([{"role": "user", "content": "I need insurance"}])

    assert content == "I recommend Term Life Insurance."
    assert metrics.prompt_tokens == 45
    assert metrics.completion_tokens == 12
    assert metrics.total_tokens == 57
    assert metrics.latency_ms >= 0


@pytest.mark.asyncio
async def test_unauthorized_error_fails_immediately_without_retrying(mock_mistral_client):
    """HTTP 401 must fail immediately with MistralAuthenticationError without retrying."""
    client, mock_complete = mock_mistral_client

    err = Exception("Unauthorized: Invalid API key")
    err.status_code = 401
    mock_complete.side_effect = err

    with pytest.raises(MistralAuthenticationError):
        await client.generate([{"role": "user", "content": "Hello"}])

    # Must be called exactly once (no retry on auth error)
    assert mock_complete.call_count == 1


@pytest.mark.asyncio
async def test_rate_limit_bounded_retries(mock_mistral_client):
    """HTTP 429 rate limit triggers bounded retries up to 3 times before failing."""
    client, mock_complete = mock_mistral_client

    err = Exception("Rate limit reached")
    err.status_code = 429
    mock_complete.side_effect = err

    with pytest.raises(MistralRateLimitError):
        await client.generate([{"role": "user", "content": "Hello"}])

    # Bounded retries: 3 attempts max
    assert mock_complete.call_count == 3

