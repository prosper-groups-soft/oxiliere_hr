import logging
from typing import List, Optional
from uuid   import UUID
from django.db    import transaction
from django.utils import timezone

from hr.jobs.models import Vacancy, Position
from hr.jobs.enums  import VacancyPriority, VacancyStatus


logger = logging.getLogger(__name__)


class VacancyService:
    """ Manages job vacancies - open positions that need to be filled. """

    def list_vacancies(
        self,
        filters=None,
    ) -> List[Vacancy]:
        """
        Retrieves paginated list of vacancies with optional filtering.
        Returns (queryset_page, total_count).
        """
        queryset = Vacancy.objects.select_related('position', 'position__job_family', 'position__org_unit').all()

        # Apply filters if provided
        if filters:
            return filters.filter(queryset)
        return list(queryset)

    def get_vacancy(self, vacancy_id: UUID) -> Optional[Vacancy]:
        """ Retrieves a single vacancy by ID with related data. """
        try:
            return Vacancy.objects.select_related(
                'position', 'position__job_family', 'position__org_unit'
            ).get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            return None

    @transaction.atomic
    def create_vacancy(
        self,
        position_id: UUID,
        priority: str = 'MEDIUM',
        status: str = 'OPEN',
        opened_date: Optional[str] = None,
        target_date: Optional[str] = None,
        reason: Optional[str] = None,
        created_by_id: Optional[UUID] = None
    ) -> Vacancy:
        """ Creates a new vacancy record. """
        # Validate position exists
        try:
            position = Position.objects.get(id=position_id)
        except Position.DoesNotExist:
            raise ValueError(f"Position {position_id} not found")

        # Validate priority
        if priority not in [p.value for p in VacancyPriority]:
            raise ValueError(f"Invalid priority: {priority}")

        # Validate status
        if status not in [s.value for s in VacancyStatus]:
            raise ValueError(f"Invalid status: {status}")

        # Parse dates
        from datetime import datetime as dt
        parsed_opened = dt.strptime(opened_date, '%Y-%m-%d').date() if opened_date else timezone.now().date()
        parsed_target = dt.strptime(target_date, '%Y-%m-%d').date() if target_date else None

        # Create vacancy
        vacancy = Vacancy.objects.create(
            position=position,
            priority=priority,
            status=status,
            opened_date=parsed_opened,
            target_date=parsed_target,
            reason=reason,
            created_by_id=created_by_id
        )

        logger.info(f"Created vacancy for position {position_id} with priority {priority}")
        return vacancy

    @transaction.atomic
    def update_vacancy(
        self,
        vacancy_id: UUID,
        position_id: Optional[UUID] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        opened_date: Optional[str] = None,
        target_date: Optional[str] = None,
        reason: Optional[str] = None,
        filled_date: Optional[str] = None
    ) -> Vacancy:
        """ Updates an existing vacancy. """
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            raise ValueError(f"Vacancy {vacancy_id} not found")

        # Update fields if provided
        if position_id is not None:
            try:
                vacancy.position = Position.objects.get(id=position_id)
            except Position.DoesNotExist:
                raise ValueError(f"Position {position_id} not found")

        if priority is not None:
            if priority not in [p.value for p in VacancyPriority]:
                raise ValueError(f"Invalid priority: {priority}")
            vacancy.priority = priority

        if status is not None:
            if status not in [s.value for s in VacancyStatus]:
                raise ValueError(f"Invalid status: {status}")
            vacancy.status = status

        from datetime import datetime as dt

        if opened_date is not None:
            vacancy.opened_date = dt.strptime(opened_date, '%Y-%m-%d').date()

        if target_date is not None:
            vacancy.target_date = dt.strptime(target_date, '%Y-%m-%d').date() if target_date else None

        if reason is not None:
            vacancy.reason = reason

        if filled_date is not None:
            vacancy.filled_date = dt.strptime(filled_date, '%Y-%m-%d').date() if filled_date else None

        vacancy.save()
        logger.info(f"Updated vacancy {vacancy_id}")
        return vacancy

    @transaction.atomic
    def close_vacancy(self, vacancy_id: UUID, transition_id: Optional[UUID] = None) -> Vacancy:
        """ Marks a vacancy as filled. """
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            raise ValueError(f"Vacancy {vacancy_id} not found")

        vacancy.status = VacancyStatus.FILLED.value
        vacancy.filled_date = timezone.now().date()

        if transition_id:
            from hr.jobs.models import EmployeeTransition
            try:
                vacancy.filled_by_transition = EmployeeTransition.objects.get(id=transition_id)
            except EmployeeTransition.DoesNotExist:
                logger.warning(f"Transition {transition_id} not found when closing vacancy {vacancy_id}")

        vacancy.save()
        logger.info(f"Closed vacancy {vacancy_id}")
        return vacancy

    @transaction.atomic
    def delete_vacancy(self, vacancy_id: UUID) -> bool:
        """ Soft deletes a vacancy. """
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)
            vacancy.delete()
            logger.info(f"Deleted vacancy {vacancy_id}")
            return True
        except Vacancy.DoesNotExist:
            return False
