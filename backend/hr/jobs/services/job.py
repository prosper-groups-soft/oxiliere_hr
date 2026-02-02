import logging
from typing import List, Optional, Dict
from uuid import UUID
from django.db import transaction
from django.db.models import QuerySet
from hr.jobs.models import JobFamily, Position
from hr.jobs.enums import PositionLevel


logger = logging.getLogger(__name__)


class JobService:
    """ Manages the corporate job repository, position levels, and logical career paths. """

    @transaction.atomic
    def create_position_with_family(
        self, 
        name: str, 
        family_name: str, 
        level: PositionLevel, 
        description: Optional[str] = None
    ) -> Position:
        """ Defines a new position and ensures its associated job family exists. """
        family, created = JobFamily.objects.get_or_create(name=family_name)
        if created:
            logger.info(f"New Job Family registered: {family.name}")

        position, p_created = Position.objects.get_or_create(
            job_family=family,
            name=name,
            level=level,
            defaults={'description': description}
        )

        if not p_created:
            logger.warning(f"Position '{name}' already exists in {family.name}")
        
        return position
        
    def get_career_path(self, job_family_id: UUID) -> List[Position]:
        """ Retrieves the logical sequence of roles within a job family. """
        ordered_levels = PositionLevel.values
        positions = Position.objects.filter(job_family_id=job_family_id)
        
        return sorted(
            positions, 
            key=lambda x: ordered_levels.index(x.level) if x.level in ordered_levels else 99
        )

    def get_positions_by_level(self, level: PositionLevel) -> QuerySet[Position]:
        """ Lists all company roles at a specific seniority level. """
        return Position.objects.filter(level=level).select_related('job_family')

    def get_family_structure(self) -> Dict[str, List[str]]:
        """ Provides a mapping of job families to their available roles. """
        families = JobFamily.objects.prefetch_related('positions').all()
        return {
            family.name: [p.name for p in family.positions.all()]
            for family in families
        }

