"""Deterministic Actuarial Pricing Engine for Insurance Products."""
from typing import Any, Dict, List, Optional
from app.core.exceptions import BusinessRuleViolationException
from app.models.pricing_matrix import ProductPricingMatrix


class PremiumCalculationBreakdown:
    def __init__(
        self,
        base_annual_rate_per_k: float,
        sum_assured: float,
        age_band: str,
        gender_multiplier: float,
        smoker_loading_factor: float,
        health_tier_factor: float,
        base_annual_premium: float,
        health_loaded_annual_premium: float,
        health_loading_amount: float,
        rider_items: List[Dict[str, Any]],
        rider_annual_premium: float,
        annual_net_premium: float,
        payment_frequency: str,
        frequency_multiplier: float,
        installment_net_premium: float,
        tax_rate_percent: float,
        tax_amount: float,
        total_premium_payable: float,
        matrix_version: str,
    ):
        self.base_annual_rate_per_k = base_annual_rate_per_k
        self.sum_assured = sum_assured
        self.age_band = age_band
        self.gender_multiplier = gender_multiplier
        self.smoker_loading_factor = smoker_loading_factor
        self.health_tier_factor = health_tier_factor
        self.base_annual_premium = base_annual_premium
        self.health_loaded_annual_premium = health_loaded_annual_premium
        self.health_loading_amount = health_loading_amount
        self.rider_items = rider_items
        self.rider_annual_premium = rider_annual_premium
        self.annual_net_premium = annual_net_premium
        self.payment_frequency = payment_frequency
        self.frequency_multiplier = frequency_multiplier
        self.installment_net_premium = installment_net_premium
        self.tax_rate_percent = tax_rate_percent
        self.tax_amount = tax_amount
        self.total_premium_payable = total_premium_payable
        self.matrix_version = matrix_version

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matrix_version": self.matrix_version,
            "pricing_source": "APPROVED_CONFIG_V1",
            "age_band": self.age_band,
            "base_annual_rate_per_k": self.base_annual_rate_per_k,
            "sum_assured": self.sum_assured,
            "factors": {
                "gender_multiplier": self.gender_multiplier,
                "smoker_loading_factor": self.smoker_loading_factor,
                "health_tier_factor": self.health_tier_factor,
                "frequency_multiplier": self.frequency_multiplier,
            },
            "annual_amounts": {
                "base_premium": round(self.base_annual_premium, 2),
                "health_loading": round(self.health_loading_amount, 2),
                "rider_premium": round(self.rider_annual_premium, 2),
                "net_premium": round(self.annual_net_premium, 2),
            },
            "installment_amounts": {
                "payment_frequency": self.payment_frequency,
                "net_installment_premium": round(self.installment_net_premium, 2),
                "tax_rate_percent": self.tax_rate_percent,
                "tax_amount": round(self.tax_amount, 2),
                "total_premium_payable": round(self.total_premium_payable, 2),
            },
            "rider_breakdown": self.rider_items,
        }


class ActuarialPricingService:
    """Executes deterministic mathematical formula-based insurance pricing."""

    @staticmethod
    def resolve_age_band(age: int) -> str:
        if age <= 25:
            return "18-25"
        elif age <= 35:
            return "26-35"
        elif age <= 45:
            return "36-45"
        elif age <= 55:
            return "46-55"
        elif age <= 65:
            return "56-65"
        else:
            return "66-75"

    @classmethod
    def calculate_premium(
        cls,
        matrix: ProductPricingMatrix,
        sum_assured: float,
        policy_term_years: int,
        age: int = 30,
        gender: str = "male",
        is_smoker: bool = False,
        health_tier: str = "standard",
        payment_frequency: str = "annually",
        selected_rider_codes: Optional[List[str]] = None,
    ) -> PremiumCalculationBreakdown:
        if sum_assured <= 0:
            raise BusinessRuleViolationException("Sum Assured must be greater than zero.")

        age_band = cls.resolve_age_band(age)
        age_rates = matrix.age_band_rates_json
        if age_band not in age_rates:
            # Fallback to closest highest age band
            age_band = max(age_rates.keys())

        base_rate = age_rates[age_band]

        # 1. Gender Multiplier
        gender_map = matrix.gender_multipliers_json or {"male": 1.0, "female": 0.9}
        gender_multiplier = gender_map.get(gender.lower(), 1.0)

        # 2. Smoker Factor
        smoker_map = matrix.smoker_loading_factors_json or {"non_smoker": 1.0, "smoker": 1.35}
        smoker_key = "smoker" if is_smoker else "non_smoker"
        smoker_factor = smoker_map.get(smoker_key, 1.0)

        # Base Annual Premium before health loadings
        units_of_thousand = sum_assured / 1000.0
        base_annual_premium = units_of_thousand * base_rate * gender_multiplier * smoker_factor

        # 3. Health Tier Factor
        health_map = matrix.health_tier_loadings_json or {"standard": 1.0, "preferred_plus": 0.95}
        health_tier_factor = health_map.get(health_tier.lower(), 1.0)
        health_loaded_annual_premium = base_annual_premium * health_tier_factor
        health_loading_amount = max(0.0, health_loaded_annual_premium - base_annual_premium)

        # 4. Optional Riders
        rider_cards = matrix.rider_rate_cards_json or {}
        rider_items: List[Dict[str, Any]] = []
        rider_annual_premium = 0.0

        if selected_rider_codes:
            for r_code in selected_rider_codes:
                if r_code in rider_cards:
                    r_card = rider_cards[r_code]
                    r_rate = r_card.get("rate_per_k", 0.0)
                    r_cost = units_of_thousand * r_rate
                    rider_annual_premium += r_cost
                    rider_items.append({
                        "rider_code": r_code,
                        "rider_name": r_card.get("name", r_code),
                        "rate_per_k": r_rate,
                        "annual_cost": round(r_cost, 2),
                    })

        # 5. Annual Net Premium
        annual_net_premium = health_loaded_annual_premium + rider_annual_premium

        # 6. Payment Frequency Multiplier
        freq_map = matrix.frequency_multipliers_json or {
            "annually": 1.0,
            "half_yearly": 0.51,
            "quarterly": 0.26,
            "monthly": 0.088,
        }
        freq_factor = freq_map.get(payment_frequency.lower(), 1.0)
        installment_net_premium = annual_net_premium * freq_factor

        # 7. Statutory Tax (18% GST)
        tax_rate = float(matrix.tax_rate_percent or 18.00)
        tax_amount = installment_net_premium * (tax_rate / 100.0)
        total_premium_payable = installment_net_premium + tax_amount

        return PremiumCalculationBreakdown(
            base_annual_rate_per_k=base_rate,
            sum_assured=sum_assured,
            age_band=age_band,
            gender_multiplier=gender_multiplier,
            smoker_loading_factor=smoker_factor,
            health_tier_factor=health_tier_factor,
            base_annual_premium=base_annual_premium,
            health_loaded_annual_premium=health_loaded_annual_premium,
            health_loading_amount=health_loading_amount,
            rider_items=rider_items,
            rider_annual_premium=rider_annual_premium,
            annual_net_premium=annual_net_premium,
            payment_frequency=payment_frequency,
            frequency_multiplier=freq_factor,
            installment_net_premium=installment_net_premium,
            tax_rate_percent=tax_rate,
            tax_amount=tax_amount,
            total_premium_payable=total_premium_payable,
            matrix_version=matrix.matrix_version,
        )

