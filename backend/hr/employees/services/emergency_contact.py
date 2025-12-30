from uuid import UUID
from django.db import transaction, models
from hr.employees.schemas import EmployeeEmergencyContactFilterIn
from hr.employees.models import (
    Employee, 
    EmployeeEmergencyContact,
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
    def get_contact(contact_id: UUID) -> EmployeeEmergencyContact:
        """
        Retrieves a single emergency contact by its ID.
        """
        return EmployeeEmergencyContact.objects.get(id=contact_id)

    @staticmethod
    def get_contacts(
        *,
        employee_id: UUID,
        filters: EmployeeEmergencyContactFilterIn
    ):
        """
        Search contacts for a specific employee by name or phone.
        """
        # raises Employee.DoesNotExist ifnot found
        Employee.objects.get(id=employee_id)

        qs = EmployeeEmergencyContact.objects.filter(employee_id=employee_id)

        # Search text
        if filters.search:
            qs = qs.filter(
                models.Q(first_name__icontains=filters.search) |
                models.Q(middle_name__icontains=filters.search) |
                models.Q(last_name__icontains=filters.search) |
                models.Q(phone__icontains=filters.search)
            )

        return qs

