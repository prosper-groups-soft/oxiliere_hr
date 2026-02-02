import logging
from uuid import UUID
from datetime import date
from typing import Any, Dict
from django.db import transaction
from django.core.exceptions import ValidationError

from hr.employees.models import Employee, EmployeeChild
from hr.utils.core import update_instance


logger = logging.getLogger(__name__)


class EmployeeFamilyService:
    """ Manages dependents and legal family registry. """

    @transaction.atomic
    def declare_child(
        self, 
        employee: Employee, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeChild:
        """ Registers a child for benefits and family tracking. """
        birthdate = data.get('birthdate')
        if birthdate and isinstance(birthdate, date) and birthdate > date.today():
            raise ValidationError({"birthdate": "Birthdate cannot be in the future."})

        child = EmployeeChild.objects.create(
            parent=employee,
            first_name=data.get('first_name', ''),
            middle_name=data.get('middle_name', ''),
            last_name=data.get('last_name', ''),
            gender=data.get('gender'),
            birthdate=birthdate,
            is_dependent=data.get('is_dependent', True),
            created_by=actor
        )

        logger.info(f"[FAMILY] Child added: {employee.matricule}")
        return child

    @transaction.atomic
    def update_child_info(
        self, 
        child: EmployeeChild, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeChild:
        """ Updates child details or dependency status. """
        allowed_fields = [
            'first_name', 'middle_name', 'last_name', 
            'gender', 'birthdate', 'is_dependent'
        ]
        
        update_instance(
            instance=child,
            allowed_fields=allowed_fields,
            data=data
        )
        
        child.updated_by = actor
        child.save(update_fields=['updated_by'])
        
        return child

    @staticmethod
    def get_dependent_count(employee_id: UUID) -> int:
        """ Count of active legal dependents for payroll. """
        return EmployeeChild.objects.filter(
            parent_id=employee_id, 
            is_dependent=True
        ).count()
        
    @transaction.atomic
    def remove_child(self, child: EmployeeChild, actor: Any = None) -> None:
        """ Removes a child record from the registry. """
        child.updated_by = actor
        child.delete() 
        logger.warning(f"[FAMILY] Removed child: {child.id}")
        
