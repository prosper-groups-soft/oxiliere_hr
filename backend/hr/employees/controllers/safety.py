import logging
from uuid import UUID
from injector import inject

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from ninja_extra import (
    api_controller,
    http_post,
    http_patch,
    http_delete,
    ControllerBase,
)

# Schemas & Models
from hr.employees.schemas import (
    EmergencyContactOut,
    EmergencyContactCreate,
    EmergencyContactUpdate,
)
from hr.employees.models import EmergencyContact

# Services
from hr.employees.services import (
    EmployeeEmergencyService,
    EmployeeQueryService,
)


logger = logging.getLogger(__name__)


@api_controller('/employees', tags=['Employee Safety'])
class EmployeeSafetyController(ControllerBase):
    """ API endpoints for employee emergency contacts and safety data. """

    @inject
    def __init__(self, safety_service: EmployeeEmergencyService, query_service: EmployeeQueryService):
        self.safety_service = safety_service
        self.query_service = query_service

    @http_post('/{employee_id}/emergency-contacts', response={201: EmergencyContactOut})
    def add_emergency_contact(self, employee_id: UUID, data: EmergencyContactCreate):
        """ Registers a new emergency contact with priority sequencing. """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Registering emergency contact for {employee.matricule}")

        try:
            return 201, self.safety_service.add_contact(
                employee=employee,
                data=data.model_dump(),
                actor=actor,
            )
        except ValidationError as e:
            return self.create_response(e.message_dict, status_code=400)

    @http_patch('/emergency-contacts/{contact_id}', response=EmergencyContactOut)
    def update_contact(self, contact_id: UUID, data: EmergencyContactUpdate):
        """ Updates contact information or call priority. """
        contact = get_object_or_404(EmergencyContact, id=contact_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Updating emergency contact {contact_id}")

        try:
            return self.safety_service.update_contact(
                contact=contact,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
        except ValidationError as e:
            return self.create_response(e.message_dict, status_code=400)

    @http_delete('/emergency-contacts/{contact_id}', response={204: None})
    def remove_contact(self, contact_id: UUID):
        """ Removes an emergency contact and reorders remaining ones. """
        contact = get_object_or_404(EmergencyContact, id=contact_id)
        actor = getattr(self.context.request, 'user', None)
        self.safety_service.remove_contact(contact=contact, actor=actor)
        return 204, None

