"""Structured Output Parser & Pydantic Validation Engine for Mistral."""
import json
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
from app.ai.client.exceptions import SchemaValidationError
from app.ai.client.mistral_client import LLMUsageMetrics, MistralClientWrapper, mistral_client
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class StructuredLLMResponse(BaseModel):
    """Container for parsed structured data along with execution metadata."""
    raw_content: str
    parsed_json: Dict[str, Any]
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    validation_passed: bool


class StructuredOutputEngine:
    """Manages structured Pydantic schema output extraction and automatic repair."""

    def __init__(self, client: Optional[MistralClientWrapper] = None):
        self.client = client or mistral_client

    async def generate_structured(
        self,
        schema: Type[T],
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.1,
    ) -> tuple[T, StructuredLLMResponse]:
        """
        Requests structured JSON from Mistral and validates it strictly against the target Pydantic schema.
        If validation fails, an automatic single repair attempt is performed.
        """
        json_schema_str = json.dumps(schema.model_json_schema(), indent=2)

        augmented_system_prompt = (
            f"{system_prompt}\n\n"
            "CRITICAL INSTRUCTION: You MUST return a single, valid JSON object conforming exactly to this JSON Schema:\n"
            f"```json\n{json_schema_str}\n```\n"
            "Return ONLY the raw JSON object. Do not wrap in markdown quotes, backticks, or prepend explanatory text."
        )

        messages = [
            {"role": "system", "content": augmented_system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # 1. Primary Attempt
        raw_text, metrics = await self.client.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        try:
            parsed = self._extract_and_validate(raw_text, schema)
            response_meta = StructuredLLMResponse(
                raw_content=raw_text,
                parsed_json=parsed.model_dump(),
                model_name=model or "default",
                prompt_tokens=metrics.prompt_tokens,
                completion_tokens=metrics.completion_tokens,
                total_tokens=metrics.total_tokens,
                latency_ms=metrics.latency_ms,
                validation_passed=True,
            )
            return parsed, response_meta

        except (ValidationError, json.JSONDecodeError) as first_err:
            logger.warning(f"First structured output validation attempt failed: {first_err}. Attempting repair...")

            # 2. Bounded Repair Attempt
            repair_prompt = (
                f"Your previous JSON output failed validation against the schema:\n"
                f"Error: {str(first_err)}\n\n"
                f"Your previous output was:\n{raw_text}\n\n"
                f"Please fix the validation error and return the corrected JSON object conforming exactly to the schema."
            )
            messages.append({"role": "assistant", "content": raw_text})
            messages.append({"role": "user", "content": repair_prompt})

            repaired_text, repair_metrics = await self.client.generate(
                messages=messages,
                model=model,
                temperature=0.0,
                response_format={"type": "json_object"},
            )

            try:
                repaired_parsed = self._extract_and_validate(repaired_text, schema)
                response_meta = StructuredLLMResponse(
                    raw_content=repaired_text,
                    parsed_json=repaired_parsed.model_dump(),
                    model_name=model or "default",
                    prompt_tokens=metrics.prompt_tokens + repair_metrics.prompt_tokens,
                    completion_tokens=metrics.completion_tokens + repair_metrics.completion_tokens,
                    total_tokens=metrics.total_tokens + repair_metrics.total_tokens,
                    latency_ms=metrics.latency_ms + repair_metrics.latency_ms,
                    validation_passed=True,
                )
                logger.info("Structured output repaired successfully on second attempt.")
                return repaired_parsed, response_meta

            except Exception as final_err:
                errors_list = [str(first_err), str(final_err)]
                logger.error(f"Structured repair failed. Raising SchemaValidationError: {errors_list}")
                raise SchemaValidationError(
                    message="Mistral structured output failed Pydantic schema validation after repair attempt.",
                    raw_output=repaired_text,
                    validation_errors=errors_list,
                )

    def _extract_and_validate(self, text: str, schema: Type[T]) -> T:
        """Clean markdown wrapping if present and parse into Pydantic model."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        return schema.model_validate(data)


structured_engine = StructuredOutputEngine()

