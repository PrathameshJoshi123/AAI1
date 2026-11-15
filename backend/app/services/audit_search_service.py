"""Audit Search Service: Multi-parameter compliance vault search and export engine."""
import csv
import io
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog
from app.models.auth import User
from app.schemas.admin import AuditLogItem, AuditLogSearchResponse


class AuditSearchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_audit_records(
        self,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        size: int = 25,
    ) -> AuditLogSearchResponse:
        """Search compliance records with dynamic filters and pagination."""
        base_query = select(AuditLog, User.email).outerjoin(User, AuditLog.user_id == User.id)

        if action:
            base_query = base_query.where(AuditLog.action.ilike(f"%{action}%"))
        if resource_type:
            base_query = base_query.where(AuditLog.resource_type.ilike(f"%{resource_type}%"))
        if resource_id:
            base_query = base_query.where(AuditLog.resource_id.ilike(f"%{resource_id}%"))
        if user_id:
            base_query = base_query.where(AuditLog.user_id == user_id)
        if from_date:
            base_query = base_query.where(AuditLog.timestamp >= from_date)
        if to_date:
            base_query = base_query.where(AuditLog.timestamp <= to_date)

        # Count total
        count_query = select(func.count(AuditLog.id))
        if action:
            count_query = count_query.where(AuditLog.action.ilike(f"%{action}%"))
        if resource_type:
            count_query = count_query.where(AuditLog.resource_type.ilike(f"%{resource_type}%"))
        if resource_id:
            count_query = count_query.where(AuditLog.resource_id.ilike(f"%{resource_id}%"))
        if user_id:
            count_query = count_query.where(AuditLog.user_id == user_id)
        if from_date:
            count_query = count_query.where(AuditLog.timestamp >= from_date)
        if to_date:
            count_query = count_query.where(AuditLog.timestamp <= to_date)

        total_res = await self.session.execute(count_query)
        total = total_res.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        exec_query = base_query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(size)
        rows = (await self.session.execute(exec_query)).all()

        records: List[AuditLogItem] = []
        for log, user_email in rows:
            records.append(
                AuditLogItem(
                    id=log.id,
                    user_id=log.user_id,
                    user_email=user_email,
                    action=log.action,
                    resource_type=log.resource_type,
                    resource_id=log.resource_id,
                    ip_address=log.ip_address,
                    changes_json=log.changes_json,
                    timestamp=log.timestamp,
                )
            )

        return AuditLogSearchResponse(records=records, total=total, page=page, size=size)

    async def export_audit_csv(
        self,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 1000,
    ) -> str:
        """Export matching audit records as a CSV string."""
        base_query = (
            select(AuditLog, User.email)
            .outerjoin(User, AuditLog.user_id == User.id)
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
        )
        if action:
            base_query = base_query.where(AuditLog.action.ilike(f"%{action}%"))
        if resource_type:
            base_query = base_query.where(AuditLog.resource_type.ilike(f"%{resource_type}%"))
        if from_date:
            base_query = base_query.where(AuditLog.timestamp >= from_date)
        if to_date:
            base_query = base_query.where(AuditLog.timestamp <= to_date)

        rows = (await self.session.execute(base_query)).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Timestamp", "User Email", "Action", "Resource Type", "Resource ID", "IP Address"])

        for log, user_email in rows:
            writer.writerow([
                log.id,
                log.timestamp.isoformat() if log.timestamp else "",
                user_email or "System/Anonymous",
                log.action,
                log.resource_type,
                log.resource_id,
                log.ip_address or "",
            ])

        return output.getvalue()

