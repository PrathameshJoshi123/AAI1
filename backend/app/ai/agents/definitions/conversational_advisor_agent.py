"""Conversational Insurance Advisor Agent for Phase 5 Customer Experience."""
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.core.logging import logger


class ActionButton(BaseModel):
    label: str = Field(..., description="Action button label (e.g. 'View & Customize Quote', 'Start Onboarding')")
    url: str = Field(..., description="Target relative URL (e.g. '/customer/quotes?product_id=...&sum_assured=10000000&term=30')")
    variant: str = Field("default", description="Button visual variant: 'default', 'outline', or 'secondary'")


class ConversationalAdvisorInput(BaseModel):
    user_message: str = Field(..., description="Customer message")
    language: str = Field("en", description="Preferred language (en or hi)")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    customer_profile: Dict[str, Any] = Field(default_factory=dict)
    qualification_data: Dict[str, Any] = Field(default_factory=dict)
    available_plans: List[Dict[str, Any]] = Field(default_factory=list, description="Approved active catalog plans from database")


class ConversationalAdvisorOutput(BaseModel):
    response_text: str = Field(..., description="Advisor response message")
    suggested_chips: List[str] = Field(default_factory=list, description="2-4 short quick-reply options")
    recommended_category: Optional[str] = Field(None, description="Recommended category if identified: term_life, health, motor")
    missing_info_prompt: Optional[str] = Field(None, description="Single question asked to gather missing requirement")
    action_buttons: List[ActionButton] = Field(default_factory=list, description="Interactive action buttons to guide user to quotes, onboarding, or recommendations")
    widget: Optional[Dict[str, Any]] = Field(None, description="Inline widget configuration if applicable")
    indicative_disclaimer: str = Field(
        "Indicative Estimate: Actual coverage, rates, and terms are subject to formal insurer underwriting.",
        description="Mandatory compliance disclaimer",
    )


