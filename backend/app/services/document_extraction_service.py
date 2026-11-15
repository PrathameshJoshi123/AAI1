"""Document Extraction Service: Parses document contents and structures metadata for underwriter assistance."""
from typing import Any, Dict, Optional
from app.models.application import ApplicationDocument


class DocumentExtractionService:
    @staticmethod
    async def extract_metadata(document: ApplicationDocument) -> Dict[str, Any]:
        """
        Extracts structured KYC/financial data from uploaded documents.
        Strict rule: Extracted data is saved as advisory metadata.
        Document verification status is set to 'extracted', NEVER automatically 'verified'.
        """
        doc_type = document.document_type
        extracted: Dict[str, Any] = {
            "document_type": doc_type,
            "file_name": document.file_name,
            "file_hash_prefix": document.file_hash[:16],
            "extracted_fields": {},
        }

        # Simulated structured parsing based on document type
        if doc_type == "identity_proof":
            extracted["extracted_fields"] = {
                "id_type": "PAN",
                "issuer": "Income Tax Department of India",
                "checksum_verified": True,
            }
            confidence = 0.94
        elif doc_type == "address_proof":
            extracted["extracted_fields"] = {
                "proof_type": "Aadhaar / Utility Bill",
                "address_legible": True,
            }
            confidence = 0.91
        elif doc_type == "income_proof":
            extracted["extracted_fields"] = {
                "proof_type": "ITR-V / Salary Slip",
                "financial_year_detected": "2025-2026",
            }
            confidence = 0.88
        else:
            extracted["extracted_fields"] = {
                "general_doc_type": doc_type,
                "readability": "clear",
            }
            confidence = 0.85

        document.extracted_data_json = extracted
        document.ocr_confidence_score = confidence
        document.verification_status = "extracted"

        return extracted
