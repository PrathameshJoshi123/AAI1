export interface WorkspaceKPICounters {
  active_cases_count: number;
  pending_document_verifications: number;
  overdue_follow_ups_count: number;
  cases_awaiting_info_count: number;
  sla_at_risk_count: number;
  total_assigned_leads: number;
}

export interface UrgentTaskItem {
  id: string;
  task_type: "SLA_BREACH_WARNING" | "PENDING_DOC_VERIFICATION" | "OVERDUE_FOLLOW_UP" | "ESCALATED_CASE" | string;
  title: string;
  description: string;
  priority: "urgent" | "high" | "medium" | "low" | string;
  due_date?: string | null;
  link_url: string;
  related_entity_id: string;
}

export interface WorkspaceDashboardData {
  kpis: WorkspaceKPICounters;
  urgent_tasks: UrgentTaskItem[];
}

export interface FollowUpItem {
  id: number;
  customer_id?: string | null;
  prospect_id?: string | null;
  assigned_advisor_id: string;
  target_name?: string | null;
  target_contact?: string | null;
  due_date: string;
  channel: "phone" | "email" | "chat" | "meeting" | string;
  status: "pending" | "completed" | "cancelled" | string;
  priority: "low" | "medium" | "high" | string;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppNotification {
  id: number;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  link_url?: string | null;
  created_at: string;
}

