import logging
from typing import Any, Dict
from django.db import transaction
from hr.employees.models import Employee, EmergencyContact
from hr.utils.core import update_instance


logger = logging.getLogger(__name__)


class EmployeeEmergencyService:
    """
    Service managing emergency contacts with automatic priority sequencing.
    Ensures priority constraints are respected during add/update/delete.
    """

    @transaction.atomic
    def add_contact(
        self, 
        employee: Employee, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmergencyContact:
        """
        Register a new emergency contact.
        If the priority is already taken, it will be reordered
        automatically after creation to maintain a sequential order.
        """
        contact = EmergencyContact.objects.create(
            employee=employee,
            first_name=data.get('first_name', ''),
            middle_name=data.get('middle_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone'),
            relation=data.get('relation'),
            priority=data.get('priority', 1),
            created_by=actor
        )

        logger.info(
            f"[EMERGENCY] Contact {contact.first_name} "
            f"added for {employee.matricule} (Prio: {contact.priority})"
        )

        # Reorder priorities after add to ensure sequence
        self._reorder_priorities(employee=employee, actor=actor)

        return contact

    @transaction.atomic
    def update_contact(
        self, 
        contact: EmergencyContact, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmergencyContact:
        """
        Update contact details or priority level.
        Uses partial update. Reorders priorities if needed.
        """
        allowed_fields = [
            'first_name', 'middle_name', 'last_name', 
            'phone', 'relation', 'priority'
        ]

        update_instance(
            instance=contact,
            allowed_fields=allowed_fields,
            data=data
        )

        contact.updated_by = actor
        contact.save(update_fields=['updated_by', 'priority'])

        # Reorder priorities after update to maintain sequence
        self._reorder_priorities(employee=contact.employee, actor=actor)

        return contact

    @transaction.atomic
    def remove_contact(self, contact: EmergencyContact, actor: Any = None) -> None:
        """
        Remove an emergency contact.
        Soft-delete with audit trail. Reorders remaining contacts.
        """
        contact_name = f"{contact.first_name} {contact.last_name}"
        employee = contact.employee
        contact.updated_by = actor
        contact.delete()

        logger.warning(f"[EMERGENCY] Contact {contact_name} removed for {employee.matricule} by {actor}")

        # Reorder remaining contacts
        self._reorder_priorities(employee=employee, actor=actor)

    @transaction.atomic
    def _reorder_priorities(self, employee: Employee, actor: Any = None) -> None:
        """
        Ensure emergency contacts are sequentially ordered by priority.
        Reassigns priority 1..N to avoid duplicates.
        """
        contacts = list(employee.emergency_contacts.all().order_by('priority', 'id'))
        for idx, contact in enumerate(contacts, start=1):
            if contact.priority != idx:
                contact.priority = idx
                contact.updated_by = actor
                contact.save(update_fields=['priority', 'updated_by'])

        if contacts:
            logger.info(f"[EMERGENCY] Priorities reordered for {employee.matricule}")

