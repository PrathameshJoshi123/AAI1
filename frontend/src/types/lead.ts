export type LeadStatus =
  | "new"
  | "engaged"
  | "qualified"
  | "converted"
  | "dropped"
  | string;

export type LeadSegment =
  | "top_of_funnel"
  | "warm_consideration"
  | "high_intent"
  | "price_sensitive"
  | "dormant"
  | string;

export type SignalType =
  | "page_view"
  | "time_on_page"
  | "quote_attempt"
  | "coverage_calculator_used"
  | "comparison_viewed"
  | "faq_opened"
  | "drop_off_step"
  | "chat_initiated"
  | string;

export type ConsentType =
  | "terms_of_service"
  | "privacy_policy"
  | "marketing_contact"
  | "quote_generation"
  | "medical_record_access"
  | string;

export type ScoreCategory =
  | "profile"
  | "intent"
  | "engagement"
  | "consent"
  | "penalty"
  | string;

export type TimelineEventType =
  | "PROSPECT_CREATED"
  | "CONSENT_GRANTED"
  | "CONSENT_REVOKED"
  | "BEHAVIORAL_SIGNAL"
  | "SCORE_RECALCULATED"
  | "ADVISOR_ASSIGNED"
  | "AI_INTERACTION_SUMMARY"
  | "ADVISOR_NOTE_ADDED"
  | string;

export interface ScoreFactor {
  rule_code: string;
  rule_name: string;
  category: ScoreCategory;
  points_awarded: number;
  rationale: string;
}

export interface LeadScore {
  id?: number;
  prospect_id?: string;
  score: number;
  calculated_at: string;
  factors?: ScoreFactor[];
  score_factors_json?: {
    total_score?: number;
    factors: ScoreFactor[];
  };
}

export interface BehavioralSignal {
  id?: number;
  prospect_id?: string;
  session_id: string;
  signal_type: SignalType;
  payload_json?: Record<string, unknown>;
  payload?: Record<string, unknown>;
  client_timestamp?: string;
  created_at: string;
}

export interface ConsentRecord {
  id?: number;
  prospect_id: string;
  consent_type: ConsentType;
  consent_version: string;
  is_granted: boolean;
  ip_address?: string | null;
  user_agent?: string | null;
  granted_at?: string | null;
  revoked_at?: string | null;
  revocation_reason?: string | null;
  created_at?: string;
}

export interface LeadRecord {
  id: string;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  source?: string | null;
  source_id?: number | null;
  source_name?: string | null;
  status: LeadStatus;
  segment: LeadSegment;
  target_insurance_type?: string | null;
  assigned_advisor_id?: string | null;
  assigned_advisor_name?: string | null;
  assigned_at?: string | null;
  leadScore?: number;
  score?: number;
  latest_score?: LeadScore | null;
  can_contact?: boolean;
  active_consents?: string[];
  signals_count?: number;
  estimated_budget_min?: number | null;
  estimated_budget_max?: number | null;
  created_at: string;
  createdAt?: string;
  last_activity_at: string;
}

export interface ProspectDetail {
  id: string;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  status: LeadStatus;
  segment: LeadSegment;
  target_insurance_type?: string | null;
  source_id?: number | null;
  source_name?: string | null;
  utm_source?: string | null;
  utm_medium?: string | null;
  utm_campaign?: string | null;
  utm_term?: string | null;
  utm_content?: string | null;
  assigned_advisor_id?: string | null;
  assigned_advisor_name?: string | null;
  assigned_at?: string | null;
  created_at: string;
  last_activity_at: string;
  latest_score?: LeadScore | null;
  active_consents: string[];
  can_contact: boolean;
  signals_count: number;
  signals?: BehavioralSignal[];
  consents?: ConsentRecord[];
  estimated_budget_min?: number | null;
  estimated_budget_max?: number | null;
  qualification_notes?: string | null;
}

export interface ProspectFilterParams {
  query?: string;
  status?: string | string[];
  segment?: string | string[];
  source_id?: number;
  source_name?: string;
  assigned_advisor_id?: string;
  min_score?: number;
  max_score?: number;
  consented_only?: boolean;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  sort_by?: "last_activity_at" | "created_at" | "score" | string;
  sort_order?: "asc" | "desc";
}

export interface AdvisorSummary {
  id: string;
  user_id?: string;
  name: string;
  email?: string;
  license_number: string;
  specializations?: string | string[];
  current_active_cases: number;
  max_active_cases: number;
  is_available: boolean;
  load_percentage?: number;
}

export interface LeadTimelineEvent {
  id: string | number;
  event_type: TimelineEventType;
  title: string;
  description: string;
  timestamp: string;
  actor?: string;
  metadata?: Record<string, unknown>;
}

export interface PaginatedLeadsResponse {
  items: LeadRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AssignedLeadItem {
  id: string;
  prospect_id: string;
  customer_name: string;
  customer_email?: string | null;
  customer_phone?: string | null;
  intended_coverage: string;
  score: number;
  segment: LeadSegment;
  can_contact: boolean;
  contact_channels: string[];
  assigned_at: string;
  last_activity_at: string;
  status: string;
  notes_count?: number;
  last_note?: string | null;
}

export interface OutreachLogRequest {
  outcome: "connected_interested" | "busy_callback_requested" | "unreachable" | "not_interested";
  notes: string;
  channel: "phone" | "email" | "whatsapp" | "meeting";
  follow_up_date?: string;
  target_status?: "contacted" | "qualified" | "disqualified";
}
