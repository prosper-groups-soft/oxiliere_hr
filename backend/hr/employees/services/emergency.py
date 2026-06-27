import logging
from typing import Any, Dict
from django.db import transaction, models
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
        """ Adds a contact with auto-calculated priority (next available). """
        
        # Calculate next priority automatically
        max_priority = employee.emergency_contacts.aggregate(
            max_p=models.Max('priority')
        )['max_p'] or 0
        priority = max_priority + 1
        
        contact = EmergencyContact.objects.create(
            employee=employee,
            first_name=data.get('first_name', ''),
            middle_name=data.get('middle_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone'),
            relation=data.get('relation'),
            priority=priority,
            created_by=actor
        )

        logger.info(f"[EMERGENCY] Contact added: {employee.matricule}")

        return contact

    @transaction.atomic
    def update_contact(
        self, 
        contact: EmergencyContact, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmergencyContact:
        """ Updates contact details. """
        allowed_fields = [
            'first_name', 'middle_name', 'last_name', 
            'phone', 'relation', 'is_primary'
        ]

        update_instance(
            instance=contact,
            allowed_fields=allowed_fields,
            data=data
        )

        contact.updated_by = actor
        contact.save(update_fields=['updated_by'])

        return contact

    @transaction.atomic
    def remove_contact(self, contact: EmergencyContact, actor: Any = None) -> None:
        """ Removes a contact and reorders remaining priorities. """
        employee = contact.employee
        contact.updated_by = actor
        contact.delete()

        logger.warning(f"[EMERGENCY] Contact removed for {employee.matricule}")

        # Réorganiser les priorités pour éviter les trous et respecter la contrainte
        self._reorder_priorities(employee=employee, actor=actor)

    @transaction.atomic
    def _reorder_priorities(self, employee: Employee, actor: Any = None) -> None:
        """ Réorganise les priorités en évitant TOUT risque de violation de contrainte. """
        # Récupérer les contacts restants triés par priorité actuelle
        contacts = list(employee.emergency_contacts.all().order_by('priority', 'id'))
        
        if not contacts:
            return
        
        # ÉTAPE 1: Assigner des priorités temporaires négatives uniques
        # Cela libère COMPLÈTEMENT les priorités positives
        temp_priorities = range(-1000, -1000 - len(contacts), -1)
        for contact, temp_prio in zip(contacts, temp_priorities):
            contact.priority = temp_prio
            contact.updated_by = actor
            contact.save(update_fields=['priority', 'updated_by'])
        
        # ÉTAPE 2: Assigner les priorités finales séquentielles
        # Comme toutes les priorités positives sont libres, aucun conflit possible
        for idx, contact in enumerate(contacts, start=1):
            contact.priority = idx
            contact.updated_by = actor
            contact.save(update_fields=['priority', 'updated_by'])
