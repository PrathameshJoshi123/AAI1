"""Needs Assessment Agent adhering to Section 13 of AGENTS.md."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.ai.tools.agent_tools import RecordCustomerNeedsTool
from app.core.logging import logger


class NeedsAssessmentInput(BaseModel):
    customer_id: str
    age: int = 30
    dependents: int = 1
    annual_income: float = 60000.0
    liabilities_total: float = 0.0
    existing_coverage: float = 0.0
    primary_goal: str = "Income Protection"


class CustomerNeedProfile(BaseModel):
    customer_id: str
    category: str = Field(description="Primary category, e.g. Term Life, Health, Critical Illness")
    recommended_coverage_amount: float = Field(gt=0, description="Actuarially sound coverage benchmark")
    recommended_tenure_years: int = Field(gt=0, description="Recommended policy tenure in years")
    priorities: List[str] = Field(description="Key customer objectives in order of priority")
    life_stage_summary: str = Field(description="Empathetic summary of customer's financial life stage")


class NeedsAssessmentAgent(BaseAgent):
    id = "needs-assessment-agent"
    name = "Needs Assessment Agent"
    description = "Discovers and models family protection, income replacement, and liability coverage requirements."
    purpose = "Quantifies coverage need benchmarks objectively using established financial planning principles."
    input_schema = NeedsAssessmentInput
    output_schema = CustomerNeedProfile
    required_permissions = []
    registered_tools = [RecordCustomerNeedsTool()]
    temperature = 0.1

    async def run(self, input_data: NeedsAssessmentInput, context: Dict[str, Any]) -> CustomerNeedProfile:
        # Actuarial rule of thumb: 10-15x annual income + liabilities - existing coverage
        baseline_coverage = max(
            200_000.0,
            (input_data.annual_income * 10.0) + input_data.liabilities_total - input_data.existing_coverage,
        )
        tenure = max(10, min(40, 65 - input_data.age))

        prompt = (
            f"You are the Needs Assessment Specialist for PS-21 Insurance.\n"
            f"Customer Profile:\n"
            f"- Customer ID: {input_data.customer_id}\n"
            f"- Age: {input_data.age}, Dependents: {input_data.dependents}\n"
            f"- Annual Income: ${input_data.annual_income:,.2f}\n"
            f"- Liabilities: ${input_data.liabilities_total:,.2f}\n"
            f"- Existing Coverage: ${input_data.existing_coverage:,.2f}\n"
            f"- Primary Goal: {input_data.primary_goal}\n\n"
            f"Actuarial Baseline Need: ${baseline_coverage:,.2f} over {tenure} years.\n"
            f"Synthesize this into a structured CustomerNeedProfile. Return strict JSON."
        )

        try:
            response = await mistral_client.chat(
                messages=[
                    {"role": "system", "content": "You are a chartered financial planner AI for insurance. Return strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.get("content", "{}")
            return CustomerNeedProfile.model_validate_json(content)
        except Exception as e:
            logger.error(f"NeedsAssessmentAgent execution error: {e}")
            raise
