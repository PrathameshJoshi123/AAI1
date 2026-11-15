"""Hardened Asynchronous Mistral Client using LangChain MistralAI with Structured Output & Instrumentation."""
import asyncio
import time
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

from app.ai.client.exceptions import (
    AIConfigurationError,
    MistralAPIError,
    MistralAuthenticationError,
    MistralRateLimitError,
)
from app.ai.config import ai_config
from app.core.config import settings
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class LLMUsageMetrics:
    """Captured metrics for an LLM execution turn."""
    def __init__(self, prompt_tokens: int, completion_tokens: int, total_tokens: int, latency_ms: int):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        self.latency_ms = latency_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
        }


def _convert_messages(messages: List[Any]) -> List[BaseMessage]:
    """Convert raw role-dict or BaseMessage list to LangChain message objects."""
    converted: List[BaseMessage] = []
    for msg in messages:
        if isinstance(msg, BaseMessage):
            converted.append(msg)
        elif isinstance(msg, dict):
            role = msg.get("role", "user").lower()
            content = msg.get("content", "")
            if role == "system":
                converted.append(SystemMessage(content=content))
            elif role in ("assistant", "agent"):
                converted.append(AIMessage(content=content))
            else:
                converted.append(HumanMessage(content=content))
        elif isinstance(msg, tuple) and len(msg) == 2:
            role, content = msg
            if role == "system":
                converted.append(SystemMessage(content=content))
            elif role in ("assistant", "agent"):
                converted.append(AIMessage(content=content))
            else:
                converted.append(HumanMessage(content=content))
    return converted


class MistralClientWrapper:
    """Mistral AI Client powered by LangChain ChatMistralAI."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key

    @property
    def api_key(self) -> Optional[str]:
        return (
            self._api_key
            or ai_config.MISTRAL_API_KEY
            or getattr(settings, "MISTRAL_API_KEY", None)
        )

    def _get_llm(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> ChatMistralAI:
        """Initialize ChatMistralAI with configuration parameters."""
        key = self.api_key
        if not key or not key.strip():
            raise AIConfigurationError(
                "MISTRAL_API_KEY is not configured or empty. AI operations cannot proceed."
            )

        target_model = (
            model
            or ai_config.MISTRAL_MODEL
            or ai_config.MISTRAL_DEFAULT_MODEL
            or "ministral-8b-2512"
        )
        target_temp = temperature if temperature is not None else ai_config.MISTRAL_TEMPERATURE
        target_max_tokens = max_tokens or ai_config.MISTRAL_MAX_TOKENS

        return ChatMistralAI(
            model=target_model,
            mistral_api_key=key.strip(),
            temperature=target_temp,
            max_tokens=target_max_tokens,
            timeout=ai_config.MISTRAL_REQUEST_TIMEOUT_SECONDS,
        )

    async def generate_structured(
        self,
        messages: List[Any],
        response_format: Type[T],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> T:
        """Generate typed, structured Pydantic output using LangChain with_structured_output."""
        llm = self._get_llm(model=model, temperature=temperature)
        structured_llm = llm.with_structured_output(response_format)
        formatted_messages = _convert_messages(messages)

        start_time = time.perf_counter()
        try:
            result = await structured_llm.ainvoke(formatted_messages)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info(f"Mistral structured call succeeded | Latency: {elapsed_ms}ms")
            return result
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error(f"Mistral structured call failed ({elapsed_ms}ms): {e}")
            raise

    async def generate(
        self,
        messages: List[Any],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> tuple[str, LLMUsageMetrics]:
        """Execute chat completion via LangChain ChatMistralAI."""
        llm = self._get_llm(model=model, temperature=temperature, max_tokens=max_tokens)
        formatted_messages = _convert_messages(messages)

        start_time = time.perf_counter()
        try:
            response = await llm.ainvoke(formatted_messages)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            content = response.content if isinstance(response.content, str) else str(response.content)
            usage = getattr(response, "usage_metadata", None) or {}
            metrics = LLMUsageMetrics(
                prompt_tokens=usage.get("input_tokens", 0),
                completion_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                latency_ms=elapsed_ms,
            )

            logger.info(
                f"Mistral LLM call succeeded | Latency: {elapsed_ms}ms | Tokens: {metrics.total_tokens}"
            )
            return content, metrics

        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            error_str = str(e)
            logger.error(f"Mistral invocation failed ({elapsed_ms}ms): {error_str}")
            if "unauthorized" in error_str.lower() or "invalid api key" in error_str.lower():
                raise MistralAuthenticationError(f"Mistral authentication failed: {error_str}") from e
            if "rate limit" in error_str.lower():
                raise MistralRateLimitError(f"Mistral rate limit exceeded: {error_str}") from e
            raise MistralAPIError(f"Mistral API request failed: {error_str}") from e


# Singleton default client
mistral_client = MistralClientWrapper()
