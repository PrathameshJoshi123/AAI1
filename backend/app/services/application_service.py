"""Application Service: Multi-step proposal drafting, step validation, checksum generation, and underwriting handoff."""
import hashlib
import json
import random
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import (
    BusinessRuleViolationException,
    EntityNotFoundException,
    PermissionDeniedException,
)
from app.models.application import Application
from app.models.auth import User
from app.models.underwriting import UnderwritingCase
from app.repositories.application_repository import ApplicationRepository
from app.repositories.quote_repository import QuoteRepository
from app.schemas.application import ApplicationDraftUpdate, ApplicationSubmitRequest


class ApplicationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.app_repo = ApplicationRepository(session)
        self.quote_repo = QuoteRepository(session)

    async def get_or_create_draft(self, quote_id: str, current_user: User) -> Application:
        """Fetch existing application draft or initialize a new draft for the given quote."""
        quote = await self.quote_repo.get_by_id(quote_id)
        if not quote:
            raise EntityNotFoundException("Specified quote does not exist.")

        # Customer isolation
        user_roles = [r.name for r in current_user.roles]
        if "Customer" in user_roles:
            if not current_user.customer or current_user.customer.id != quote.customer_id:
                raise PermissionDeniedException("You are not authorized to start a proposal for this quote.")

        # Check for existing application
        existing = await self.app_repo.get_by_quote_id(quote_id)
        if existing:
            return existing

        now = datetime.now(timezone.utc)
        app_number = f"APP-{now.year}-{random.randint(100000, 999999)}"

        new_app = Application(
            application_number=app_number,
            customer_id=quote.customer_id,
            quote_id=quote.id,
            product_id=quote.product_id,
            status="draft",
            current_step=1,
            step_progress_json={
                "personal_info": False,
                "contact_address": False,
                "employment_financial": False,
                "family_coverage": False,
                "medical_lifestyle": False,
                "nominee_details": False,
                "statutory_declarations": False,
                "document_upload": False,
            },
            proposal_data_json={},
        )
        created = await self.app_repo.create(new_app)
        return await self.app_repo.get_by_id_with_relations(created.id)

    async def update_draft(
        self, application_id: str, data: ApplicationDraftUpdate, current_user: User
    ) -> Application:
        """Incrementally auto-save step data and progress."""
        app = await self.app_repo.get_by_id_with_relations(application_id)
        if not app:
            raise EntityNotFoundException("Application not found.")

        # Customer isolation check
        user_roles = [r.name for r in current_user.roles]
        if "Customer" in user_roles:
            if not current_user.customer or current_user.customer.id != app.customer_id:
                raise PermissionDeniedException("Unauthorized to modify this application.")

        if app.status not in ["draft", "documents_pending", "additional_info_required"]:
            raise BusinessRuleViolationException(
                f"Cannot edit proposal in '{app.status}' status. Form is locked for underwriting."
            )

        # Merge step data
        existing_data = dict(app.proposal_data_json or {})
        existing_data[data.step_key] = data.step_data
        app.proposal_data_json = existing_data

        # Update step progress
        progress = dict(app.step_progress_json or {})
        progress[data.step_key] = True
        app.step_progress_json = progress

        # Update current step marker
        if data.current_step > app.current_step:
            app.current_step = data.current_step

        await self.session.commit()
        return app

    async def submit_proposal(
        self, application_id: str, data: ApplicationSubmitRequest, current_user: User
    ) -> Application:
        """Formally validates proposal steps, verifies required documents, generates checksum, and triggers underwriting."""
        app = await self.app_repo.get_by_id_with_relations(application_id)
        if not app:
            raise EntityNotFoundException("Application not found.")

        # Customer isolation check
        user_roles = [r.name for r in current_user.roles]
        if "Customer" in user_roles:
            if not current_user.customer or current_user.customer.id != app.customer_id:
                raise PermissionDeniedException("Unauthorized to submit this application.")

        if app.status == "submitted":
            return app

        proposal_data = app.proposal_data_json or {}

        # 1. Validate mandatory proposal sections
        required_steps = [
            "personal_info",
            "contact_address",
            "employment_financial",
            "medical_lifestyle",
            "nominee_details",
            "statutory_declarations",
        ]
        missing_steps = [step for step in required_steps if step not in proposal_data]
        if missing_steps:
            raise BusinessRuleViolationException(
                f"Proposal is incomplete. The following sections are required: {', '.join(missing_steps)}."
            )

        # 2. Validate nominee total share equals 100%
        nominee_data = proposal_data.get("nominee_details", {})
        nominees = nominee_data.get("nominees", [])
        if not nominees:
            raise BusinessRuleViolationException("At least one nominee is mandatory.")
        total_share = sum(float(n.get("share_percentage", 0)) for n in nominees)
        if abs(total_share - 100.0) > 0.01:
            raise BusinessRuleViolationException(
                f"Nominee share percentages must total exactly 100%. Current total: {total_share}%."
            )

        # 3. Validate mandatory documents uploaded
        uploaded_doc_types = {doc.document_type for doc in app.documents}
        if "identity_proof" not in uploaded_doc_types:
            raise BusinessRuleViolationException("Mandatory Government Identity Proof (PAN) has not been uploaded.")
        if "address_proof" not in uploaded_doc_types:
            raise BusinessRuleViolationException("Mandatory Address Proof has not been uploaded.")

        now = datetime.now(timezone.utc)

        # 4. Generate proposal checksum
        proposal_serialized = json.dumps(proposal_data, sort_keys=True)
        checksum = hashlib.sha256(proposal_serialized.encode("utf-8")).hexdigest()

        # Record e-signature in proposal data
        proposal_data["e_signature"] = {
            "signatory_name": data.e_signature_name,
            "acknowledged": data.acknowledged_declarations,
            "signed_at": now.isoformat(),
            "checksum": checksum,
        }
        app.proposal_data_json = proposal_data
        app.proposal_checksum = checksum
        app.status = "submitted"
        app.submitted_at = now

        # 5. Convert associated quote
        quote = await self.quote_repo.get_by_id(app.quote_id)
        if quote:
            quote.status = "converted"

        # 6. Instantiate UnderwritingCase
        case_number = f"UW-{now.year}-{random.randint(100000, 999999)}"
        uw_case = UnderwritingCase(
            case_number=case_number,
            application_id=app.id,
            customer_id=app.customer_id,
            risk_rating="standard",
            status="assigned",
        )
        self.session.add(uw_case)

        await self.session.commit()
        return await self.app_repo.get_by_id_with_relations(app.id)
