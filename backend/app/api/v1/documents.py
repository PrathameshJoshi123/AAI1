"""Document Vault Endpoints: Multipart upload, secure streaming download, versioned replacement, and review."""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, get_scoped_customer_id
from app.core.exceptions import (
    BusinessRuleViolationException,
    EntityNotFoundException,
    PermissionDeniedException,
)
from app.models.application import ApplicationDocument
from app.models.auth import User
from app.repositories.application_repository import ApplicationRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.common import APIResponse
from app.schemas.document import DocumentRead, DocumentUploadResponse, DocumentVerifyRequest
from app.services.document_extraction_service import DocumentExtractionService
from app.services.document_storage_service import DocumentStorageService

router = APIRouter(prefix="/documents", tags=["Document Vault"])


@router.post("/upload", response_model=APIResponse[DocumentUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_document(
    application_id: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Securely upload a KYC or proposal document with MIME verification and SHA-256 integrity."""
    app_repo = ApplicationRepository(session)
    application = await app_repo.get_by_id_with_relations(application_id)
    if not application:
        raise EntityNotFoundException("Referenced application does not exist.")

    # Guard: customer can only upload to their own applications
    user_roles = [r.name for r in current_user.roles]
    if "Customer" in user_roles:
        if not current_user.customer or current_user.customer.id != application.customer_id:
            raise PermissionDeniedException("You do not have permission to upload documents for this application.")

    # Validate file and write to isolated filesystem
    file_path, file_name, file_size, mime_type, file_hash = await DocumentStorageService.validate_and_store(
        file=file,
        customer_id=application.customer_id,
        application_id=application.id,
        document_type=document_type,
    )

    doc_repo = DocumentRepository(session)
    # Check if a previous document of this type exists to increment version
    latest = await doc_repo.get_latest_version(application.id, document_type)
    next_version = (latest.version + 1) if latest else 1

    doc = ApplicationDocument(
        application_id=application.id,
        customer_id=application.customer_id,
        document_type=document_type,
        version=next_version,
        file_name=file_name,
        file_path=file_path,
        file_size_bytes=file_size,
        mime_type=mime_type,
        file_hash=file_hash,
        verification_status="pending",
    )
    created_doc = await doc_repo.create(doc)

    # Trigger metadata extraction pipeline
    await DocumentExtractionService.extract_metadata(created_doc)
    await session.commit()

    return APIResponse(
        data=DocumentUploadResponse(
            document=DocumentRead.model_validate(created_doc),
            message="Document uploaded successfully with verified SHA-256 integrity hash.",
        )
    )


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Stream authorized document binary with RBAC and customer data isolation."""
    doc_repo = DocumentRepository(session)
    doc = await doc_repo.get_by_id_with_relations(document_id)
    if not doc:
        raise EntityNotFoundException("Requested document not found.")

    # Customer isolation
    user_roles = [r.name for r in current_user.roles]
    if "Customer" in user_roles:
        if not current_user.customer or current_user.customer.id != doc.customer_id:
            raise PermissionDeniedException("Unauthorized to access this document.")

    physical_path = DocumentStorageService.resolve_physical_path(doc.file_path)

    return FileResponse(
        path=str(physical_path),
        filename=doc.file_name,
        media_type=doc.mime_type,
    )


@router.get("/customer", response_model=APIResponse[List[DocumentRead]])
async def list_customer_documents(
    customer_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List all documents belonging to a customer vault."""
    user_roles = [r.name for r in current_user.roles]
    if "Customer" in user_roles:
        if not current_user.customer:
            return APIResponse(data=[])
        effective_customer_id = current_user.customer.id
    else:
        if not customer_id:
            raise PermissionDeniedException("customer_id is required for administrative lookup.")
        effective_customer_id = await get_scoped_customer_id(customer_id, current_user)

    doc_repo = DocumentRepository(session)
    docs = await doc_repo.list_by_customer(effective_customer_id)
    return APIResponse(data=[DocumentRead.model_validate(d) for d in docs])


@router.get("/application/{application_id}", response_model=APIResponse[List[DocumentRead]])
async def list_application_documents(
    application_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List all documents attached to a specific application."""
    app_repo = ApplicationRepository(session)
    app = await app_repo.get_by_id_with_relations(application_id)
    if not app:
        raise EntityNotFoundException("Application not found.")

    user_roles = [r.name for r in current_user.roles]
    if "Customer" in user_roles:
        if not current_user.customer or current_user.customer.id != app.customer_id:
            raise PermissionDeniedException("Unauthorized to access documents for this application.")

    doc_repo = DocumentRepository(session)
    docs = await doc_repo.list_by_application(application_id)
    return APIResponse(data=[DocumentRead.model_validate(d) for d in docs])


@router.get("/queue", response_model=APIResponse[List[DocumentRead]])
async def list_document_verification_queue(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List documents in verification queue for advisors and underwriters."""
    user_roles = [r.name for r in current_user.roles]
    if not any(r in ["Underwriter", "Advisor", "Admin", "Owner"] for r in user_roles):
        raise PermissionDeniedException("Unauthorized to access document verification queue.")

    doc_repo = DocumentRepository(session)
    docs = await doc_repo.list_queue(status=status, limit=limit, offset=offset)
    return APIResponse(data=[DocumentRead.model_validate(d) for d in docs])


@router.post("/{document_id}/verify", response_model=APIResponse[DocumentRead])
async def verify_document(
    document_id: str,
    req: DocumentVerifyRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Underwriter and Advisor endpoint to formally verify or reject a document."""
    user_roles = [r.name for r in current_user.roles]
    if not any(r in ["Underwriter", "Advisor", "Admin", "Owner"] for r in user_roles):
        raise PermissionDeniedException("Only authorized Underwriters and Advisors may verify documents.")

    doc_repo = DocumentRepository(session)
    doc = await doc_repo.get_by_id_with_relations(document_id)
    if not doc:
        raise EntityNotFoundException("Document not found.")

    doc.verification_status = req.decision
    doc.verified_by_id = current_user.id
    doc.verified_at = datetime.now(timezone.utc)
    if req.decision == "rejected":
        doc.rejection_reason = req.rejection_reason or "Document rejected during underwriting review."
    else:
        doc.rejection_reason = None

    await session.commit()
    return APIResponse(
        data=DocumentRead.model_validate(doc),
        message=f"Document successfully marked as {req.decision}.",
    )
