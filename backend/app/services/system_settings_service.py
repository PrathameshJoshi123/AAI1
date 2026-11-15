"""System Settings Service: Dynamic configuration management with audit diff logging."""
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import utc_now
from app.models.system import SystemSetting
from app.models.audit import AuditLog
from app.core.exceptions import NotFoundException
from app.schemas.admin import SystemSettingResponse, SystemSettingUpdateRequest

DEFAULT_SETTINGS = [
    {
        "key": "underwriting_sla_hours",
        "description": "Standard, urgent, and substandard turnaround SLA limits in hours.",
        "value_json": {"standard": 24, "urgent": 4, "substandard": 48},
    },
    {
        "key": "lead_auto_assignment",
        "description": "Rules for automated prospect distribution among available advisors.",
        "value_json": {"enabled": True, "strategy": "round_robin", "max_lead_cap": 30},
    },
    {
        "key": "business_hours",
        "description": "Operational working hours and days for SLA countdown calculation.",
        "value_json": {
            "start_time": "09:00",
            "end_time": "18:00",
            "timezone": "Asia/Kolkata",
            "work_days": [1, 2, 3, 4, 5],
        },
    },
    {
        "key": "compliance_disclosures",
        "description": "Mandatory IRDAI statutory notices and record retention parameters.",
        "value_json": {
            "mandate_irdai_notice": True,
            "record_retention_years": 8,
            "cooling_off_period_days": 15,
        },
    },
]


class SystemSettingsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _ensure_default_settings(self) -> None:
        """Seed default settings if missing."""
        for item in DEFAULT_SETTINGS:
            query = select(SystemSetting).where(SystemSetting.key == item["key"])
            existing = (await self.session.execute(query)).scalar_one_or_none()
            if not existing:
                setting = SystemSetting(
                    key=item["key"],
                    description=item["description"],
                    value_json=item["value_json"],
                    is_encrypted=False,
                )
                self.session.add(setting)
        await self.session.commit()

    async def get_all_settings(self) -> List[SystemSettingResponse]:
        """Fetch all dynamic system settings."""
        await self._ensure_default_settings()

        query = select(SystemSetting).order_by(SystemSetting.key)
        result = await self.session.execute(query)
        settings_list = result.scalars().all()

        return [
            SystemSettingResponse(
                id=s.id,
                key=s.key,
                value_json=s.value_json,
                description=s.description,
                updated_at=s.updated_at,
            )
            for s in settings_list
        ]

    async def update_setting(
        self, key: str, req: SystemSettingUpdateRequest, admin_user_id: Optional[str] = None
    ) -> SystemSettingResponse:
        """Update a specific system setting and record an audit entry."""
        query = select(SystemSetting).where(SystemSetting.key == key)
        result = await self.session.execute(query)
        setting = result.scalar_one_or_none()

        if not setting:
            raise NotFoundException(f"System setting '{key}' not found.")

        old_val = setting.value_json
        setting.value_json = req.value_json
        if req.description:
            setting.description = req.description

        audit = AuditLog(
            user_id=admin_user_id,
            action="UPDATE_SYSTEM_SETTING",
            resource_type="SystemSetting",
            resource_id=key,
            changes_json={"old_value": old_val, "new_value": req.value_json},
            timestamp=utc_now(),
        )
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(setting)

        return SystemSettingResponse(
            id=setting.id,
            key=setting.key,
            value_json=setting.value_json,
            description=setting.description,
            updated_at=setting.updated_at,
        )

