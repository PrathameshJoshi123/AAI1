"""Repository for Application Documents and Customer Vault."""
from typing import Optional, Sequence
from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.application import ApplicationDocument
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[ApplicationDocument]):
    def __init__(self, session: AsyncSession):
        super().__init__(ApplicationDocument, session)

    async def get_by_id_with_relations(self, document_id: str) -> Optional[ApplicationDocument]:
        stmt = (
            select(ApplicationDocument)
            .where(ApplicationDocument.id == document_id)
            .options(
                selectinload(ApplicationDocument.application),
                selectinload(ApplicationDocument.customer),
                selectinload(ApplicationDocument.verified_by),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_application(self, application_id: str) -> Sequence[ApplicationDocument]:
        stmt = (
            select(ApplicationDocument)
            .where(ApplicationDocument.application_id == application_id)
            .order_by(desc(ApplicationDocument.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_customer(self, customer_id: str) -> Sequence[ApplicationDocument]:
        stmt = (
            select(ApplicationDocument)
            .where(ApplicationDocument.customer_id == customer_id)
            .order_by(desc(ApplicationDocument.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_queue(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[ApplicationDocument]:
        stmt = (
            select(ApplicationDocument)
            .options(
                selectinload(ApplicationDocument.application),
                selectinload(ApplicationDocument.customer),
                selectinload(ApplicationDocument.verified_by),
            )
            .order_by(desc(ApplicationDocument.created_at))
            .limit(limit)
            .offset(offset)
        )
        if status:
            stmt = stmt.where(ApplicationDocument.verification_status == status)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_latest_version(self, application_id: str, document_type: str) -> Optional[ApplicationDocument]:
        stmt = (
            select(ApplicationDocument)
            .where(
                ApplicationDocument.application_id == application_id,
                ApplicationDocument.document_type == document_type,
            )
            .order_by(desc(ApplicationDocument.version))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
