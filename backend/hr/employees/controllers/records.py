import logging
from uuid import UUID
from injector import inject
from ninja_extra import (
    api_controller,
    http_post,
    http_patch,
    http_delete,
    ControllerBase,
)
from ninja import File
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

# Schemas & Models
from hr.employees.schemas import (
    EmployeeDocumentOut,
    EmployeeDocumentCreate,
    EmployeeAddressOut,
    EmployeeAddressMoveIn,
    EmployeeAddressCorrectIn,
)
from hr.employees.models import EmployeeDocument, EmployeeAddress

# Services
from hr.employees.services import (
    EmployeeDocumentService,
    EmployeeAddressService,
    EmployeeQueryService,
)


logger = logging.getLogger(__name__)


@api_controller('/employees', tags=['Employee Records & Vault'])
class EmployeeRecordController(ControllerBase):
    """
    ORCHESTRATION LAYER:
    Handles digital vaulting and residential history. Ensures that binary
    files are correctly linked to employee profiles and that moves
    are registered with temporal integrity.
    """

    @inject
    def __init__(
        self,
        doc_service: EmployeeDocumentService,
        address_service: EmployeeAddressService,
        query_service: EmployeeQueryService,
    ):
        self.doc_service = doc_service
        self.address_service = address_service
        self.query_service = query_service

    # --- DOCUMENT VAULT ---

    @http_post('/{employee_id}/documents', response={201: EmployeeDocumentOut})
    def upload_document(
        self,
        employee_id: UUID,
        data: EmployeeDocumentCreate,
        file: File[UploadedFile],
    ):
        """
        Digitalization of HR artifacts (KYC).
        Merges metadata and file stream.
        """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Uploading {data.document_type} for {employee.matricule}")

        try:
            document = self.doc_service.upload_document(
                employee=employee,
                file_obj=file,
                data=data.model_dump(),
                actor=actor,
            )
            return 201, document
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_patch('/documents/{document_id}/verify', response=EmployeeDocumentOut)
    def verify_document(self, document_id: UUID):
        """
        Compliance audit.
        Service-driven status toggle with audit trail.
        """
        document = get_object_or_404(EmployeeDocument, id=document_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Verifying document {document_id} (Auditor: {actor})")
        return self.doc_service.verify_document(document=document, actor=actor)

    # --- GEOGRAPHY (ADDRESSES) ---

    @http_post('/{employee_id}/addresses/move', response=EmployeeAddressOut)
    def register_move(self, employee_id: UUID, data: EmployeeAddressMoveIn):
        """
        Residential history management.
        
        Implements a logical "Address Switch". The service closes
        the current record and opens the new one in a single transaction.
        """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Residential move registration for {employee.matricule}")

        # The service automatically archives the previous address
        return self.address_service.register_move(
            employee=employee,
            data=data.model_dump(),
            actor=actor,
        )
    
    @http_patch('/addresses/{address_id}', response=EmployeeAddressOut)
    def correct_address(self, address_id: UUID, data: EmployeeAddressCorrectIn):
        """
        Correction of an existing address.
        TECHNICAL: Does NOT change historical 'current' flags or create a new move.
        """
        address = get_object_or_404(EmployeeAddress, id=address_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Correcting address {address_id} for employee {address.employee.matricule}")

        corrected = self.address_service.correct_address(
            address_id=address_id,
            data=data.model_dump(exclude_unset=True),
            actor=actor
        )
        return corrected

    @http_delete('/documents/{document_id}', response={204: None})
    def remove_document(self, document_id: UUID):
        """
        Document revocation or cleanup.
        """
        document = get_object_or_404(EmployeeDocument, id=document_id)
        actor = getattr(self.context.request, 'user', None)

        logger.warning(f"[API] Removing document {document_id} (Actor: {actor})")

        self.doc_service.remove_document(
            document=document,
            actor=actor,
        )
        return 204, None

