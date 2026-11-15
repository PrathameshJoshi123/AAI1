"""Dynamic Proposal Service: Resolves product-specific and regulatory declarations & document checklists."""
from typing import List
from app.models.product import InsuranceProduct
from app.models.recommendation import Quote
from app.schemas.application import DynamicDeclarationItem, DynamicRequirementsResponse
from app.schemas.document import DocumentRequirementItem

# Standard IRDAI statutory declarations if not explicitly customized
DEFAULT_STATUTORY_DECLARATIONS: List[dict] = [
    {
        "id": "dec_tobacco",
        "category": "lifestyle",
        "question": "Have you used any form of tobacco, cigarettes, cigars, or beedis in the past 36 months?",
        "field_type": "boolean",
        "required": True,
        "sub_fields_on_true": [
            {"id": "tobacco_type", "label": "Form of tobacco", "field_type": "select", "options": ["Cigarettes", "Bidi", "Chewing Tobacco", "Vape/E-Cigarette"]},
            {"id": "tobacco_quantity_per_day", "label": "Average units per day", "field_type": "number", "min": 1},
        ],
    },
    {
        "id": "dec_diabetes",
        "category": "medical",
        "question": "Have you ever been diagnosed with, treated for, or advised regarding Diabetes, High Blood Sugar, or Glycosuria?",
        "field_type": "boolean",
        "required": True,
        "sub_fields_on_true": [
            {"id": "diabetes_diagnosis_year", "label": "Year of initial diagnosis", "field_type": "number"},
            {"id": "diabetes_treatment_mode", "label": "Current treatment", "field_type": "select", "options": ["Diet/Exercise Only", "Oral Tablets", "Insulin Injections"]},
        ],
    },
    {
        "id": "dec_hypertension",
        "category": "medical",
        "question": "Have you ever been diagnosed with Hypertension, High Blood Pressure, or Heart/Cardiac conditions?",
        "field_type": "boolean",
        "required": True,
        "sub_fields_on_true": [
            {"id": "bp_reading_typical", "label": "Typical systolic/diastolic BP reading", "field_type": "text"},
        ],
    },
    {
        "id": "dec_hospitalization_5yr",
        "category": "medical",
        "question": "Have you undergone any surgery, medical investigation, or hospitalization in the last 5 years?",
        "field_type": "boolean",
        "required": True,
        "sub_fields_on_true": [
            {"id": "hospitalization_details", "label": "Reason, hospital name, and year", "field_type": "text"},
        ],
    },
]

# Standard mandatory documents
DEFAULT_DOCUMENTS: List[dict] = [
    {
        "document_type": "identity_proof",
        "title": "Government Identity Proof (PAN Card mandatory)",
        "description": "Upload a clear scan or photo of your official PAN card.",
        "mandatory": True,
        "accepted_mime_types": ["application/pdf", "image/jpeg", "image/png"],
    },
    {
        "document_type": "address_proof",
        "title": "Residential Address Proof",
        "description": "Aadhaar (front & back), Passport, Voter ID, or Utility bill (last 2 months).",
        "mandatory": True,
        "accepted_mime_types": ["application/pdf", "image/jpeg", "image/png"],
    },
    {
        "document_type": "income_proof",
        "title": "Income & Financial Proof",
        "description": "Latest 3 months salary slips, Form 16, or ITR-V assessment copy.",
        "mandatory": False,
        "condition_description": "Mandatory for Sum Assured >= ₹50,00,000",
        "accepted_mime_types": ["application/pdf"],
    },
    {
        "document_type": "photograph",
        "title": "Recent Passport-sized Photograph",
        "description": "Clear color photograph with white background taken in the last 6 months.",
        "mandatory": True,
        "accepted_mime_types": ["image/jpeg", "image/png"],
    },
]


class DynamicProposalService:
    @staticmethod
    def resolve_requirements(
        application_id: str,
        product: InsuranceProduct,
        quote: Quote,
    ) -> DynamicRequirementsResponse:
        """
        Dynamically calculates required medical/financial declarations and document checklist
        based on product rules, policy type, and quote sum assured thresholds.
        """
        declarations: List[DynamicDeclarationItem] = []
        product_decs = getattr(product, "required_declarations_json", None)

        if product_decs and isinstance(product_decs, list) and len(product_decs) > 0:
            for item in product_decs:
                if isinstance(item, dict):
                    declarations.append(DynamicDeclarationItem(**item))
                elif isinstance(item, str):
                    declarations.append(
                        DynamicDeclarationItem(
                            id=f"dec_{hash(item) % 100000}",
                            category="general",
                            question=item,
                            field_type="boolean",
                            required=True,
                        )
                    )
        else:
            declarations = [DynamicDeclarationItem(**d) for d in DEFAULT_STATUTORY_DECLARATIONS]

        # Resolve documents
        documents: List[DocumentRequirementItem] = []
        product_docs = getattr(product, "required_documents_json", None)

        if product_docs and isinstance(product_docs, list) and len(product_docs) > 0:
            for d in product_docs:
                if isinstance(d, dict):
                    documents.append(DocumentRequirementItem(**d))
        else:
            for d in DEFAULT_DOCUMENTS:
                doc_item = DocumentRequirementItem(**d)
                # If sum assured is >= 50,00,000, enforce income proof as mandatory
                if doc_item.document_type == "income_proof" and quote.sum_assured >= 5000000:
                    doc_item.mandatory = True
                documents.append(doc_item)

        return DynamicRequirementsResponse(
            application_id=application_id,
            product_id=product.id,
            product_name=product.name,
            product_category=product.category,
            declarations=declarations,
            required_documents=documents,
        )
