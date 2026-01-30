import logging
from datetime import date
from typing import Any, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from hr.employees.models import Employee, StatusHistory
from hr.employees.enums import EmployeeStatus
from hr.utils.core import update_instance


logger = logging.getLogger(__name__)


class EmployeeStatusService:
    """
    Service managing the professional lifecycle and contract states.
    Ensures that every status change is documented and auditable.
    """

    @transaction.atomic
    def transition_status(
        self, 
        employee: Employee, 
        new_status: EmployeeStatus, 
        effective_date: date, 
        reason: str, 
        actor: Any = None
    ) -> StatusHistory:
        """
        Business Intent: Move an employee from one professional state to another.
        
        Logic:
        1. Validates that the transition is logical.
        2. Closes the previous status (sets end_date).
        3. Creates the new status entry.
        4. Updates the Employee root flags (is_active, can_connect).
        """
        # 1. Basic validation
        if employee.status_history.filter(status=new_status, end_date__isnull=True).exists():
            raise ValidationError(f"Employee is already in status: {new_status}")

        # 2. Closing the previous status
        # Find the current status (the one with no end date)
        current_status_entry = employee.status_history.filter(end_date__isnull=True).first()
        if current_status_entry:
            current_status_entry.end_date = effective_date
            current_status_entry.save(update_fields=['end_date'])

        # 3. Creating the new history record
        new_entry = StatusHistory.objects.create(
            employee=employee,
            status=new_status,
            start_date=effective_date,
            reason=reason,
            created_by=actor
        )

        # 4. Updating the Root entity state (Employee)
        # Business rules for visibility/access are defined here
        is_active = new_status not in [EmployeeStatus.TERMINATED, EmployeeStatus.RESIGNED]
        can_connect = new_status == EmployeeStatus.ACTIVE
        
        update_instance(
            instance=employee,
            allowed_fields=['is_active', 'can_connect'],
            data={'is_active': is_active, 'can_connect': can_connect}
        )

        logger.info(f"[STATUS] {employee.matricule} transitioned to {new_status} by {actor}")
        return new_entry

    @transaction.atomic
    def suspend_access(self, employee: Employee, reason: str, actor: Any = None) -> Employee:
        """
        Business Intent: Temporary administrative lockout.
        TECHNICAL: Transitions the employee to the 'SUSPENDED' status.
        This automatically handles the history, the reason, and the flags.
        """
        self.transition_status(
            employee=employee,
            new_status=EmployeeStatus.SUSPENDED,
            effective_date=timezone.now().date(),
            reason=reason,
            actor=actor
        )
        
        logger.warning(f"[SECURITY] Employee {employee.matricule} moved to SUSPENDED status. Reason: {reason}")
        return employee
        
    @transaction.atomic
    def reactivate_employee(
        self, 
        employee: Employee, 
        reason: str, 
        actor: Any = None,
        is_active: Optional[bool] = True,
        can_connect: Optional[bool] = True
    ) -> Employee:
        """
        BUSINESS: Ends a suspension or leave period.
        TECHNICAL: Returns the employee to ACTIVE status, restores 'can_connect', and updates 'is_active'.
        """
        # Transition status
        self.transition_status(
            employee=employee,
            new_status=EmployeeStatus.ACTIVE,
            effective_date=timezone.now().date(),
            reason=reason,
            actor=actor
        )

        # Apply flags from API schema
        employee.is_active = is_active if is_active is not None else True
        employee.can_connect = can_connect if can_connect is not None else True
        employee.save(update_fields=['is_active', 'can_connect'])

        logger.info(f"[RESTORE] {employee.matricule} has been reactivated by {actor}")
        return employee

    @transaction.atomic
    def offboard_employee(
        self, 
        employee: Employee, 
        termination_date: date, 
        reason: str, 
        actor: Any = None
    ) -> Employee:
        """
        Business Intent: Formal exit from the company.
        """
        # Utilise la transition de statut pour la cohérence
        self.transition_status(
            employee=employee,
            new_status=EmployeeStatus.TERMINATED,
            effective_date=termination_date,
            reason=reason,
            actor=actor
        )
        
        # Enregistre la date de fin officielle sur le profil
        employee.termination_date = termination_date
        employee.save(update_fields=['termination_date'])
        
        logger.info(f"[EXIT] {employee.matricule} officially offboarded on {termination_date}")
        return employee

