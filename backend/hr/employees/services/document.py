import os
from pathlib import Path
from typing import Any, Dict
import logging
from django.db import transaction
from django.core.exceptions import ValidationError

from hr.employees.models import Employee, EmployeeDocument


logger = logging.getLogger(__name__)


class EmployeeDocumentService:
    """
    Service handling digital records and legal proofs (KYC: Know Your Customer).
    Aligned with the updated EmpDocument model schema.
    """

    @transaction.atomic
    def upload_document(
        self, 
        employee: Employee, 
        file_obj: Any, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeDocument:
        """
        Business Intent: Add a new legal or academic proof with full metadata.
        
        Responsibilities:
        - Ensures document category is defined.
        - Captures the Issuing Authority for verification tracking.
        - Sets initial verification status to False.
        """
        document_type = data.get('document_type')
        if not document_type:
            raise ValidationError("Document type is mandatory.")

        document = EmployeeDocument.objects.create(
            employee=employee,
            document_type=document_type,
            document_number=data.get('document_number'),
            issuing_authority=data.get('issuing_authority'),
            file=file_obj,
            issue_date=data.get('issue_date'),
            expiry_date=data.get('expiry_date'),
            is_verified=False,
            created_by=actor
        )

        logger.info(
            f"[DOC] Document '{document_type}' uploaded for {employee.matricule}"
            f"(Auth: {document.issuing_authority})"
        )
        return document

    @transaction.atomic
    def verify_document(
        self, 
        document: EmployeeDocument, 
        actor: Any
    ) -> EmployeeDocument:
        """
        Business Intent: Official validation of the digital scan.
        The auditor (actor) confirms the issuing authority's stamp/signature is valid.
        """
        document.is_verified = True
        document.updated_by = actor
        document.save(update_fields=['is_verified', 'updated_by'])

        logger.info(f"[DOC] Document {document.id} (from {document.issuing_authority}) verified by {actor}")
        return document

    @transaction.atomic
    def remove_document(self, document: EmployeeDocument, actor: Any = None) -> None:
        """
        Remove a document using SafeDelete logic AND delete the file on disk.
        Also cleans up empty folders in the path.
        """
        actor = actor or getattr(document, 'updated_by', None)

        # store file path before deletion
        file_path = Path(document.file.path) if document.file else None

        # soft-delete the DB record
        document.updated_by = actor
        document.delete()

        if file_path and file_path.exists():
            # delete the file
            file_path.unlink()
            logger.warning(f"[DOC] File {file_path} physically removed by {actor}")

            # recursively remove empty parent directories up to "employee_docs"
            for parent in file_path.parents:
                if parent.name == "employee_docs":
                    break  # stop at base folder
                try:
                    parent.rmdir()  # only removes if empty
                    logger.info(f"[DOC] Removed empty folder {parent}")
                except OSError:
                    break  # folder not empty, stop cleanup
        elif file_path:
            logger.warning(f"[DOC] File {file_path} not found on disk")

        logger.warning(f"[DOC] Document {document.id} soft-deleted by {actor}")

