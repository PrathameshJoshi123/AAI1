"""Service aggregating Advisor & Underwriter Workspace KPIs and urgent actions."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.application import ApplicationDocument
from app.models.auth import User
from app.models.prospect import Prospect
from app.models.system import FollowUp
from app.models.underwriting import UnderwritingCase
from app.repositories.follow_up_repository import FollowUpRepository
from app.repositories.underwriting_repository import UnderwritingRepository
from app.schemas.advisor import UrgentTaskItem, WorkspaceDashboardData, WorkspaceKPICounters


class AdvisorWorkspaceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.uw_repo = UnderwritingRepository(session)
        self.follow_up_repo = FollowUpRepository(session)

    async def get_dashboard_data(self, current_user: User) -> WorkspaceDashboardData:
        user_roles = [r.name for r in current_user.roles]
        advisor_id = current_user.advisor.id if "Advisor" in user_roles and current_user.advisor else None
        underwriter_id = current_user.underwriter.id if "Underwriter" in user_roles and current_user.underwriter else None

        if any(r in ("Admin", "Owner") for r in user_roles):
            advisor_id = None
            underwriter_id = None

        now = datetime.now(timezone.utc)
        sla_threshold = now + timedelta(hours=4)

        # 1. Active cases count
        case_stmt = select(func.count(UnderwritingCase.id)).where(
            UnderwritingCase.status.in_(["assigned", "in_review", "escalated"])
        )
        if advisor_id:
            case_stmt = case_stmt.where(UnderwritingCase.assigned_advisor_id == advisor_id)
        elif underwriter_id:
            case_stmt = case_stmt.where(UnderwritingCase.assigned_underwriter_id == underwriter_id)
        active_cases_res = await self.session.execute(case_stmt)
        active_cases = active_cases_res.scalar() or 0

        # 2. Pending document verifications
        doc_stmt = select(func.count(ApplicationDocument.id)).where(
            ApplicationDocument.verification_status.in_(["pending", "extracted"])
        )
        pending_docs_res = await self.session.execute(doc_stmt)
        pending_docs = pending_docs_res.scalar() or 0

        # 3. Overdue follow-ups
        overdue_fu = await self.follow_up_repo.count_overdue(advisor_id=advisor_id, now=now)

        # 4. Cases awaiting info
        awaiting_stmt = select(func.count(UnderwritingCase.id)).where(
            UnderwritingCase.status == "more_info_needed"
        )
        if advisor_id:
            awaiting_stmt = awaiting_stmt.where(UnderwritingCase.assigned_advisor_id == advisor_id)
        elif underwriter_id:
            awaiting_stmt = awaiting_stmt.where(UnderwritingCase.assigned_underwriter_id == underwriter_id)
        awaiting_res = await self.session.execute(awaiting_stmt)
        cases_awaiting_info = awaiting_res.scalar() or 0

        # 5. SLA at risk (< 4h)
        sla_stmt = select(func.count(UnderwritingCase.id)).where(
            UnderwritingCase.status.in_(["assigned", "in_review"]),
            UnderwritingCase.sla_deadline <= sla_threshold,
        )
        if advisor_id:
            sla_stmt = sla_stmt.where(UnderwritingCase.assigned_advisor_id == advisor_id)
        elif underwriter_id:
            sla_stmt = sla_stmt.where(UnderwritingCase.assigned_underwriter_id == underwriter_id)
        sla_res = await self.session.execute(sla_stmt)
        sla_at_risk = sla_res.scalar() or 0

        # 6. Assigned leads count
        lead_stmt = select(func.count(Prospect.id))
        if advisor_id:
            lead_stmt = lead_stmt.where(Prospect.assigned_advisor_id == advisor_id)
        leads_res = await self.session.execute(lead_stmt)
        assigned_leads = leads_res.scalar() or 0

        kpis = WorkspaceKPICounters(
            active_cases_count=active_cases,
            pending_document_verifications=pending_docs,
            overdue_follow_ups_count=overdue_fu,
            cases_awaiting_info_count=cases_awaiting_info,
            sla_at_risk_count=sla_at_risk,
            total_assigned_leads=assigned_leads,
        )

        # Build urgent tasks
        tasks: List[UrgentTaskItem] = []

        # Urgent SLA cases
        urgent_cases = await self.uw_repo.list_triage(
            advisor_id=advisor_id,
            underwriter_id=underwriter_id,
            priority="urgent",
            limit=5,
        )
        for c in urgent_cases:
            tasks.append(
                UrgentTaskItem(
                    id=f"task-case-{c.id}",
                    task_type="SLA_BREACH_WARNING",
                    title=f"Urgent Case Review: {c.case_number}",
                    description=f"Risk rating: {c.risk_rating.title()}. SLA deadline requires priority scrutiny.",
                    priority="urgent",
                    due_date=c.sla_deadline,
                    link_url=f"/advisor/underwriting/{c.case_number}",
                    related_entity_id=c.id,
                )
            )

        # Overdue follow-ups
        overdue_items = await self.follow_up_repo.list_for_advisor(
            advisor_id=advisor_id,
            status="pending",
            due_before=now,
        )
        for fu in overdue_items[:5]:
            t_name = fu.customer.user.full_name if fu.customer and fu.customer.user else (fu.prospect.full_name if fu.prospect else "Prospect")
            tasks.append(
                UrgentTaskItem(
                    id=f"task-fu-{fu.id}",
                    task_type="OVERDUE_FOLLOW_UP",
                    title=f"Overdue {fu.channel.title()} Follow-up: {t_name}",
                    description=fu.notes or "Scheduled customer engagement is overdue.",
                    priority=fu.priority,
                    due_date=fu.due_date,
                    link_url="/advisor/follow-ups",
                    related_entity_id=str(fu.id),
                )
            )

        # Pending document verification task if documents exist
        if pending_docs > 0:
            tasks.append(
                UrgentTaskItem(
                    id="task-docs-pending",
                    task_type="PENDING_DOC_VERIFICATION",
                    title=f"{pending_docs} Documents Awaiting Verification",
                    description="Customer uploaded KYC and income proofs require human sign-off.",
                    priority="high" if pending_docs > 5 else "medium",
                    due_date=now + timedelta(hours=24),
                    link_url="/advisor/documents",
                    related_entity_id="doc-queue",
                )
            )

        return WorkspaceDashboardData(kpis=kpis, urgent_tasks=tasks)

