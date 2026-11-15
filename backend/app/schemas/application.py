"""Pydantic schemas for Applications, Onboarding Proposals, and Steps."""
from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.document import DocumentRead, DocumentRequirementItem


class NomineeItem(BaseModel):
    nominee_name: str = Field(..., min_length=2, max_length=150)
    relation: Literal["spouse", "child", "parent", "sibling", "other"]
    date_of_birth: str  # YYYY-MM-DD
    share_percentage: float = Field(..., gt=0, le=100)
    appointee_name: Optional[str] = None
    appointee_relation: Optional[str] = None
    appointee_contact: Optional[str] = None


class DependentItem(BaseModel):
    name: str
    relation: str
    age: int = Field(..., ge=0, le=120)
    financially_dependent: bool = True


class ExistingPolicyItem(BaseModel):
    insurer_name: str
    policy_number: Optional[str] = None
    sum_assured: float = Field(..., gt=0)
    year_issued: Optional[int] = None


class StepPersonalInfo(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    date_of_birth: str  # YYYY-MM-DD
    gender: Literal["male", "female", "other"]
    marital_status: Literal["single", "married", "divorced", "widowed"]
    pan_number: str = Field(..., pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    aadhaar_last_four: str = Field(..., pattern=r"^[0-9]{4}$")
    nationality: str = Field(default="IN", max_length=2)


class StepContactAddress(BaseModel):
    mobile_number: str = Field(..., pattern=r"^[6-9]\d{9}$")
    email: EmailStr
    residential_address_line1: str = Field(..., min_length=3)
    residential_address_line2: Optional[str] = None
    city: str = Field(..., min_length=2)
    state: str = Field(..., min_length=2)
    pincode: str = Field(..., pattern=r"^[1-9][0-9]{5}$")
    is_permanent_same: bool = True
    permanent_address: Optional[Dict[str, Any]] = None


class StepEmploymentFinancial(BaseModel):
    occupation_type: Literal["salaried", "self_employed_professional", "business_owner", "retired", "homemaker", "student"]
    employer_or_business_name: str = Field(..., min_length=2)
    designation: str = Field(..., min_length=2)
    nature_of_duties: Literal["desk_office", "light_manual", "heavy_manual", "hazardous_substances", "aviation_offshore"]
    gross_annual_income: float = Field(..., gt=0)
    tax_resident_india_only: bool = True
    politically_exposed_person: bool = False


class StepFamilyCoverage(BaseModel):
    dependents: List[DependentItem] = Field(default_factory=list)
    has_existing_insurance: bool = False
    existing_policies: List[ExistingPolicyItem] = Field(default_factory=list)
    has_previous_rejections: bool = False
    rejection_details: Optional[str] = None


class StepMedicalLifestyle(BaseModel):
    height_cm: float = Field(..., ge=80, le=250)
    weight_kg: float = Field(..., ge=20, le=250)
    tobacco_use: bool = False
    tobacco_details: Optional[Dict[str, Any]] = None
    alcohol_consumption: Literal["none", "occasional", "regular"] = "none"
    pre_existing_conditions: Dict[str, bool] = Field(default_factory=dict)
    hospitalization_past_5_years: bool = False
    hospitalization_details: Optional[str] = None
    family_history_critical: bool = False
    family_history_details: Optional[str] = None


class StepNominee(BaseModel):
    nominees: List[NomineeItem] = Field(..., min_length=1, max_length=3)


class StepStatutoryDeclarations(BaseModel):
    declaration_truthfulness: bool = True
    section_45_insurance_act: bool = True
    dpdp_consent: bool = True
    consent_ckyc_verification: bool = True
    consent_timestamp: Optional[str] = None


class ApplicationCreate(BaseModel):
    quote_id: str


class ApplicationDraftUpdate(BaseModel):
    current_step: int = Field(..., ge=1, le=8)
    step_key: str
    step_data: Dict[str, Any]


class ApplicationSubmitRequest(BaseModel):
    e_signature_name: str = Field(..., min_length=2)
    acknowledged_declarations: bool = True


class DynamicDeclarationItem(BaseModel):
    id: str
    category: str
    question: str
    field_type: str  # boolean, text, select, number
    required: bool = True
    options: Optional[List[str]] = None
    sub_fields_on_true: Optional[List[Dict[str, Any]]] = None


class DynamicRequirementsResponse(BaseModel):
    application_id: str
    product_id: str
    product_name: str
    product_category: str
    declarations: List[DynamicDeclarationItem]
    required_documents: List[DocumentRequirementItem]


class ApplicationRead(BaseModel):
    id: str
    application_number: str
    customer_id: str
    quote_id: str
    product_id: str
    status: str
    current_step: int
    step_progress_json: Optional[Dict[str, Any]] = None
    proposal_data_json: Optional[Dict[str, Any]] = None
    proposal_checksum: Optional[str] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    documents: List[DocumentRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ApplicationDetailRead(ApplicationRead):
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    insurer_name: Optional[str] = None
    quote_number: Optional[str] = None
    sum_assured: Optional[float] = None
    policy_term_years: Optional[int] = None
    total_premium: Optional[float] = None
