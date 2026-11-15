"""Unified chronological activity timeline aggregator."""
from typing import Any, Dict, List
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.audit import AuditLog, ConsentRecord
from app.models.profile import Advisor
from app.models.prospect import BehavioralSignal, LeadScore, Prospect
from app.models.system import FollowUp


class TimelineService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_lead_timeline(self, prospect_id: str) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []

        # 1. Prospect creation event
        stmt_p = (
            select(Prospect)
            .where(Prospect.id == prospect_id)
            .options(
                selectinload(Prospect.source),
                selectinload(Prospect.assigned_advisor).selectinload(Advisor.user),
            )
        )
        res_p = await self.session.execute(stmt_p)
        prospect = res_p.scalar_one_or_none()
        if not prospect:
            return []

        source_name = prospect.source.name if prospect.source else "web_direct"
        events.append({
            "id": f"evt-create-{prospect.id}",
            "event_type": "PROSPECT_CREATED",
            "category": "lifecycle",
            "title": "Prospect Ingested",
            "description": f"Lead captured via channel: {source_name}",
            "timestamp": prospect.created_at,
            "metadata": {
                "source": source_name,
                "status": prospect.status,
                "initial_segment": prospect.segment,
            },
        })

        # 2. Consent events
        stmt_c = select(ConsentRecord).where(ConsentRecord.prospect_id == prospect_id)
        res_c = await self.session.execute(stmt_c)
        for c in res_c.scalars().all():
            events.append({
                "id": f"evt-consent-{c.id}",
                "event_type": "CONSENT_GRANTED",
                "category": "compliance",
                "title": f"Consent Granted: {c.consent_type.replace('_', ' ').title()}",
                "description": f"Version {c.consent_version} recorded from IP {c.ip_address or 'unknown'}",
                "timestamp": c.granted_at,
                "metadata": {
                    "consent_type": c.consent_type,
                    "version": c.consent_version,
                    "ip": c.ip_address,
                },
            })
            if c.revoked_at:
                events.append({
                    "id": f"evt-consent-revoked-{c.id}",
                    "event_type": "CONSENT_REVOKED",
                    "category": "compliance",
                    "title": f"Consent Revoked: {c.consent_type.replace('_', ' ').title()}",
                    "description": "User revoked communication consent under DPDP guidelines",
                    "timestamp": c.revoked_at,
                    "metadata": {"consent_type": c.consent_type},
                })

        # 3. Behavioral signals
        stmt_s = (
            select(BehavioralSignal)
            .where(BehavioralSignal.prospect_id == prospect_id)
            .order_by(desc(BehavioralSignal.created_at))
            .limit(40)
        )
        res_s = await self.session.execute(stmt_s)
        for s in res_s.scalars().all():
            sig_name = s.signal_type.replace("_", " ").title()
            meta = s.payload_json or {}
            detail = ""
            if s.signal_type == "page_view":
                detail = f"Page: {meta.get('path', 'unknown')}"
            elif s.signal_type == "time_on_page":
                detail = f"Dwell duration: {meta.get('duration_seconds', 0)}s on {meta.get('path', '')}"
            elif s.signal_type == "quote_attempt":
                detail = f"Product: {meta.get('product_name', 'General')}"
            elif s.signal_type == "coverage_calculator_used":
                detail = f"Sum assured: ₹{meta.get('sum_assured', 'N/A')}"
            else:
                detail = f"Action recorded in session {s.session_id[:8]}"

            events.append({
                "id": f"evt-sig-{s.id}",
                "event_type": "BEHAVIORAL_SIGNAL",
                "category": "behavior",
                "title": f"Signal: {sig_name}",
                "description": detail,
                "timestamp": s.created_at,
                "metadata": meta,
            })

        # 4. Lead scores
        stmt_scores = (
            select(LeadScore)
            .where(LeadScore.prospect_id == prospect_id)
            .order_by(desc(LeadScore.calculated_at))
            .limit(10)
        )
        res_scores = await self.session.execute(stmt_scores)
        for sc in res_scores.scalars().all():
            factor_count = len((sc.score_factors_json or {}).get("factors", []))
            events.append({
                "id": f"evt-score-{sc.id}",
                "event_type": "SCORE_RECALCULATED",
                "category": "intelligence",
                "title": f"Lead Score Updated: {sc.score}/100",
                "description": f"Calculated based on {factor_count} explainable criteria",
                "timestamp": sc.calculated_at,
                "metadata": sc.score_factors_json or {},
            })

        # 5. Follow-ups & Advisor notes
        stmt_f = select(FollowUp).where(FollowUp.prospect_id == prospect_id)
        res_f = await self.session.execute(stmt_f)
        for f in res_f.scalars().all():
            events.append({
                "id": f"evt-followup-{f.id}",
                "event_type": "ADVISOR_OUTREACH",
                "category": "outreach",
                "title": f"Advisor Outreach ({f.channel.title()} - {f.status.title()})",
                "description": f.notes or "Scheduled follow-up contact",
                "timestamp": f.created_at,
                "metadata": {
                    "channel": f.channel,
                    "status": f.status,
                    "due_date": f.due_date.isoformat(),
                },
            })

        # 6. Audit logs (Assignments, etc.)
        stmt_a = (
            select(AuditLog)
            .where(AuditLog.resource_type == "Prospect", AuditLog.resource_id == prospect_id)
        )
        res_a = await self.session.execute(stmt_a)
        for a in res_a.scalars().all():
            events.append({
                "id": f"evt-audit-{a.id}",
                "event_type": a.action,
                "category": "audit",
                "title": f"Action: {a.action.replace('_', ' ').title()}",
                "description": f"Performed by user: {a.user_id or 'System'}",
                "timestamp": a.timestamp,
                "metadata": a.changes_json or {},
            })

        # Sort all descending
        events.sort(key=lambda e: e["timestamp"], reverse=True)
        return events

    async def get_recent_enterprise_timeline(self, limit: int = 100) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []

        # 1. Audit logs
        stmt_a = (
            select(AuditLog)
            .options(selectinload(AuditLog.user))
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
        )
        res_a = await self.session.execute(stmt_a)
        for a in res_a.scalars().all():
            actor = a.user.full_name if a.user else "System Engine"
            events.append({
                "id": f"evt-audit-{a.id}",
                "event_type": a.action,
                "category": "audit",
                "title": a.action.replace("_", " ").title(),
                "description": f"Target: {a.resource_type} (#{a.resource_id}) by {actor}",
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                "actor": actor,
                "metadata": a.changes_json or {},
            })

        # 2. Follow-ups
        stmt_f = (
            select(FollowUp)
            .options(
                selectinload(FollowUp.customer).selectinload(Customer.user),
                selectinload(FollowUp.prospect),
                selectinload(FollowUp.assigned_advisor).selectinload(Advisor.user),
            )
            .order_by(desc(FollowUp.created_at))
            .limit(limit // 2)
        )
        res_f = await self.session.execute(stmt_f)
        for f in res_f.scalars().all():
            adv_name = f.assigned_advisor.user.full_name if f.assigned_advisor and f.assigned_advisor.user else "Advisor"
            t_name = f.customer.user.full_name if f.customer and f.customer.user else (f.prospect.full_name if f.prospect else "Prospect")
            events.append({
                "id": f"evt-fu-{f.id}",
                "event_type": "FOLLOW_UP_SCHEDULED",
                "category": "outreach",
                "title": f"{f.channel.title()} Follow-up: {t_name}",
                "description": f.notes or "Scheduled customer engagement task",
                "timestamp": f.created_at.isoformat() if f.created_at else None,
                "actor": adv_name,
                "metadata": {"status": f.status, "channel": f.channel, "priority": f.priority},
            })

        events.sort(key=lambda e: e["timestamp"] or "", reverse=True)
        return events[:limit]

