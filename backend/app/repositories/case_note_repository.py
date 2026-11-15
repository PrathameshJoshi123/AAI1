"""Repository for Case Notes (Internal collaboration)."""
from typing import List, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.underwriting import CaseNote
from app.repositories.base import BaseRepository


class CaseNoteRepository(BaseRepository[CaseNote]):
    def __init__(self, session: AsyncSession):
        super().__init__(CaseNote, session)

    async def list_for_case(self, case_id: str, include_confidential: bool = False) -> Sequence[CaseNote]:
        stmt = (
            select(CaseNote)
            .where(CaseNote.case_id == case_id)
            .options(selectinload(CaseNote.author))
            .order_by(CaseNote.created_at.desc())
        )
        if not include_confidential:
            stmt = stmt.where(CaseNote.is_confidential == False)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_note(self, note: CaseNote) -> CaseNote:
        self.session.add(note)
        await self.session.flush()
        return note

