export interface UnderwritingReview {
  id: number;
  case_id: string;
  reviewer_id: string;
  review_type: string;
  decision: "approved_standard" | "approved_with_loading" | "declined" | "more_info_needed";
  loading_percentage: number;
  notes: string;
  conditions?: string | null;
  reviewed_at: string;
}

export interface CaseNote {
  id: string;
  case_id: string;
  author_id: string;
  author_name: string;
  author_role: string;
  note_type: "internal_note" | "inquiry" | "underwriter_query" | "customer_communication";
  content: string;
  is_confidential: boolean;
  created_at: string;
}

export interface RiskFlag {
  category: "medical" | "financial" | "lifestyle" | "identity" | string;
  severity: "low" | "medium" | "high" | "critical" | string;
  flag: string;
  source: string;
}

export interface UnderwritingCaseSummary {
  id: string;
  case_number: string;
  application_id: string;
  customer_id: string;
  customer_name: string;
  product_name: string;
  sum_assured: number;
  total_premium: number;
  priority: "low" | "medium" | "high" | "urgent" | string;
  risk_rating: "preferred" | "standard" | "substandard" | "decline" | string;
  status: "assigned" | "in_review" | "more_info_needed" | "approved" | "declined" | string;
  sla_deadline?: string | null;
  sla_hours_remaining?: number | null;
  risk_flags_count: number;
  assigned_advisor_name?: string | null;
  assigned_underwriter_name?: string | null;
  created_at: string;
}

export interface UnderwritingCaseDetail {
  id: string;
  case_number: string;
  application_id: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  customer_phone?: string | null;
  customer_dob?: string | null;
  customer_city?: string | null;
  product_id?: string | null;
  product_name: string;
  product_category: string;
  sum_assured: number;
  policy_term_years: number;
  total_premium: number;
  priority: string;
  risk_rating: string;
  status: string;
  sla_deadline?: string | null;
  sla_hours_remaining?: number | null;
  risk_flags: RiskFlag[];
  medical_risk_summary?: string | null;
  financial_risk_summary?: string | null;
  proposal_data?: Record<string, any> | null;
  proposal_checksum?: string | null;
  documents: Array<{
    id: string;
    document_type: string;
    file_name: string;
    file_size_bytes: number;
    mime_type: string;
    verification_status: string;
    ocr_confidence_score?: number | null;
    extracted_data_json?: Record<string, any> | null;
    rejection_reason?: string | null;
    created_at?: string | null;
  }>;
  reviews: UnderwritingReview[];
  notes: CaseNote[];
  created_at: string;
  updated_at: string;
}

export interface ReviewSubmissionPayload {
  review_type: string;
  decision: "approved_standard" | "approved_with_loading" | "declined" | "more_info_needed";
  loading_percentage: number;
  notes: string;
  conditions?: string;
}

