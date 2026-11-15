"""Service for human document verification, rejection, and audit tracking."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException
from app.models.application import Application, ApplicationDocument
from app.models.audit import AuditLog
from app.models.auth import User
from app.models.system import Notification
from app.schemas.underwriting import DocumentRejectionActionRequest, DocumentVerificationActionRequest


class DocumentVerificationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def verify_document(
        self, document_id: str, data: Optional[DocumentVerificationActionRequest], current_user: User
    ) -> ApplicationDocument:
        user_roles = [r.name for r in current_user.roles]
        if not any(r in ("Advisor", "Underwriter", "Admin", "Owner") for r in user_roles):
            raise PermissionDeniedException("Unauthorized to verify documents.")

        stmt = (
            select(ApplicationDocument)
            .where(ApplicationDocument.id == document_id)
            .options(
                selectinload(ApplicationDocument.application).selectinload(Application.documents),
                selectinload(ApplicationDocument.customer),
            )
        )
        res = await self.session.execute(stmt)
        doc = res.scalar_one_or_none()
        if not doc:
            raise EntityNotFoundException("Document not found.")

        now = datetime.now(timezone.utc)
        doc.verification_status = "verified"
        doc.verified_by_id = current_user.id
        doc.verified_at = now
        doc.rejection_reason = None

        # Check if all application documents are now verified
        app = doc.application
        if app and app.documents:
            all_verified = all(d.verification_status == "verified" for d in app.documents)
            if all_verified and app.status == "documents_pending":
                app.status = "under_review"

        audit = AuditLog(
            user_id=current_user.id,
            action="VERIFY_DOCUMENT",
            resource_type="ApplicationDocument",
            resource_id=doc.id,
            changes_json={
                "file_name": doc.file_name,
                "document_type": doc.document_type,
                "notes": data.verification_notes if data else None,
            },
        )
        self.session.add(audit)
        await self.session.commit()
        return doc

    async def reject_document(
        self, document_id: str, data: DocumentRejectionActionRequest, current_user: User
    ) -> ApplicationDocument:
        user_roles = [r.name for r in current_user.roles]
        if not any(r in ("Advisor", "Underwriter", "Admin", "Owner") for r in user_roles):
            raise PermissionDeniedException("Unauthorized to reject documents.")

        stmt = (
            select(ApplicationDocument)
            .where(ApplicationDocument.id == document_id)
            .options(
                selectinload(ApplicationDocument.application),
                selectinload(ApplicationDocument.customer),
            )
        )
        res = await self.session.execute(stmt)
        doc = res.scalar_one_or_none()
        if not doc:
            raise EntityNotFoundException("Document not found.")

        now = datetime.now(timezone.utc)
        reason_text = f"[{data.rejection_reason_code}] {data.detailed_instructions}"
        doc.verification_status = "rejected"
        doc.verified_by_id = current_user.id
        doc.verified_at = now
        doc.rejection_reason = reason_text

        # Update application status back to documents_pending
        if doc.application:
            doc.application.status = "documents_pending"

        # Notify customer
        if doc.customer and doc.customer.user_id:
            notif = Notification(
                user_id=doc.customer.user_id,
                title="Document Needs Replacement",
                message=f"Your {doc.document_type.replace('_', ' ').title()} was rejected: {data.detailed_instructions}. Please upload a fresh copy.",
                notification_type="case_update",
                link_url="/customer/documents",
            )
            self.session.add(notif)

        audit = AuditLog(
            user_id=current_user.id,
            action="REJECT_DOCUMENT",
            resource_type="ApplicationDocument",
            resource_id=doc.id,
            changes_json={
                "file_name": doc.file_name,
                "document_type": doc.document_type,
                "rejection_code": data.rejection_reason_code,
                "instructions": data.detailed_instructions,
            },
        )
        self.session.add(audit)
        await self.session.commit()
        return doc

