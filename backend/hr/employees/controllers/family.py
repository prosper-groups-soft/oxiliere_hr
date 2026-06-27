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

from hr.employees.models import (
    EmployeeChild, 
    EmployeeEducation
)

# Services
from hr.employees.services import (
    EmployeeFamilyService,
    EmployeeEducationService,
    EmployeeQueryService,
    EmployeeCacheService,
)


logger = logging.getLogger(__name__)


@api_controller('/employees', tags=['Family & Education'])
class EmployeeFamilyController(ControllerBase):
    """ API endpoints for employee family dependents and academic background. """

    @inject
    def __init__(
        self,
        family_service: EmployeeFamilyService,
        education_service: EmployeeEducationService,
        query_service: EmployeeQueryService,
        cache_service: EmployeeCacheService,
    ):
        self.family_service = family_service
        self.education_service = education_service
        self.query_service = query_service
        self.cache_service = cache_service

    @http_post('/{employee_id}/family/children', response={201: EmployeeChildOut})
    def add_child(self, employee_id: UUID, data: EmployeeChildCreate):
        """ Declares a child for HR benefits and records. """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Adding child for {employee.matricule}")

        try:
            result = self.family_service.declare_child(
                employee=employee,
                data=data.model_dump(),
                actor=actor,
            )
            # Invalidate cache so get_employee_detail returns fresh data
            self.cache_service.clear_employee_cache(employee)
            return 201, result
        except ValidationError as e:
            return self.create_response(e.message_dict, status_code=400)

    @http_delete('/family/children/{child_id}', response={204: None})
    def remove_child(self, child_id: UUID):
        """ Removes a child dependent record from the profile. """
        child = get_object_or_404(EmployeeChild, id=child_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Removing child record {child_id}")
        self.family_service.remove_child(child=child, actor=actor)
        # Invalidate cache so get_employee_detail returns fresh data
        self.cache_service.clear_employee_cache(child.parent)
        return 204, None

    @http_patch('/family/children/{child_id}', response=EmployeeChildOut)
    def update_child(self, child_id: UUID, data: EmployeeChildCreate):
        """ Updates details of an existing child record. """
        child = get_object_or_404(EmployeeChild, id=child_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Updating child record {child_id}")

        try:
            result = self.family_service.update_child_info(
                child=child,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            # Invalidate cache so get_employee_detail returns fresh data
            self.cache_service.clear_employee_cache(child.parent)
            return result
        except ValidationError as e:
            return self.create_response(e.message_dict, status_code=400)

    @http_post('/{employee_id}/education', response={201: EmployeeEducationOut})
    def add_education(self, employee_id: UUID, data: EmployeeEducationCreate):
        """ Registers a new degree or academic qualification. """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Recording qualification for {employee.matricule}")

        try:
            return 201, self.education_service.add_education(
                employee=employee,
                data=data.model_dump(),
                actor=actor,
            )
        except ValidationError as e:
            return self.create_response(e.message_dict, status_code=400)

    @http_patch('/education/{education_id}', response=EmployeeEducationOut)
    def update_education(self, education_id: UUID, data: EmployeeEducationUpdate):
        """ Updates details of an existing academic record. """
        education = get_object_or_404(EmployeeEducation, id=education_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Updating academic record {education_id}")

        return self.education_service.update_education(
            education=education,
            data=data.model_dump(exclude_unset=True),
            actor=actor,
        )

    @http_delete('/education/{education_id}', response={204: None})
    def remove_education(self, education_id: UUID):
        """ Removes an existing academic record. """
        education = get_object_or_404(EmployeeEducation, id=education_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Removing academic record {education_id}")

        self.education_service.remove_education(education=education, actor=actor)
        # Invalidate cache so get_employee_detail returns fresh data
        self.cache_service.clear_employee_cache(education.employee)
        return 204, None

