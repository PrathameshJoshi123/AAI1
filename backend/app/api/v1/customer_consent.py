"""Customer DPDP / IRDAI Consent and Privacy Endpoints."""
from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.audit import ConsentRecord
from app.models.auth import User
from app.schemas.common import APIResponse

router = APIRouter(prefix="/customer/consent", tags=["Customer Privacy & Consent"])


class ConsentItem(BaseModel):
    id: int
    consent_type: str
    consent_version: str
    is_active: bool
    granted_at: datetime
    revoked_at: datetime | None = None


class CustomerConsentGrant(BaseModel):
    consent_type: str = Field(..., pattern=r"^(terms_of_service|privacy_policy|marketing_contact|medical_record_access)$")
    consent_version: str = Field("2026.1", max_length=20)


class CustomerConsentRevoke(BaseModel):
    consent_type: str


@router.get("", response_model=APIResponse[List[ConsentItem]])
async def list_consents(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    stmt = (
        select(ConsentRecord)
        .where(ConsentRecord.user_id == current_user.id)
        .order_by(ConsentRecord.granted_at.desc())
    )
    res = await session.execute(stmt)
    records = res.scalars().all()

    items = [
        ConsentItem(
            id=r.id,
            consent_type=r.consent_type,
            consent_version=r.consent_version,
            is_active=r.revoked_at is None,
            granted_at=r.granted_at,
            revoked_at=r.revoked_at,
        )
        for r in records
    ]
    return APIResponse(data=items, message="Customer consent records retrieved.")


@router.post("/grant", response_model=APIResponse[ConsentItem])
async def grant_consent(
    payload: CustomerConsentGrant,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    record = ConsentRecord(
        user_id=current_user.id,
        consent_type=payload.consent_type,
        consent_version=payload.consent_version,
        granted_at=datetime.now(timezone.utc),
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)

    item = ConsentItem(
        id=record.id,
        consent_type=record.consent_type,
        consent_version=record.consent_version,
        is_active=True,
        granted_at=record.granted_at,
        revoked_at=None,
    )
    return APIResponse(data=item, message=f"Consent for '{payload.consent_type}' granted successfully.")


@router.post("/revoke", response_model=APIResponse[dict])
async def revoke_consent(
    payload: CustomerConsentRevoke,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    stmt = (
        select(ConsentRecord)
        .where(
            ConsentRecord.user_id == current_user.id,
            ConsentRecord.consent_type == payload.consent_type,
            ConsentRecord.revoked_at.is_(None),
        )
    )
    res = await session.execute(stmt)
    active_records = res.scalars().all()

    now_utc = datetime.now(timezone.utc)
    for r in active_records:
        r.revoked_at = now_utc

    await session.commit()
    return APIResponse(
        data={"revoked_count": len(active_records), "consent_type": payload.consent_type},
        message=f"Consent for '{payload.consent_type}' revoked successfully.",
    )