class ConversationalAdvisorAgent(BaseAgent):
    id = "conversational_advisor_agent"
    name = "Conversational Insurance Advisor Agent"
    description = "Guides customers through needs discovery, explains terminology, and asks progressive questions."
    purpose = "Understand protection requirements and guide customers toward indicative quotes without hallucination."
    input_schema = ConversationalAdvisorInput
    output_schema = ConversationalAdvisorOutput
    required_permissions = []
    temperature = 0.2

    async def run(
        self,
        input_data: ConversationalAdvisorInput,
        context: Dict[str, Any] = None,
    ) -> ConversationalAdvisorOutput:
        lang_prompt = (
            "Respond in English with a professional, transparent, and empathetic tone."
            if input_data.language == "en"
            else "Respond in clear, accessible Hindi (Devanagari script) with a professional and helpful tone."
        )

        plans_text = ""
        if input_data.available_plans:
            plans_text = "OFFICIAL ACTIVE INSURANCE PLANS FROM DATABASE (STRICT GROUND TRUTH):\n"
            for p in input_data.available_plans:
                plans_text += (
                    f"- Product Name: {p.get('name')} (Code: {p.get('code')}, Category: {p.get('category')}, Database ID: {p.get('id')})\n"
                    f"  Insurer: {p.get('insurer_name', 'Star Union Life & General')}\n"
                    f"  Description: {p.get('description', '')}\n"
                    f"  Approved Tiers & Coverage Limits: {p.get('configurations_summary', '')}\n"
                    f"  Policy Benefits: {', '.join(p.get('key_benefits', []))}\n"
                    f"  Actuarial Pricing Rules: {p.get('pricing_summary', '')}\n"
                    f"  Exact Quote URL Template: /customer/quotes?product_id={p.get('id')}&sum_assured=10000000&term=30\n\n"
                )
        else:
            plans_text = (
                "OFFICIAL ACTIVE INSURANCE PLANS FROM DATABASE:\n"
                "- Product Name: Term Secure Plus (Code: TERM_SECURE_PLUS, Category: term_life, Insurer: Star Union Life & General)\n"
                "  Coverage: Pure risk term life cover from ₹25L to ₹5Cr, 10 to 40 years term, 98.7% CSR, terminal illness acceleration, Section 80C tax benefits.\n"
                "- Product Name: Health Shield Pro (Code: HEALTH_SHIELD_PRO, Category: health, Insurer: Star Union Life & General)\n"
                "  Coverage: Hospitalization cover with zero co-pay, 10,000+ cashless hospitals, Section 80D tax benefits.\n"
            )

        system_prompt = f"""You are the certified PS-21 Conversational Insurance Advisor.
{lang_prompt}

{plans_text}

STRICT NON-NEGOTIABLE OPERATIONAL RULES:
1. ONLY USE REAL PLANS FROM THE DATABASE LIST ABOVE:
   - Always base your recommendations and answers strictly on the approved plans listed above (e.g. "Term Secure Plus" for term life, "Health Shield Pro" for health).
   - If the user asks what plans are available or asks for recommendations, list and explain the matching plans from the database list above.
   - Detail their actual verified benefits (e.g., 98.7% claim settlement ratio, terminal illness acceleration, Section 80C/80D tax exemptions).
   - Never invent imaginary plan names, other insurers, or unconfigured limits.

2. CLEAN RESPONSE TEXT (NO RAW JSON LEAKS):
   - The `response_text` field MUST contain ONLY natural, helpful, conversational Markdown text for the customer.
   - NEVER output raw JSON, code fences containing JSON, 'Suggested Chips:', or 'Action Button:' in `response_text`.
   - Put all clickable interactive buttons into the structured `action_buttons` field array.
   - Put all quick-reply choices into the structured `suggested_chips` field array.

3. ACTION BUTTONS SCHEMA:
   - Whenever a quote, recommendation, or next action is relevant, provide 1 to 3 items in `action_buttons`.
   - The URL parameter names MUST be snake_case with underscores: `product_id`, `sum_assured`, and `term`. Never omit underscores (do NOT use productid or sumassured).
   - Example Term Life Quote Button:
     `{{"label": "View & Customize Quote for ₹1 Crore (30 yrs)", "url": "/customer/quotes?product_id={input_data.available_plans[0].get('id') if input_data.available_plans else ''}&sum_assured=10000000&term=30", "variant": "default"}}`
   - Example Proposal Onboarding Button:
     `{{"label": "Start Proposal Onboarding", "url": "/customer/onboarding", "variant": "secondary"}}`

4. DO NOT STOP IN BETWEEN OR SAY "PLEASE HOLD ON":
   When the customer confirms interest or requests a formal quote, explain the upcoming steps (actuarial breakdown, KYC & nominee designation, declarations, underwriting) and provide the direct quote button.

5. ASK EXACTLY ONE FOCUSED QUESTION AT A TIME when gathering missing requirements.
6. COMPLIANCE: Every response must reflect that quotes are indicative and subject to formal underwriting.
"""

        messages = [{"role": "system", "content": system_prompt}]
        for turn in input_data.conversation_history[-6:]:
            messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})
        messages.append({"role": "user", "content": input_data.user_message})

        try:
            parsed = await mistral_client.generate_structured(
                messages=messages,
                response_format=ConversationalAdvisorOutput,
                temperature=self.temperature,
            )
            # Ensure action buttons exist if user asked for a quote
            user_msg_lower = input_data.user_message.lower()
            if any(k in user_msg_lower for k in ["quote", "proceed", "apply", "1 crore", "yes", "formal"]) and not parsed.action_buttons:
                term_prod_id = input_data.available_plans[0].get("id") if input_data.available_plans else ""
                parsed.action_buttons = [
                    ActionButton(
                        label="View & Customize Formal Quote",
                        url=f"/customer/quotes?product_id={term_prod_id}&sum_assured=10000000&term=30" if term_prod_id else "/customer/quotes",
                        variant="default",
                    ),
                    ActionButton(
                        label="Start Proposal Onboarding",
                        url="/customer/onboarding",
                        variant="secondary",
                    ),
                ]
            return parsed
        except Exception as e:
            logger.warning(f"Mistral structured completion encountered error: {e}. Generating compliant structured output.")
            is_hindi = input_data.language == "hi"
            term_prod_id = input_data.available_plans[0].get("id") if input_data.available_plans else ""
            quote_url = f"/customer/quotes?product_id={term_prod_id}&sum_assured=10000000&term=30" if term_prod_id else "/customer/quotes"
            
            user_msg_lower = input_data.user_message.lower()
            if any(k in user_msg_lower for k in ["quote", "formal", "proceed", "yes", "1 crore"]):
                msg = (
                    "Here is your next step for the **Term Secure Plus** policy (₹1 Crore cover for 30 years by Star Union Life & General Insurance):\n\n"
                    "**What happens next:**\n"
                    "1. **Formal Quote Customization:** Check the exact premium breakdown (~₹1,056/month base + 18% GST) and select payment schedule.\n"
                    "2. **Proposal Application:** Fill in nominee details (Section 39) and personal KYC (Aadhaar / PAN).\n"
                    "3. **Medical & Lifestyle Declarations:** Simple self-declaration with tele-MER verification under Section 45.\n"
                    "4. **Policy Issuance:** Instant digital policy generation upon underwriting approval.\n\n"
                    "Click the button below to review your formal quote and begin onboarding:"
                ) if not is_hindi else (
                    "**Term Secure Plus** (₹1 करोड़ कवर, 30 वर्ष) के लिए आपके अगले कदम:\n\n"
                    "1. **औपचारिक कोटेशन समीक्षा:** प्रीमियम विवरण (~₹1,056/माह + GST) देखें।\n"
                    "2. **प्रस्ताव फॉर्म:** नॉमिनी विवरण और केवाईसी पूरा करें।\n"
                    "3. **चिकित्सा घोषणा:** स्वास्थ्य घोषणा और टेली-एमईआर।\n"
                    "4. **पॉलिसी जारी:** त्वरित अंडरराइटिंग और पॉलिसी डिलीवरी।"
                )
                action_buttons = [
                    ActionButton(label="View & Customize Formal Quote", url=quote_url, variant="default"),
                    ActionButton(label="Start Proposal Onboarding", url="/customer/onboarding", variant="secondary"),
                    ActionButton(label="Explore All Plans", url="/customer/recommendations", variant="outline"),
                ]
                chips = ["Proceed to Proposal", "Add Accidental Rider", "Change Payment to Annual", "Talk to Advisor"]
            else:
                msg = (
                    "Namaste! Aapke parivar ki suraksha ke liye hum Star Union Life ki **Term Secure Plus** aur **Health Shield Pro** provide karte hain. Aap kis prakar ka insurance dekh rahe hain?"
                    if is_hindi
                    else "Hello! I am your PS-21 Insurance Advisor. We offer approved **Term Secure Plus** (pure life cover up to ₹5 Cr) and **Health Shield Pro** underwritten by Star Union Life & General. What coverage amount or plan would you like to explore?"
                )
                action_buttons = [
                    ActionButton(label="Explore Approved Plans", url="/customer/recommendations", variant="default"),
                    ActionButton(label="Calculate Human Life Value", url="/customer/calculator", variant="outline"),
                ]
                chips = (
                    ["Term Secure Plus (₹1 Cr)", "Health Shield Pro", "Calculate My Need"]
                    if is_hindi
                    else ["₹1 Crore Term Cover", "Family Health Plan", "Calculate Coverage", "Explore All Plans"]
                )

            return ConversationalAdvisorOutput(
                response_text=msg,
                suggested_chips=chips,
                recommended_category="term_life",
                action_buttons=action_buttons,
                missing_info_prompt=None,
            )
