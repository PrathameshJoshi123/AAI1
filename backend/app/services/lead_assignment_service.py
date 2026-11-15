"""Advisor workload-aware matching and manual assignment service."""
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.audit import AuditLog
from app.models.auth import User
from app.models.base import utc_now
from app.models.profile import Advisor, Customer
from app.models.prospect import Prospect


class LeadAssignmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_advisors_with_workload(self) -> List[Dict[str, Any]]:
        """List active advisors with real-time capacity and caseload metrics."""
        stmt = (
            select(Advisor)
            .options(
                selectinload(Advisor.user),
                selectinload(Advisor.assigned_customers),
                selectinload(Advisor.assigned_prospects),
            )
            .order_by(Advisor.license_number)
        )
        res = await self.session.execute(stmt)
        advisors = res.scalars().all()

        workload_list = []
        for adv in advisors:
            active_cust_count = len(adv.assigned_customers)
            active_prospect_count = len([
                p for p in adv.assigned_prospects
                if p.status in ("new", "engaged", "qualified")
            ])
            total_active = active_cust_count + active_prospect_count
            user_name = f"{adv.user.first_name} {adv.user.last_name}".strip() if adv.user else "Advisor"

            workload_list.append({
                "advisor_id": adv.id,
                "name": user_name,
                "license_number": adv.license_number,
                "specializations": adv.specializations or "General Insurance",
                "max_active_cases": adv.max_active_cases,
                "current_active_cases": total_active,
                "is_available": adv.is_available,
                "capacity_percentage": round((total_active / max(adv.max_active_cases, 1)) * 100, 1),
            })
        return workload_list

    async def auto_assign_lead(self, prospect: Prospect) -> Optional[Advisor]:
        """Matches available advisor with capacity and matching specialization."""
        advisors_workload = await self.get_advisors_with_workload()

        # Filter available and under capacity
        eligible = [
            a for a in advisors_workload
            if a["is_available"] and a["current_active_cases"] < a["max_active_cases"]
        ]
        if not eligible:
            return None

        # Prioritize matching specialization if specified
        target_type = (prospect.target_insurance_type or "").lower()
        if target_type:
            matching = [
                a for a in eligible
                if target_type in (a["specializations"] or "").lower()
            ]
            if matching:
                eligible = matching

        # Sort by lowest capacity ratio
        eligible.sort(key=lambda a: a["current_active_cases"] / a["max_active_cases"])
        best_candidate = eligible[0]

        # Fetch actual advisor record
        stmt = select(Advisor).where(Advisor.id == best_candidate["advisor_id"])
        res = await self.session.execute(stmt)
        chosen_advisor = res.scalar_one_or_none()

        if chosen_advisor:
            prospect.assigned_advisor_id = chosen_advisor.id
            prospect.assigned_at = utc_now()
            await self.session.flush()

        return chosen_advisor

    async def manually_assign_lead(
        self,
        prospect: Prospect,
        advisor_id: Optional[str],
        actor_user_id: Optional[str] = None,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[Advisor]:
        """Manually assigns or unassigns lead with mandatory audit logging."""
        old_advisor_id = prospect.assigned_advisor_id
        assigned_advisor = None

        if advisor_id:
            stmt = select(Advisor).where(Advisor.id == advisor_id)
            res = await self.session.execute(stmt)
            assigned_advisor = res.scalar_one_or_none()
            if not assigned_advisor:
                raise ValueError(f"Advisor with ID {advisor_id} does not exist.")

            prospect.assigned_advisor_id = assigned_advisor.id
            prospect.assigned_at = utc_now()
        else:
            prospect.assigned_advisor_id = None
            prospect.assigned_at = None

        # Create audit record
        audit_entry = AuditLog(
            user_id=actor_user_id,
            action="LEAD_ADVISOR_ASSIGNMENT",
            resource_type="Prospect",
            resource_id=prospect.id,
            ip_address=ip_address,
            changes_json={
                "previous_advisor_id": old_advisor_id,
                "new_advisor_id": advisor_id,
                "notes": notes,
                "assigned_at": utc_now().isoformat(),
            },
            timestamp=utc_now(),
        )
        self.session.add(audit_entry)
        await self.session.flush()

        return assigned_advisor

