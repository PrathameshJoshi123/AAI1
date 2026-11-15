"""Customer Chat Service coordinating multi-turn dialogue and message persistence."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import Customer
from app.models.conversation import Conversation, ConversationMessage
from app.models.recommendation import CustomerQualification
from app.repositories.product_repository import ProductRepository
from app.ai.agents.definitions.conversational_advisor_agent import (
    ConversationalAdvisorAgent,
    ConversationalAdvisorInput,
)
from app.schemas.conversation import (
    CustomerChatTurnRequest,
    ConversationMessageRead,
    ConversationThreadRead,
    WidgetDataPayload,
)


class CustomerChatService:
    def __init__(self):
        self.advisor_agent = ConversationalAdvisorAgent()

    async def execute_turn(
        self,
        session: AsyncSession,
        customer: Customer,
        turn_request: CustomerChatTurnRequest,
    ) -> ConversationMessageRead:
        now_utc = datetime.now(timezone.utc)

        # 1. Load or initialize Conversation
        conv_id = turn_request.conversation_id or customer.active_conversation_id
        conv = None
        if conv_id:
            stmt = (
                select(Conversation)
                .where(Conversation.id == conv_id)
                .options(selectinload(Conversation.messages))
            )
            res = await session.execute(stmt)
            conv = res.scalar_one_or_none()

        if not conv:
            conv = Conversation(
                customer_id=customer.id,
                channel="web_chat",
                status="active",
                thread_title="Personal Insurance Consultation",
                conversation_mode="general_advisory",
                last_turn_at=now_utc,
            )
            session.add(conv)
            await session.flush()
            customer.active_conversation_id = conv.id

        # 2. Persist Customer Message
        user_msg = ConversationMessage(
            conversation_id=conv.id,
            sender_type="user",
            sender_id=customer.user_id,
            content=turn_request.message,
            message_type="text",
            created_at=now_utc,
        )
        session.add(user_msg)
        await session.flush()

        # 3. Build context for the AI Advisor
        history: List[Dict[str, str]] = []
        if conv.messages:
            for m in conv.messages[-8:]:
                role = "assistant" if m.sender_type == "agent" else "user"
                history.append({"role": role, "content": m.content})

        # Fetch latest qualification
        qual_stmt = (
            select(CustomerQualification)
            .where(CustomerQualification.customer_id == customer.id)
            .order_by(CustomerQualification.created_at.desc())
        )
        q_res = await session.execute(qual_stmt)
        latest_qual = q_res.scalars().first()
        qual_dict = latest_qual.factors_json if latest_qual and latest_qual.factors_json else {}

        profile_dict = {
            "city": customer.city,
            "annual_income": float(customer.annual_income) if customer.annual_income else None,
            "occupation": customer.occupation,
            "tobacco_user": customer.tobacco_user,
            "onboarding_stage": customer.onboarding_stage,
        }

        # 4. Fetch available catalog plans for accurate grounding
        product_repo = ProductRepository(session)
        products = await product_repo.list_active_products()
        available_plans: List[Dict[str, Any]] = []
        term_prod_id = ""
        for p in products:
            if p.category == "term_life" and not term_prod_id:
                term_prod_id = p.id
            config_summaries = []
            if p.configurations:
                for c in p.configurations:
                    config_summaries.append(
                        f"{c.tier_name}: ₹{c.min_sum_assured:,.0f} - ₹{c.max_sum_assured:,.0f}, terms {c.term_options_json} yrs"
                    )
            pricing_summary = ""
            if p.pricing_matrices:
                matrix = p.pricing_matrices[0]
                rates = matrix.age_band_rates_json or {}
                pricing_summary = f"Age 18-25: ₹{rates.get('18-25', 1.2)}/k base rate, tax: {matrix.tax_rate_percent}%"

            benefits = [b.get("name") for b in (p.benefits_list_json or []) if isinstance(b, dict)]
            available_plans.append({
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "category": p.category,
                "insurer_name": getattr(p, "insurer_name", "Star Union Life & General") or "Star Union Life & General",
                "description": p.description,
                "configurations_summary": "; ".join(config_summaries),
                "key_benefits": benefits,
                "pricing_summary": pricing_summary,
            })

        # 5. Invoke the Conversational Advisor Agent
        agent_input = ConversationalAdvisorInput(
            user_message=turn_request.message,
            language=turn_request.language or customer.preferred_language or "en",
            conversation_history=history,
            customer_profile=profile_dict,
            qualification_data=qual_dict,
            available_plans=available_plans,
        )

        agent_output = await self.advisor_agent.run(agent_input)

        # 6. Process action buttons with fallback safeguard
        action_buttons_data: List[Dict[str, Any]] = []
        if agent_output.action_buttons:
            for b in agent_output.action_buttons:
                if hasattr(b, "model_dump"):
                    action_buttons_data.append(b.model_dump())
                elif isinstance(b, dict):
                    action_buttons_data.append(b)

        # Normalize URL params (e.g. fix productid -> product_id, sumassured -> sum_assured)
        for b in action_buttons_data:
            if "url" in b and isinstance(b["url"], str):
                b["url"] = b["url"].replace("productid=", "product_id=").replace("sumassured=", "sum_assured=")

        user_msg_lower = turn_request.message.lower()
        if any(k in user_msg_lower for k in ["quote", "formal", "proceed", "yes", "1 crore", "apply"]):
            quote_link = f"/customer/quotes?product_id={term_prod_id}&sum_assured=10000000&term=30" if term_prod_id else "/customer/quotes"
            if not any("quote" in b.get("url", "") for b in action_buttons_data):
                action_buttons_data.insert(0, {
                    "label": "View & Customize Formal Quote",
                    "url": quote_link,
                    "variant": "default",
                })
            if not any("onboarding" in b.get("url", "") for b in action_buttons_data):
                action_buttons_data.append({
                    "label": "Start Proposal Onboarding",
                    "url": "/customer/onboarding",
                    "variant": "secondary",
                })

        # Sanitize response text so raw JSON or 'Action Button:' snippets never leak into chat bubble
        import re
        clean_content = agent_output.response_text or ""
        clean_content = re.sub(r"(?i)\baction\s*buttons?:\s*\{[^}]*\}", "", clean_content)
        clean_content = re.sub(r"(?i)\baction\s*buttons?:\s*\[[^\]]*\]", "", clean_content)
        clean_content = re.sub(r"(?i)\bsuggested\s*chips?:\s*(?:\n\s*[-*•]?[^\n]+)+", "", clean_content)
        clean_content = re.sub(r"```(?:json)?\s*\{\s*\"label\"[^\`]*```", "", clean_content)
        clean_content = clean_content.strip()

        # 7. Persist Agent Response Message
        widget_data_dict = {
            "chips": agent_output.suggested_chips,
            "disclaimer": agent_output.indicative_disclaimer,
            "widget": agent_output.widget,
            "action_buttons": action_buttons_data,
        }

        agent_msg = ConversationMessage(
            conversation_id=conv.id,
            sender_type="agent",
            sender_id="ps21_advisor_agent",
            content=clean_content,
            message_type="suggested_chips" if agent_output.suggested_chips else "text",
            widget_data_json=widget_data_dict,
            created_at=datetime.now(timezone.utc),
        )
        session.add(agent_msg)

        conv.last_turn_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(agent_msg)

        widget_payload = None
        if agent_output.widget and isinstance(agent_output.widget, dict):
            widget_payload = WidgetDataPayload(**agent_output.widget)

        return ConversationMessageRead(
            id=agent_msg.id,
            conversation_id=conv.id,
            sender_type="agent",
            sender_name="PS-21 AI Insurance Advisor",
            content=agent_msg.content,
            message_type=agent_msg.message_type,
            suggested_chips=agent_output.suggested_chips,
            widget_data=widget_payload,
            action_buttons=action_buttons_data,
            created_at=agent_msg.created_at,
        )

    async def get_history(
        self,
        session: AsyncSession,
        customer: Customer,
        conversation_id: Optional[str] = None,
    ) -> ConversationThreadRead:
        conv_id = conversation_id or customer.active_conversation_id
        if not conv_id:
            now_utc = datetime.now(timezone.utc)
            conv = Conversation(
                customer_id=customer.id,
                channel="web_chat",
                status="active",
                thread_title="Insurance Advisory Consultation",
                last_turn_at=now_utc,
            )
            session.add(conv)
            await session.commit()
            customer.active_conversation_id = conv.id
            await session.commit()
            conv_id = conv.id

        # Get term product id if available for links in history
        product_repo = ProductRepository(session)
        products = await product_repo.list_active_products(category="term_life")
        term_prod_id = products[0].id if products else ""
        quote_link = f"/customer/quotes?product_id={term_prod_id}&sum_assured=10000000&term=30" if term_prod_id else "/customer/quotes"

        stmt = (
            select(Conversation)
            .where(Conversation.id == conv_id, Conversation.customer_id == customer.id)
            .options(selectinload(Conversation.messages))
        )
        res = await session.execute(stmt)
        conv = res.scalar_one_or_none()
        if not conv:
            raise ValueError("Conversation not found or unauthorized access.")

        messages_read: List[ConversationMessageRead] = []
        for m in conv.messages:
            chips = None
            widget_payload = None
            action_buttons = None
            if m.widget_data_json and isinstance(m.widget_data_json, dict):
                chips = m.widget_data_json.get("chips")
                action_buttons = m.widget_data_json.get("action_buttons")
                w_raw = m.widget_data_json.get("widget")
                if w_raw and isinstance(w_raw, dict):
                    widget_payload = WidgetDataPayload(**w_raw)

            # Auto-supplement buttons for historical messages where agent paused or offered quotes
            if m.sender_type == "agent" and not action_buttons:
                content_lower = (m.content or "").lower()
                if any(w in content_lower for w in ["formal quote", "arrange this", "hold on", "1 crore", "underwriting"]):
                    action_buttons = [
                        {"label": "View & Customize Formal Quote", "url": quote_link, "variant": "default"},
                        {"label": "Start Proposal Onboarding", "url": "/customer/onboarding", "variant": "secondary"},
                    ]

            messages_read.append(
                ConversationMessageRead(
                    id=m.id,
                    conversation_id=conv.id,
                    sender_type=m.sender_type,
                    sender_name="You" if m.sender_type == "user" else "PS-21 AI Insurance Advisor",
                    content=m.content,
                    message_type=m.message_type or "text",
                    suggested_chips=chips,
                    widget_data=widget_payload,
                    action_buttons=action_buttons,
                    created_at=m.created_at,
                )
            )

        return ConversationThreadRead(
            id=conv.id,
            customer_id=customer.id,
            title=conv.thread_title or "Insurance Advisory Consultation",
            status=conv.status,
            mode=conv.conversation_mode or "general_advisory",
            messages=messages_read,
            created_at=conv.initiated_at,
            last_turn_at=conv.last_turn_at,
        )

    async def list_for_advisor(self, session: AsyncSession) -> List[Dict[str, Any]]:
        stmt = (
            select(Conversation)
            .options(
                selectinload(Conversation.customer).selectinload(Customer.user),
                selectinload(Conversation.messages),
            )
            .order_by(desc(Conversation.last_turn_at).nullslast(), desc(Conversation.initiated_at))
            .limit(100)
        )
        res = await session.execute(stmt)
        convs = res.scalars().all()
        results = []
        for c in convs:
            cust_name = c.customer.user.full_name if c.customer and c.customer.user else "Customer"
            cust_email = c.customer.user.email if c.customer and c.customer.user else ""
            results.append({
                "id": c.id,
                "customer_id": c.customer_id,
                "customer_name": cust_name,
                "customer_email": cust_email,
                "title": c.thread_title or "Insurance Advisory Consultation",
                "status": c.status,
                "mode": c.conversation_mode or "general_advisory",
                "channel": c.channel,
                "message_count": len(c.messages),
                "last_message": c.messages[-1].content if c.messages else "No messages yet",
                "last_turn_at": c.last_turn_at.isoformat() if c.last_turn_at else c.initiated_at.isoformat(),
            })
        return results

    async def get_by_id_for_advisor(self, session: AsyncSession, conversation_id: str) -> Optional[ConversationThreadRead]:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        res = await session.execute(stmt)
        conv = res.scalar_one_or_none()
        if not conv:
            return None

        messages_read: List[ConversationMessageRead] = []
        for m in conv.messages:
            chips = None
            widget_payload = None
            if m.widget_data_json and isinstance(m.widget_data_json, dict):
                chips = m.widget_data_json.get("chips")
                w_raw = m.widget_data_json.get("widget")
                if w_raw and isinstance(w_raw, dict):
                    widget_payload = WidgetDataPayload(**w_raw)

            messages_read.append(
                ConversationMessageRead(
                    id=m.id,
                    conversation_id=conv.id,
                    sender_type=m.sender_type,
                    sender_name="Customer" if m.sender_type == "user" else "PS-21 AI Insurance Advisor",
                    content=m.content,
                    message_type=m.message_type or "text",
                    suggested_chips=chips,
                    widget_data=widget_payload,
                    created_at=m.created_at,
                )
            )

        return ConversationThreadRead(
            id=conv.id,
            customer_id=conv.customer_id,
            title=conv.thread_title or "Insurance Advisory Consultation",
            status=conv.status,
            mode=conv.conversation_mode or "general_advisory",
            messages=messages_read,
            created_at=conv.initiated_at,
            last_turn_at=conv.last_turn_at,
        )


customer_chat_service = CustomerChatService()

