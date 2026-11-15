"""Underwriting Escalation Agent: Advisory risk analysis and discrepancy detection for human underwriters."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent


class UnderwritingEscalationInput(BaseModel):
    case_number: str
    customer_age: int
    annual_income: float
    sum_assured: float
    tobacco_user: bool = False
    medical_declarations: Dict[str, Any] = Field(default_factory=dict)
    existing_coverage_amount: float = 0.0
    document_count: int = 0


class RiskFlagOutput(BaseModel):
    category: str  # medical, financial, lifestyle, identity
    severity: str  # low, medium, high, critical
    flag: str
    source: str


class UnderwritingEscalationOutput(BaseModel):
    case_number: str
    recommended_priority: str  # low, medium, high, urgent
    indicated_risk_tier: str  # preferred, standard, substandard, decline
    risk_flags: List[RiskFlagOutput]
    medical_risk_assessment: str
    financial_risk_assessment: str
    advisory_recommendations: str
    requires_senior_underwriter: bool
    is_binding_decision: bool = False  # Strictly False: AI never makes binding underwriting decisions


class UnderwritingEscalationAgent(BaseAgent):
    id = "underwriting-escalation-agent"
    name = "Underwriting Escalation Agent"
    description = "Assists human underwriters by synthesizing multi-source proposal disclosures, calculating risk tiers, and flagging discrepancies."
    purpose = "Accelerates case triage and risk scrutiny while strictly delegating all binding decisions to authorized human underwriters."
    input_schema = UnderwritingEscalationInput
    output_schema = UnderwritingEscalationOutput
    required_permissions = ["underwriting:evaluate"]
    registered_tools = []

    async def run(self, input_data: UnderwritingEscalationInput, context: Dict[str, Any]) -> UnderwritingEscalationOutput:
        flags: List[RiskFlagOutput] = []
        indicated_tier = "standard"
        priority = "medium"
        requires_senior = False

        # 1. Financial Multiple Check (Income vs Sum Assured)
        if input_data.annual_income > 0:
            multiple = input_data.sum_assured / input_data.annual_income
            if multiple > 25:
                flags.append(
                    RiskFlagOutput(
                        category="financial",
                        severity="high",
                        flag=f"High Sum Assured Multiple ({multiple:.1f}x annual income exceeds standard 25x threshold)",
                        source="proposal_step_3_income",
                    )
                )
                priority = "high"
                requires_senior = True
            elif multiple > 20:
                flags.append(
                    RiskFlagOutput(
                        category="financial",
                        severity="medium",
                        flag=f"Elevated Sum Assured Multiple ({multiple:.1f}x annual income)",
                        source="proposal_step_3_income",
                    )
                )
        else:
            flags.append(
                RiskFlagOutput(
                    category="financial",
                    severity="high",
                    flag="Zero or undeclared annual income on high sum-assured proposal",
                    source="proposal_step_3_income",
                )
            )
            priority = "urgent"

        # 2. Medical Declarations Check
        meds = input_data.medical_declarations
        has_diabetes = bool(meds.get("has_diabetes") or meds.get("diabetes"))
        has_hypertension = bool(meds.get("has_hypertension") or meds.get("hypertension"))
        has_surgery = bool(meds.get("has_surgeries") or meds.get("surgeries"))
        has_heart = bool(meds.get("heart_condition") or meds.get("cardiac"))

        if has_heart:
            flags.append(
                RiskFlagOutput(
                    category="medical",
                    severity="critical",
                    flag="Pre-existing cardiac condition disclosed",
                    source="proposal_step_6_medical",
                )
            )
            indicated_tier = "substandard"
            priority = "urgent"
            requires_senior = True

        if has_diabetes and has_hypertension:
            flags.append(
                RiskFlagOutput(
                    category="medical",
                    severity="high",
                    flag="Co-morbid condition: Both Diabetes Mellitus and Hypertension disclosed",
                    source="proposal_step_6_medical",
                )
            )
            indicated_tier = "substandard"
            priority = "high"
        elif has_diabetes:
            flags.append(
                RiskFlagOutput(
                    category="medical",
                    severity="medium",
                    flag="History of Diabetes disclosed — HbA1c verification recommended",
                    source="proposal_step_6_medical",
                )
            )
            indicated_tier = "substandard"
        elif has_hypertension:
            flags.append(
                RiskFlagOutput(
                    category="medical",
                    severity="medium",
                    flag="History of Hypertension disclosed — BP monitoring records recommended",
                    source="proposal_step_6_medical",
                )
            )

        if has_surgery:
            flags.append(
                RiskFlagOutput(
                    category="medical",
                    severity="low",
                    flag="Past surgical history declared — discharge summary verification advised",
                    source="proposal_step_6_medical",
                )
            )

        # 3. Tobacco / Lifestyle Check
        if input_data.tobacco_user:
            flags.append(
                RiskFlagOutput(
                    category="lifestyle",
                    severity="medium",
                    flag="Active tobacco consumption declared — smoker rates apply",
                    source="proposal_step_6_lifestyle",
                )
            )
            if indicated_tier == "preferred":
                indicated_tier = "standard"

        # 4. Age Check
        if input_data.customer_age > 50:
            flags.append(
                RiskFlagOutput(
                    category="medical",
                    severity="medium",
                    flag=f"Applicant age ({input_data.customer_age}) qualifies for mandatory Tele-Medical / MER review",
                    source="customer_demographics",
                )
            )

        # Synthesis
        med_summary = (
            f"Evaluated health profile for {input_data.customer_age}-year-old applicant. "
            f"{'Tobacco user. ' if input_data.tobacco_user else 'Non-smoker. '}"
            f"{len([f for f in flags if f.category == 'medical'])} clinical risk indicator(s) noted."
        )
        fin_summary = (
            f"Income: ₹{input_data.annual_income:,.2f} vs Requested Coverage: ₹{input_data.sum_assured:,.2f}. "
            f"Existing portfolio: ₹{input_data.existing_coverage_amount:,.2f}."
        )
        advisory = (
            "Advisory Recommendation: Proceed with human clinical review. "
            f"{'Special medical examination required. ' if requires_senior else 'Standard underwriting checks apply. '}"
            "Note: Formal decision must be recorded by licensed underwriter."
        )

        return UnderwritingEscalationOutput(
            case_number=input_data.case_number,
            recommended_priority=priority,
            indicated_risk_tier=indicated_tier,
            risk_flags=flags,
            medical_risk_assessment=med_summary,
            financial_risk_assessment=fin_summary,
            advisory_recommendations=advisory,
            requires_senior_underwriter=requires_senior,
            is_binding_decision=False,
        )

