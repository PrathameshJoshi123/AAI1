"""Conversion Funnel Service: Multi-stage acquisition & onboarding funnel analysis."""
from typing import List
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prospect import Prospect
from app.models.conversation import Conversation
from app.models.recommendation import CustomerQualification, Recommendation, Quote
from app.models.application import Application
from app.models.underwriting import UnderwritingReview
from app.schemas.admin import ConversionFunnelResponse, FunnelStage


class ConversionFunnelService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_funnel_metrics(self) -> ConversionFunnelResponse:
        """Calculate exact counts and step-by-step conversion drop-offs across the 8 stages."""
        # Stage 1: Prospect Capture
        s1_res = await self.session.execute(select(func.count(Prospect.id)))
        s1_count = s1_res.scalar() or 0

        # Stage 2: AI Conversation Engaged
        s2_res = await self.session.execute(
            select(func.count(func.distinct(Conversation.prospect_id)))
        )
        s2_count = s2_res.scalar() or 0

        # Stage 3: Needs Qualification Completed
        s3_res = await self.session.execute(
            select(func.count(func.distinct(CustomerQualification.customer_id)))
        )
        s3_count = s3_res.scalar() or 0

        # Stage 4: Recommendations Provided
        s4_res = await self.session.execute(
            select(func.count(func.distinct(Recommendation.customer_id)))
        )
        s4_count = s4_res.scalar() or 0

        # Stage 5: Indicative Quote Generated
        s5_res = await self.session.execute(
            select(func.count(func.distinct(Quote.customer_id)))
        )
        s5_count = s5_res.scalar() or 0

        # Stage 6: Application Started (draft)
        s6_res = await self.session.execute(
            select(func.count(Application.id))
        )
        s6_count = s6_res.scalar() or 0

        # Stage 7: Application Submitted
        s7_res = await self.session.execute(
            select(func.count(Application.id)).where(Application.status != "draft")
        )
        s7_count = s7_res.scalar() or 0

        # Stage 8: Underwriting Decision Made
        s8_res = await self.session.execute(
            select(func.count(UnderwritingReview.id))
        )
        s8_count = s8_res.scalar() or 0

        raw_stages = [
            ("prospect_capture", "1. Prospect Ingestion", s1_count),
            ("ai_conversation", "2. AI Conversation Engaged", s2_count),
            ("needs_qualified", "3. Needs Assessed", s3_count),
            ("recommended", "4. Recommendation Generated", s4_count),
            ("quote_generated", "5. Indicative Quote Delivered", s5_count),
            ("app_started", "6. Application Drafted", s6_count),
            ("app_submitted", "7. Proposal Submitted", s7_count),
            ("underwritten", "8. Underwriting Decided", s8_count),
        ]

        stages: List[FunnelStage] = []
        prev_count = s1_count

        for idx, (key, label, count) in enumerate(raw_stages):
            if idx == 0:
                conv_rate = 100.0 if count > 0 else 0.0
                drop_off = 0
            else:
                conv_rate = round((count / prev_count * 100.0), 2) if prev_count > 0 else 0.0
                drop_off = max(0, prev_count - count)

            stages.append(
                FunnelStage(
                    stage_key=key,
                    label=label,
                    count=count,
                    conversion_from_prev=conv_rate,
                    drop_off_count=drop_off,
                )
            )
            prev_count = count

        overall_conv = round((s8_count / s1_count * 100.0), 2) if s1_count > 0 else 0.0

        return ConversionFunnelResponse(stages=stages, overall_conversion=overall_conv)

