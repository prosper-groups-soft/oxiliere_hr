import os
from pathlib import Path
from typing import Any, Dict
import logging
from django.db import transaction
from django.core.exceptions import ValidationError

from hr.employees.models import Employee, EmployeeDocument


logger = logging.getLogger(__name__)


class EmployeeDocumentService:
    """ Handles digital records and legal identification validation. """

    @transaction.atomic
    def upload_document(
        self, 
        employee: Employee, 
        file_obj: Any, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeDocument:
        """ Saves a new legal or professional document file. """
        document_type = data.get('document_type')
        if not document_type:
            raise ValidationError("Document type required.")

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

        logger.info(f"[DOC] Uploaded: {document_type} for {employee.matricule}")
        return document

    @transaction.atomic
    def verify_document(
        self, 
        document: EmployeeDocument, 
        actor: Any
    ) -> EmployeeDocument:
        """ Marks a document as reviewed and verified. """
        document.is_verified = True
        document.updated_by = actor
        document.save(update_fields=['is_verified', 'updated_by'])

        logger.info(f"[DOC] Verified: {document.id}")
        return document

    @transaction.atomic
    def remove_document(self, document: EmployeeDocument, actor: Any = None) -> None:
        """ Deletes document record and associated file on disk. """
        actor = actor or getattr(document, 'updated_by', None)
        file_path = Path(document.file.path) if document.file else None

        # Delete record
        document.updated_by = actor
        document.delete()

        # Delete physical file
        if file_path and file_path.exists():
            file_path.unlink()
            
            # Cleanup empty folders
            for parent in file_path.parents:
                if parent.name == "employee_docs":
                    break
                try:
                    parent.rmdir() 
                except OSError:
                    break

        logger.warning(f"[DOC] Removed: {document.id}")

    @transaction.atomic
    def update_document(
        self, 
        document: EmployeeDocument, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeDocument:
        """ Updates document metadata. """
        for attr, value in data.items():
            if hasattr(document, attr) and value is not None:
                setattr(document, attr, value)
        
        document.updated_by = actor
        document.save()
        
        logger.info(f"[DOC] Updated: {document.id}")
        return document

    @transaction.atomic
    def replace_document_file(
        self, 
        document: EmployeeDocument, 
        file_obj: Any, 
        actor: Any = None
    ) -> EmployeeDocument:
        """ Replaces physical file and updates record. """
        # Delete old file
        if document.file and document.file.path:
            old_file = Path(document.file.path)
            if old_file.exists():
                old_file.unlink()
        
        # Set new file
        document.file = file_obj
        document.updated_by = actor
        document.save()
        
        logger.info(f"[DOC] File replaced: {document.id}")
        return document

