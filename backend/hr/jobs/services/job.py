import logging
from typing import List, Optional, Dict
from uuid import UUID
from django.db import transaction
from django.db.models import QuerySet
from hr.jobs.models import (
    JobFamily, 
    Position, 
    PositionSeniority, 
    SeniorityLevel
)
from hr.jobs.enums import PositionLevel
from hr.jobs.services.cache import JobsCacheService
from safedelete import HARD_DELETE


logger = logging.getLogger(__name__)


class JobService:
    """ Manages the corporate job repository, position levels, and logical career paths. """

    @transaction.atomic
    def create_position_with_seniority_levels(
        self, 
        name: str, 
        family_name: str, 
        org_unit_id: Optional[UUID] = None,
        description: Optional[str] = None,
        seniority_levels: Optional[List[Dict[str, any]]] = None,
        requirements: Optional[List[str]] = None,
        skills: Optional[List[dict]] = None
    ) -> Position:
        """ Defines a new position with multiple seniority levels. """
        family, created = JobFamily.objects.get_or_create(name=family_name)
        if created:
            logger.info(f"New Job Family registered: {family.name}")

        # Create the position
        position = Position.objects.create(
            job_family=family,
            name=name,
            description=description or '',
            org_unit_id=org_unit_id,
            requirements=requirements or [],
            skills=skills or []
        )
        
        # Create seniority levels if provided
        if seniority_levels:
            for level_data in seniority_levels:
                try:
                    seniority_level = SeniorityLevel.objects.get(level=level_data['seniority_level'])
                    PositionSeniority.objects.create(
                        position=position,
                        seniority_level=seniority_level,
                        salary_min=level_data['salary_min'],
                        salary_max=level_data['salary_max'],
                        rank=level_data.get('rank', 1),
                        next_level_id=level_data.get('next_level_id'),
                        is_active=level_data.get('is_active', True)
                    )
                except SeniorityLevel.DoesNotExist:
                    logger.warning(f"Seniority level '{level_data['seniority_level']}' not found for position '{name}'")
        
        logger.info(f"Created position '{name}' with {len(seniority_levels or [])} seniority levels")
        return position
        
    def get_career_path(self, job_family_id: UUID) -> List[Position]:
        """ Retrieves the logical sequence of roles within a job family. """
        ordered_levels = PositionLevel.values
        positions = Position.objects.filter(job_family_id=job_family_id)
        
        return sorted(
            positions, 
            key=lambda x: ordered_levels.index(x.level) if x.level in ordered_levels else 99
        )

    def get_positions_by_seniority_level(self, level: str) -> QuerySet[Position]:
        """ Lists all company roles at a specific seniority level. """
        return Position.objects.filter(
            seniority_levels__seniority_level__level=level
        ).select_related('job_family').distinct()

    def get_family_structure(self) -> Dict[str, List[str]]:
        """ Provides a mapping of job families to their available roles. """
        families = JobFamily.objects.prefetch_related('positions').all()
        return {
            family.name: [p.name for p in family.positions.all()]
            for family in families
        }

    def get_seniority_levels(self) -> List[Dict[str, any]]:
        """ Returns all seniority levels with rank and requirements from database. """
        
        levels = SeniorityLevel.objects.filter(is_active=True).order_by('rank')
        
        # Si pas encore initialisé, créer les valeurs par défaut
        if not levels.exists():
            self.initialize_default_seniority_levels()
            levels = SeniorityLevel.objects.filter(is_active=True).order_by('rank')
        
        return [
            {
                "id": level.id,
                "level": level.level,
                "rank": level.rank,
                "label": level.label,
                "requirements": level.requirements,
                "is_active": level.is_active
            }
            for level in levels
        ]
    
    def initialize_default_seniority_levels(self) -> List[Dict[str, any]]:
        """ 
        Initialize default seniority levels in database if empty.
        Returns the created/existing levels with their IDs.
        """        
        defaults = self._get_default_seniority_levels()
        result_levels = []
        
        for data in defaults:
            level_def, created = SeniorityLevel.objects.get_or_create(
                level=data['level'],
                defaults={
                    'rank': data['rank'],
                    'label': data['label'],
                    'requirements': data['requirements'],
                    'is_active': True
                }
            )
            result_levels.append({
                'id': level_def.id,
                'level': level_def.level,
                'rank': level_def.rank,
                'label': level_def.label,
                'requirements': level_def.requirements,
                'is_active': level_def.is_active
            })
            if created:
                logger.info(f"Created seniority level: {level_def.level}")
        
        return result_levels
    
    def create_seniority_level(self, data: Dict[str, any]) -> Dict[str, any]:
        """
        Create a new seniority level definition.
        Raises exception if level already exists.
        Returns the created level with its ID.
        """
        
        # Check if level already exists
        if SeniorityLevel.objects.filter(level=data['level']).exists():
            raise ValueError(f"Seniority level '{data['level']}' already exists")
        
        # Create new level
        level_def = SeniorityLevel.objects.create(
            level=data['level'],
            label=data['label'],
            rank=data['rank'],
            requirements=data.get('requirements', []),
            is_active=data.get('is_active', True)
        )

        # Lier la classe de la grille (si fournie)
        category_id = data.get('professional_category_id')
        if category_id:
            from hr.jobs.models import ProfessionalCategory
            try:
                level_def.professional_category = ProfessionalCategory.objects.get(id=category_id)
                level_def.save(update_fields=['professional_category'])
            except ProfessionalCategory.DoesNotExist:
                raise ValueError(f"Professional category '{category_id}' does not exist")
        
        logger.info(f"Created new seniority level: {level_def.level} (id={level_def.id})")
        
        return {
            'id': level_def.id,
            'level': level_def.level,
            'rank': level_def.rank,
            'label': level_def.label,
            'requirements': level_def.requirements,
            'is_active': level_def.is_active
        }
    
    def update_seniority_level(self, level: str, data: Dict[str, any]) -> Dict[str, any]:
        """
        Update a seniority level definition (label, rank, requirements, is_active).
        Creates the level if it doesn't exist.
        Returns the updated/created level with its ID.
        """

        defn, created = SeniorityLevel.objects.get_or_create(
            level=level,
            defaults={
                'rank': data.get('rank') or PositionLevel.values.index(level) + 1,
                'label': data.get('label') or level,
                'requirements': data.get('requirements') or [],
                'is_active': data.get('is_active', True)
            }
        )
        
        if not created:
            if data.get('label') is not None:
                defn.label = data['label']
            if data.get('rank') is not None:
                defn.rank = data['rank']
            if data.get('requirements') is not None:
                defn.requirements = data['requirements']
            if data.get('is_active') is not None:
                defn.is_active = data['is_active']
            defn.save()
        
        logger.info(f"Seniority level {level} {'created' if created else 'updated'}")
        
        return {
            'id': defn.id,
            'level': defn.level,
            'rank': defn.rank,
            'label': defn.label,
            'requirements': defn.requirements,
            'is_active': defn.is_active
        }
    
    def partial_update_seniority_level(self, level_id: str, data: Dict[str, any]) -> Dict[str, any]:
        """
        Partial update of a seniority level by ID.
        Only updates fields that are provided (not None).
        Returns the updated level.
        Raises DoesNotExist if level not found.
        """
        
        defn = SeniorityLevel.objects.get(id=level_id)
        
        # Only update fields that are explicitly provided (not None)
        if 'label' in data and data['label'] is not None:
            defn.label = data['label']
        if 'rank' in data and data['rank'] is not None:
            defn.rank = data['rank']
        if 'requirements' in data and data['requirements'] is not None:
            defn.requirements = data['requirements']
        if 'is_active' in data and data['is_active'] is not None:
            defn.is_active = data['is_active']
        if 'professional_category_id' in data:
            from hr.jobs.models import ProfessionalCategory
            if data['professional_category_id'] is None:
                defn.professional_category = None
            else:
                try:
                    defn.professional_category = ProfessionalCategory.objects.get(id=data['professional_category_id'])
                except ProfessionalCategory.DoesNotExist:
                    raise ValueError(f"Professional category '{data['professional_category_id']}' does not exist")
        
        defn.save()
        
        logger.info(f"Seniority level {defn.level} (id={level_id}) partially updated")
        
        return {
            'id': defn.id,
            'level': defn.level,
            'rank': defn.rank,
            'label': defn.label,
            'requirements': defn.requirements,
            'is_active': defn.is_active
        }
    
    def delete_seniority_level(self, level_id: str) -> bool:
        """
        Delete a seniority level by its ID (hard delete).
        Returns True if deleted, False if not found.
        """
        
        try:
            level = SeniorityLevel.objects.get(id=level_id)
            level.delete(force_policy=HARD_DELETE)
            logger.info(f"Seniority level {level.level} (id={level_id}) hard deleted")
            return True
        except SeniorityLevel.DoesNotExist:
            logger.warning(f"Seniority level with id={level_id} not found")
            return False
    
    def reset_seniority_levels(self) -> List[Dict[str, any]]:
        """
        Delete all existing seniority levels and reinitialize with defaults.
        WARNING: This will remove any custom configurations!
        """
        
        # Hard delete all existing records (including soft-deleted ones)
        deleted_count, _ = SeniorityLevel.objects.all(force_visibility=True).delete(force_policy=HARD_DELETE)
        logger.warning(f"Hard deleted {deleted_count} existing seniority level definitions")
        
        # Clear cache via le service de cache dédié
        JobsCacheService.clear_seniority_levels_cache()
        
        # Reinitialize with defaults
        return self.initialize_default_seniority_levels()
    
    def _get_default_seniority_levels(self) -> List[Dict[str, any]]:
        """ Default seniority levels for initial setup. """
        return [
            {
                "level": PositionLevel.TRAINEE, 
                "rank": 1, 
                "label": "Stagiaire", 
                "requirements": ["Formation initiale en cours"]
            },
            {
                "level": PositionLevel.APPRENTICE, 
                "rank": 2, 
                "label": "Apprenti", 
                "requirements": ["Apprentissage pratique"]
            },
            {
                "level": PositionLevel.JUNIOR, 
                "rank": 3, 
                "label": "Junior", 
                "requirements": ["Première expérience autonome"]
            },
            {
                "level": PositionLevel.INTERMEDIATE, 
                "rank": 4, 
                "label": "Intermédiaire", 
                "requirements": ["2-5 ans d'expérience", "Maîtrise des outils"]
            },
            {
                "level": PositionLevel.SENIOR, 
                "rank": 5, 
                "label": "Senior", 
                "requirements": ["5+ ans d'expérience", "Expertise avancée", "Mentorat"]
            },
            {
                "level": PositionLevel.LEAD, 
                "rank": 6, 
                "label": "Lead", 
                "requirements": ["Leadership technique", "Guidage d'équipe"]
            },
            {
                "level": PositionLevel.MANAGER, 
                "rank": 7, 
                "label": "Manager", 
                "requirements": ["Gestion équipe", "Responsabilités RH"]
            },
            {
                "level": PositionLevel.DIRECTOR, 
                "rank": 8, 
                "label": "Directeur", 
                "requirements": ["Vision stratégique", "Gestion multi-équipes"]
            },
            {
                "level": PositionLevel.EXECUTIVE, 
                "rank": 9, 
                "label": "Exécutif", 
                "requirements": ["Leadership exécutif", "Décisions stratégiques"]
            }
        ]
    
    def update_position_seniority_levels(self, position_id: UUID, seniority_levels: List[Dict[str, any]]) -> None:
        """ Updates all seniority levels for a position (replace operation). """
        
        position = Position.objects.get(id=position_id)
        
        with transaction.atomic():
            # First, force delete all existing seniority levels for this position
            PositionSeniority.objects.filter(position_id=position_id).delete()
            
            # Then create new seniority levels
            for level_data in seniority_levels:
                try:
                    seniority_level = SeniorityLevel.objects.get(level=level_data['seniority_level'])
                    PositionSeniority.objects.create(
                        position=position,
                        seniority_level=seniority_level,
                        salary_min=level_data['salary_min'],
                        salary_max=level_data['salary_max'],
                        rank=level_data.get('rank', 1),
                        next_level_id=level_data.get('next_level_id'),
                        is_active=level_data.get('is_active', True)
                    )
                except SeniorityLevel.DoesNotExist:
                    logger.warning(f"Seniority level '{level_data['seniority_level']}' not found for position '{position.name}'")
        
        logger.info(f"Updated {len(seniority_levels)} seniority levels for position {position_id}")
    
    def add_position_seniority_level(self, position_id: UUID, level_data: Dict[str, any]) -> PositionSeniority:
        """ Adds a single seniority level to a position. """
        position = Position.objects.get(id=position_id)
        
        try:
            seniority_level = SeniorityLevel.objects.get(level=level_data['seniority_level'])
        except SeniorityLevel.DoesNotExist:
            raise ValueError(f"Seniority level '{level_data['seniority_level']}' not found")
        
        return PositionSeniority.objects.create(
            position=position,
            seniority_level=seniority_level,
            salary_min=level_data['salary_min'],
            salary_max=level_data['salary_max'],
            rank=level_data.get('rank', 1),
            next_level_id=level_data.get('next_level_id'),
            is_active=level_data.get('is_active', True)
        )
    
    def update_position_seniority_level(self, position_id: UUID, seniority_id: UUID, level_data: Dict[str, any]) -> PositionSeniority:
        """ Updates a specific seniority level for a position. """
        position_seniority = PositionSeniority.objects.get(id=seniority_id, position_id=position_id)
        
        if 'seniority_level' in level_data:
            seniority_level = SeniorityLevel.objects.get(level=level_data['seniority_level'])
            position_seniority.seniority_level = seniority_level
        
        if 'salary_min' in level_data:
            position_seniority.salary_min = level_data['salary_min']
        if 'salary_max' in level_data:
            position_seniority.salary_max = level_data['salary_max']
        if 'rank' in level_data:
            position_seniority.rank = level_data['rank']
        if 'next_level_id' in level_data:
            position_seniority.next_level_id = level_data['next_level_id']
        if 'is_active' in level_data:
            position_seniority.is_active = level_data['is_active']
        
        position_seniority.save()
        return position_seniority
    
    def delete_position_seniority_level(self, position_id: UUID, seniority_id: UUID) -> bool:
        """ Removes a seniority level from a position. """
        try:
            position_seniority = PositionSeniority.objects.get(id=seniority_id, position_id=position_id)
            position_seniority.delete()
            return True
        except PositionSeniority.DoesNotExist:
            return False
    
    def get_position_career_progression(self, position_id: UUID) -> List[PositionSeniority]:
        """ Returns the career progression structure for a position. """
        return list(PositionSeniority.objects
                   .filter(position_id=position_id, is_active=True)
                   .select_related('seniority_level')
                   .order_by('rank'))

