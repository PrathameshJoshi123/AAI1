"""Onboarding Agent: Guides applicants through proposal steps, clauses, and statutory disclosures."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent


class OnboardingAgentInput(BaseModel):
    step_name: str = Field(..., description="Active step name, e.g. personal_info, medical_lifestyle, nominee, statutory")
    user_question: Optional[str] = Field(None, description="Optional question from customer")
    product_category: str = Field(default="term_life")
    sum_assured: float = Field(default=10000000)


class OnboardingAgentOutput(BaseModel):
    guidance_message: str = Field(description="Helpful explanation of why this step is required")
    statutory_context: str = Field(description="Explanation of applicable IRDAI rules or Section 45")
    tips: List[str] = Field(description="Helpful tips for smooth proposal completion")
    completion_recommendation: str = Field(description="Next actionable step")


class OnboardingAgent(BaseAgent):
    id = "onboarding-agent"
    name = "Onboarding Agent"
    description = "Guides insurance applicants through multi-step proposal completion and statutory declarations."
    purpose = "Explains legal and medical disclosures in plain language to prevent proposal drop-offs and misstatements."
    input_schema = OnboardingAgentInput
    output_schema = OnboardingAgentOutput
    required_permissions = ["applications:create"]
    registered_tools = []

    async def run(self, input_data: OnboardingAgentInput, context: Dict[str, Any]) -> OnboardingAgentOutput:
        step = input_data.step_name.lower()
        if "nominee" in step:
            return OnboardingAgentOutput(
                guidance_message=(
                    "A nominee is the designated individual entitled to receive the policy proceeds in the event of a claim. "
                    "You can designate up to 3 nominees (e.g., spouse, children, parents). The sum of all allocated shares must equal exactly 100%."
                ),
                statutory_context=(
                    "Under Section 39 of the Insurance Act 1938, if your nominee is under 18 years of age, you must designate an adult Appointee "
                    "who can receive funds on their behalf until they reach maturity."
                ),
                tips=[
                    "Ensure nominee's legal name matches their Aadhaar or PAN card exactly.",
                    "Verify the date of birth to prevent disputes during claim processing.",
                    "If splitting between two nominees (e.g. two children), allocate 50% to each.",
                ],
                completion_recommendation="Enter your nominee's name, relationship, and allocation percentage to complete this step.",
            )
        elif "medical" in step or "lifestyle" in step:
            return OnboardingAgentOutput(
                guidance_message=(
                    "Medical disclosures provide underwriters with the facts required to assess your risk profile accurately. "
                    "Full and honest disclosure guarantees that future claims will be paid without dispute or delay."
                ),
                statutory_context=(
                    "Section 45 of the Insurance Act 1938 stipulates that a policy cannot be questioned after 3 continuous years "
                    "except in cases of established fraudulent non-disclosure. Transparent declarations now safeguard your family's coverage."
                ),
                tips=[
                    "Disclose any medication you take regularly (e.g. for blood pressure or thyroid).",
                    "Declare any past hospitalizations or surgical procedures within the past 5 years.",
                    "Disclose tobacco usage transparently; non-smoker rates only apply if completely tobacco-free for 36 months.",
                ],
                completion_recommendation="Fill in height, weight, and answer each medical disclosure truthfully.",
            )
        elif "statutory" in step:
            return OnboardingAgentOutput(
                guidance_message=(
                    "The statutory declaration step confirms that all information provided across your application is true, accurate, and complete."
                ),
                statutory_context=(
                    "In accordance with the Digital Personal Data Protection (DPDP) Act 2023 and IRDAI regulations, your data is processed "
                    "strictly for underwriting and KYC validation and is protected under bank-grade security protocols."
                ),
                tips=[
                    "Carefully read the declaration statements before checking the acknowledgment boxes.",
                    "Your electronic sign-off creates a tamper-evident SHA-256 proposal checksum.",
                ],
                completion_recommendation="Agree to the statutory declarations to proceed to final document upload.",
            )
        else:
            return OnboardingAgentOutput(
                guidance_message=(
                    "Please ensure all personal and demographic information matches your official government identity documents."
                ),
                statutory_context=(
                    "IRDAI Master Guidelines on KYC mandate valid PAN and residential address proofs before policy issuance."
                ),
                tips=[
                    "Use your full name as printed on your PAN card.",
                    "Ensure your mobile number is active for OTP and underwriter verification calls.",
                ],
                completion_recommendation="Verify your details and click 'Next Step' to proceed.",
            )
