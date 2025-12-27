from django.db import transaction
from hr.employees.models import (
    Employee, 
    EmployeeEmergencyContact
)


class EmployeeEmergencyContactWriterService:
    """
    Handles creation, update, and deletion of employee emergency contacts.
    """

    @staticmethod
    @transaction.atomic
    def add_contact(
        employee_id: int, 
        first_name: str, 
        last_name: str, 
        phone: str, 
        relation: str, 
        priority: int = 1
    ) -> EmployeeEmergencyContact:
        """
        Adds a new emergency contact for the given employee.
        """
        employee = Employee.objects.get(id=employee_id)
        return EmployeeEmergencyContact.objects.create(
            employee=employee,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            relation=relation,
            priority=priority
        )

    @staticmethod
    @transaction.atomic
    def update_contact(contact_id: int, **kwargs) -> EmployeeEmergencyContact:
        """
        Updates an existing emergency contact.
        Accepts kwargs corresponding to EmployeeEmergencyContact fields.
        """
        contact = EmployeeEmergencyContact.objects.get(id=contact_id)
        for field, value in kwargs.items():
            if hasattr(contact, field):
                setattr(contact, field, value)
        contact.save()
        return contact

    @staticmethod
    @transaction.atomic
    def remove_contact(contact_id: int) -> None:
        """
        Deletes an emergency contact.
        """
        EmployeeEmergencyContact.objects.filter(id=contact_id).delete()


class EmployeeEmergencyContactReaderService:   
    """
    Handles retrieval and search of EmployeeEmergencyContact records.
    """

    @staticmethod
    def list_contacts(employee_id: int):
        """
        Returns all emergency contacts for a given employee.
        """
        return EmployeeEmergencyContact.objects.filter(employee_id=employee_id)

    @staticmethod
    def get_contact(contact_id: int) -> EmployeeEmergencyContact | None:
        """
        Retrieves a single emergency contact by its ID.
        """
        try:
            return EmployeeEmergencyContact.objects.get(id=contact_id)
        except EmployeeEmergencyContact.DoesNotExist:
            return None
