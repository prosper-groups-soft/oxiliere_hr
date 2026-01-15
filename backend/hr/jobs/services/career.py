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
    """
    Service responsible for managing employee career movements, 
    promotions, and historical tracking.
    """

    @transaction.atomic
    def assign_initial_position(
        self, 
        employee: Employee, 
        position: Position, 
        department: Department, 
        start_date: Optional[date] = None
    ) -> EmployeePositionHistory:
        """
        Assigns the very first position to an employee (Onboarding).
        """
        start_date = start_date or timezone.now().date()

        # Safety check: does the employee already have a history?
        if EmployeePositionHistory.objects.filter(employee=employee).exists():
            raise ValueError(
                f"Employee {employee.id} already has a position history. Use promote_employee instead."
            )

        history = EmployeePositionHistory.objects.create(
            employee=employee,
            position=position,
            department=department,
            start_date=start_date,
            is_current=True
        )
        
        logger.info(f"Initial position {position.name} assigned to employee {employee.id}")
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
        """
        Handles promotions, lateral moves, or department transfers.
        The model's save() method will automatically handle closing the previous position.
        """
        effective_date = effective_date or timezone.now().date()
        
        # 1. Fetch current position to log the transition
        current_history = EmployeePositionHistory.objects.filter(
            employee=employee, 
            is_current=True
        ).first()

        if current_history:
            # Logic check: Can't move to a date before the current position started
            if effective_date < current_history.start_date:
                raise ValueError("The effective date cannot be before the current position's start date.")
            
            # Logic check: Avoid duplicate active position if it's exactly the same
            if current_history.position == new_position and current_history.department == new_department:
                return current_history

        # 2. Create new history record
        # Note: The model's save() handles 'is_current=False' and 'end_date' for the old record.
        new_history = EmployeePositionHistory.objects.create(
            employee=employee,
            position=new_position,
            department=new_department or (current_history.department if current_history else None),
            start_date=effective_date,
            is_current=True,
            description=description or f"Transition to {new_position.name}"
        )

        logger.info(f"Employee {employee.id} moved to {new_position.name} in {new_department}")
        return new_history

    def get_active_staff_count(self, department: Department, include_subs: bool = True) -> int:
        """
        Counts current employees in a department.
        """
        query = models.Q(department=department)
        if include_subs:
            # We use the recursive related name from your model
            query |= models.Q(department__parent=department) 
            
        return EmployeePositionHistory.objects.filter(query, is_current=True).count()

    def get_career_summary(self, employee: Employee) -> List[dict]:
        """
        Returns a list of all positions held with duration.
        """
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

