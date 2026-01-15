import logging
from uuid import UUID
from injector import inject

from ninja_extra import (
    api_controller, 
    http_post, 
    http_patch, 
    http_delete, 
    ControllerBase
)
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

# Schemas
from hr.employees.schemas import (
    EmployeeChildCreate,
    EmployeeChildOut,
    EmployeeEducationCreate,
    EmployeeEducationUpdate,
    EmployeeEducationOut,
)
from hr.employees.models import EmployeeChild, EmployeeEducation

# Services
from hr.employees.services import (
    EmployeeFamilyService,
    EmployeeEducationService,
    EmployeeQueryService,
)


logger = logging.getLogger(__name__)


@api_controller('/employees', tags=['Family & Education'])
class EmployeeFamilyController(ControllerBase):
    """
    ORCHESTRATION LAYER:
    Manages the socio-academic profile. Bridges Django Ninja's request
    lifecycle with specialized domain services.
    """

    @inject
    def __init__(
        self,
        family_service: EmployeeFamilyService,
        education_service: EmployeeEducationService,
        query_service: EmployeeQueryService,
    ):
        self.family_service = family_service
        self.education_service = education_service
        self.query_service = query_service

    # --- FAMILY & DEPENDENTS ---

    @http_post('/{employee_id}/family/children', response={201: EmployeeChildOut})
    def add_child(self, employee_id: UUID, data: EmployeeChildCreate):
        """
        Declaration of a child for benefits.
        """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Adding dependent for employee {employee.matricule}")

        try:
            child = self.family_service.declare_child(
                employee=employee,
                data=data.model_dump(),
                actor=actor,
            )
            return 201, child
        except ValidationError as e:
            # Captures business validation (future birthdate) without modifying service
            return self.create_response(e.message_dict, status_code=400)

    @http_delete('/family/children/{child_id}', response={204: None})
    def remove_child(self, child_id: UUID):
        """
        Removal of a dependent record.
        """
        child = get_object_or_404(EmployeeChild, id=child_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Deleting child record {child_id} by {actor}")

        self.family_service.remove_child(child=child, actor=actor)
        return 204, None

    # --- EDUCATION ---

    @http_post('/{employee_id}/education', response={201: EmployeeEducationOut})
    def add_education(self, employee_id: UUID, data: EmployeeEducationCreate):
        """
        Academic background enrichment.
        """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Recording qualification for {employee.matricule}")

        try:
            education = self.education_service.add_education(
                employee=employee,
                data=data.model_dump(),
                actor=actor,
            )
            return 201, education
        except ValidationError as e:
            # Handles duplicate (degree/institute) errors caught by the service
            return self.create_response(e.message_dict, status_code=400)

    @http_patch('/education/{education_id}', response=EmployeeEducationOut)
    def update_education(self, education_id: UUID, data: EmployeeEducationUpdate):
        """
        Correcting academic details.
        """
        education = get_object_or_404(EmployeeEducation, id=education_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Updating academic record {education_id} by {actor}")

        # Integration with update_education which handles normalization internally
        return self.education_service.update_education(
            education=education,
            data=data.model_dump(exclude_unset=True),
            actor=actor,
        )

