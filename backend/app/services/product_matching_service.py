"""Deterministic product matching and fit scoring service."""
from typing import Any, Dict, List, Optional
from app.models.product import InsuranceProduct, ProductConfiguration
from app.models.recommendation import CustomerQualification
from app.services.eligibility_service import EligibilityService


class MatchEvaluationResult:
    def __init__(
        self,
        product: InsuranceProduct,
        configuration: Optional[ProductConfiguration],
        match_score: float,
        recommended_sum_assured: float,
        recommended_term_years: int,
        match_factors: Dict[str, Any],
        assumptions: List[str],
        limitations: List[str],
        alternative_options: List[Dict[str, Any]],
        rationale: str,
    ):
        self.product = product
        self.configuration = configuration
        self.match_score = match_score
        self.recommended_sum_assured = recommended_sum_assured
        self.recommended_term_years = recommended_term_years
        self.match_factors = match_factors
        self.assumptions = assumptions
        self.limitations = limitations
        self.alternative_options = alternative_options
        self.rationale = rationale


class ProductMatchingService:
    """Computes deterministic fit score (0-100) and rationale for customer profiles."""

    @classmethod
    def match_product(
        cls,
        product: InsuranceProduct,
        qualification: Optional[CustomerQualification],
        target_category: Optional[str] = None,
        override_sum_assured: Optional[float] = None,
    ) -> Optional[MatchEvaluationResult]:
        if not product.is_active:
            return None

        # Extract qualification attributes with safe defaults
        age = qualification.age if qualification and qualification.age else 30
        financial_capacity = float(qualification.financial_capacity) if qualification and qualification.financial_capacity else 600000.0
        health_tier = qualification.health_tier if qualification else "standard"
        has_pre_existing = qualification.has_pre_existing_conditions if qualification else False
        dependents = qualification.dependents_count if qualification else 1
        target_cat = target_category or (qualification.target_category if qualification else product.category)

        # 1. Eligibility Check
        eligibility = EligibilityService.evaluate(
            product=product,
            age=age,
            annual_income=financial_capacity,
            is_smoker=False,
            has_pre_existing_conditions=has_pre_existing,
        )
        if not eligibility.is_eligible:
            return None

        # 2. Optimal Sum Assured & Tenure Calculation
        if override_sum_assured and override_sum_assured > 0:
            recommended_sa = float(override_sum_assured)
            recommended_term = max(15, min(40, 65 - age)) if product.category == "term_life" else 1
        elif product.category == "term_life":
            # Standard Human Life Value (HLV) principle: 10x-15x income + liabilities
            recommended_sa = float(qualification.recommended_sum_assured) if qualification and qualification.recommended_sum_assured else max(5000000.0, financial_capacity * 12.0)
            recommended_term = max(15, min(40, 65 - age))
        else:  # Health
            recommended_sa = float(qualification.recommended_sum_assured) if qualification and qualification.recommended_sum_assured else (1000000.0 if dependents > 1 else 500000.0)
            recommended_term = 1  # 1-year renewable

        # 3. Select matching configuration tier
        matching_config: Optional[ProductConfiguration] = None
        for config in product.configurations:
            min_sa = float(config.min_sum_assured)
            max_sa = float(config.max_sum_assured)
            if min_sa <= recommended_sa <= max_sa:
                matching_config = config
                break

        if not matching_config and product.configurations:
            # Pick the configuration tier with the closest boundary
            matching_config = min(
                product.configurations,
                key=lambda c: abs(float(c.min_sum_assured) - recommended_sa),
            )
            # Clamp sum assured to configuration boundaries
            min_sa = float(matching_config.min_sum_assured)
            max_sa = float(matching_config.max_sum_assured)
            recommended_sa = max(min_sa, min(max_sa, recommended_sa))

        # 4. Multi-Factor Scoring (0 to 100)
        # Factor A: Category Alignment (35 pts max)
        cat_score = 35.0 if product.category == target_cat else 15.0

        # Factor B: Coverage Adequacy & Limits (30 pts max)
        cov_score = 28.0
        if matching_config:
            min_sa = float(matching_config.min_sum_assured)
            max_sa = float(matching_config.max_sum_assured)
            if min_sa <= recommended_sa <= max_sa:
                cov_score = 30.0

        # Factor C: Affordability Ratio (20 pts max)
        # Rule of thumb: life insurance should not exceed 4% of annual income
        estimated_annual_cost = (recommended_sa / 1000.0) * 1.8
        cost_ratio = (estimated_annual_cost / financial_capacity) if financial_capacity > 0 else 0.02
        if cost_ratio <= 0.05:
            affordability_score = 20.0
        elif cost_ratio <= 0.10:
            affordability_score = 15.0
        else:
            affordability_score = 10.0

        # Factor D: Health Risk Admissibility (15 pts max)
        if health_tier == "preferred_plus":
            health_score = 15.0
        elif health_tier == "standard":
            health_score = 14.0
        else:
            health_score = 10.0

        total_match_score = round(cat_score + cov_score + affordability_score + health_score, 1)

        # 5. Build Structured Match Factors, Assumptions, Limitations
        match_factors = {
            "category_alignment_score": cat_score,
            "coverage_adequacy_score": cov_score,
            "affordability_score": affordability_score,
            "health_admissibility_score": health_score,
            "financial_capacity": financial_capacity,
            "target_category": target_cat,
            "selected_tier": matching_config.tier_name if matching_config else "Standard",
        }

        assumptions = [
            f"Income protection requirement estimated at {int(recommended_sa / financial_capacity if financial_capacity else 10)}x annual income",
            f"Retirement age projected at 65 years with policy tenure of {recommended_term} years",
            f"Non-smoker standard mortality rate applied (subject to underwriting confirmation)",
        ]

        limitations = [
            "Policy benefits are conditional upon medical disclosures and insurer underwriting approval",
        ]
        if product.exclusions_list_json:
            for exc in product.exclusions_list_json[:2]:
                limitations.append(f"Exclusion: {exc.get('title', 'Standard exclusion')}")

        alternatives: List[Dict[str, Any]] = []
        if product.configurations:
            for cfg in product.configurations:
                if cfg != matching_config:
                    alternatives.append({
                        "tier_name": cfg.tier_name,
                        "min_sum_assured": float(cfg.min_sum_assured),
                        "max_sum_assured": float(cfg.max_sum_assured),
                    })

        rationale = (
            f"{product.name} scored {total_match_score}% fit for your profile. "
            f"The recommended Sum Assured of ₹{recommended_sa:,.0f} provides comprehensive financial "
            f"security for your dependents without exceeding your declared budget."
        )

        return MatchEvaluationResult(
            product=product,
            configuration=matching_config,
            match_score=total_match_score,
            recommended_sum_assured=recommended_sa,
            recommended_term_years=recommended_term,
            match_factors=match_factors,
            assumptions=assumptions,
            limitations=limitations,
            alternative_options=alternatives,
            rationale=rationale,
        )

