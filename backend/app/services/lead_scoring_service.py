"""Deterministic lead scoring and explainable factor evaluation service."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import utc_now
from app.models.prospect import LeadScore, Prospect
from app.repositories.consent_repository import ConsentRepository
from app.repositories.scoring_rule_repository import ScoringRuleRepository
from app.repositories.signal_repository import SignalRepository


class LeadScoringService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.rule_repo = ScoringRuleRepository(session)
        self.signal_repo = SignalRepository(session)
        self.consent_repo = ConsentRepository(session)

    async def calculate_and_record_score(self, prospect: Prospect) -> LeadScore:
        """Evaluates active database rules against prospect profile, signals, and consents."""
        rules = await self.rule_repo.get_active_rules()
        signals = await self.signal_repo.get_signals_for_prospect(prospect.id, limit=200)
        signal_counts = await self.signal_repo.get_signal_counts_by_type(prospect.id)
        cumulative_dwell = await self.signal_repo.get_cumulative_dwell_seconds(prospect.id)
        distinct_pages = await self.signal_repo.get_distinct_pages_visited(prospect.id)
        active_consents = await self.consent_repo.get_active_consents_for_prospect(prospect.id)
        has_marketing_consent = any(c.consent_type == "marketing_contact" for c in active_consents)

        # Check for any revoked consent
        has_revoked_consent = await self.consent_repo.has_revoked_consent(prospect.id, "marketing_contact")

        # Calculate session count
        distinct_sessions = len(set(s.session_id for s in signals if s.session_id))

        total_points = 0
        factors: List[Dict[str, Any]] = []

        now = utc_now()
        days_inactive = (now - (prospect.last_activity_at or prospect.created_at)).days

        for rule in rules:
            code = rule.rule_code
            awarded = 0
            rationale = ""

            if code == "RULE_PROFILE_PHONE" and prospect.phone and prospect.phone.strip():
                awarded = rule.point_value
                rationale = "Verified mobile contact number provided"
            elif code == "RULE_PROFILE_EMAIL" and prospect.email and prospect.email.strip():
                awarded = rule.point_value
                rationale = "Verified contact email address provided"
            elif code == "RULE_PROFILE_NAME" and prospect.name and prospect.name.strip():
                awarded = rule.point_value
                rationale = "Full customer legal name provided"
            elif code == "RULE_INTENT_QUOTE_STARTED" and signal_counts.get("quote_attempt", 0) >= 1:
                awarded = rule.point_value
                rationale = f"Initiated quote calculator ({signal_counts.get('quote_attempt')} times)"
            elif code == "RULE_INTENT_CALCULATOR_USED" and signal_counts.get("coverage_calculator_used", 0) >= 1:
                awarded = rule.point_value
                rationale = "Interacted with coverage slider and tenure controls"
            elif code == "RULE_INTENT_COMPARISON" and signal_counts.get("comparison_viewed", 0) >= 1:
                awarded = rule.point_value
                rationale = "Compared multiple policy tiers side-by-side"
            elif code == "RULE_ENGAGEMENT_DWELL_TIME" and cumulative_dwell >= 120:
                awarded = rule.point_value
                rationale = f"High engagement dwell time ({cumulative_dwell}s on discovery tools)"
            elif code == "RULE_ENGAGEMENT_MULTI_PAGE" and distinct_pages >= 3:
                awarded = rule.point_value
                rationale = f"Explored {distinct_pages} distinct policy and education pages"
            elif code == "RULE_ENGAGEMENT_RETURN_VISIT" and distinct_sessions >= 2:
                awarded = rule.point_value
                rationale = f"Multiple discovery sessions ({distinct_sessions} sessions)"
            elif code == "RULE_CONSENT_MARKETING" and has_marketing_consent:
                awarded = rule.point_value
                rationale = "Explicit DPDP advisory and communication consent granted"
            elif code == "RULE_CONSENT_REVOKED" and has_revoked_consent:
                awarded = rule.point_value  # negative e.g. -50
                rationale = "Communication consent was explicitly revoked by visitor"
            elif code == "RULE_PENALTY_INACTIVITY_30D" and days_inactive >= 30:
                awarded = rule.point_value  # negative e.g. -20
                rationale = f"Prospect has been inactive for {days_inactive} days"

            if awarded != 0:
                total_points += awarded
                factors.append({
                    "rule_code": rule.rule_code,
                    "rule_name": rule.rule_name,
                    "category": rule.category,
                    "points_awarded": awarded,
                    "rationale": rationale,
                })

        # Clamp between 0.0 and 100.0
        final_score = max(0.0, min(100.0, float(total_points)))

        # Determine segment
        if final_score >= 70.0 and has_marketing_consent:
            prospect.segment = "high_intent"
            if prospect.status == "new":
                prospect.status = "qualified"
        elif final_score >= 40.0:
            prospect.segment = "warm_consideration"
            if prospect.status == "new":
                prospect.status = "engaged"
        elif days_inactive >= 14:
            prospect.segment = "dormant"
        else:
            prospect.segment = "top_of_funnel"

        # Create LeadScore record
        lead_score = LeadScore(
            prospect_id=prospect.id,
            score=final_score,
            score_factors_json={"total_points": total_points, "factors": factors},
            calculated_at=utc_now(),
        )
        self.session.add(lead_score)
        await self.session.flush()

        return lead_score
