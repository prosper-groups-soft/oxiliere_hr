import logging
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from hr.employees.models import Employee
from hr.jobs.models import (
    Position,
    SeniorityLevel,
    EmployeeTransition,
    EmployeePositionHistory
)
from hr.jobs.enums import TransitionType


logger = logging.getLogger(__name__)


class TransitionService:
    """ Manages employee career transitions (promotions, transfers, hires, offboards). """

    def list_transitions(
        self,
        filters=None
    ) -> List[EmployeeTransition]:
        """ Retrieves transitions with optional filtering using TransitionFilter schema. """
        queryset = EmployeeTransition.objects.all().select_related(
            'employee', 'from_position', 'to_position', 'from_seniority_level', 'to_seniority_level'
        )

        # Apply filters from TransitionFilter schema if provided
        if filters:
            queryset = filters.filter(queryset)

        return list(queryset.order_by('-date', '-created_at'))

    def get_transition(self, transition_id: UUID) -> Optional[EmployeeTransition]:
        """ Retrieves a single transition by ID. """
        try:
            return EmployeeTransition.objects.select_related(
                'employee', 'from_position', 'to_position', 'from_seniority_level', 'to_seniority_level'
            ).get(id=transition_id)
        except EmployeeTransition.DoesNotExist:
            return None

    def get_employee_transitions(self, employee_id: UUID) -> List[EmployeeTransition]:
        """ Retrieves all transitions for a specific employee. """
        return list(EmployeeTransition.objects.filter(
            employee_id=employee_id
        ).select_related(
            'from_position', 'to_position', 'from_seniority_level', 'to_seniority_level'
        ).order_by('-date', '-created_at'))

    def _parse_date(self, date_value: Optional[str]) -> date:
        """Convert ISO date string to date object."""
        if date_value is None:
            return timezone.now().date()
        if isinstance(date_value, date):
            return date_value
        return datetime.strptime(date_value, '%Y-%m-%d').date()

    @transaction.atomic
    def create_transition(
        self,
        employee_id: UUID,
        transition_type: str,
        from_position_id: Optional[UUID] = None,
        from_seniority_level_id: Optional[UUID] = None,
        to_position_id: Optional[UUID] = None,
        to_seniority_level_id: Optional[UUID] = None,
        date: Optional[str] = None,
        reason: Optional[str] = None,
        created_by_id: Optional[UUID] = None
    ) -> EmployeeTransition:
        """ Creates a new employee transition record. """
        # Get employee
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            raise ValueError(f"Employee {employee_id} not found")

        # Validate transition type
        if transition_type not in [t.value for t in TransitionType]:
            raise ValueError(f"Invalid transition type: {transition_type}")

        # Get related objects if IDs provided
        # Auto-detect current position from EmployeePositionHistory if from_position_id not provided
        if from_position_id:
            from_position = Position.objects.filter(id=from_position_id).first()
        else:
            # Get current position from position history
            current_history = EmployeePositionHistory.objects.filter(
                employee=employee,
                is_current=True
            ).select_related('position', 'seniority_level').first()
            from_position = current_history.position if current_history else None
            from_seniority_level = current_history.seniority_level if current_history else None

        to_position = Position.objects.filter(id=to_position_id).first() if to_position_id else None
        
        # Get seniority levels if IDs provided
        from_seniority_level = SeniorityLevel.objects.filter(id=from_seniority_level_id).first() if from_seniority_level_id else from_seniority_level
        to_seniority_level = SeniorityLevel.objects.filter(id=to_seniority_level_id).first() if to_seniority_level_id else None

        # Parse date string to date object
        transition_date = self._parse_date(date)

        # Create transition
        transition = EmployeeTransition.objects.create(
            employee=employee,
            transition_type=transition_type,
            from_position=from_position,
            from_seniority_level=from_seniority_level,
            to_position=to_position,
            to_seniority_level=to_seniority_level,
            date=transition_date,
            reason=reason,
            created_by_id=created_by_id
        )

        logger.info(f"Created {transition_type} transition for employee {employee_id}")

        # Auto-update EmployeePositionHistory for certain transitions
        if transition_type in [TransitionType.PROMOTION.value, TransitionType.TRANSFER.value]:
            if to_position:
                self._update_position_history(transition)

        return transition

    @transaction.atomic
    def update_transition(
        self,
        transition_id: UUID,
        transition_type: Optional[str] = None,
        from_position_id: Optional[UUID] = None,
        from_seniority_level_id: Optional[UUID] = None,
        to_position_id: Optional[UUID] = None,
        to_seniority_level_id: Optional[UUID] = None,
        date: Optional[str] = None,
        reason: Optional[str] = None
    ) -> EmployeeTransition:
        """ Updates an existing transition. """
        try:
            transition = EmployeeTransition.objects.get(id=transition_id)
        except EmployeeTransition.DoesNotExist:
            raise ValueError(f"Transition {transition_id} not found")

        # Update fields if provided
        if transition_type:
            if transition_type not in [t.value for t in TransitionType]:
                raise ValueError(f"Invalid transition type: {transition_type}")
            transition.transition_type = transition_type

        if from_position_id is not None:
            transition.from_position = Position.objects.filter(id=from_position_id).first()
        if from_seniority_level_id is not None:
            transition.from_seniority_level = SeniorityLevel.objects.filter(id=from_seniority_level_id).first()
        if to_position_id is not None:
            transition.to_position = Position.objects.filter(id=to_position_id).first()
        if to_seniority_level_id is not None:
            transition.to_seniority_level = SeniorityLevel.objects.filter(id=to_seniority_level_id).first()
        if date:
            transition.date = self._parse_date(date)
        if reason is not None:
            transition.reason = reason

        transition.save()
        logger.info(f"Updated transition {transition_id}")

        return transition

    @transaction.atomic
    def delete_transition(self, transition_id: UUID) -> bool:
        """ Deletes a transition record. """
        try:
            transition = EmployeeTransition.objects.get(id=transition_id)
            transition.delete()
            logger.info(f"Deleted transition {transition_id}")
            return True
        except EmployeeTransition.DoesNotExist:
            return False

    def _update_position_history(self, transition: EmployeeTransition):
        """ Updates EmployeePositionHistory based on transition data. """
        # Close current position if exists
        EmployeePositionHistory.objects.filter(
            employee=transition.employee,
            is_current=True
        ).update(is_current=False, end_date=transition.date)

        # Get org_unit from position if available
        org_unit = None
        if transition.to_position and hasattr(transition.to_position, 'org_unit'):
            org_unit = transition.to_position.org_unit

        # Get salary for the seniority level if available
        salary_at_assignment = None
        if transition.to_position and transition.to_seniority_level:
            # Find the salary range for this position and seniority level
            from hr.jobs.models import PositionSeniority
            position_seniority = PositionSeniority.objects.filter(
                position=transition.to_position,
                seniority_level=transition.to_seniority_level
            ).first()
            if position_seniority:
                salary_at_assignment = position_seniority.salary_min  # or salary_max, depending on policy

        # Create new position history entry
        EmployeePositionHistory.objects.create(
            employee=transition.employee,
            position=transition.to_position,
            seniority_level=transition.to_seniority_level,
            salary_at_assignment=salary_at_assignment,
            org_unit=org_unit,
            start_date=transition.date,
            is_current=True,
            description=transition.reason or f"{transition.get_transition_type_display()}"
        )

        logger.info(f"Updated position history for employee {transition.employee_id}")

