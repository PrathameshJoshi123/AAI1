"""Risk Information Analysis Agent adhering to Section 13 of AGENTS.md."""
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.ai.tools.agent_tools import ValidateRiskDeclarationsTool
from app.core.logging import logger


class RiskInformationInput(BaseModel):
    customer_id: str
    age: int = 30
    is_smoker: bool = False
    medical_conditions: List[str] = Field(default_factory=list)
    occupation: str = "Standard Office"
    hazardous_activities: List[str] = Field(default_factory=list)
    requested_coverage: float = 250000.0


class StructuredRiskAnalysis(BaseModel):
    customer_id: str
    risk_category: str = Field(description="Standard, Preferred, Substandard, or High_Risk")
    flagged_conditions: List[str] = Field(description="Specific items that may require underwriting scrutiny")
    straight_through_processing: bool = Field(description="Whether the case qualifies for instant digital issue")
    underwriting_notes: str = Field(description="Factual summary prepared for underwriter review")
    recommended_disclosures: List[str] = Field(description="Declarations the customer must confirm under good faith")


class RiskInformationAnalysisAgent(BaseAgent):
    id = "risk-information-analysis-agent"
    name = "Risk Information Analysis Agent"
    description = "Organizes declared risk information without making formal underwriting decisions."
    purpose = (
        "Structures medical, occupational, and lifestyle disclosures for underwriting transparency "
        "while respecting regulatory boundaries."
    )
    input_schema = RiskInformationInput
    output_schema = StructuredRiskAnalysis
    required_permissions = []
    registered_tools = [ValidateRiskDeclarationsTool()]
    temperature = 0.1

    async def run(self, input_data: RiskInformationInput, context: Dict[str, Any]) -> StructuredRiskAnalysis:
        # Evaluate deterministic flags
        validator = ValidateRiskDeclarationsTool()
        tool_ctx = context.get("tool_context")
        tool_res = await validator.execute(
            tool_ctx,
            age=input_data.age,
            is_smoker=input_data.is_smoker,
            has_pre_existing_conditions=len(input_data.medical_conditions) > 0,
            hazardous_occupation="hazardous" in input_data.occupation.lower(),
            desired_sum_assured=input_data.requested_coverage,
        )

        stp_eligible = tool_res.get("straight_through_eligible", True)
        flags = tool_res.get("risk_flags", [])

        prompt = (
            f"You are the Risk Information Analysis Specialist for PS-21.\n"
            f"Applicant Data:\n"
            f"- Age: {input_data.age}\n"
            f"- Tobacco User: {input_data.is_smoker}\n"
            f"- Medical Disclosures: {input_data.medical_conditions}\n"
            f"- Occupation: {input_data.occupation}\n"
            f"- Hazardous Pursuits: {input_data.hazardous_activities}\n"
            f"- Requested Coverage: ${input_data.requested_coverage:,.2f}\n"
            f"Deterministic STP Eligible: {stp_eligible}\n"
            f"Deterministic Flags: {flags}\n\n"
            f"STRICT INSTRUCTIONS:\n"
            f"1. Do not decide policy acceptance or invent loading percentages.\n"
            f"2. Factual structuring only.\n"
            f"3. Return strict JSON matching StructuredRiskAnalysis."
        )

        try:
            response = await mistral_client.chat(
                messages=[
                    {"role": "system", "content": "You are an actuarial risk profiling AI. Return strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.get("content", "{}")
            return StructuredRiskAnalysis.model_validate_json(content)
        except Exception as e:
            logger.error(f"RiskInformationAnalysisAgent execution error: {e}")
            raise
