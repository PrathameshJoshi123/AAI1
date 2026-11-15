"""Seed baseline actuarial pricing matrices for products."""
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.product import InsuranceProduct
from app.models.pricing_matrix import ProductPricingMatrix


PRICING_MATRICES = [
    {
        "product_code": "TERM_SECURE_PLUS",
        "matrix_version": "v1.0.0-term-2026",
        "is_active": True,
        "age_band_rates_json": {
            "18-25": 1.20,
            "26-35": 1.65,
            "36-45": 2.95,
            "46-55": 5.80,
            "56-65": 11.40,
        },
        "gender_multipliers_json": {
            "male": 1.00,
            "female": 0.90,
            "other": 1.00,
        },
        "smoker_loading_factors_json": {
            "non_smoker": 1.00,
            "smoker": 1.35,
        },
        "frequency_multipliers_json": {
            "annually": 1.00,
            "half_yearly": 0.51,
            "quarterly": 0.26,
            "monthly": 0.088,
        },
        "health_tier_loadings_json": {
            "preferred_plus": 0.95,
            "standard": 1.00,
            "substandard_1": 1.20,
            "substandard_2": 1.40,
        },
        "rider_rate_cards_json": {
            "ACC_DEATH": {
                "name": "Accidental Death Benefit",
                "rate_per_k": 0.25,
                "description": "Additional 100% payout in event of accidental demise",
            },
            "CRIT_ILL": {
                "name": "Accelerated Critical Illness Cover",
                "rate_per_k": 0.75,
                "description": "Lump sum payout upon diagnosis of 36 critical illnesses",
            },
            "PREM_WAIVER": {
                "name": "Waiver of Premium on Total Disability",
                "rate_per_k": 0.15,
                "description": "All future premiums waived upon permanent disability",
            },
        },
        "tax_rate_percent": 18.00,
    },
    {
        "product_code": "HEALTH_SHIELD_PRO",
        "matrix_version": "v1.0.0-health-2026",
        "is_active": True,
        "age_band_rates_json": {
            "18-25": 8.50,
            "26-35": 11.20,
            "36-45": 16.80,
            "46-55": 26.50,
            "56-65": 44.00,
            "66-75": 72.00,
        },
        "gender_multipliers_json": {
            "male": 1.00,
            "female": 0.95,
            "other": 1.00,
        },
        "smoker_loading_factors_json": {
            "non_smoker": 1.00,
            "smoker": 1.25,
        },
        "frequency_multipliers_json": {
            "annually": 1.00,
            "half_yearly": 0.52,
            "quarterly": 0.27,
            "monthly": 0.090,
        },
        "health_tier_loadings_json": {
            "preferred_plus": 0.90,
            "standard": 1.00,
            "substandard_1": 1.25,
            "substandard_2": 1.50,
        },
        "rider_rate_cards_json": {
            "OPD_DENTAL": {
                "name": "Outpatient & Dental Care",
                "rate_per_k": 1.20,
                "description": "Reimbursement for consultations, pharmacy, and dental procedures",
            },
            "MATERNITY": {
                "name": "Maternity & Newborn Cover",
                "rate_per_k": 1.50,
                "description": "Inpatient delivery costs and 90-day infant care",
            },
            "RESTORATION": {
                "name": "100% Sum Assured Restoration",
                "rate_per_k": 0.40,
                "description": "Automatic reinstatement of full sum assured upon exhaustion",
            },
        },
        "tax_rate_percent": 18.00,
    },
]


async def seed_pricing_matrices(session):
    for matrix_data in PRICING_MATRICES:
        p_code = matrix_data.pop("product_code")
        stmt = select(InsuranceProduct).where(InsuranceProduct.code == p_code)
        res = await session.execute(stmt)
        product = res.scalar_one_or_none()
        if not product:
            print(f"Product {p_code} not found, skipping matrix seeding.")
            continue

        version = matrix_data["matrix_version"]
        m_stmt = select(ProductPricingMatrix).where(ProductPricingMatrix.matrix_version == version)
        m_res = await session.execute(m_stmt)
        existing = m_res.scalar_one_or_none()
        if not existing:
            pricing_matrix = ProductPricingMatrix(
                product_id=product.id,
                **matrix_data,
            )
            session.add(pricing_matrix)
            await session.flush()
            print(f"Seeded pricing matrix {version} for {product.name}.")
        else:
            print(f"Pricing matrix {version} already exists.")


async def main():
    async with AsyncSessionLocal() as session:
        try:
            await seed_pricing_matrices(session)
            await session.commit()
            print("Actuarial pricing matrices seeded successfully!")
        except Exception as e:
            await session.rollback()
            print(f"Error seeding matrices: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())

