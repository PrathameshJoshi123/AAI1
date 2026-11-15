"""Legal consent tracking repository."""
from datetime import datetime
from typing import List, Optional, Sequence
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import ConsentRecord
from app.models.base import utc_now
from app.repositories.base import BaseRepository


class ConsentRepository(BaseRepository[ConsentRecord]):
    def __init__(self, session: AsyncSession):
        super().__init__(ConsentRecord, session)

    async def get_active_consents_for_prospect(
        self, prospect_id: str
    ) -> Sequence[ConsentRecord]:
        stmt = (
            select(ConsentRecord)
            .where(
                ConsentRecord.prospect_id == prospect_id,
                ConsentRecord.revoked_at.is_(None),
            )
            .order_by(desc(ConsentRecord.granted_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def has_active_consent(
        self, prospect_id: str, consent_type: str = "marketing_contact"
    ) -> bool:
        stmt = (
            select(ConsentRecord)
            .where(
                ConsentRecord.prospect_id == prospect_id,
                ConsentRecord.consent_type == consent_type,
                ConsentRecord.revoked_at.is_(None),
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def has_revoked_consent(
        self, prospect_id: str, consent_type: str = "marketing_contact"
    ) -> bool:
        stmt = (
            select(ConsentRecord)
            .where(
                ConsentRecord.prospect_id == prospect_id,
                ConsentRecord.consent_type == consent_type,
                ConsentRecord.revoked_at.is_not(None),
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def revoke_consent(
        self, prospect_id: str, consent_type: str
    ) -> Optional[ConsentRecord]:
        stmt = (
            select(ConsentRecord)
            .where(
                ConsentRecord.prospect_id == prospect_id,
                ConsentRecord.consent_type == consent_type,
                ConsentRecord.revoked_at.is_(None),
            )
            .order_by(desc(ConsentRecord.granted_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if record:
            record.revoked_at = utc_now()
            await self.session.flush()
        return record
