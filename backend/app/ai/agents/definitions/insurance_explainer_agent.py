"""Insurance Terminology and Policy Explainer Agent."""
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.core.logging import logger


class InsuranceExplainerInput(BaseModel):
    term: str = Field(..., description="Insurance term or clause to explain")
    language: str = Field("en", description="Language preference: en or hi")


class InsuranceExplainerOutput(BaseModel):
    term: str
    plain_explanation: str = Field(..., description="Clear explanation avoiding legal jargon")
    why_it_matters: str = Field(..., description="Practical impact on customer claims or premiums")
    suggested_questions: List[str] = Field(default_factory=list)


class InsuranceExplainerAgent(BaseAgent):
    id = "insurance_explainer_agent"
    name = "Insurance Jargon Explainer Agent"
    description = "Demystifies technical insurance terms like waiting periods, co-pays, deductibles, and sub-limits."
    purpose = "Enhance customer literacy and trust without making policy guarantees."
    input_schema = InsuranceExplainerInput
    output_schema = InsuranceExplainerOutput
    required_permissions = []
    temperature = 0.1

    async def run(
        self,
        input_data: InsuranceExplainerInput,
        context: Dict[str, Any] = None,
    ) -> InsuranceExplainerOutput:
        system_prompt = (
            "You are an insurance educator explaining complex concepts in simple, transparent terms. "
            "Never make false guarantees. Keep explanations under 120 words."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Explain the insurance term '{input_data.term}' in language '{input_data.language}'."},
        ]

        try:
            return await mistral_client.generate_structured(
                messages=messages,
                response_format=InsuranceExplainerOutput,
                temperature=self.temperature,
            )
        except Exception as e:
            logger.warning(f"Explainer fallback invoked due to: {e}")
            return InsuranceExplainerOutput(
                term=input_data.term,
                plain_explanation=f"'{input_data.term}' is a key provision in insurance contracts defining how benefits, limits, or claims are handled.",
                why_it_matters="Understanding this clause ensures there are no surprises when you make a claim.",
                suggested_questions=["How does this apply to my policy?", "Are there exceptions?"],
            )

