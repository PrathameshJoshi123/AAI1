"""Diagnostic AI Agent for automated testing and health verification."""
from typing import Any, Dict
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent


class DiagnosticInput(BaseModel):
    query: str = Field(description="Diagnostic test input query")


class DiagnosticOutput(BaseModel):
    status: str = Field(description="Diagnostic execution status")
    echo: str = Field(description="Processed echo query")
    model_used: str = Field(description="Model identifier")


class DiagnosticAgent(BaseAgent):
    id = "diagnostic-agent"
    name = "Diagnostic Verification Agent"
    description = "Foundational verification agent for AI infrastructure testing and diagnostics."
    purpose = "Used to verify structured output parsing, schema compliance, and Mistral connectivity."
    input_schema = DiagnosticInput
    output_schema = DiagnosticOutput
    required_permissions = []
    registered_tools = []

    async def run(self, input_data: DiagnosticInput, context: Dict[str, Any]) -> DiagnosticOutput:
        return DiagnosticOutput(
            status="healthy",
            echo=input_data.query,
            model_used=self.model_name,
        )

