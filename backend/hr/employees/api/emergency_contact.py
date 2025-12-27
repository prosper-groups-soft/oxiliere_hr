from typing import List
from uuid import UUID
from django.shortcuts import get_object_or_404
from ninja_extra import api_controller, ControllerBase, route
from ninja.errors import HttpError

from hr.employees.models import (
    Employee, 
    EmployeeEmergencyContact
)
from hr.employees.schemas import (
    EmployeeEmergencyContactCreateIn,
    EmployeeEmergencyContactUpdateIn,
    EmployeeEmergencyContactDetailOut
)
from hr.employees.services import (
    EmployeeEmergencyContactWriterService,
    EmployeeEmergencyContactReaderService
)


@api_controller("/employees/{employee_id}/emergency-contacts", tags=["Emergency Contacts"])
class EmployeeEmergencyContactAPI(ControllerBase):
    """
    API for managing employee emergency contacts.
    """

    @route.get("/", response=List[EmployeeEmergencyContactDetailOut])
    def get_contacts(self, employee_id: UUID, q: str | None = None):
        """
        List or search emergency contacts for a specific employee.
        """
        get_object_or_404(Employee, id=employee_id)
        return EmployeeEmergencyContactReaderService.search(employee_id, query=q)

    @route.post("/", response=EmployeeEmergencyContactDetailOut)
    def add_contact(self, employee_id: UUID, payload: EmployeeEmergencyContactCreateIn):
        """
        Add a new emergency contact.
        """
        try:
            return EmployeeEmergencyContactWriterService.add_contact(
                employee_id, 
                **payload.dict(exclude_unset=True)
            )
        except Employee.DoesNotExist:
            raise HttpError(404, "Employee not found")

    @route.get("/{contact_id}", response=EmployeeEmergencyContactDetailOut)
    def get_contact(self, employee_id: UUID, contact_id: UUID):
        """
        Retrieve a specific emergency contact record.
        """
        try:
            contact = EmployeeEmergencyContactReaderService.get_contact(contact_id)
            if contact.employee_id != employee_id:
                raise HttpError(403, "Access denied: Contact belongs to another employee")
            return contact
        except EmployeeEmergencyContact.DoesNotExist:
            raise HttpError(404, "Emergency contact not found")

    @route.put("/{contact_id}", response=EmployeeEmergencyContactDetailOut)
    def update_contact(self, employee_id: UUID, contact_id: UUID, payload: EmployeeEmergencyContactUpdateIn):
        """
        Update an emergency contact record.
        """
        try:
            contact = EmployeeEmergencyContactReaderService.get_contact(contact_id)
            if contact.employee_id != employee_id:
                raise HttpError(403, "Access denied")
            
            return EmployeeEmergencyContactWriterService.update_contact(
                contact_id, 
                **payload.dict(exclude_unset=True)
            )
        except EmployeeEmergencyContact.DoesNotExist:
            raise HttpError(404, "Emergency contact not found")

    @route.delete("/{contact_id}")
    def remove_contact(self, employee_id: UUID, contact_id: UUID):
        """
        Delete an emergency contact record.
        """
        try:
            contact = EmployeeEmergencyContactReaderService.get_contact(contact_id)
            if contact.employee_id != employee_id:
                raise HttpError(403, "Access denied")
            
            EmployeeEmergencyContactWriterService.remove_contact(contact_id)
            return {"success": True}
        except EmployeeEmergencyContact.DoesNotExist:
            raise HttpError(404, "Emergency contact not found")

