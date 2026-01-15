import logging
from datetime import date
from typing import Any, Dict
from django.db import transaction
from django.core.exceptions import ValidationError

from hr.employees.models import Employee, EmployeeChild
from hr.utils import update_instance


logger = logging.getLogger(__name__)


class EmployeeFamilyService:
    """
    Service managing dependents and legal family records.
    Crucial for payroll benefits and tax reductions in the DRC context.
    """

    @transaction.atomic
    def declare_child(
        self, 
        employee: Employee, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeChild:
        """
        Business Intent: Formal registration of a child for HR benefits and family informations.
        
        Rules:
        - Normalizes names to Title Case.
        - Validates that the birthdate is in the past.
        - Automatically marks as a dependent upon creation.
        """
        birthdate = data.get('birthdate')
        if birthdate and isinstance(birthdate, date) and birthdate > date.today():
            raise ValidationError({"birthdate": "A child's birthdate cannot be in the future."})

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

        logger.info(f"[FAMILY] Child {child.first_name} added for employee {employee.matricule} by {actor}")
        return child

    @transaction.atomic
    def update_child_info(
        self, 
        child: EmployeeChild, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeChild:
        """
        Business Intent: Update child details or dependency status.
        Example: Unchecking 'is_dependent' when a child reaches legal age.
        """
        allowed_fields = [
            'first_name', 
            'middle_name', 
            'last_name', 
            'gender', 
            'birthdate', 
            'is_dependent'
        ]
        
        update_instance(
            instance=child,
            allowed_fields=allowed_fields,
            data=data
        )
        
        child.updated_by = actor
        child.save(update_fields=['updated_by'])
        
        return child

    @transaction.atomic
    def remove_child(self, child: EmployeeChild, actor: Any = None) -> None:
        """
        Business Intent: Remove a child record (e.g., error in entry).
        
        Technical Note: 
        Uses Soft Delete (SafeDeleteModelMixin). The record will be 
        masked but preserved for historical payroll audit logs.
        """
        child.updated_by = actor
        child.delete() 
        
        logger.warning(f"[FAMILY] Child record {child.id} soft-deleted by {actor}")
        
