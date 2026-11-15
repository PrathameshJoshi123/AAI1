"""Pydantic schemas for Audit and Compliance."""
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: int
    user_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    changes_json: Optional[Dict[str, Any]] = None
    timestamp: datetime

    model_config = {"from_attributes": True}

