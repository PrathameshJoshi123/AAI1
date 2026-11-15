"""Quote Coordination Agent for validating and presenting indicative insurance quotes."""
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent


class QuoteCoordinationInput(BaseModel):
    product_name: str
    sum_assured: float
    policy_term_years: int
    payment_frequency: str
    total_premium: float
    tax_amount: float
    selected_riders: List[str] = Field(default_factory=list)


class QuoteCoordinationOutput(BaseModel):
    summary_message: str = Field(description="Clear, concise message summarizing the indicative quote")
    tax_savings_note: str = Field(description="Applicable statutory tax benefits under Indian tax laws")
    disclaimer_notice: str = Field(description="Mandatory IRDAI regulatory disclosure notice")
    next_steps_guidance: str = Field(description="Clear guidance on how to proceed to proposal onboarding")


class QuoteCoordinationAgent(BaseAgent):
    id = "quote-coordination-agent"
    name = "Quote Coordination Agent"
    description = "Presents deterministic quotes to customers with full statutory compliance disclaimers."
    purpose = "Coordinates quote delivery in conversational interfaces without altering actuarial prices."
    input_schema = QuoteCoordinationInput
    output_schema = QuoteCoordinationOutput
    required_permissions = ["quotes:create"]
    registered_tools = []

    async def run(self, input_data: QuoteCoordinationInput, context: Dict[str, Any]) -> QuoteCoordinationOutput:
        riders_text = f" with {len(input_data.selected_riders)} added rider(s)" if input_data.selected_riders else " with standard benefits"
        
        return QuoteCoordinationOutput(
            summary_message=(
                f"Your indicative quote for {input_data.product_name} provides ₹{input_data.sum_assured:,.0f} "
                f"Sum Assured for {input_data.policy_term_years} years{riders_text}. "
                f"The premium is ₹{input_data.total_premium:,.2f} ({input_data.payment_frequency.title()}), "
                f"which includes ₹{input_data.tax_amount:,.2f} applicable GST."
            ),
            tax_savings_note=(
                "Eligible for tax deductions under Section 80C (life insurance up to ₹1.5 Lakhs) or "
                "Section 80D (health insurance up to ₹75,000) of the Income Tax Act, 1961."
            ),
            disclaimer_notice=(
                "STATUTORY DISCLOSURE: This is an indicative quote based on self-declared parameters. "
                "Final premium and issuance remain subject to formal underwriting review, verification "
                "of medical declarations, and approval by Star Union Life & General Insurance."
            ),
            next_steps_guidance=(
                "To lock in this quote and initiate proposal verification, click 'Apply for this Policy' "
                "to complete your identity and nominee onboarding."
            ),
        )

