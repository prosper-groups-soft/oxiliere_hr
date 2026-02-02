import logging
from typing import Any, Dict
from django.db import transaction
from hr.employees.models import Employee, EmergencyContact
from hr.utils.core import update_instance


logger = logging.getLogger(__name__)


class EmployeeEmergencyService:
    """ Manages emergency contacts with priority sequencing. """

    @transaction.atomic
    def add_contact(
        self, 
        employee: Employee, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmergencyContact:
        """ Adds a contact and reorders priorities. """
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

        logger.info(f"[EMERGENCY] Contact added: {employee.matricule}")

        # Maintain sequence
        self._reorder_priorities(employee=employee, actor=actor)

        return contact

    @transaction.atomic
    def update_contact(
        self, 
        contact: EmergencyContact, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmergencyContact:
        """ Updates contact details and adjusts priority order. """
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

        # Maintain sequence
        self._reorder_priorities(employee=contact.employee, actor=actor)

        return contact

    @transaction.atomic
    def remove_contact(self, contact: EmergencyContact, actor: Any = None) -> None:
        """ Removes a contact and reorders remaining ones. """
        employee = contact.employee
        contact.updated_by = actor
        contact.delete()

        logger.warning(f"[EMERGENCY] Contact removed for {employee.matricule}")

        self._reorder_priorities(employee=employee, actor=actor)

    @transaction.atomic
    def _reorder_priorities(self, employee: Employee, actor: Any = None) -> None:
        """ Ensures priorities are sequential from 1 upward. """
        contacts = list(employee.emergency_contacts.all().order_by('priority', 'id'))
        for idx, contact in enumerate(contacts, start=1):
            if contact.priority != idx:
                contact.priority = idx
                contact.updated_by = actor
                contact.save(update_fields=['priority', 'updated_by'])

