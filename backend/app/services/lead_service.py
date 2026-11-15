"""Lead management facade orchestrating ingestion, scoring, signals, and outreach."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog, ConsentRecord
from app.models.base import utc_now
from app.models.profile import Advisor
from app.models.prospect import BehavioralSignal, LeadScore, LeadSource, Prospect
from app.models.system import FollowUp
from app.repositories.consent_repository import ConsentRepository
from app.repositories.prospect_repository import ProspectRepository
from app.repositories.signal_repository import SignalRepository
from app.schemas.consent import ConsentGrantRequest, ConsentRevokeRequest
from app.schemas.prospect import AdvisorOutreachNoteCreate, ProspectCreate, ProspectUpdate
from app.schemas.signal import SignalIngestRequest
from app.services.lead_assignment_service import LeadAssignmentService
from app.services.lead_scoring_service import LeadScoringService


class LeadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.prospect_repo = ProspectRepository(session)
        self.signal_repo = SignalRepository(session)
        self.consent_repo = ConsentRepository(session)
        self.scoring_service = LeadScoringService(session)
        self.assignment_service = LeadAssignmentService(session)

    async def ingest_prospect(self, data: ProspectCreate, ip_address: Optional[str] = None) -> Prospect:
        """Ingests a new prospect or updates an existing prospect matching email/phone."""
        # Check existing by email or phone
        existing_prospect = None
        if data.email:
            existing_prospect = await self.prospect_repo.get_by_email(str(data.email))
        if not existing_prospect and data.phone:
            existing_prospect = await self.prospect_repo.get_by_phone(data.phone)

        # Resolve or create lead source
        stmt_src = select(LeadSource).where(LeadSource.name == data.source_name)
        res_src = await self.session.execute(stmt_src)
        source = res_src.scalar_one_or_none()
        if not source:
            source = LeadSource(
                name=data.source_name,
                channel_type="web",
                utm_campaign=data.utm_campaign,
                is_active=True,
            )
            self.session.add(source)
            await self.session.flush()

        if existing_prospect:
            if data.name:
                existing_prospect.name = data.name
            if data.phone and not existing_prospect.phone:
                existing_prospect.phone = data.phone
            if data.email and not existing_prospect.email:
                existing_prospect.email = str(data.email)
            if data.target_insurance_type:
                existing_prospect.target_insurance_type = data.target_insurance_type
            if data.estimated_budget_min is not None:
                existing_prospect.estimated_budget_min = data.estimated_budget_min
            if data.estimated_budget_max is not None:
                existing_prospect.estimated_budget_max = data.estimated_budget_max

            existing_prospect.last_activity_at = utc_now()
            prospect = existing_prospect
        else:
            prospect = Prospect(
                name=data.name,
                email=str(data.email) if data.email else None,
                phone=data.phone,
                source_id=source.id,
                status="new",
                segment="top_of_funnel",
                target_insurance_type=data.target_insurance_type,
                estimated_budget_min=data.estimated_budget_min,
                estimated_budget_max=data.estimated_budget_max,
                last_activity_at=utc_now(),
            )
            self.session.add(prospect)
            await self.session.flush()

        # Record initial signal if session was provided
        if data.initial_session_id:
            signal = BehavioralSignal(
                prospect_id=prospect.id,
                session_id=data.initial_session_id,
                signal_type="page_view",
                payload_json={
                    "utm_source": data.utm_source,
                    "utm_medium": data.utm_medium,
                    "utm_campaign": data.utm_campaign,
                    "utm_term": data.utm_term,
                    "utm_content": data.utm_content,
                    "ip": ip_address,
                },
                created_at=utc_now(),
            )
            self.session.add(signal)
            await self.session.flush()

        # Recalculate score
        score = await self.scoring_service.calculate_and_record_score(prospect)

        # If high-intent, attempt auto-assignment
        if score.score >= 70.0 and not prospect.assigned_advisor_id:
            await self.assignment_service.auto_assign_lead(prospect)

        return prospect

    async def ingest_signal(self, data: SignalIngestRequest) -> Optional[BehavioralSignal]:
        """Ingests a behavioral signal and recalculates prospect score."""
        target_prospect_id = data.prospect_id

        if not target_prospect_id and data.session_id:
            # Lookup prospect from prior signals with same session_id
            signals = await self.signal_repo.get_signals_by_session(data.session_id)
            if signals:
                target_prospect_id = signals[0].prospect_id

        if not target_prospect_id:
            # Anonymous signal without prospect: create anonymous prospect
            anon_prospect = Prospect(
                name="Anonymous Visitor",
                status="new",
                segment="top_of_funnel",
                last_activity_at=utc_now(),
            )
            self.session.add(anon_prospect)
            await self.session.flush()
            target_prospect_id = anon_prospect.id

        signal = BehavioralSignal(
            prospect_id=target_prospect_id,
            session_id=data.session_id,
            signal_type=data.signal_type,
            payload_json=data.payload_json,
            created_at=data.client_timestamp or utc_now(),
        )
        self.session.add(signal)
        await self.session.flush()

        # Update last activity
        prospect = await self.prospect_repo.get_by_id(target_prospect_id)
        if prospect:
            prospect.last_activity_at = utc_now()
            score = await self.scoring_service.calculate_and_record_score(prospect)
            if score.score >= 70.0 and not prospect.assigned_advisor_id:
                await self.assignment_service.auto_assign_lead(prospect)

        return signal

    async def grant_consent(self, data: ConsentGrantRequest) -> ConsentRecord:
        """Records DPDP/IRDAI explicit consent grant and updates score."""
        consent = ConsentRecord(
            prospect_id=data.prospect_id,
            consent_type=data.consent_type,
            consent_version=data.consent_version,
            ip_address=data.ip_address,
            granted_at=utc_now(),
        )
        self.session.add(consent)
        await self.session.flush()

        prospect = await self.prospect_repo.get_by_id(data.prospect_id)
        if prospect:
            prospect.last_activity_at = utc_now()
            await self.scoring_service.calculate_and_record_score(prospect)

        return consent

    async def revoke_consent(self, data: ConsentRevokeRequest) -> Optional[ConsentRecord]:
        """Revokes consent and updates score."""
        record = await self.consent_repo.revoke_consent(data.prospect_id, data.consent_type)
        if record:
            prospect = await self.prospect_repo.get_by_id(data.prospect_id)
            if prospect:
                prospect.last_activity_at = utc_now()
                await self.scoring_service.calculate_and_record_score(prospect)
        return record

    async def check_contactability(self, prospect_id: str) -> bool:
        """Returns True ONLY if marketing_contact consent is granted and active."""
        return await self.consent_repo.has_active_consent(prospect_id, "marketing_contact")

    async def advisor_log_outreach(
        self,
        prospect_id: str,
        advisor_id: str,
        data: AdvisorOutreachNoteCreate,
        actor_user_id: str,
    ) -> FollowUp:
        """Logs an outreach touchpoint for an assigned lead, verifying DPDP consent first."""
        prospect = await self.prospect_repo.get_by_id(prospect_id)
        if not prospect:
            raise ValueError(f"Prospect {prospect_id} not found.")

        if prospect.assigned_advisor_id != advisor_id:
            raise PermissionError("Access denied: You are not the assigned advisor for this lead.")

        # STRICT CONSENT GUARDRAIL
        can_contact = await self.check_contactability(prospect_id)
        if not can_contact:
            raise PermissionError(
                "Outreach blocked: Prospect has not granted active marketing/communication consent under DPDP regulations."
            )

        # Update prospect status based on outcome
        if data.outcome == "connected_interested":
            prospect.status = "qualified"
        elif data.outcome in ("callback_requested", "info_provided"):
            prospect.status = "engaged"
        elif data.outcome == "not_interested":
            prospect.status = "dropped"

        prospect.last_activity_at = utc_now()

        # Record FollowUp entry
        follow_up = FollowUp(
            prospect_id=prospect.id,
            assigned_advisor_id=advisor_id,
            due_date=data.follow_up_date or utc_now(),
            channel=data.follow_up_channel,
            status="pending" if data.schedule_follow_up else "completed",
            notes=f"[{data.outcome.upper()}] {data.notes}",
        )
        self.session.add(follow_up)

        # Audit log
        audit = AuditLog(
            user_id=actor_user_id,
            action="ADVISOR_LEAD_OUTREACH",
            resource_type="Prospect",
            resource_id=prospect.id,
            changes_json={
                "outcome": data.outcome,
                "notes": data.notes,
                "channel": data.follow_up_channel,
                "new_status": prospect.status,
            },
            timestamp=utc_now(),
        )
        self.session.add(audit)
        await self.session.flush()

        return follow_up

