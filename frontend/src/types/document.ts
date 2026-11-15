export type DocumentVerificationStatus = "pending" | "extracted" | "verified" | "rejected";

export interface DocumentItem {
  id: string;
  application_id: string;
  customer_id: string;
  document_type: string;
  version: number;
  file_name: string;
  file_size_bytes: number;
  mime_type: string;
  file_hash: string;
  verification_status: DocumentVerificationStatus;
  extracted_data_json?: Record<string, any>;
  ocr_confidence_score?: number;
  verified_by_id?: string;
  verified_at?: string;
  rejection_reason?: string;
  created_at: string;
}

export interface DocumentRequirement {
  document_type: string;
  title: string;
  description?: string;
  mandatory: boolean;
  accepted_mime_types: string[];
  condition_description?: string;
}
