"""Seed baseline insurance products and policy configurations with full actuarial metadata."""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.product import InsuranceProduct, ProductConfiguration


PRODUCTS_CONFIG = [
    {
        "code": "TERM_SECURE_PLUS",
        "name": "Term Secure Plus",
        "category": "term_life",
        "description": "Comprehensive pure term life insurance protecting your family with financial security, critical illness cover, and accidental death benefit.",
        "is_active": True,
        "insurer_name": "Star Union Life & General",
        "insurer_code": "SULG-IN",
        "insurer_solvency_ratio": 2.15,
        "policy_type": "individual",
        "base_rules_json": {
            "min_age": 18,
            "max_age": 65,
            "max_expiry_age": 85,
            "smoker_loading_factor": 1.35,
            "min_annual_income": 300000.0,
        },
        "coverage_summary_json": [
            "Pure risk death benefit with immediate lump sum payout",
            "Accelerated critical illness benefit covering 36 life-threatening ailments",
            "Optional accidental total and permanent disability waiver of premium",
            "Tax exemptions under Section 80C and Section 10(10D) of Income Tax Act",
        ],
        "benefits_list_json": [
            {"name": "Death Benefit", "description": "100% Sum Assured paid to registered nominee upon death"},
            {"name": "Terminal Illness", "description": "Up to 50% accelerated sum assured payout upon diagnosis"},
            {"name": "Tax Savings", "description": "Tax deductions up to ₹1.5 Lakhs annually under Section 80C"},
            {"name": "Claim Settlement Ratio", "description": "98.7% verified claim settlement ratio (IRDAI 2025-26)"},
        ],
        "exclusions_list_json": [
            {"code": "SUICIDE_CLAUSE", "title": "Suicide within 12 Months", "description": "Death resulting from suicide within 12 months from policy inception pays 80% of premiums paid without interest."},
            {"code": "HAZARDOUS_SPORTS", "title": "Hazardous Pursuits", "description": "Demise or disability while engaging in aviation (other than commercial passenger), deep-sea diving, or racing."},
            {"code": "CRIMINAL_ACT", "title": "Breach of Law", "description": "Claims arising directly from active participation in illegal or criminal activities."},
        ],
        "waiting_periods_json": {
            "initial_waiting_days": 0,
            "accidental_coverage_days": 0,
            "critical_illness_waiting_days": 90,
            "survival_period_days": 30,
        },
        "required_declarations_json": [
            {"id": "tobacco_usage", "question": "Have you consumed any tobacco, nicotine, or smoking products in the past 36 months?", "type": "boolean"},
            {"id": "major_surgeries", "question": "Have you undergone any surgery or hospitalization exceeding 7 days in the last 5 years?", "type": "boolean"},
            {"id": "family_history", "question": "Has any immediate family member suffered from cancer, heart disease, or diabetes before age 60?", "type": "boolean"},
        ],
        "required_documents_json": [
            {"code": "DOC_PAN", "name": "Permanent Account Number (PAN) Card", "category": "identity"},
            {"code": "DOC_AADHAAR", "name": "Aadhaar Card / Passport (Address Proof)", "category": "address"},
            {"code": "DOC_INCOME", "name": "Latest 3 Months Salary Slips or Form 16 / ITR-V", "category": "income"},
        ],
        "configurations": [
            {
                "tier_name": "Essential",
                "min_sum_assured": 2500000.0,
                "max_sum_assured": 10000000.0,
                "sum_assured_step": 500000.0,
                "term_options_json": [10, 15, 20, 25, 30],
                "available_frequencies_json": ["monthly", "quarterly", "annually"],
                "riders_json": [
                    {"code": "ACC_DEATH", "name": "Accidental Death Benefit", "rate_per_k": 0.25}
                ],
            },
            {
                "tier_name": "Comprehensive",
                "min_sum_assured": 10000000.0,
                "max_sum_assured": 50000000.0,
                "sum_assured_step": 1000000.0,
                "term_options_json": [15, 20, 25, 30, 35, 40],
                "available_frequencies_json": ["monthly", "quarterly", "half_yearly", "annually"],
                "riders_json": [
                    {"code": "ACC_DEATH", "name": "Accidental Death Benefit", "rate_per_k": 0.25},
                    {"code": "CRIT_ILL", "name": "Accelerated Critical Illness Cover", "rate_per_k": 0.75},
                    {"code": "PREM_WAIVER", "name": "Waiver of Premium on Total Disability", "rate_per_k": 0.15},
                ],
            },
        ],
    },
    {
        "code": "HEALTH_SHIELD_PRO",
        "name": "Health Shield Pro",
        "category": "health",
        "description": "Top-tier health hospitalization protection featuring zero co-pay, international second medical opinion, and 10,000+ cashless hospital networks.",
        "is_active": True,
        "insurer_name": "Star Union Life & General",
        "insurer_code": "SULG-IN",
        "insurer_solvency_ratio": 2.15,
        "policy_type": "individual",
        "base_rules_json": {
            "min_age": 18,
            "max_age": 70,
            "pre_existing_waiting_period_months": 24,
            "min_annual_income": 200000.0,
        },
        "coverage_summary_json": [
            "100% cashless hospitalization across 10,000+ partner network hospitals",
            "Zero room rent sub-limits and zero compulsory copay",
            "Pre-hospitalization expenses (60 days) and Post-hospitalization expenses (180 days)",
            "AYUSH inpatient treatment covered up to 100% Sum Insured",
        ],
        "benefits_list_json": [
            {"name": "Cashless Hospitalization", "description": "Over 10,000 cashless partner hospitals nationwide"},
            {"name": "No Room Rent Capping", "description": "Choose any room category including single private room without penalty"},
            {"name": "Cumulative Bonus", "description": "Up to 100% bonus coverage for claim-free years"},
            {"name": "Tax Exemption", "description": "Tax deduction up to ₹75,000 under Section 80D"},
        ],
        "exclusions_list_json": [
            {"code": "COSMETIC_SURGERY", "title": "Cosmetic or Plastic Surgery", "description": "Aesthetic treatments or non-accidental cosmetic reconstruction are excluded."},
            {"code": "ALCOHOL_SUBSTANCE", "title": "Substance Abuse", "description": "Treatment directly or indirectly resulting from alcoholism or drug abuse."},
            {"code": "UNPROVEN_TREATMENTS", "title": "Experimental Treatments", "description": "Investigational treatments or procedures not approved by medical authorities."},
        ],
        "waiting_periods_json": {
            "initial_waiting_days": 30,
            "accidental_coverage_days": 0,
            "specific_illnesses_months": 24,
            "pre_existing_conditions_months": 24,
        },
        "required_declarations_json": [
            {"id": "pre_existing_disease", "question": "Do you have any diagnosed conditions such as diabetes, hypertension, asthma, or cardiac disorder?", "type": "boolean"},
            {"id": "continuous_medication", "question": "Are you currently taking any prescription medications on an ongoing basis?", "type": "boolean"},
            {"id": "past_claims", "question": "Have you filed any health insurance claims with any insurer in the past 3 years?", "type": "boolean"},
        ],
        "required_documents_json": [
            {"code": "DOC_PAN", "name": "Permanent Account Number (PAN) Card", "category": "identity"},
            {"code": "DOC_AADHAAR", "name": "Aadhaar Card / Passport (Address Proof)", "category": "address"},
            {"code": "DOC_MEDICAL_REPORTS", "name": "Prior Medical Records / Discharge Summary (if declared)", "category": "medical"},
        ],
        "configurations": [
            {
                "tier_name": "Individual Essential",
                "min_sum_assured": 500000.0,
                "max_sum_assured": 1500000.0,
                "sum_assured_step": 250000.0,
                "term_options_json": [1, 2, 3],
                "available_frequencies_json": ["monthly", "quarterly", "annually"],
                "riders_json": [
                    {"code": "OPD_DENTAL", "name": "Outpatient & Dental Care", "rate_per_k": 1.20}
                ],
            },
            {
                "tier_name": "Family Comprehensive",
                "min_sum_assured": 1500000.0,
                "max_sum_assured": 5000000.0,
                "sum_assured_step": 500000.0,
                "term_options_json": [1, 2, 3],
                "available_frequencies_json": ["quarterly", "annually"],
                "riders_json": [
                    {"code": "MATERNITY", "name": "Maternity & Newborn Cover", "rate_per_k": 1.50},
                    {"code": "RESTORATION", "name": "100% Sum Assured Restoration", "rate_per_k": 0.40},
                ],
            },
        ],
    },
]


