"""Follow-up Coordination Agent adhering to Section 13 of AGENTS.md."""
from typing import Any, Dict
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.ai.tools.agent_tools import ScheduleFollowupReminderTool
from app.core.logging import logger


class FollowUpCoordinationInput(BaseModel):
    customer_id: str
    preferred_channel: str = "email"
    last_interaction_type: str = "indicative_quote"
    consent_active: bool = True
    hours_since_inquiry: int = 24


class FollowUpPlan(BaseModel):
    customer_id: str
    channel: str = Field(description="Channel to dispatch: email, in_app, or advisor_call")
    scheduled_delay_hours: int = Field(description="Optimal wait duration before dispatching")
    message_subject: str = Field(description="Non-intrusive, clear subject line")
    message_body_preview: str = Field(description="Empathetic, helpful draft message")
    compliance_note: str = Field(description="Confirmation of consent and unsubscribe instructions")


class FollowUpCoordinationAgent(BaseAgent):
    id = "follow-up-coordination-agent"
    name = "Follow-up Coordination Agent"
    description = "Manages consent-based follow-up tasks, advisor notifications, and non-intrusive prompts."
    purpose = "Coordinates respectful, timely communication that honors customer consent boundaries."
    input_schema = FollowUpCoordinationInput
    output_schema = FollowUpPlan
    required_permissions = []
    registered_tools = [ScheduleFollowupReminderTool()]
    temperature = 0.1

    async def run(self, input_data: FollowUpCoordinationInput, context: Dict[str, Any]) -> FollowUpPlan:
        if not input_data.consent_active:
            return FollowUpPlan(
                customer_id=input_data.customer_id,
                channel="none",
                scheduled_delay_hours=0,
                message_subject="No Outreach",
                message_body_preview="Outreach suppressed: Customer has not granted active marketing/follow-up consent.",
                compliance_note="Strict consent enforcement applied in compliance with DPDP and IRDAI regulations.",
            )

        prompt = (
            f"You are the Follow-up Coordination Specialist for PS-21.\n"
            f"Parameters:\n"
            f"- Customer ID: {input_data.customer_id}\n"
            f"- Preferred Channel: {input_data.preferred_channel}\n"
            f"- Stage: {input_data.last_interaction_type}\n"
            f"- Hours Inactive: {input_data.hours_since_inquiry}\n\n"
            f"Design a polite, helpful follow-up reminder. Always include opt-out reminder.\n"
            f"Return strict JSON matching FollowUpPlan."
        )

        try:
            response = await mistral_client.chat(
                messages=[
                    {"role": "system", "content": "You are a courteous customer communication AI for regulated insurance. Return strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.get("content", "{}")
            return FollowUpPlan.model_validate_json(content)
        except Exception as e:
            logger.error(f"FollowUpCoordinationAgent execution error: {e}")
            raise
