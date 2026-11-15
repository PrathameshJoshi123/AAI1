"""Actuarial and Deterministic Coverage Calculator Service."""
from app.schemas.calculator import HLVCalculationRequest, HLVCalculationResponse


class CoverageCalculatorService:
    @staticmethod
    def calculate_human_life_value(payload: HLVCalculationRequest) -> HLVCalculationResponse:
        working_years = max(1, payload.retirement_age - payload.current_age)

        # Personal consumption deduction (standard 30% personal maintenance)
        family_dependency_income = payload.annual_income * 0.70

        # Real discount rate adjustment: assuming nominal return of 8% and user-supplied inflation rate
        nominal_return = 0.08
        inflation = payload.inflation_rate_percent / 100.0
        real_rate = (nominal_return - inflation) / (1 + inflation)

        if abs(real_rate) < 0.001:
            capitalized_income = family_dependency_income * working_years
        else:
            # Present Value of Annuity formula: PV = PMT * ((1 - (1+r)^-n) / r)
            capitalized_income = family_dependency_income * ((1 - ((1 + real_rate) ** -working_years)) / real_rate)

        gross_hlv = capitalized_income + payload.outstanding_liabilities
        net_gap = max(0.0, gross_hlv - payload.current_liquid_investments)

        # Round to nearest 5,00,000 INR (actuarial standard for sum assured)
        rounded_recommendation = round(net_gap / 500000.0) * 500000.0
        if rounded_recommendation < 2500000.0:
            rounded_recommendation = 2500000.0  # Industry baseline minimum for term life

        multiplier = round(rounded_recommendation / payload.annual_income, 1)

        return HLVCalculationResponse(
            recommended_term_cover=float(rounded_recommendation),
            human_life_value_raw=round(gross_hlv, 2),
            outstanding_liabilities_component=float(payload.outstanding_liabilities),
            existing_cover_offset=float(payload.current_liquid_investments),
            net_protection_gap=round(net_gap, 2),
            rule_of_thumb_multiplier=f"{multiplier}x Annual Income",
            calculation_breakdown={
                "working_years_remaining": working_years,
                "annual_family_income_secured": round(family_dependency_income, 2),
                "assumed_real_discount_rate_percent": round(real_rate * 100, 2),
                "capitalized_future_income": round(capitalized_income, 2),
                "liabilities_added": payload.outstanding_liabilities,
                "existing_coverage_subtracted": payload.current_liquid_investments,
            },
            formula_explanation=(
                f"Based on {working_years} remaining earning years until age {payload.retirement_age}, "
                f"accounting for {payload.inflation_rate_percent}% inflation and your existing financial assets."
            ),
        )

