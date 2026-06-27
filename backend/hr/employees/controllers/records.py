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
    """ API endpoints for employee digital documents and residential history. """

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

    @http_post('/{employee_id}/documents', response={201: EmployeeDocumentOut})
    def upload_document(
        self,
        employee_id: UUID,
        data: EmployeeDocumentCreate,
        file: File[UploadedFile],
    ):
        """ Uploads and links a new legal or professional document. """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Uploading {data.document_type} for {employee.matricule}")

        try:
            return 201, self.doc_service.upload_document(
                employee=employee,
                file_obj=file,
                data=data.model_dump(),
                actor=actor,
            )
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_patch('/documents/{document_id}/verify', response=EmployeeDocumentOut)
    def verify_document(self, document_id: UUID):
        """ Marks a document as verified after compliance review. """
        document = get_object_or_404(EmployeeDocument, id=document_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Verifying document {document_id}")
        return self.doc_service.verify_document(document=document, actor=actor)

    @http_post('/{employee_id}/addresses/move', response=EmployeeAddressOut)
    def register_move(self, employee_id: UUID, data: EmployeeAddressMoveIn):
        """ Registers a change of residence and archives old address. """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Registering move for {employee.matricule}")

        return self.address_service.register_move(
            employee=employee,
            data=data.model_dump(),
            actor=actor,
        )
    
    @http_patch('/addresses/{address_id}', response=EmployeeAddressOut)
    def correct_address(self, address_id: UUID, data: EmployeeAddressCorrectIn):
        """ Performs administrative corrections on an existing address record. """
        address = get_object_or_404(EmployeeAddress, id=address_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Correcting address {address_id}")

        return self.address_service.correct_address(
            address_id=address_id,
            data=data.model_dump(exclude_unset=True),
            actor=actor
        )

    @http_delete('/documents/{document_id}', response={204: None})
    def remove_document(self, document_id: UUID):
        """ Deletes a document record and its associated file. """
        document = get_object_or_404(EmployeeDocument, id=document_id)
        actor = getattr(self.context.request, 'user', None)

        logger.warning(f"[API] Removing document {document_id}")

        self.doc_service.remove_document(
            document=document,
            actor=actor,
        )
        return 204, None

    @http_patch('/documents/{document_id}', response=EmployeeDocumentOut)
    def update_document(
        self, 
        document_id: UUID, 
        data: EmployeeDocumentCreate
    ):
        """ Updates a document record. """
        document = get_object_or_404(EmployeeDocument, id=document_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Updating document {document_id}")
        
        return self.doc_service.update_document(
            document=document,
            data=data.model_dump(exclude_unset=True),
            actor=actor
        )

    @http_post('/documents/{document_id}/upload', response=EmployeeDocumentOut)
    def upload_document_file(
        self, 
        document_id: UUID, 
        file: File[UploadedFile]
    ):
        """ Replaces the physical file of an existing document record. """
        document = get_object_or_404(EmployeeDocument, id=document_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Uploading file for document {document_id}")
        
        return self.doc_service.replace_document_file(
            document=document,
            file_obj=file,
            actor=actor
        )

