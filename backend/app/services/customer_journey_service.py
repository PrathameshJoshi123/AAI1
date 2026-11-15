"""Customer Journey Progression and Resumption Service."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import Customer
from app.models.recommendation import CustomerQualification, Quote
from app.models.application import Application
from app.models.conversation import Conversation
from app.schemas.journey import JourneyStatusResponse, ResumeJourneyResponse


class CustomerJourneyService:
    @staticmethod
    async def get_journey_status(
        session: AsyncSession,
        customer: Customer,
    ) -> JourneyStatusResponse:
        # Check active quote
        quote_stmt = (
            select(Quote)
            .where(Quote.customer_id == customer.id, Quote.status == "active")
            .order_by(Quote.created_at.desc())
        )
        q_res = await session.execute(quote_stmt)
        active_quote = q_res.scalars().first()

        # Check active application
        app_stmt = (
            select(Application)
            .where(Application.customer_id == customer.id)
            .order_by(Application.created_at.desc())
        )
        a_res = await session.execute(app_stmt)
        active_app = a_res.scalars().first()

        # Check latest qualification
        qual_stmt = (
            select(CustomerQualification)
            .where(CustomerQualification.customer_id == customer.id)
            .order_by(CustomerQualification.created_at.desc())
        )
        qual_res = await session.execute(qual_stmt)
        latest_qual = qual_res.scalars().first()

        missing_steps: List[str] = []
        if not customer.annual_income or not customer.occupation:
            missing_steps.append("complete_personal_profile")
        if not latest_qual:
            missing_steps.append("complete_needs_assessment")
        if not active_quote:
            missing_steps.append("generate_indicative_quote")
        if not active_app:
            missing_steps.append("submit_proposal_application")

        now_utc = datetime.now(timezone.utc)

        current_stage = customer.onboarding_stage or "discovery"
        if latest_qual and current_stage in ("discovery", "needs_assessment"):
            current_stage = "product_matching"

        return JourneyStatusResponse(
            customer_id=customer.id,
            current_stage=current_stage,
            active_conversation_id=customer.active_conversation_id,
            has_active_quote=active_quote is not None,
            active_quote_id=active_quote.id if active_quote else None,
            has_active_application=active_app is not None,
            active_application_id=active_app.id if active_app else None,
            qualification_completed=latest_qual is not None,
            qualification_data=latest_qual.factors_json if latest_qual else None,
            missing_requirements=missing_steps,
            last_activity_at=customer.updated_at or now_utc,
        )

    @staticmethod
    async def transition_stage(
        session: AsyncSession,
        customer: Customer,
        target_stage: str,
    ) -> str:
        customer.onboarding_stage = target_stage
        await session.commit()
        return customer.onboarding_stage

    @staticmethod
    async def resume_journey(
        session: AsyncSession,
        customer: Customer,
    ) -> ResumeJourneyResponse:
        # 1. Retrieve active conversation or create one
        conv = None
        if customer.active_conversation_id:
            conv_stmt = (
                select(Conversation)
                .where(Conversation.id == customer.active_conversation_id)
                .options(selectinload(Conversation.messages))
            )
            res = await session.execute(conv_stmt)
            conv = res.scalar_one_or_none()

        if not conv:
            conv = Conversation(
                customer_id=customer.id,
                channel="web_chat",
                status="active",
                thread_title="Insurance Advisory Consultation",
                conversation_mode="general_advisory",
            )
            session.add(conv)
            await session.flush()
            customer.active_conversation_id = conv.id
            await session.commit()

        # Latest qualification
        qual_stmt = (
            select(CustomerQualification)
            .where(CustomerQualification.customer_id == customer.id)
            .order_by(CustomerQualification.created_at.desc())
        )
        qual_res = await session.execute(qual_stmt)
        latest_qual = qual_res.scalars().first()

        last_message_text = None
        if conv.messages:
            last_message_text = conv.messages[-1].content

        stage = customer.onboarding_stage or "discovery"
        suggested_action = "Explore available coverage plans or speak with your AI Insurance Advisor."
        if stage == "needs_assessment":
            suggested_action = "Complete your family and health needs questionnaire to discover tailored plans."
        elif stage == "product_matching":
            suggested_action = "Review your recommended policies and generate an indicative quote."
        elif stage == "quote_review":
            suggested_action = "Review your indicative quote and proceed to proposal onboarding."

        return ResumeJourneyResponse(
            thread_id=conv.id,
            conversation_id=conv.id,
            stage=stage,
            last_message=last_message_text,
            suggested_action=suggested_action,
            qualification_snapshot=latest_qual.factors_json if latest_qual and latest_qual.factors_json else {},
        )

