"""V1 API Router Aggregator."""
from fastapi import APIRouter
from app.api.v1 import (
    advisor_leads,
    ai,
    applications,
    audit,
    auth,
    consent,
    customer_calculator,
    customer_chat,
    customer_consent,
    customer_journey,
    customer_needs,
    customer_profile,
    documents,
    health,
    products,
    prospects,
    quotes,
    recommendations,
    admin_pricing,
    roles,
    signals,
    underwriting,
    advisor_workspace,
    follow_ups,
    notifications,
    admin_overview,
    admin_analytics,
    admin_funnel,
    admin_agents,
    admin_employees,
    admin_products,
    admin_audit,
    admin_integrations,
    admin_settings,
    email,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(ai.router)
api_router.include_router(products.router)
api_router.include_router(quotes.router)
api_router.include_router(recommendations.router)
api_router.include_router(admin_pricing.router)
api_router.include_router(applications.router)
api_router.include_router(documents.router)
api_router.include_router(underwriting.router)
api_router.include_router(advisor_workspace.router)
api_router.include_router(follow_ups.router)
api_router.include_router(notifications.router)
api_router.include_router(admin_overview.router)
api_router.include_router(admin_analytics.router)
api_router.include_router(admin_funnel.router)
api_router.include_router(admin_agents.router)
api_router.include_router(admin_employees.router)
api_router.include_router(admin_products.router)
api_router.include_router(admin_audit.router)
api_router.include_router(admin_integrations.router)
api_router.include_router(admin_settings.router)
api_router.include_router(roles.router)
api_router.include_router(audit.router)
api_router.include_router(prospects.router)
api_router.include_router(signals.router)
api_router.include_router(consent.router)
api_router.include_router(advisor_leads.router)
api_router.include_router(customer_profile.router)
api_router.include_router(customer_journey.router)
api_router.include_router(customer_chat.router)
api_router.include_router(customer_needs.router)
api_router.include_router(customer_calculator.router)
api_router.include_router(customer_consent.router)
api_router.include_router(email.router)


