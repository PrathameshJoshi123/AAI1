"""Drop-off Detection Agent adhering to Section 13 of AGENTS.md."""
from typing import Any, Dict
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.core.logging import logger


class DropOffDetectionInput(BaseModel):
    session_id: str
    customer_id: str
    last_completed_step: str = "quote_viewed"
    minutes_inactive: int = 45
    funnel_stage: str = "proposal_filling"


class DropOffDiagnosis(BaseModel):
    session_id: str
    customer_id: str
    friction_reason: str = Field(description="Identified cause of stalled progress, e.g. document friction or price check")
    drop_off_probability: float = Field(ge=0.0, le=1.0, description="Estimated churn probability")
    recommended_recovery_action: str = Field(description="Actionable re-engagement strategy")
    should_trigger_followup: bool = Field(description="Whether follow-up coordination should be queued")


class DropOffDetectionAgent(BaseAgent):
    id = "drop-off-detection-agent"
    name = "Drop-off Detection Agent"
    description = "Detects incomplete customer journeys and diagnoses friction points in the onboarding funnel."
    purpose = "Identifies stalled applicants and suggests empathetic, non-intrusive re-engagement."
    input_schema = DropOffDetectionInput
    output_schema = DropOffDiagnosis
    required_permissions = []
    registered_tools = []
    temperature = 0.1

    async def run(self, input_data: DropOffDetectionInput, context: Dict[str, Any]) -> DropOffDiagnosis:
        prompt = (
            f"You are the Drop-off Detection Specialist for PS-21.\n"
            f"Journey Context:\n"
            f"- Customer: {input_data.customer_id}\n"
            f"- Funnel Stage: {input_data.funnel_stage}\n"
            f"- Last Step: {input_data.last_completed_step}\n"
            f"- Inactive Minutes: {input_data.minutes_inactive}\n\n"
            f"Diagnose the friction point and determine if re-engagement is appropriate.\n"
            f"Return strict JSON matching DropOffDiagnosis."
        )

        try:
            response = await mistral_client.chat(
                messages=[
                    {"role": "system", "content": "You are a customer journey analytics AI. Return strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.get("content", "{}")
            return DropOffDiagnosis.model_validate_json(content)
        except Exception as e:
            logger.error(f"DropOffDetectionAgent execution error: {e}")
            raise
