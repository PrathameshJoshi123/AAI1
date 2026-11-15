"""Prospect Intelligence Agent adhering to Section 13 of AGENTS.md."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.ai.tools.agent_tools import QueryProspectSignalsTool
from app.core.logging import logger


class ProspectSignalInput(BaseModel):
    prospect_id: str
    channel: str = "organic"
    campaign: Optional[str] = None
    device_type: str = "mobile"
    interaction_count: int = 1


class ProspectIntelligenceReport(BaseModel):
    prospect_id: str
    engagement_tier: str = Field(description="Low, Medium, or High engagement tier")
    recommended_approach: str = Field(description="Conversational orientation recommended for customer engagement")
    high_value_indicator: bool = Field(description="Whether signals suggest strong commercial interest")
    rationale: str = Field(description="Transparent reasoning based strictly on observed signals")


class ProspectIntelligenceAgent(BaseAgent):
    id = "prospect-intelligence-agent"
    name = "Prospect Intelligence Agent"
    description = "Interprets permitted acquisition signals and channel context without tracking violations."
    purpose = "Classifies inbound prospect interest to personalize initial conversational onboarding."
    input_schema = ProspectSignalInput
    output_schema = ProspectIntelligenceReport
    required_permissions = []
    registered_tools = [QueryProspectSignalsTool()]
    temperature = 0.1

    async def run(self, input_data: ProspectSignalInput, context: Dict[str, Any]) -> ProspectIntelligenceReport:
        prompt = (
            f"You are the Prospect Intelligence Agent for PS-21 Insurance.\n"
            f"Analyze the inbound customer signals:\n"
            f"- Prospect ID: {input_data.prospect_id}\n"
            f"- Channel: {input_data.channel}\n"
            f"- Campaign: {input_data.campaign or 'Direct'}\n"
            f"- Device: {input_data.device_type}\n"
            f"- Prior Interactions: {input_data.interaction_count}\n\n"
            f"Rules:\n"
            f"1. Do not assume or store sensitive personal attributes.\n"
            f"2. Return strict JSON matching ProspectIntelligenceReport schema."
        )

        try:
            response = await mistral_client.chat(
                messages=[
                    {"role": "system", "content": "You are a professional insurance marketing intelligence AI. Return strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.get("content", "{}")
            return ProspectIntelligenceReport.model_validate_json(content)
        except Exception as e:
            logger.error(f"ProspectIntelligenceAgent execution error: {e}")
            raise
