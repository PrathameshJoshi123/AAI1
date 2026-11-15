"""Admin Overview Service: Real-time database aggregations for executive KPIs and activity stream."""
from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import utc_now
from app.models.prospect import Prospect, LeadScore
from app.models.conversation import Conversation
from app.models.recommendation import Quote
from app.models.application import Application
from app.models.underwriting import UnderwritingCase
from app.models.system import FollowUp
from app.models.audit import AuditLog
from app.models.auth import User
from app.models.profile import Customer, Advisor
from app.schemas.admin import (
    ExecutiveMetricsResponse,
    RecentActivityItem,
    RecentActivityResponse,
    AdminCustomerItem,
)


class AdminOverviewService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_executive_metrics(self) -> ExecutiveMetricsResponse:
        """Calculate real database-backed metrics for all 8 executive KPI cards."""
        # 1. Total prospects
        total_prospects_res = await self.session.execute(select(func.count(Prospect.id)))
        total_prospects = total_prospects_res.scalar() or 0

        # 2. Qualified leads (score >= 60)
        qualified_leads_res = await self.session.execute(
            select(func.count(func.distinct(LeadScore.prospect_id))).where(LeadScore.score >= 60)
        )
        qualified_leads = qualified_leads_res.scalar() or 0

        # 3. Active conversations in past 24 hours
        cutoff_24h = utc_now() - timedelta(hours=24)
        active_convs_res = await self.session.execute(
            select(func.count(Conversation.id)).where(
                Conversation.status == "active",
                Conversation.updated_at >= cutoff_24h
            )
        )
        active_conversations = active_convs_res.scalar() or 0

        # 4. Quotes generated
        quotes_res = await self.session.execute(select(func.count(Quote.id)))
        quotes_generated = quotes_res.scalar() or 0

        # 5. Applications submitted (status != 'draft')
        submitted_apps_res = await self.session.execute(
            select(func.count(Application.id)).where(Application.status != "draft")
        )
        apps_submitted = submitted_apps_res.scalar() or 0

        # 6. Applications awaiting review
        awaiting_review_res = await self.session.execute(
            select(func.count(UnderwritingCase.id)).where(
                UnderwritingCase.status.in_(["new", "assigned", "in_review", "under_review", "more_info_needed", "more_info_required", "escalated"])
            )
        )
        apps_awaiting_review = awaiting_review_res.scalar() or 0

        # 7. Overall Conversion Rate (%)
        conversion_rate = 0.0
        if total_prospects > 0:
            conversion_rate = round((apps_submitted / total_prospects) * 100.0, 2)

        # 8. Pending Follow-up tasks
        pending_follow_ups_res = await self.session.execute(
            select(func.count(FollowUp.id)).where(FollowUp.status == "pending")
        )
        pending_follow_ups = pending_follow_ups_res.scalar() or 0

        return ExecutiveMetricsResponse(
            total_prospects=total_prospects,
            qualified_leads=qualified_leads,
            active_conversations=active_conversations,
            quotes_generated=quotes_generated,
            applications_submitted=apps_submitted,
            applications_awaiting_review=apps_awaiting_review,
            conversion_rate=conversion_rate,
            pending_follow_ups=pending_follow_ups,
        )

    async def get_recent_activity_pulse(self, limit: int = 15) -> RecentActivityResponse:
        """Fetch the most recent system activities from the immutable audit logs."""
        query = (
            select(AuditLog, User.email)
            .outerjoin(User, AuditLog.user_id == User.id)
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(query)
        rows = result.all()

        activities: List[RecentActivityItem] = []
        for log, user_email in rows:
            desc_text = f"{log.action} on {log.resource_type} ({log.resource_id})"
            activities.append(
                RecentActivityItem(
                    id=str(log.id),
                    action=log.action,
                    resource_type=log.resource_type,
                    resource_id=log.resource_id,
                    actor_email=user_email,
                    description=desc_text,
                    timestamp=log.timestamp,
                )
            )

        return RecentActivityResponse(activities=activities, total=len(activities))

    async def list_customers(self) -> List[AdminCustomerItem]:
        """Fetch all registered customer accounts with lifecycle onboarding status."""
        query = (
            select(Customer, User)
            .join(User, Customer.user_id == User.id)
            .order_by(Customer.created_at.desc())
        )
        result = await self.session.execute(query)
        rows = result.all()

        customers: List[AdminCustomerItem] = []
        for cust, usr in rows:
            adv_name = None
            if cust.assigned_advisor_id:
                adv_user_res = await self.session.execute(
                    select(User.first_name, User.last_name)
                    .join(Advisor, Advisor.user_id == User.id)
                    .where(Advisor.id == cust.assigned_advisor_id)
                )
                adv_row = adv_user_res.first()
                if adv_row:
                    adv_name = f"{adv_row[0]} {adv_row[1]}"

            customers.append(
                AdminCustomerItem(
                    id=cust.id,
                    user_id=usr.id,
                    full_name=f"{usr.first_name} {usr.last_name}",
                    email=usr.email,
                    phone=usr.phone,
                    city=cust.city,
                    state=cust.state,
                    onboarding_stage=cust.onboarding_stage,
                    risk_tier=cust.risk_tier,
                    annual_income=float(cust.annual_income) if cust.annual_income else None,
                    occupation=cust.occupation,
                    assigned_advisor_name=adv_name,
                    created_at=cust.created_at,
                )
            )
        return customers
