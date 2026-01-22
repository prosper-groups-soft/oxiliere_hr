import logging
from typing import List, Optional, Dict
from uuid import UUID
from django.db import transaction
from django.db.models import QuerySet
from hr.jobs.models import JobFamily, Position
from hr.jobs.enums import PositionLevel


logger = logging.getLogger(__name__)


class JobService:
    """
    Service to manage the corporate job repository, including families, 
    positions, and career progression logic.
    """

    @transaction.atomic
    def create_position_with_family(
        self, 
        name: str, 
        family_name: str, 
        level: PositionLevel, 
        description: Optional[str] = None
    ) -> Position:
        """
        Ensures a JobFamily exists and creates a Position within it.
        Prevents duplicates by checking unique constraints.
        """
        # Get or create the family (normalization is handled by the model's clean method)
        family, created = JobFamily.objects.get_or_create(name=family_name)
        if created:
            logger.info(f"New JobFamily created: {family.name}")

        # Create the position; unique_together constraint ensures data integrity
        position, p_created = Position.objects.get_or_create(
            job_family=family,
            name=name,
            level=level,
            defaults={'description': description}
        )

        if not p_created:
            logger.warning(f"Position '{name}' already exists in {family.name} at level {level}")
        
        return position
        
    def get_career_path(self, job_family_id: UUID) -> List[Position]:
        """
        Returns the progression of positions within a family, 
        sorted by the hierarchical value defined in PositionLevel.
        """
        # Get defined values from TextChoices for sorting (e.g., ['TRAINEE', 'JUNIOR', ...])
        ordered_levels = PositionLevel.values
        
        positions = Position.objects.filter(job_family_id=job_family_id)
        
        # Sort positions based on their index in the Enum to guarantee logical career progression
        return sorted(
            positions, 
            key=lambda x: ordered_levels.index(x.level) if x.level in ordered_levels else 99
        )

    def get_positions_by_level(self, level: PositionLevel) -> QuerySet[Position]:
        """
        Returns all positions across the company at a specific seniority level.
        """
        return Position.objects.filter(level=level).select_related('job_family')

    def get_family_structure(self) -> Dict[str, List[str]]:
        """
        Returns a dictionary mapping each JobFamily to its available position titles.
        """
        families = JobFamily.objects.prefetch_related('positions').all()
        return {
            family.name: [p.name for p in family.positions.all()]
            for family in families
        }

