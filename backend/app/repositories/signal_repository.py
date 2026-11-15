"""Behavioral signals data access repository."""
from typing import List, Optional, Sequence
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prospect import BehavioralSignal
from app.repositories.base import BaseRepository


class SignalRepository(BaseRepository[BehavioralSignal]):
    def __init__(self, session: AsyncSession):
        super().__init__(BehavioralSignal, session)

    async def get_signals_for_prospect(
        self, prospect_id: str, limit: int = 50
    ) -> Sequence[BehavioralSignal]:
        stmt = (
            select(BehavioralSignal)
            .where(BehavioralSignal.prospect_id == prospect_id)
            .order_by(desc(BehavioralSignal.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_signals_by_session(
        self, session_id: str
    ) -> Sequence[BehavioralSignal]:
        stmt = (
            select(BehavioralSignal)
            .where(BehavioralSignal.session_id == session_id)
            .order_by(BehavioralSignal.created_at)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_signal_counts_by_type(
        self, prospect_id: str
    ) -> dict[str, int]:
        stmt = (
            select(BehavioralSignal.signal_type, func.count(BehavioralSignal.id))
            .where(BehavioralSignal.prospect_id == prospect_id)
            .group_by(BehavioralSignal.signal_type)
        )
        result = await self.session.execute(stmt)
        return dict(result.all())

    async def get_cumulative_dwell_seconds(self, prospect_id: str) -> int:
        """Sum duration_seconds stored in payload_json for time_on_page signals."""
        signals = await self.get_signals_for_prospect(prospect_id, limit=200)
        total_seconds = 0
        for s in signals:
            if s.signal_type == "time_on_page" and s.payload_json:
                total_seconds += int(s.payload_json.get("duration_seconds", 0))
        return total_seconds

    async def get_distinct_pages_visited(self, prospect_id: str) -> int:
        """Count distinct page paths visited by this prospect."""
        signals = await self.get_signals_for_prospect(prospect_id, limit=200)
        pages = set()
        for s in signals:
            if s.signal_type == "page_view" and s.payload_json:
                path = s.payload_json.get("path") or s.payload_json.get("url")
                if path:
                    pages.add(path)
        return len(pages)

