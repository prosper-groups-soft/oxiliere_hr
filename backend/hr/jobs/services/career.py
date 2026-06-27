import logging
from datetime import date
from typing import Optional, List
from django.db import transaction, models
from django.utils import timezone

from hr.employees.models import Employee
from hr.jobs.models import (
    Position, 
    OrgUnit, 
    SeniorityLevel,
    EmployeePositionHistory
)


logger = logging.getLogger(__name__)


class CareerService:
    """ Manages employee career progression, promotions, and organizational movements. """

    @transaction.atomic
    def assign_initial_position(
        self, 
        employee: Employee, 
        position: Position, 
        org_unit: OrgUnit, 
        seniority_level: Optional[SeniorityLevel] = None,
        start_date: Optional[date] = None
    ) -> EmployeePositionHistory:
        """ Formally records an employee's starting role and organizational unit. """
        start_date = start_date or timezone.now().date()

        if EmployeePositionHistory.objects.filter(employee=employee).exists():
            raise ValueError(
                f"Employee {employee.id} already has a recorded history."
            )

        history = EmployeePositionHistory.objects.create(
            employee=employee,
            position=position,
            org_unit=org_unit,
            seniority_level=seniority_level,
            start_date=start_date,
            is_current=True
        )
        
        logger.info(f"Initial role {position.name} assigned to {employee.id}")
        return history

    @transaction.atomic
    def move_employee(
        self,
        employee: Employee,
        new_position: Position,
        new_seniority_level: Optional[SeniorityLevel] = None,
        new_org_unit: Optional[OrgUnit] = None,
        effective_date: Optional[date] = None,
        description: Optional[str] = None
    ) -> EmployeePositionHistory:
        """ Processes promotions, lateral moves, or organizational unit transfers. """
        effective_date = effective_date or timezone.now().date()
        
        current_history = EmployeePositionHistory.objects.filter(
            employee=employee, 
            is_current=True
        ).first()

        if current_history:
            if effective_date < current_history.start_date:
                raise ValueError("Effective date cannot precede the current role's start date.")
            
            # If everything is the same, no need to move
            if (current_history.position == new_position and 
                current_history.org_unit == new_org_unit and 
                current_history.seniority_level == new_seniority_level):
                return current_history

            # Close current history
            current_history.is_current = False
            current_history.end_date = effective_date
            current_history.save(update_fields=['is_current', 'end_date'])

        # Create new history entry
        new_history = EmployeePositionHistory.objects.create(
            employee=employee,
            position=new_position,
            org_unit=new_org_unit or (current_history.org_unit if current_history else None),
            seniority_level=new_seniority_level or (current_history.seniority_level if current_history else None),
            start_date=effective_date,
            is_current=True,
            description=description or f"Transition vers {new_position.name}"
        )

        logger.info(f"Employee {employee.id} transitioned to {new_position.name}")
        return new_history

    def get_active_staff_count(self, org_unit: OrgUnit, include_subs: bool = True) -> int:
        """ Calculates current headcount for a specific organizational unit. """
        query = models.Q(org_unit=org_unit)
        if include_subs:
            query |= models.Q(org_unit__parent=org_unit) 
            
        return EmployeePositionHistory.objects.filter(query, is_current=True).count()

    def get_career_summary(self, employee: Employee) -> List[dict]:
        """ Provides a timeline of all roles held by an employee. """
        history = EmployeePositionHistory.objects.filter(employee=employee).order_by('-start_date')
        summary = []
        for entry in history:
            end = entry.end_date or timezone.now().date()
            duration = (end - entry.start_date).days
            summary.append({
                "position": entry.position.name if entry.position else "Inconnu",
                "level": entry.seniority_level.label if entry.seniority_level else None,
                "org_unit": entry.org_unit.name if entry.org_unit else None,
                "days_spent": duration,
                "is_current": entry.is_current
            })
        return summary

