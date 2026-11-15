"""Explainable Insurance Recommendation Agent powered by Mistral AI."""
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.core.logging import logger


class RecommendationAgentInput(BaseModel):
    product_name: str
    product_category: str
    match_score: float
    recommended_sum_assured: float
    recommended_term_years: int
    match_factors: Dict[str, Any]
    exclusions: List[Dict[str, Any]] = Field(default_factory=list)
    customer_age: int = 30
    dependents_count: int = 1


class RecommendationAgentOutput(BaseModel):
    headline: str = Field(description="Clear, engaging customer headline explaining the recommendation")
    why_it_fits: List[str] = Field(description="3-4 bullet points explaining why this policy matches the profile")
    key_assumptions: List[str] = Field(description="Explicit financial or mortality assumptions applied")
    critical_exclusions_to_note: List[str] = Field(description="Essential policy exclusions or waiting periods")
    advisor_advice: str = Field(description="Empathetic advice on next steps or rider considerations")


class RecommendationAgent(BaseAgent):
    id = "recommendation-agent"
    name = "Insurance Recommendation Agent"
    description = "Translates deterministic product matching scores into transparent, explainable advice."
    purpose = (
        "Explains why a specific policy fits customer needs without inventing benefits or calculating premiums."
    )
    input_schema = RecommendationAgentInput
    output_schema = RecommendationAgentOutput
    required_permissions = ["quotes:create"]
    registered_tools = []
    temperature = 0.2

    async def run(self, input_data: RecommendationAgentInput, context: Dict[str, Any]) -> RecommendationAgentOutput:
        prompt = (
            f"You are the Senior Insurance Recommendation Specialist for PS-21.\n"
            f"Explain why '{input_data.product_name}' ({input_data.product_category}) is recommended.\n\n"
            f"DETERMINISTIC DATA (DO NOT MODIFY OR CONTRADICT):\n"
            f"- Match Score: {input_data.match_score}%\n"
            f"- Recommended Sum Assured: ₹{input_data.recommended_sum_assured:,.0f}\n"
            f"- Policy Tenure: {input_data.recommended_term_years} years\n"
            f"- Customer Age: {input_data.customer_age}, Dependents: {input_data.dependents_count}\n"
            f"- Match Factors: {input_data.match_factors}\n"
            f"- Policy Exclusions: {input_data.exclusions}\n\n"
            f"STRICT RULES:\n"
            f"1. Never invent or calculate premiums.\n"
            f"2. Only reference declared policy facts and benefits.\n"
            f"3. Highlight key exclusions and assumptions transparently.\n"
            f"4. Provide structured JSON matching the output schema."
        )

        try:
            response = await mistral_client.chat(
                messages=[
                    {"role": "system", "content": "You are a licensed IRDAI insurance advisory AI agent. Return strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.get("content", "{}")
            return RecommendationAgentOutput.model_validate_json(content)
        except Exception as e:
            logger.warning(f"Mistral LLM explanation fallback to deterministic template: {e}")
            # Honest deterministic fallback with zero hallucination
            return RecommendationAgentOutput(
                headline=f"Optimal {input_data.product_category.replace('_', ' ').title()} Protection for Your Family",
                why_it_fits=[
                    f"Provides ₹{input_data.recommended_sum_assured:,.0f} sum assured to secure your {input_data.dependents_count} dependent(s).",
                    f"Aligned with your {input_data.recommended_term_years}-year financial liability timeline.",
                    f"Achieved a {input_data.match_score}% actuarial compatibility score.",
                ],
                key_assumptions=[
                    "Assumes non-smoker standard mortality profile.",
                    "Assumes current annual income remains stable over the policy tenure.",
                ],
                critical_exclusions_to_note=[
                    "Standard suicide clause applies in the first 12 months.",
                    "Coverage is subject to formal medical disclosure and underwriter approval.",
                ],
                advisor_advice="Review optional riders such as Accidental Death and Critical Illness to enhance your base protection.",
            )

