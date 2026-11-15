"""Customer Conversational AI Endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_customer, get_db, require_roles
from app.core.exceptions import EntityNotFoundException
from app.models.auth import User
from app.models.profile import Customer
from app.schemas.common import APIResponse
from app.schemas.conversation import (
    CustomerChatTurnRequest,
    ConversationMessageRead,
    ConversationThreadRead,
)
from app.services.customer_chat_service import customer_chat_service

router = APIRouter(prefix="/customer/chat", tags=["Customer Conversational AI"])


@router.get("/advisor/conversations", response_model=APIResponse[List[dict]])
async def list_conversations_for_advisor(
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """List customer AI conversation threads for employee inspection."""
    convs = await customer_chat_service.list_for_advisor(session)
    return APIResponse(data=convs)


@router.get("/advisor/conversations/{conversation_id}", response_model=APIResponse[ConversationThreadRead])
async def get_conversation_for_advisor(
    conversation_id: str,
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve full transcript of a customer conversation thread for review."""
    conv = await customer_chat_service.get_by_id_for_advisor(session, conversation_id)
    if not conv:
        raise EntityNotFoundException("Conversation thread not found.")
    return APIResponse(data=conv)


@router.post("/turn", response_model=APIResponse[ConversationMessageRead])
async def execute_chat_turn(
    payload: CustomerChatTurnRequest,
    customer: Customer = Depends(get_current_customer),
    session: AsyncSession = Depends(get_db),
):
    reply = await customer_chat_service.execute_turn(session, customer, payload)
    return APIResponse(data=reply, message="Conversational turn executed successfully.")


@router.get("/history", response_model=APIResponse[ConversationThreadRead])
async def get_chat_history(
    conversation_id: Optional[str] = Query(None, description="Optional conversation ID"),
    customer: Customer = Depends(get_current_customer),
    session: AsyncSession = Depends(get_db),
):
    history = await customer_chat_service.get_history(session, customer, conversation_id)
    return APIResponse(data=history, message="Conversation history retrieved successfully.")

