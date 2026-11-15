"""Tests for Structured Output Parser and Pydantic validation."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import BaseModel, Field
from app.ai.client.exceptions import SchemaValidationError
from app.ai.client.structured_output import StructuredOutputEngine


class NeedsAssessmentSchema(BaseModel):
    product_category: str = Field(description="Insurance category")
    desired_coverage: float = Field(gt=0, description="Coverage amount")
    urgency: str = Field(description="Low, Medium, or High")


@pytest.mark.asyncio
async def test_structured_output_valid():
    """Valid JSON from LLM validates cleanly into typed Pydantic instance."""
    mock_client = MagicMock()
    mock_metrics = MagicMock(prompt_tokens=30, completion_tokens=15, total_tokens=45, latency_ms=120)
    mock_client.generate = AsyncMock(
        return_value=(
            '{"product_category": "Term Life", "desired_coverage": 500000.0, "urgency": "High"}',
            mock_metrics,
        )
    )

    engine = StructuredOutputEngine(client=mock_client)
    parsed, meta = await engine.generate_structured(
        schema=NeedsAssessmentSchema,
        system_prompt="Assess insurance needs",
        user_prompt="I want 500k life insurance quickly",
    )

    assert isinstance(parsed, NeedsAssessmentSchema)
    assert parsed.product_category == "Term Life"
    assert parsed.desired_coverage == 500000.0
    assert parsed.urgency == "High"
    assert meta.validation_passed is True


@pytest.mark.asyncio
async def test_structured_output_repair_success():
    """Malformed output triggers automatic repair attempt that succeeds."""
    mock_client = MagicMock()
    mock_metrics = MagicMock(prompt_tokens=25, completion_tokens=10, total_tokens=35, latency_ms=100)

    # First attempt: invalid coverage string; Second attempt: valid float
    mock_client.generate = AsyncMock(
        side_effect=[
            ('{"product_category": "Term Life", "desired_coverage": -100, "urgency": "Low"}', mock_metrics),
            ('{"product_category": "Term Life", "desired_coverage": 100000.0, "urgency": "Low"}', mock_metrics),
        ]
    )

    engine = StructuredOutputEngine(client=mock_client)
    parsed, meta = await engine.generate_structured(
        schema=NeedsAssessmentSchema,
        system_prompt="Assess needs",
        user_prompt="I want life insurance",
    )

    assert parsed.desired_coverage == 100000.0
    assert mock_client.generate.call_count == 2


@pytest.mark.asyncio
async def test_structured_output_failure_raises_schema_error():
    """Unrepairable malformed JSON raises SchemaValidationError."""
    mock_client = MagicMock()
    mock_metrics = MagicMock(prompt_tokens=25, completion_tokens=10, total_tokens=35, latency_ms=100)

    # Both attempts invalid
    mock_client.generate = AsyncMock(
        return_value=('{"invalid": "unrelated"}', mock_metrics)
    )

    engine = StructuredOutputEngine(client=mock_client)
    with pytest.raises(SchemaValidationError) as exc_info:
        await engine.generate_structured(
            schema=NeedsAssessmentSchema,
            system_prompt="Assess needs",
            user_prompt="I want life insurance",
        )
    assert "failed Pydantic schema validation" in str(exc_info.value)

