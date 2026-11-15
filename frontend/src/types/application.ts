import { DocumentItem, DocumentRequirement } from "./document";

export type ApplicationStatus =
  | "draft"
  | "documents_pending"
  | "submitted"
  | "under_review"
  | "additional_info_required"
  | "approved"
  | "rejected";

export interface NomineeData {
  nominee_name: string;
  relation: "spouse" | "child" | "parent" | "sibling" | "other";
  date_of_birth: string;
  share_percentage: number;
  appointee_name?: string;
  appointee_relation?: string;
  appointee_contact?: string;
}

export interface DependentData {
  name: string;
  relation: string;
  age: number;
  financially_dependent: boolean;
}

export interface ExistingPolicyData {
  insurer_name: string;
  policy_number?: string;
  sum_assured: number;
  year_issued?: number;
}

export interface PersonalInfoData {
  full_name: string;
  date_of_birth: string;
  gender: "male" | "female" | "other";
  marital_status: "single" | "married" | "divorced" | "widowed";
  pan_number: string;
  aadhaar_last_four: string;
  nationality: string;
}

export interface ContactAddressData {
  mobile_number: string;
  email: string;
  residential_address_line1: string;
  residential_address_line2?: string;
  city: string;
  state: string;
  pincode: string;
  is_permanent_same: boolean;
  permanent_address?: Record<string, any>;
}

export interface EmploymentFinancialData {
  occupation_type: "salaried" | "self_employed_professional" | "business_owner" | "retired" | "homemaker" | "student";
  employer_or_business_name: string;
  designation: string;
  nature_of_duties: "desk_office" | "light_manual" | "heavy_manual" | "hazardous_substances" | "aviation_offshore";
  gross_annual_income: number;
  tax_resident_india_only: boolean;
  politically_exposed_person: boolean;
}

export interface FamilyCoverageData {
  dependents: DependentData[];
  has_existing_insurance: boolean;
  existing_policies: ExistingPolicyData[];
  has_previous_rejections: boolean;
  rejection_details?: string;
}

export interface MedicalLifestyleData {
  height_cm: number;
  weight_kg: number;
  tobacco_use: boolean;
  tobacco_details?: Record<string, any>;
  alcohol_consumption: "none" | "occasional" | "regular";
  pre_existing_conditions: Record<string, boolean>;
  hospitalization_past_5_years: boolean;
  hospitalization_details?: string;
  family_history_critical: boolean;
  family_history_details?: string;
}

export interface StatutoryDeclarationsData {
  declaration_truthfulness: boolean;
  section_45_insurance_act: boolean;
  dpdp_consent: boolean;
  consent_ckyc_verification: boolean;
  consent_timestamp?: string;
}

export interface DynamicDeclaration {
  id: string;
  category: string;
  question: string;
  field_type: string;
  required: boolean;
  options?: string[];
  sub_fields_on_true?: Array<Record<string, any>>;
}

export interface DynamicRequirements {
  application_id: string;
  product_id: string;
  product_name: string;
  product_category: string;
  declarations: DynamicDeclaration[];
  required_documents: DocumentRequirement[];
}

export interface ApplicationItem {
  id: string;
  application_number: string;
  customer_id: string;
  quote_id: string;
  product_id: string;
  status: ApplicationStatus;
  current_step: number;
  step_progress_json?: Record<string, boolean>;
  proposal_data_json?: Record<string, any>;
  proposal_checksum?: string;
  submitted_at?: string;
  created_at: string;
  documents: DocumentItem[];
}

export interface ApplicationDetail extends ApplicationItem {
  product_name?: string;
  product_code?: string;
  insurer_name?: string;
  quote_number?: string;
  sum_assured?: number;
  policy_term_years?: number;
  total_premium?: number;
}
