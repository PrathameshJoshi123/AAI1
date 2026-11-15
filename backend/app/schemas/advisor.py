"""Pydantic schemas for Advisor Workspace and Cockpit."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class WorkspaceKPICounters(BaseModel):
    active_cases_count: int
    pending_document_verifications: int
    overdue_follow_ups_count: int
    cases_awaiting_info_count: int
    sla_at_risk_count: int
    total_assigned_leads: int


class UrgentTaskItem(BaseModel):
    id: str
    task_type: str  # SLA_BREACH_WARNING, PENDING_DOC_VERIFICATION, OVERDUE_FOLLOW_UP, ESCALATED_CASE
    title: str
    description: str
    priority: str  # urgent, high, medium
    due_date: Optional[datetime] = None
    link_url: str
    related_entity_id: str


class WorkspaceDashboardData(BaseModel):
    kpis: WorkspaceKPICounters
    urgent_tasks: List[UrgentTaskItem]

