import logging
from datetime import date
from typing import Optional, List
from django.db import transaction, models
from django.utils import timezone

from hr.employees.models import Employee
from hr.jobs.models import (
    Position, 
    Department, 
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
        department: Department, 
        start_date: Optional[date] = None
    ) -> EmployeePositionHistory:
        """ Formally records an employee's starting role and department. """
        start_date = start_date or timezone.now().date()

        if EmployeePositionHistory.objects.filter(employee=employee).exists():
            raise ValueError(
                f"Employee {employee.id} already has a recorded history."
            )

        history = EmployeePositionHistory.objects.create(
            employee=employee,
            position=position,
            department=department,
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
        new_department: Optional[Department] = None,
        effective_date: Optional[date] = None,
        description: Optional[str] = None
    ) -> EmployeePositionHistory:
        """ Processes promotions, lateral moves, or departmental transfers. """
        effective_date = effective_date or timezone.now().date()
        
        current_history = EmployeePositionHistory.objects.filter(
            employee=employee, 
            is_current=True
        ).first()

        if current_history:
            if effective_date < current_history.start_date:
                raise ValueError("Effective date cannot precede the current role's start date.")
            
            if current_history.position == new_position and current_history.department == new_department:
                return current_history

        new_history = EmployeePositionHistory.objects.create(
            employee=employee,
            position=new_position,
            department=new_department or (current_history.department if current_history else None),
            start_date=effective_date,
            is_current=True,
            description=description or f"Transition to {new_position.name}"
        )

        logger.info(f"Employee {employee.id} transitioned to {new_position.name}")
        return new_history

    def get_active_staff_count(self, department: Department, include_subs: bool = True) -> int:
        """ Calculates current headcount for a specific department. """
        query = models.Q(department=department)
        if include_subs:
            query |= models.Q(department__parent=department) 
            
        return EmployeePositionHistory.objects.filter(query, is_current=True).count()

    def get_career_summary(self, employee: Employee) -> List[dict]:
        """ Provides a timeline of all roles held by an employee. """
        history = EmployeePositionHistory.objects.filter(employee=employee).order_by('-start_date')
        summary = []
        for entry in history:
            end = entry.end_date or timezone.now().date()
            duration = (end - entry.start_date).days
            summary.append({
                "position": entry.position.name,
                "level": entry.position.level,
                "department": entry.department.name if entry.department else None,
                "days_spent": duration,
                "is_current": entry.is_current
            })
        return summary