async def seed_products(session):
    for p_data in PRODUCTS_CONFIG:
        configs = p_data.pop("configurations")
        stmt = select(InsuranceProduct).where(InsuranceProduct.code == p_data["code"])
        result = await session.execute(stmt)
        product = result.scalar_one_or_none()
        if not product:
            product = InsuranceProduct(**p_data)
            session.add(product)
            await session.flush()

            for c_data in configs:
                config = ProductConfiguration(product_id=product.id, **c_data)
                session.add(config)
            await session.flush()
            print(f"Product seeded: {product.name} ({product.code}) with {len(configs)} tiers.")
        else:
            # Update metadata fields if already existing
            for k, v in p_data.items():
                setattr(product, k, v)
            await session.flush()

            # Ensure configurations match the updated tiers
            stmt_cfg = select(ProductConfiguration).where(ProductConfiguration.product_id == product.id)
            existing_cfgs = (await session.execute(stmt_cfg)).scalars().all()
            for ec in existing_cfgs:
                await session.delete(ec)
            await session.flush()

            for c_data in configs:
                config = ProductConfiguration(product_id=product.id, **c_data)
                session.add(config)
            await session.flush()
            print(f"Product {product.name} updated with rich Phase 6 metadata and {len(configs)} configurations.")


async def main():
    async with AsyncSessionLocal() as session:
        try:
            await seed_products(session)
            await session.commit()
            print("Products seeded successfully!")
        except Exception as e:
            await session.rollback()
            print(f"Error seeding products: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
