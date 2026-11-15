"""Underwriting and Case Management Service."""
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException, ValidationException
from app.models.application import Application
from app.models.audit import AuditLog
from app.models.auth import User
from app.models.system import Notification
from app.models.underwriting import CaseNote, UnderwritingCase, UnderwritingReview
from app.repositories.application_repository import ApplicationRepository
from app.repositories.case_note_repository import CaseNoteRepository
from app.repositories.underwriting_repository import UnderwritingRepository
from app.schemas.underwriting import (
    CaseNoteCreate,
    CaseNoteRead,
    RiskFlagItem,
    UnderwritingCaseDetailRead,
    UnderwritingCaseSummaryRead,
    UnderwritingReviewCreate,
    UnderwritingReviewRead,
)


class UnderwritingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UnderwritingRepository(session)
        self.notes_repo = CaseNoteRepository(session)
        self.app_repo = ApplicationRepository(session)

    async def list_triage_cases(
        self,
        current_user: User,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        risk_rating: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[UnderwritingCaseSummaryRead]:
        user_roles = [r.name for r in current_user.roles]
        advisor_id = current_user.advisor.id if "Advisor" in user_roles and current_user.advisor else None
        underwriter_id = current_user.underwriter.id if "Underwriter" in user_roles and current_user.underwriter else None

        # Admins and Owners can see all
        if any(r in ("Admin", "Owner") for r in user_roles):
            advisor_id = None
            underwriter_id = None

        cases = await self.repo.list_triage(
            advisor_id=advisor_id,
            underwriter_id=underwriter_id,
            status=status,
            priority=priority,
            risk_rating=risk_rating,
            limit=limit,
            offset=offset,
        )

        now = datetime.now(timezone.utc)
        summaries = []
        for c in cases:
            hours_rem = None
            if c.sla_deadline:
                deadline = c.sla_deadline if c.sla_deadline.tzinfo else c.sla_deadline.replace(tzinfo=timezone.utc)
                diff = (deadline - now).total_seconds() / 3600.0
                hours_rem = round(diff, 1)

            cust_name = c.customer.user.full_name if c.customer and c.customer.user else "Unknown Customer"
            prod_name = c.application.product.name if c.application and c.application.product else "Insurance Plan"
            sum_ass = float(c.application.quote.sum_assured) if c.application and c.application.quote and c.application.quote.sum_assured else 0.0
            tot_prem = float(c.application.quote.total_premium) if c.application and c.application.quote and c.application.quote.total_premium else 0.0
            adv_name = c.assigned_advisor.user.full_name if c.assigned_advisor and c.assigned_advisor.user else None
            uw_name = c.assigned_underwriter.user.full_name if c.assigned_underwriter and c.assigned_underwriter.user else None
            flags_count = len(c.risk_flags_json) if c.risk_flags_json else 0

            summaries.append(
                UnderwritingCaseSummaryRead(
                    id=c.id,
                    case_number=c.case_number,
                    application_id=c.application_id,
                    customer_id=c.customer_id,
                    customer_name=cust_name,
                    product_name=prod_name,
                    sum_assured=sum_ass,
                    total_premium=tot_prem,
                    priority=c.priority,
                    risk_rating=c.risk_rating,
                    status=c.status,
                    sla_deadline=c.sla_deadline,
                    sla_hours_remaining=hours_rem,
                    risk_flags_count=flags_count,
                    assigned_advisor_name=adv_name,
                    assigned_underwriter_name=uw_name,
                    created_at=c.created_at,
                )
            )
        return summaries

    async def get_case_detail_360(self, case_number_or_id: str, current_user: User) -> UnderwritingCaseDetailRead:
        case = await self.repo.get_by_case_number_full(case_number_or_id)
        if not case:
            case = await self.repo.get_by_id_full(case_number_or_id)
        if not case:
            raise EntityNotFoundException(f"Underwriting case '{case_number_or_id}' not found.")

        user_roles = [r.name for r in current_user.roles]
        user_permissions = {p.code for r in current_user.roles for p in r.permissions}
        has_medical_access = "medical_data:view" in user_permissions or any(r in ("Underwriter", "Admin", "Owner") for r in user_roles)

        # Check permissions for Advisor (scoped access)
        if "Advisor" in user_roles and not any(r in ("Admin", "Owner", "Underwriter") for r in user_roles):
            if current_user.advisor and case.assigned_advisor_id and case.assigned_advisor_id != current_user.advisor.id:
                raise PermissionDeniedException("Unauthorized to access this case.")

        # Compute hours remaining
        now = datetime.now(timezone.utc)
        hours_rem = None
        if case.sla_deadline:
            deadline = case.sla_deadline if case.sla_deadline.tzinfo else case.sla_deadline.replace(tzinfo=timezone.utc)
            hours_rem = round((deadline - now).total_seconds() / 3600.0, 1)

        # Documents formatting
        docs = []
        if case.application and case.application.documents:
            for d in case.application.documents:
                # If medical report and unprivileged, hide file path
                is_medical_doc = d.document_type == "medical_report"
                if is_medical_doc and not has_medical_access:
                    continue
                docs.append({
                    "id": d.id,
                    "document_type": d.document_type,
                    "file_name": d.file_name,
                    "file_size_bytes": d.file_size_bytes,
                    "mime_type": d.mime_type,
                    "verification_status": d.verification_status,
                    "ocr_confidence_score": float(d.ocr_confidence_score) if d.ocr_confidence_score else None,
                    "extracted_data_json": d.extracted_data_json,
                    "rejection_reason": d.rejection_reason,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                })

        # Risk flags
        risk_flags = []
        if case.risk_flags_json:
            for item in case.risk_flags_json:
                if isinstance(item, dict):
                    risk_flags.append(
                        RiskFlagItem(
                            category=item.get("category", "general"),
                            severity=item.get("severity", "medium"),
                            flag=item.get("flag", "Risk flag noted"),
                            source=item.get("source", "system"),
                        )
                    )

        # Reviews
        reviews = [UnderwritingReviewRead.model_validate(r) for r in case.reviews]

        # Notes
        include_confidential = has_medical_access
        notes_list = await self.notes_repo.list_for_case(case.id, include_confidential=include_confidential)
        notes = [
            CaseNoteRead(
                id=n.id,
                case_id=n.case_id,
                author_id=n.author_id,
                author_name=n.author.full_name if n.author else "Staff Member",
                author_role=n.author.roles[0].name if n.author and n.author.roles else "Advisor",
                note_type=n.note_type,
                content=n.content,
                is_confidential=n.is_confidential,
                created_at=n.created_at,
            )
            for n in notes_list
        ]

        # Audit view log
        audit = AuditLog(
            user_id=current_user.id,
            action="VIEW_CASE_FILE",
            resource_type="UnderwritingCase",
            resource_id=case.case_number,
        )
        self.session.add(audit)
        await self.session.flush()

        med_summary = case.medical_risk_summary
        if not has_medical_access and med_summary:
            med_summary = "[RESTRICTED - AUTHORIZED UNDERWRITER ONLY]"

        app = case.application
        quote = app.quote if app else None
        prod = app.product if app else None

        return UnderwritingCaseDetailRead(
            id=case.id,
            case_number=case.case_number,
            application_id=case.application_id,
            customer_id=case.customer_id,
            customer_name=case.customer.user.full_name if case.customer and case.customer.user else "Customer",
            customer_email=case.customer.user.email if case.customer and case.customer.user else "",
            customer_phone=case.customer.user.phone_number if case.customer and case.customer.user else None,
            customer_dob=str(case.customer.date_of_birth) if case.customer and case.customer.date_of_birth else None,
            customer_city=case.customer.city if case.customer else None,
            product_id=prod.id if prod else None,
            product_name=prod.name if prod else "Insurance Product",
            product_category=prod.category if prod else "Life",
            sum_assured=float(quote.sum_assured) if quote and quote.sum_assured else 0.0,
            policy_term_years=quote.policy_term_years if quote and quote.policy_term_years else 0,
            total_premium=float(quote.total_premium) if quote and quote.total_premium else 0.0,
            priority=case.priority,
            risk_rating=case.risk_rating,
            status=case.status,
            sla_deadline=case.sla_deadline,
            sla_hours_remaining=hours_rem,
            risk_flags=risk_flags,
            medical_risk_summary=med_summary,
            financial_risk_summary=case.financial_risk_summary,
            proposal_data=app.proposal_data_json if app else None,
            proposal_checksum=app.proposal_checksum if app else None,
            documents=docs,
            reviews=reviews,
            notes=notes,
            created_at=case.created_at,
            updated_at=case.updated_at,
        )

    async def submit_formal_review(
        self, case_number: str, data: UnderwritingReviewCreate, current_user: User
    ) -> UnderwritingReviewRead:
        user_roles = [r.name for r in current_user.roles]
        if not any(r in ("Underwriter", "Admin", "Owner") for r in user_roles):
            raise PermissionDeniedException("Only authorized Underwriters or Administrators can submit underwriting decisions.")

        case = await self.repo.get_by_case_number(case_number)
        if not case:
            raise EntityNotFoundException(f"Underwriting case '{case_number}' not found.")

        # Create review record
        review = UnderwritingReview(
            case_id=case.id,
            reviewer_id=current_user.id,
            review_type=data.review_type,
            decision=data.decision,
            loading_percentage=data.loading_percentage,
            notes=data.notes,
            conditions=data.conditions,
        )
        created_review = await self.repo.add_review(review)

        # Synchronize statuses atomically
        app = await self.app_repo.get_by_id_with_relations(case.application_id)

        notif_title = "Underwriting Update"
        notif_msg = ""

        if data.decision == "approved_standard":
            case.status = "approved"
            case.risk_rating = "standard"
            if app:
                app.status = "approved"
                if app.quote:
                    app.quote.status = "approved"
            notif_msg = f"Your proposal for application {app.application_number if app else ''} has been approved at standard rates."

        elif data.decision == "approved_with_loading":
            case.status = "approved"
            case.risk_rating = "substandard"
            if app:
                app.status = "approved"
                if app.quote:
                    app.quote.status = "approved"
            notif_msg = f"Your proposal has been approved with a {data.loading_percentage}% loading. Conditions: {data.conditions or 'Standard terms'}."

        elif data.decision == "declined":
            case.status = "declined"
            case.risk_rating = "decline"
            if app:
                app.status = "rejected"
            notif_msg = "Your insurance application could not be accepted under current underwriting guidelines."

        elif data.decision == "more_info_needed":
            case.status = "more_info_needed"
            if app:
                app.status = "additional_info_required"
            notif_msg = f"The underwriting team has requested additional information: {data.notes}"

        # Send notification to customer
        if case.customer and case.customer.user_id:
            notif = Notification(
                user_id=case.customer.user_id,
                title=notif_title,
                message=notif_msg,
                notification_type="case_update",
                link_url=f"/customer/applications/{app.id if app else ''}",
            )
            self.session.add(notif)

        # Audit log entry
        audit = AuditLog(
            user_id=current_user.id,
            action="SUBMIT_UNDERWRITING_DECISION",
            resource_type="UnderwritingCase",
            resource_id=case.case_number,
            changes_json={
                "decision": data.decision,
                "loading_percentage": data.loading_percentage,
                "review_type": data.review_type,
                "new_status": case.status,
            },
        )
        self.session.add(audit)
        await self.session.commit()

        return UnderwritingReviewRead.model_validate(created_review)

    async def add_case_note(self, case_id: str, data: CaseNoteCreate, current_user: User) -> CaseNoteRead:
        case = await self.repo.get_by_id(case_id)
        if not case:
            raise EntityNotFoundException(f"Case with ID '{case_id}' not found.")

        note = CaseNote(
            case_id=case.id,
            author_id=current_user.id,
            note_type=data.note_type,
            content=data.content,
            is_confidential=data.is_confidential,
        )
        saved = await self.notes_repo.add_note(note)

        audit = AuditLog(
            user_id=current_user.id,
            action="ADD_CASE_NOTE",
            resource_type="UnderwritingCase",
            resource_id=case.case_number,
        )
        self.session.add(audit)
        await self.session.commit()

        return CaseNoteRead(
            id=saved.id,
            case_id=saved.case_id,
            author_id=saved.author_id,
            author_name=current_user.full_name,
            author_role=current_user.roles[0].name if current_user.roles else "Advisor",
            note_type=saved.note_type,
            content=saved.content,
            is_confidential=saved.is_confidential,
            created_at=saved.created_at,
        )

