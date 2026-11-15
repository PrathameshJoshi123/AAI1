"""AI-specific domain exceptions and error definitions."""
from typing import Any, Optional


class AIException(Exception):
    """Base exception for all AI infrastructure errors."""
    def __init__(self, message: str, code: str = "AI_ERROR", details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


class AIConfigurationError(AIException):
    """Raised when required AI configuration (e.g. MISTRAL_API_KEY) is missing or invalid."""
    def __init__(self, message: str = "MISTRAL_API_KEY is not configured. AI operations cannot proceed."):
        super().__init__(message=message, code="AI_CONFIG_ERROR")


class MistralAPIError(AIException):
    """Raised when the Mistral API returns an error."""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message=message, code="MISTRAL_API_ERROR", details=details)
        self.status_code = status_code


class MistralRateLimitError(MistralAPIError):
    """Raised when Mistral rate limit (HTTP 429) is encountered and retries exhausted."""
    def __init__(self, message: str = "Mistral API rate limit exceeded.", details: Optional[Any] = None):
        super().__init__(message=message, status_code=429, details=details)
        self.code = "MISTRAL_RATE_LIMIT"


class MistralAuthenticationError(MistralAPIError):
    """Raised when Mistral rejects the API key (HTTP 401)."""
    def __init__(self, message: str = "Mistral API authentication failed. Verify API key.", details: Optional[Any] = None):
        super().__init__(message=message, status_code=401, details=details)
        self.code = "MISTRAL_AUTH_FAILED"


class SchemaValidationError(AIException):
    """Raised when Mistral structured output fails Pydantic schema validation after repair attempt."""
    def __init__(self, message: str, raw_output: str, validation_errors: list[str]):
        super().__init__(
            message=message,
            code="SCHEMA_VALIDATION_ERROR",
            details={"raw_output": raw_output, "errors": validation_errors},
        )
        self.raw_output = raw_output
        self.validation_errors = validation_errors


class ToolExecutionError(AIException):
    """Raised when a tool invocation fails during graph execution."""
    def __init__(self, tool_name: str, message: str):
        super().__init__(
            message=f"Tool '{tool_name}' execution failed: {message}",
            code="TOOL_EXECUTION_ERROR",
            details={"tool_name": tool_name},
        )


class HumanReviewInterruption(AIException):
    """Raised/signaled when a LangGraph node halts for Human-in-the-Loop approval."""
    def __init__(self, reason: str, case_id: Optional[str] = None, data: Optional[Any] = None):
        super().__init__(
            message=f"Workflow paused for human review: {reason}",
            code="HUMAN_REVIEW_REQUIRED",
            details={"reason": reason, "case_id": case_id, "data": data},
        )

