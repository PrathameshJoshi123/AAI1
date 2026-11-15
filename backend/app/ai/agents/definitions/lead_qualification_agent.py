"""Lead Qualification Agent adhering to Section 13 of AGENTS.md."""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.ai.tools.agent_tools import EvaluateLeadQualificationTool
from app.core.logging import logger


class LeadQualificationInput(BaseModel):
    prospect_id: str
    contact_verified: bool = True
    declared_income: Optional[float] = None
    primary_goal: str = "Protection"
    urgency: str = "medium"


class LeadQualificationScorecard(BaseModel):
    prospect_id: str
    qualification_status: str = Field(description="Qualified, Needs_Information, or Disqualified")
    qualification_score: int = Field(ge=0, le=100, description="Deterministic qualification rating")
    ready_for_advisor: bool = Field(description="Whether case is mature enough for human advisor assignment")
    priority_level: str = Field(description="Low, Medium, High, or Urgent priority")
    reasoning: str = Field(description="Brief explanation of qualification outcome")


class LeadQualificationAgent(BaseAgent):
    id = "lead-qualification-agent"
    name = "Lead Qualification Agent"
    description = "Assesses prospect intent, information completeness, and readiness for quotation."
    purpose = "Evaluates inbound lead readiness and prioritizes sales/advisor outreach."
    input_schema = LeadQualificationInput
    output_schema = LeadQualificationScorecard
    required_permissions = []
    registered_tools = [EvaluateLeadQualificationTool()]
    temperature = 0.1

    async def run(self, input_data: LeadQualificationInput, context: Dict[str, Any]) -> LeadQualificationScorecard:
        # Run deterministic tool first
        eval_tool = EvaluateLeadQualificationTool()
        tool_ctx = context.get("tool_context")
        tool_res = await eval_tool.execute(
            tool_ctx,
            prospect_id=input_data.prospect_id,
            has_contact_info=input_data.contact_verified,
            expressed_intent=input_data.urgency,
            annual_income=input_data.declared_income,
        )

        score = tool_res.get("calculated_score", 50)
        is_qualified = tool_res.get("is_qualified", False)

        prompt = (
            f"You are the Lead Qualification Agent for PS-21.\n"
            f"Synthesize the qualification scorecard using these deterministic calculations:\n"
            f"- Prospect ID: {input_data.prospect_id}\n"
            f"- Deterministic Score: {score}/100\n"
            f"- Eligible: {is_qualified}\n"
            f"- Primary Goal: {input_data.primary_goal}\n"
            f"- Urgency: {input_data.urgency}\n\n"
            f"Return strict JSON matching LeadQualificationScorecard."
        )

        try:
            response = await mistral_client.chat(
                messages=[
                    {"role": "system", "content": "You are an automated insurance lead qualification specialist. Return strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.get("content", "{}")
            return LeadQualificationScorecard.model_validate_json(content)
        except Exception as e:
            logger.error(f"LeadQualificationAgent execution error: {e}")
            raise
