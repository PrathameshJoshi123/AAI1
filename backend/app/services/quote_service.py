"""Deterministic Insurance Quote Calculation and Persistence Service."""
from datetime import datetime, timedelta, timezone
import random
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.models.recommendation import Quote
from app.repositories.product_repository import ProductRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.pricing_matrix_repository import PricingMatrixRepository
from app.schemas.quote import QuoteCreate, QuoteRecalculateRequest
from app.services.actuarial_pricing_service import ActuarialPricingService


class QuoteService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.quote_repo = QuoteRepository(session)
        self.matrix_repo = PricingMatrixRepository(session)

    async def calculate_and_create_quote(
        self,
        customer_id: str,
        data: QuoteCreate,
        age: int = 30,
        gender: str = "male",
        is_smoker: bool = False,
        health_tier: str = "standard",
    ) -> Quote:
        """Calculate actuarial premium deterministically and persist quote."""
        product = await self.product_repo.get_by_id_with_details(data.product_id)
        if not product or not product.is_active:
            raise EntityNotFoundException("Selected insurance product is not available or inactive.")

        # Match configuration tier
        config = None
        if data.configuration_id:
            config = next((c for c in product.configurations if c.id == data.configuration_id), None)
        if not config:
            config = next((c for c in product.configurations if c.min_sum_assured <= data.sum_assured <= c.max_sum_assured), None)

        if not config and product.configurations:
            # Safely clamp to product's allowable configuration tiers
            all_mins = [float(c.min_sum_assured) for c in product.configurations]
            all_maxs = [float(c.max_sum_assured) for c in product.configurations]
            min_limit = min(all_mins) if all_mins else 100000.0
            max_limit = max(all_maxs) if all_maxs else 50000000.0

            if data.sum_assured < min_limit:
                data.sum_assured = min_limit
            elif data.sum_assured > max_limit:
                data.sum_assured = max_limit

            config = next((c for c in product.configurations if c.min_sum_assured <= data.sum_assured <= c.max_sum_assured), product.configurations[0])

        # Validate and clamp term options if configured
        if config and config.term_options_json and isinstance(config.term_options_json, list) and len(config.term_options_json) > 0:
            if data.policy_term_years not in config.term_options_json:
                data.policy_term_years = config.term_options_json[0]

        # Retrieve active pricing matrix
        matrix = await self.matrix_repo.get_active_by_product_id(product.id)
        if not matrix:
            # Check if product has any linked pricing matrices
            if product.pricing_matrices:
                matrix = product.pricing_matrices[0]
            else:
                raise BusinessRuleViolationException(
                    f"No active actuarial pricing matrix configured for product {product.code}."
                )

        # Run pure deterministic calculation
        breakdown = ActuarialPricingService.calculate_premium(
            matrix=matrix,
            sum_assured=data.sum_assured,
            policy_term_years=data.policy_term_years,
            age=age,
            gender=gender,
            is_smoker=is_smoker,
            health_tier=health_tier,
            payment_frequency=data.payment_frequency,
            selected_rider_codes=data.selected_rider_codes,
        )

        quote_number = f"QTE-{datetime.now(timezone.utc).year}-{random.randint(100000, 999999)}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        quote = Quote(
            quote_number=quote_number,
            customer_id=customer_id,
            product_id=product.id,
            configuration_id=config.id if config else None,
            pricing_matrix_version=matrix.matrix_version,
            sum_assured=data.sum_assured,
            policy_term_years=data.policy_term_years,
            payment_frequency=data.payment_frequency,
            selected_riders_json=breakdown.rider_items,
            base_premium=round(breakdown.base_annual_premium * breakdown.frequency_multiplier, 2),
            health_loading_amount=round(breakdown.health_loading_amount * breakdown.frequency_multiplier, 2),
            rider_premium=round(breakdown.rider_annual_premium * breakdown.frequency_multiplier, 2),
            net_premium=round(breakdown.installment_net_premium, 2),
            tax_amount=round(breakdown.tax_amount, 2),
            total_premium=round(breakdown.total_premium_payable, 2),
            calculation_breakdown_json=breakdown.to_dict(),
            expires_at=expires_at,
            status="active",
        )
        return await self.quote_repo.create(quote)

    async def recalculate_quote(
        self,
        quote_id: str,
        customer_id: str,
        data: QuoteRecalculateRequest,
        age: int = 30,
        gender: str = "male",
        is_smoker: bool = False,
        health_tier: str = "standard",
    ) -> Quote:
        """Update an existing active quote with new parameters (e.g. rider selection or frequency)."""
        quote = await self.quote_repo.get_by_id_with_details(quote_id)
        if not quote:
            raise EntityNotFoundException("Quote not found.")
        if quote.customer_id != customer_id:
            raise BusinessRuleViolationException("Unauthorized access to quote.")
        if quote.status != "active":
            raise BusinessRuleViolationException("Expired or converted quotes cannot be modified.")

        product = await self.product_repo.get_by_id_with_details(quote.product_id)
        matrix = await self.matrix_repo.get_active_by_product_id(quote.product_id)
        if not matrix:
            if product.pricing_matrices:
                matrix = product.pricing_matrices[0]
            else:
                raise BusinessRuleViolationException("No active pricing matrix available for recalculation.")

        breakdown = ActuarialPricingService.calculate_premium(
            matrix=matrix,
            sum_assured=data.sum_assured,
            policy_term_years=data.policy_term_years,
            age=age,
            gender=gender,
            is_smoker=is_smoker,
            health_tier=health_tier,
            payment_frequency=data.payment_frequency,
            selected_rider_codes=data.selected_rider_codes,
        )

        quote.sum_assured = data.sum_assured
        quote.policy_term_years = data.policy_term_years
        quote.payment_frequency = data.payment_frequency
        quote.selected_riders_json = breakdown.rider_items
        quote.base_premium = round(breakdown.base_annual_premium * breakdown.frequency_multiplier, 2)
        quote.health_loading_amount = round(breakdown.health_loading_amount * breakdown.frequency_multiplier, 2)
        quote.rider_premium = round(breakdown.rider_annual_premium * breakdown.frequency_multiplier, 2)
        quote.net_premium = round(breakdown.installment_net_premium, 2)
        quote.tax_amount = round(breakdown.tax_amount, 2)
        quote.total_premium = round(breakdown.total_premium_payable, 2)
        quote.calculation_breakdown_json = breakdown.to_dict()

        await self.session.flush()
        return quote

    async def get_quote_details(self, quote_id: str, customer_id: str) -> Quote:
        quote = await self.quote_repo.get_by_id_with_details(quote_id)
        if not quote:
            raise EntityNotFoundException("Quote not found.")
        if quote.customer_id != customer_id:
            raise BusinessRuleViolationException("Unauthorized access to quote.")
        return quote

    async def list_quotes_for_customer(self, customer_id: str) -> List[Quote]:
        quotes = await self.quote_repo.list_for_customer(customer_id)
        return list(quotes)
