export interface ExecutiveMetrics {
  total_prospects: number;
  qualified_leads: number;
  active_conversations: number;
  quotes_generated: number;
  applications_submitted: number;
  applications_awaiting_review: number;
  conversion_rate: number;
  pending_follow_ups: number;
}

export interface RecentActivityItem {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  actor_email: string | null;
  description: string;
  timestamp: string;
}

export interface RecentActivityResponse {
  activities: RecentActivityItem[];
  total: number;
}

export interface AdminCustomer {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  phone: string | null;
  city: string | null;
  state: string | null;
  onboarding_stage: string;
  risk_tier: string;
  annual_income: number | null;
  occupation: string | null;
  assigned_advisor_name: string | null;
  created_at: string;
}

export interface ChannelPerformance {
  channel: string;
  total_leads: number;
  qualified_leads: number;
  avg_score: number;
  applications_submitted: number;
  conversion_rate: number;
}

export interface ProductPerformance {
  product_id: string;
  product_name: string;
  category: string;
  quotes_count: number;
  applications_count: number;
  approved_count: number;
  conversion_rate: number;
  total_estimated_premium: number;
}

export interface AdvisorPerformance {
  advisor_id: string;
  advisor_name: string;
  email: string;
  active_cases: number;
  completed_reviews: number;
  pending_follow_ups: number;
  conversion_rate: number;
  is_available: boolean;
}

export interface TurnaroundAnalytics {
  avg_hours_to_quote: number;
  avg_hours_to_submission: number;
  avg_hours_to_underwriting_decision: number;
  sla_compliance_percentage: number;
}

export interface FunnelStage {
  stage_key: string;
  label: string;
  count: number;
  conversion_from_prev: number;
  drop_off_count: number;
}

export interface ConversionFunnelResponse {
  stages: FunnelStage[];
  overall_conversion: number;
}

export interface AgentTelemetry {
  id: number;
  agent_name: string;
  description: string | null;
  model_name: string;
  temperature: number;
  is_active: boolean;
  status: "active" | "paused" | "disabled";
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  success_rate: number;
  avg_latency_ms: number | null;
  last_executed_at: string | null;
}

export interface AgentExecutionLogItem {
  id: string;
  session_id: string;
  conversation_id: string | null;
  status: string;
  latency_ms: number | null;
  input_state: Record<string, unknown>;
  output_state: Record<string, unknown> | null;
  error_message: string | null;
  executed_at: string;
}

export interface AgentExecutionLogsResponse {
  agent_name: string;
  executions: AgentExecutionLogItem[];
  total: number;
}

export interface Employee {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  is_active: boolean;
  roles: string[];
  created_at: string;
  advisor_id?: string | null;
  license_number?: string | null;
  specializations?: string | null;
  max_active_cases?: number | null;
  active_cases_count?: number | null;
  is_available?: boolean | null;
  underwriter_id?: string | null;
  authority_level?: string | null;
  max_coverage_limit?: number | null;
}

export interface EmployeeCreatePayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role_names: string[];
  license_number?: string;
  specializations?: string;
  max_active_cases?: number;
  authority_level?: string;
  max_coverage_limit?: number;
}

export interface AdminProduct {
  id: string;
  name: string;
  category: string;
  description: string | null;
  base_premium: number;
  min_sum_assured: number;
  max_sum_assured: number;
  min_age: number;
  max_age: number;
  is_active: boolean;
  coverage_details?: Record<string, unknown> | null;
  benefits_list?: string[] | null;
  exclusions_list?: string[] | null;
  required_declarations?: string[] | null;
  required_documents?: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface AdminProductCreatePayload {
  name: string;
  category: string;
  description?: string;
  base_premium: number;
  min_sum_assured: number;
  max_sum_assured: number;
  min_age?: number;
  max_age?: number;
  is_active?: boolean;
  benefits_list?: string[];
  exclusions_list?: string[];
  required_declarations?: string[];
  required_documents?: string[];
}

export interface AuditLogRecord {
  id: number;
  user_id: string | null;
  user_email: string | null;
  action: string;
  resource_type: string;
  resource_id: string;
  ip_address: string | null;
  changes_json: Record<string, unknown> | null;
  timestamp: string;
}

export interface AuditLogSearchResponse {
  records: AuditLogRecord[];
  total: number;
  page: number;
  size: number;
}

export interface IntegrationHealth {
  service_key: string;
  name: string;
  category: "ai" | "comms" | "insurer" | "storage";
  status: "active" | "warning" | "error" | "not_configured";
  details: string;
  last_checked_at: string;
  endpoint_or_host: string | null;
}

export interface SystemSetting {
  id: number;
  key: string;
  value_json: Record<string, unknown>;
  description: string | null;
  updated_at: string;
}
