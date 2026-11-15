export interface CustomerProfile {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  date_of_birth?: string | null;
  marital_status?: string | null;
  occupation?: string | null;
  annual_income?: number | null;
  health_status?: string | null;
  risk_tier: string;
  preferred_language: string;
  city?: string | null;
  pincode?: string | null;
  state?: string | null;
  gender?: string | null;
  tobacco_user: boolean;
  onboarding_stage: string;
  active_conversation_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CustomerProfileUpdatePayload {
  first_name?: string;
  last_name?: string;
  phone?: string;
  date_of_birth?: string;
  marital_status?: string;
  occupation?: string;
  annual_income?: number;
  gender?: string;
  city?: string;
  pincode?: string;
  state?: string;
  tobacco_user?: boolean;
  preferred_language?: string;
}

export interface JourneyStatus {
  customer_id: string;
  current_stage: "discovery" | "needs_assessment" | "product_matching" | "quote_review" | "proposal_draft" | "submitted";
  active_conversation_id?: string | null;
  has_active_quote: boolean;
  active_quote_id?: string | null;
  has_active_application: boolean;
  active_application_id?: string | null;
  qualification_completed: boolean;
  qualification_data?: Record<string, any> | null;
  missing_requirements: string[];
  last_activity_at: string;
}

export interface ResumeJourneyData {
  thread_id: string;
  conversation_id: string;
  stage: string;
  last_message?: string | null;
  suggested_action: string;
  qualification_snapshot: Record<string, any>;
}

export interface ChatMessage {
  id: number | string;
  conversation_id: string;
  sender_type: "user" | "agent" | "advisor" | "system";
  sender_name: string;
  content: string;
  message_type: "text" | "suggested_chips" | "form_widget" | "quote_preview" | "disclaimer";
  suggested_chips?: string[] | null;
  widget_data?: any | null;
  action_buttons?: { label: string; url: string; variant?: string }[] | null;
  created_at: string;
}

export interface ConversationThread {
  id: string;
  customer_id?: string | null;
  title: string;
  status: string;
  mode: string;
  messages: ChatMessage[];
  created_at: string;
  last_turn_at: string;
}

export interface NeedsAssessmentPayload {
  category: "term_life" | "health" | "motor";
  age: number;
  annual_income: number;
  dependents_count: number;
  marital_status: string;
  occupation: string;
  tobacco_user: boolean;
  has_pre_existing_conditions: boolean;
  pre_existing_conditions_details?: string;
  existing_life_cover: number;
  existing_health_cover: number;
  desired_coverage_amount?: number;
}

export interface NeedsAssessmentResult {
  qualification_id: string;
  customer_id: string;
  category: string;
  eligibility_status: string;
  calculated_coverage_gap: number;
  recommended_sum_assured: number;
  health_risk_tier: string;
  key_observations: string[];
  qualifying_products_count: number;
  factors: Record<string, any>;
  created_at: string;
}

export interface HLVCalculationPayload {
  annual_income: number;
  current_age: number;
  retirement_age: number;
  annual_household_expenses: number;
  outstanding_liabilities: number;
  current_liquid_investments: number;
  inflation_rate_percent: number;
}

export interface HLVCalculationResult {
  methodology: string;
  recommended_term_cover: number;
  human_life_value_raw: number;
  outstanding_liabilities_component: number;
  existing_cover_offset: number;
  net_protection_gap: number;
  rule_of_thumb_multiplier: string;
  calculation_breakdown: Record<string, any>;
  formula_explanation: string;
}

export interface ConsentRecordItem {
  id: number;
  consent_type: string;
  consent_version: string;
  is_active: boolean;
  granted_at: string;
  revoked_at?: string | null;
}

export interface InsuranceProductItem {
  id: string;
  code: string;
  name: string;
  category: string;
  description: string;
  is_active: boolean;
  base_rules_json?: Record<string, any> | null;
  configurations?: any[];
}

