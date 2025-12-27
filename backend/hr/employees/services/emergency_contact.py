from uuid import UUID
from django.db import transaction, models
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
    def add_contact(employee_id: UUID, **data) -> EmployeeEmergencyContact:
        """
        Adds a new emergency contact for the given employee.
        """
        employee = Employee.objects.get(id=employee_id)
        return EmployeeEmergencyContact.objects.create(
            employee=employee,
            **data
        )

    @staticmethod
    @transaction.atomic
    def update_contact(contact_id: UUID, **kwargs) -> EmployeeEmergencyContact:
        """
        Updates an existing emergency contact record.
        """
        contact = EmployeeEmergencyContact.objects.get(id=contact_id)
        for field, value in kwargs.items():
            if hasattr(contact, field):
                setattr(contact, field, value)
        contact.save()
        return contact

    @staticmethod
    @transaction.atomic
    def remove_contact(contact_id: UUID) -> None:
        """
        Deletes an emergency contact record.
        """
        contact = EmployeeEmergencyContact.objects.get(id=contact_id)
        contact.delete()


class EmployeeEmergencyContactReaderService:   
    """
    Handles retrieval and search of EmployeeEmergencyContact records.
    """

    @staticmethod
    def search(employee_id: UUID, query: str = None):
        """
        Search contacts for a specific employee by name or phone.
        """
        qs = EmployeeEmergencyContact.objects.filter(employee_id=employee_id)
        
        if query:
            qs = qs.filter(
                models.Q(first_name__icontains=query) |
                models.Q(last_name__icontains=query) |
                models.Q(phone__icontains=query)
            )
        return qs # Meta ordering (priority, last_name) is applied automatically

    @staticmethod
    def get_contact(contact_id: UUID) -> EmployeeEmergencyContact:
        """
        Retrieves a single emergency contact by its ID.
        """
        return EmployeeEmergencyContact.objects.get(id=contact_id)

