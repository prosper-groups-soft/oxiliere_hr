import logging
from datetime import date
from typing import Any, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from hr.employees.models import Employee, StatusHistory
from hr.jobs.models import EmployeeTransition
from hr.jobs.enums import TransitionType
from hr.employees.enums import EmployeeStatus
from hr.utils.core import update_instance


logger = logging.getLogger(__name__)


class EmployeeStatusService:
    """ Manages employee professional lifecycle and contract states. """

    @transaction.atomic
    def transition_status(
        self, 
        employee: Employee, 
        new_status: EmployeeStatus, 
        effective_date: date, 
        reason: str, 
        actor: Any = None
    ) -> StatusHistory:
        """ Changes employment status and updates system access flags. """
        
        # Prevent double entry
        if employee.status_history.filter(status=new_status, end_date__isnull=True).exists():
            raise ValidationError(f"Already in status: {new_status}")

        # Close current status
        current_status_entry = employee.status_history.filter(end_date__isnull=True).first()
        if current_status_entry:
            current_status_entry.end_date = effective_date
            current_status_entry.save(update_fields=['end_date'])

        # Create new history record
        new_entry = StatusHistory.objects.create(
            employee=employee,
            status=new_status,
            start_date=effective_date,
            reason=reason,
            created_by=actor
        )

        # Update access based on status
        is_active = new_status not in [EmployeeStatus.TERMINATED, EmployeeStatus.RESIGNED]
        can_connect = new_status == EmployeeStatus.ACTIVE
        
        update_instance(
            instance=employee,
            allowed_fields=['is_active', 'can_connect'],
            data={'is_active': is_active, 'can_connect': can_connect}
        )

        logger.info(f"[STATUS] {employee.matricule} -> {new_status}")
        return new_entry

    @transaction.atomic
    def suspend_access(self, employee: Employee, reason: str, actor: Any = None) -> Employee:
        """ Triggers administrative lockout and suspension. """
        self.transition_status(
            employee=employee,
            new_status=EmployeeStatus.SUSPENDED,
            effective_date=timezone.now().date(),
            reason=reason,
            actor=actor
        )
        
        logger.warning(f"[SECURITY] Access suspended: {employee.matricule}")
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
        """ Restores active status and portal access. """
        self.transition_status(
            employee=employee,
            new_status=EmployeeStatus.ACTIVE,
            effective_date=timezone.now().date(),
            reason=reason,
            actor=actor
        )

        employee.is_active = is_active if is_active is not None else True
        employee.can_connect = can_connect if can_connect is not None else True
        employee.save(update_fields=['is_active', 'can_connect'])

        logger.info(f"[RESTORE] Reactivated: {employee.matricule}")
        return employee

    @transaction.atomic
    def offboard_employee(
        self, 
        employee: Employee, 
        termination_date: date, 
        reason: str, 
        departure_type: str = 'TERMINATED',
        actor: Any = None
    ) -> Employee:
        """ Records official exit: status transition, position closure, and career transition. """

        # Map departure_type to EmployeeStatus
        status_map = {
            'TERMINATED': EmployeeStatus.TERMINATED,
            'RESIGNED': EmployeeStatus.RESIGNED,
            'RETIRED': EmployeeStatus.RETIRED,
        }
        target_status = status_map.get(departure_type, EmployeeStatus.TERMINATED)

        # 1. Status transition
        self.transition_status(
            employee=employee,
            new_status=target_status,
            effective_date=termination_date,
            reason=reason,
            actor=actor
        )
        
        # 2. Close current position history
        current_position = employee.position_history.filter(is_current=True).first()
        if current_position:
            current_position.is_current = False
            current_position.end_date = termination_date
            current_position.save(update_fields=['is_current', 'end_date'])
            logger.info(f"[EXIT] Closed position history {current_position.id} for {employee.matricule}")

        # 3. Create EmployeeTransition (OFFBOARD)
        EmployeeTransition.objects.create(
            employee=employee,
            transition_type=TransitionType.OFFBOARD,
            from_position=current_position.position if current_position else None,
            from_seniority_level=current_position.seniority_level if current_position else None,
            date=termination_date,
            reason=reason,
        )
        logger.info(f"[EXIT] Created EmployeeTransition (OFFBOARD) for {employee.matricule}")
        
        # 4. Set termination date
        employee.termination_date = termination_date
        employee.save(update_fields=['termination_date'])
        
        logger.info(f"[EXIT] Offboarded: {employee.matricule} ({departure_type})")
        return employee

