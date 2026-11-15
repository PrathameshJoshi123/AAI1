"""Deterministic eligibility evaluation service for insurance products."""
from typing import Any, Dict, List, Optional
from app.models.product import InsuranceProduct


class EligibilityResult:
    def __init__(self, is_eligible: bool, reasons: List[str], warnings: List[str]):
        self.is_eligible = is_eligible
        self.reasons = reasons
        self.warnings = warnings


class EligibilityService:
    """Evaluates whether a customer profile satisfies hard underwriting gates."""

    @staticmethod
    def evaluate(
        product: InsuranceProduct,
        age: Optional[int],
        annual_income: Optional[float] = None,
        is_smoker: bool = False,
        has_pre_existing_conditions: bool = False,
        sum_assured: Optional[float] = None,
    ) -> EligibilityResult:
        reasons: List[str] = []
        warnings: List[str] = []
        is_eligible = True

        rules = product.base_rules_json or {}

        # 1. Age verification
        min_age = rules.get("min_age", 18)
        max_age = rules.get("max_age", 65)
        if age is not None:
            if age < min_age:
                is_eligible = False
                reasons.append(f"Age {age} is below minimum entry age of {min_age} years.")
            elif age > max_age:
                is_eligible = False
                reasons.append(f"Age {age} exceeds maximum entry age of {max_age} years.")

        # 2. Income threshold
        min_income = rules.get("min_annual_income", 0.0)
        if min_income > 0 and annual_income is not None:
            if annual_income < min_income:
                is_eligible = False
                reasons.append(f"Declared annual income ₹{annual_income:,.0f} is below minimum requirement of ₹{min_income:,.0f}.")

        # 3. Sum Assured boundaries
        if sum_assured is not None and product.configurations:
            all_mins = [float(c.min_sum_assured) for c in product.configurations]
            all_maxs = [float(c.max_sum_assured) for c in product.configurations]
            if float(sum_assured) < min(all_mins):
                is_eligible = False
                reasons.append(f"Requested Sum Assured ₹{sum_assured:,.0f} is below product minimum of ₹{min(all_mins):,.0f}.")
            elif float(sum_assured) > max(all_maxs):
                is_eligible = False
                reasons.append(f"Requested Sum Assured ₹{sum_assured:,.0f} exceeds maximum product limit of ₹{max(all_maxs):,.0f}.")

        # 4. Health & Underwriting warnings
        if has_pre_existing_conditions:
            pe_months = rules.get("pre_existing_waiting_period_months", 24)
            warnings.append(
                f"Declared pre-existing medical conditions will be subject to a {pe_months}-month waiting period upon acceptance."
            )

        if is_smoker:
            smoker_factor = rules.get("smoker_loading_factor", 1.35)
            warnings.append(
                f"Tobacco consumption requires a {int((smoker_factor - 1.0) * 100)}% actuarial mortality risk loading."
            )

        return EligibilityResult(is_eligible=is_eligible, reasons=reasons, warnings=warnings)

