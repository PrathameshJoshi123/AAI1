"""Configuration and settings for Mistral and AI Infrastructure."""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

class AIConfig(BaseSettings):
    """Configuration for AI models, Mistral client, and LangGraph orchestration."""
    model_config = SettingsConfigDict(
        env_file=_ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    MISTRAL_API_KEY: Optional[str] = Field(default=None, description="Mistral AI API Secret Key")
    MISTRAL_MODEL: Optional[str] = Field(default="ministral-8b-2512", description="Mistral Model from .env")
    MISTRAL_DEFAULT_MODEL: str = Field(default="ministral-8b-2512", description="Primary reasoning model")
    MISTRAL_FAST_MODEL: str = Field(default="ministral-8b-2512", description="Fast extraction/classification model")
    MISTRAL_TEMPERATURE: float = Field(default=0.2, ge=0.0, le=1.0, description="Sampling temperature")
    MISTRAL_MAX_TOKENS: int = Field(default=2048, gt=0, description="Max generation tokens")
    MISTRAL_REQUEST_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0.0, description="Client HTTP timeout")
    
    # LangGraph & Execution Guardrails
    GRAPH_MAX_RECURSION_LIMIT: int = Field(default=25, description="Max graph step execution depth")
    GRAPH_EXECUTION_TIMEOUT_SECONDS: float = Field(default=60.0, description="Max graph invocation duration")
    CHECKPOINTS_DB_PATH: str = Field(default="checkpoints.db", description="SQLite DB for LangGraph thread persistence")


ai_config = AIConfig()
