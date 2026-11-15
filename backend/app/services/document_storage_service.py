"""Document Storage Service: Secure file ingest, MIME verification, SHA-256 integrity, safe disk I/O."""
import hashlib
import os
import re
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from app.core.exceptions import BusinessRuleViolationException

# Allowed MIME types and magic byte headers
ALLOWED_MIME_TYPES = {
    "application/pdf": b"%PDF",
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG\r\n\x1a\n",
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

BASE_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "documents"


class DocumentStorageService:
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal and remove unsafe chars."""
        clean = os.path.basename(filename)
        clean = re.sub(r"[^\w\.-]", "_", clean)
        return clean or "document.bin"

    @classmethod
    async def validate_and_store(
        cls,
        file: UploadFile,
        customer_id: str,
        application_id: str,
        document_type: str,
    ) -> Tuple[str, str, int, str, str]:
        """
        Validates uploaded file MIME signature, size, and saves to isolated storage.
        Returns:
            (file_path_relative, sanitized_file_name, file_size_bytes, verified_mime_type, sha256_hash)
        """
        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise BusinessRuleViolationException("Uploaded file is empty.")

        if file_size > MAX_FILE_SIZE_BYTES:
            raise BusinessRuleViolationException(
                f"File size exceeds maximum permitted limit of 10 MB (Received: {file_size / (1024 * 1024):.2f} MB)."
            )

        # Binary header magic byte inspection
        verified_mime = None
        for mime, magic in ALLOWED_MIME_TYPES.items():
            if content.startswith(magic):
                verified_mime = mime
                break

        # Fallback check for PDF if version header has minor offset
        if not verified_mime and b"%PDF" in content[:1024]:
            verified_mime = "application/pdf"

        if not verified_mime:
            raise BusinessRuleViolationException(
                "Unsupported or corrupt file type. Only standard PDF (.pdf), JPEG (.jpg, .jpeg), and PNG (.png) files are permitted."
            )

        # Cryptographic integrity digest
        file_hash = hashlib.sha256(content).hexdigest()

        # Target directory isolation
        target_dir = BASE_STORAGE_DIR / customer_id / application_id
        target_dir.mkdir(parents=True, exist_ok=True)

        sanitized_name = cls._sanitize_filename(file.filename or f"{document_type}.bin")
        # Generate versioned safe name to prevent file collisions
        disk_file_name = f"{document_type}_{file_hash[:12]}_{sanitized_name}"
        full_dest_path = target_dir / disk_file_name

        with open(full_dest_path, "wb") as f:
            f.write(content)

        # Relative path stored in database
        relative_path = str(full_dest_path.relative_to(BASE_STORAGE_DIR.parent.parent))

        return relative_path, sanitized_name, file_size, verified_mime, file_hash

    @staticmethod
    def resolve_physical_path(relative_path: str) -> Path:
        """Resolve database relative path to absolute filesystem path."""
        root = Path(__file__).resolve().parent.parent.parent
        full_path = (root / relative_path).resolve()
        # Verify the path is within the project root
        if not str(full_path).startswith(str(root)):
            raise BusinessRuleViolationException("Invalid or unsafe file path requested.")
        if not full_path.exists():
            raise BusinessRuleViolationException("Referenced document file does not exist on disk.")
        return full_path
