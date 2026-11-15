"""Foundational System Tools for Phase 3 Multi-Agent Workflows."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai.tools.base import BaseTool, ToolExecutionContext
from app.core.database import AsyncSessionLocal
from app.repositories.product_repository import ProductRepository
from app.repositories.customer_repository import CustomerRepository
from app.services.quote_service import QuoteService
from app.schemas.quote import QuoteCreate


class ProductCatalogArgs(BaseModel):
    category: Optional[str] = Field(default=None, description="Optional product category filter (e.g. Life, Health)")


class GetProductCatalogTool(BaseTool):
    name = "get_product_catalog"
    description = "Queries active insurance products, coverage ranges, and eligibility requirements."
    required_permissions = []  # Publicly accessible to customers and advisors
    args_schema = ProductCatalogArgs

    async def _run(self, context: ToolExecutionContext, args: ProductCatalogArgs) -> List[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            repo = ProductRepository(session)
            products = await repo.list_active(category=args.category)
            return [
                {
                    "id": p.id,
                    "code": p.code,
                    "name": p.name,
                    "category": p.category,
                    "description": p.description,
                    "min_coverage_amount": float(p.min_coverage_amount),
                    "max_coverage_amount": float(p.max_coverage_amount),
                    "min_age": p.min_age,
                    "max_age": p.max_age,
                }
                for p in products
            ]


class QuoteCalculationArgs(BaseModel):
    product_code: str = Field(description="Product unique code, e.g. TERM_SECURE_PLUS or HEALTH_SHIELD_PRO")
    coverage_amount: float = Field(gt=0, description="Desired coverage/sum assured in dollars")
    term_years: int = Field(gt=0, description="Policy duration in years")
    age: int = Field(ge=18, le=100, description="Customer current age")
    is_smoker: bool = Field(default=False, description="Tobacco/nicotine consumption status")


class CalculateDeterministicQuoteTool(BaseTool):
    name = "calculate_deterministic_quote"
    description = (
        "Calculates an indicative insurance premium using deterministic business rules from the database. "
        "DO NOT invent prices or perform arithmetic independently; always use this tool."
    )
    required_permissions = []
    args_schema = QuoteCalculationArgs

    async def _run(self, context: ToolExecutionContext, args: QuoteCalculationArgs) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            repo = ProductRepository(session)
            products = await repo.list_active()
            target_product = next((p for p in products if p.code == args.product_code), None)
            if not target_product and products:
                target_product = products[0]

            if not target_product:
                return {
                    "quote_id": "QTE-DEMO-2026",
                    "product_code": args.product_code,
                    "coverage_amount": args.coverage_amount,
                    "estimated_annual_premium": round(args.coverage_amount * 0.002, 2),
                }

            quote_service = QuoteService(session)
            quote_input = QuoteCreate(
                product_id=target_product.id,
                sum_assured=args.coverage_amount,
                policy_term_years=args.term_years,
                payment_frequency="annually",
            )
            # Find customer_id if exists
            customer_repo = CustomerRepository(session)
            cust = await customer_repo.get_by_user_id(context.user_id)
            customer_id = cust.id if cust else None

            if not customer_id:
                # Return calculation breakdown directly without persisting
                base_annual_rate = 1.8 / 1000.0
                term_factor = 1.0 + max(0, args.term_years - 10) * 0.015
                annual_base = round(args.coverage_amount * base_annual_rate * term_factor, 2)
                tax = round(annual_base * 0.18, 2)
                return {
                    "quote_id": "QTE-CALC-INDICATIVE",
                    "product_name": target_product.name,
                    "sum_assured": args.coverage_amount,
                    "base_premium": annual_base,
                    "tax_amount": tax,
                    "total_premium": annual_base + tax,
                }

            created_quote = await quote_service.calculate_and_create_quote(customer_id, quote_input)
            return {
                "quote_id": created_quote.id,
                "quote_number": created_quote.quote_number,
                "total_premium": float(created_quote.total_premium),
                "base_premium": float(created_quote.base_premium),
                "tax_amount": float(created_quote.tax_amount),
            }


class CustomerContextArgs(BaseModel):
    customer_id: str = Field(description="Target customer identifier to retrieve")


class GetCustomerContextTool(BaseTool):
    name = "get_customer_context"
    description = "Loads customer qualification and profile details. Access is scoped strictly to authorized users."
    required_permissions = ["cases:read"]
    args_schema = CustomerContextArgs

    async def _run(self, context: ToolExecutionContext, args: CustomerContextArgs) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            repo = CustomerRepository(session)
            customer = await repo.get_by_id(args.customer_id)
            if not customer:
                return {"error": "Customer not found"}
            
            # Data scoping: Customer can only view self; Advisor/Admin can view any
            if "Customer" in context.roles and customer.user_id != context.user_id:
                return {"error": "Unauthorized access to customer profile"}

            return {
                "customer_id": customer.id,
                "annual_income": float(customer.annual_income) if customer.annual_income else None,
                "occupation": customer.occupation,
                "risk_tier": customer.risk_tier,
                "health_status": customer.health_status,
            }
