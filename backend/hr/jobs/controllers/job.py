import logging
from injector import inject
from uuid     import UUID
from typing   import List, Dict
from ninja.errors     import HttpError
from ninja_extra      import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_delete,
    ControllerBase,
)
from oxutils.permissions.perms import ScopePermission

# Schemas
from hr.jobs.schemas import (
    JobFamilyOut,
    JobFamilyCreateIn,
    JobFamilyUpdateIn,
    PositionOut,
    PositionCreateIn,
    PositionUpdateIn,
    PositionSeniorityOut,
    PositionSeniorityCreateIn,
    PositionSeniorityUpdateIn,
    SeniorityLevelOut,
    SeniorityLevelUpdateIn,
    SeniorityLevelCreateIn,
    ProfessionalCategoryOut,
    ProfessionalCategoryUpdateIn,
    ProfessionalCategoryCreateIn
)
from hr.jobs.models import JobFamily, Position, PositionSeniority, SeniorityLevel, ProfessionalCategory
from django.shortcuts import get_object_or_404

# Services
from hr.jobs.services import JobService

# Cache integration
from hr.services.cache_helpers import cache_api_response
from hr.jobs.services.cache import JobsCacheService


logger = logging.getLogger(__name__)


@api_controller('/jobs', tags=['Job Repository'])
class JobController(ControllerBase):
    """ Manages the corporate job catalog, including families and position levels. """

    @inject
    def __init__(self, job_service: JobService):
        self.job_service = job_service

    @http_get('/families', response=List[JobFamilyOut], permissions=[ScopePermission('jobs:r')])
    @cache_api_response(timeout=60*60*24, key_prefix="job_families_list", user_specific=False)
    def list_job_families(self):
        """ Retrieves all registered job families (no pagination - small dataset). """
        return list(JobFamily.objects.all().order_by('name'))

    @http_post('/families', response={201: JobFamilyOut}, permissions=[ScopePermission('jobs:w')])
    def create_job_family(self, data: JobFamilyCreateIn):
        """ Creates a new job family. """
        logger.info(f"Creating job family '{data.name}'")
        family = JobFamily.objects.create(
            name=data.name,
            description=data.description
        )
        # Clear both specific and list caches
        JobsCacheService.clear_job_family_cache(family.id)
        JobsCacheService.clear_job_families_list_cache()
        return 201, family

    @http_patch('/families/{family_id}', response=JobFamilyOut, permissions=[ScopePermission('jobs:u')])
    def update_job_family(self, family_id: UUID, data: JobFamilyUpdateIn):
        """ Updates an existing job family. """
        family = get_object_or_404(JobFamily, id=family_id)
        
        if data.name is not None:
            family.name = data.name
        if data.description is not None:
            family.description = data.description
        
        family.save()
        JobsCacheService.clear_job_family_cache(family_id)
        JobsCacheService.clear_job_families_list_cache()
        logger.info(f"Job family {family_id} updated")
        return family

    @http_delete('/families/{family_id}', response={204: None}, permissions=[ScopePermission('jobs:d')])
    def delete_job_family(self, family_id: UUID):
        """ Deletes a job family (only if no positions attached). """
        family = get_object_or_404(JobFamily, id=family_id)
        
        # Check if family has positions
        if family.positions.exists():  # type: ignore[attr-defined]
            raise HttpError(400, f"Cannot delete family '{family.name}' - it has {family.positions.count()} position(s) attached. Delete positions first.") 
        
        family.delete()
        JobsCacheService.clear_job_family_cache(family_id)
        JobsCacheService.clear_job_families_list_cache()
        logger.info(f"Job family {family_id} deleted")
        return 204, None

    @http_post('/positions', response={201: PositionOut}, permissions=[ScopePermission('jobs:w')])
    def create_position(self, data: PositionCreateIn):
        """ Defines a new position within the corporate job repository. """
        logger.info(f"Creating position '{data.name}' with {len(data.seniority_levels)} seniority levels")
        
        # Convert Pydantic models to dicts for service method
        seniority_levels_dict = [level.model_dump() for level in data.seniority_levels] if data.seniority_levels else []
        
        position = self.job_service.create_position_with_seniority_levels(
            name=data.name,
            family_name=data.family_name,
            org_unit_id=data.org_unit_id,
            description=data.description,
            seniority_levels=seniority_levels_dict,
            requirements=data.requirements,
            skills=data.skills
        )
        
        # Invalidate position caches
        JobsCacheService.clear_position_cache(position.id, position.job_family_id)
        
        return 201, position

    @http_get('/families/{family_id}/career-path', response=List[PositionOut])
    def get_family_career_path(self, family_id: UUID):
        """
        Returns the logical progression of roles within a specific family.
        Ordered by seniority (Trainee -> ... -> Executive).
        """
        return self.job_service.get_career_path(family_id)

    @http_get('/positions/level/{level}', response=List[PositionOut], permissions=[ScopePermission('jobs:r')])
    def list_positions_by_seniority(self, level: str):
        """
        Filters all company positions by a specific seniority level.
        Example: "Show me all 'Senior' roles across all organizational units."
        """
        return self.job_service.get_positions_by_seniority_level(level)

    @http_get('/catalog', response=Dict[str, List[str]])
    def get_full_catalog(self):
        """
        Returns a simplified map of the entire job catalog:
        { "Engineering": ["Junior Dev", "Senior Dev"], "HR": ["Recruiter"] }
        """
        return self.job_service.get_family_structure()

    @http_get('/seniority-levels', response=List[SeniorityLevelOut], permissions=[ScopePermission('jobs:r')])
    @cache_api_response(timeout=60*60*24, key_prefix="seniority_levels", user_specific=False)
    def list_seniority_levels(self):
        """ Returns all defined seniority levels with rank and requirements. """
        return self.job_service.get_seniority_levels()

    @http_post('/seniority-levels', response={201: SeniorityLevelOut}, permissions=[ScopePermission('jobs:w')])
    def create_seniority_level(self, data: SeniorityLevelCreateIn):
        """ Creates a new seniority level definition. """
        
        # Use service method to create
        result = self.job_service.create_seniority_level(data={
            'level': data.level,
            'label': data.label,
            'rank': data.rank,
            'requirements': data.requirements,
            'is_active': data.is_active
        })
        
        # Invalidate cache
        JobsCacheService.clear_seniority_levels_cache()
        
        logger.info(f"Seniority level {data.level} created")
        return 201, result

    @http_post('/seniority-levels/reset', response=List[SeniorityLevelOut], permissions=[ScopePermission('jobs:w')])
    def reset_seniority_levels(self):
        """ 
        Reset all seniority levels to defaults.
        WARNING: This deletes all existing custom configurations!
        """
        
        result = self.job_service.reset_seniority_levels()
        
        # Clear cache via le service dédié
        JobsCacheService.clear_seniority_levels_cache()
        
        logger.warning("Seniority levels have been reset to defaults by admin action")
        return result

    @http_post('/seniority-levels/initialize', response=List[SeniorityLevelOut], permissions=[ScopePermission('jobs:a')])
    def initialize_seniority_levels(self):
        """
        Initialize default seniority levels if none exist.
        Safe to call multiple times - won't overwrite existing levels.
        """
        result = self.job_service.initialize_default_seniority_levels()
        logger.info("Default seniority levels initialized")
        return result

    @http_patch('/seniority-levels/{level_id}', response=SeniorityLevelOut, permissions=[ScopePermission('jobs:u')])
    def update_seniority_level(self, level_id: UUID, data: SeniorityLevelUpdateIn):
        """ Updates a seniority level definition by ID (partial update). """
        
        # Get existing level first to find the level enum value
        try:
            SeniorityLevel.objects.get(id=level_id)
        except SeniorityLevel.DoesNotExist:
            raise HttpError(404, "Seniority level not found")
        
        # Use service method with the level enum value
        result = self.job_service.partial_update_seniority_level(
            level_id=str(level_id),
            data={
                'label': data.label,
                'rank': data.rank,
                'requirements': data.requirements,
                'is_active': data.is_active
            }
        )
        
        # Invalidate cache
        JobsCacheService.clear_seniority_levels_cache()
        
        return result

    @http_delete('/seniority-levels/{level_id}', permissions=[ScopePermission('jobs:d')])
    def delete_seniority_level(self, level_id: UUID):
        """ Deletes a seniority level by ID (soft delete). """
        
        success = self.job_service.delete_seniority_level(str(level_id))
        
        if not success:
            from ninja.errors import HttpError
            raise HttpError(404, "Seniority level not found")
        
        # Invalidate cache
        JobsCacheService.clear_seniority_levels_cache()
        
        return {"success": True, "message": "Seniority level deleted"}

    @http_get('/positions', response=List[PositionOut], permissions=[ScopePermission('jobs:r')])
    def list_positions(self):
        """ Lists all positions in the job catalog (no pagination - small dataset). """
        return list(Position.objects
                   .select_related('job_family', 'org_unit')
                   .prefetch_related('seniority_levels__seniority_level')
                   .all())

    @http_patch('/positions/{position_id}', response=PositionOut, permissions=[ScopePermission('jobs:u')])
    def update_position(self, position_id: UUID, data: PositionUpdateIn):
        """ Updates an existing position (partial update). """
        position = get_object_or_404(Position, id=position_id)
        
        if data.name is not None:
            position.name = data.name
        if data.family_name is not None:
            family, _ = JobFamily.objects.get_or_create(name=data.family_name)
            position.job_family = family
        if data.org_unit_id is not None:
            position.org_unit_id = data.org_unit_id 
        if data.description is not None:
            position.description = data.description
        if data.seniority_levels is not None:
            # Update seniority levels
            seniority_levels_dict = [level.model_dump() for level in data.seniority_levels]
            self.job_service.update_position_seniority_levels(position_id, seniority_levels_dict)
        if data.requirements is not None:
            position.requirements = data.requirements
        if data.skills is not None:
            position.skills = data.skills
        
        position.save()
        
        # Invalidate position caches
        JobsCacheService.clear_position_cache(position_id, position.job_family_id)  # type: ignore[attr-defined]
        
        logger.info(f"Position {position_id} updated")
        # Return refreshed position with seniority levels
        return Position.objects.select_related('job_family', 'org_unit').prefetch_related('seniority_levels__seniority_level').get(id=position_id)

    @http_delete('/positions/{position_id}', response={204: None}, permissions=[ScopePermission('jobs:d')])
    def delete_position(self, position_id: UUID):
        """ Removes a position from the catalog. """
        position = get_object_or_404(Position, id=position_id)
        family_id = position.job_family_id
        
        position.delete()
        
        # Invalidate position caches
        JobsCacheService.clear_position_cache(position_id, family_id)
        
        logger.info(f"Position {position_id} deleted")
        return 204, None

    # Position Seniority endpoints
    @http_get('/positions/{position_id}/seniority-levels', response=List[PositionSeniorityOut], permissions=[ScopePermission('jobs:r')])
    def list_position_seniority_levels(self, position_id: UUID):
        """ Returns all seniority levels available for a specific position. """
        position = get_object_or_404(Position, id=position_id)
        return list(position.seniority_levels.select_related('seniority_level').order_by('rank'))

    @http_post('/positions/{position_id}/seniority-levels', response={201: PositionSeniorityOut}, permissions=[ScopePermission('jobs:w')])
    def add_position_seniority_level(self, position_id: UUID, data: PositionSeniorityCreateIn):
        """ Adds a new seniority level to a position. """
        try:
            position_seniority = self.job_service.add_position_seniority_level(
                position_id, {
                    'seniority_level': data.seniority_level,
                    'salary_min': data.salary_min,
                    'salary_max': data.salary_max,
                    'rank': data.rank,
                    'next_level_id': data.next_level_id,
                    'is_active': data.is_active
                }
            )
            
            # Invalidate caches
            JobsCacheService.clear_position_cache(position_id, position_seniority.position.job_family_id)
            
            logger.info(f"Added seniority level {data.seniority_level} to position {position_id}")
            return 201, position_seniority
        except ValueError as e:
            raise HttpError(400, str(e))

    @http_patch('/positions/{position_id}/seniority-levels/{seniority_id}', response=PositionSeniorityOut, permissions=[ScopePermission('jobs:u')])
    def update_position_seniority_level(self, position_id: UUID, seniority_id: UUID, data: PositionSeniorityUpdateIn):
        """ Updates a position's seniority level. """
        try:
            position_seniority = self.job_service.update_position_seniority_level(
                position_id, seniority_id, {
                    'seniority_level': data.seniority_level,
                    'salary_min': data.salary_min,
                    'salary_max': data.salary_max,
                    'rank': data.rank,
                    'next_level_id': data.next_level_id,
                    'is_active': data.is_active
                }
            )
            
            # Invalidate caches
            JobsCacheService.clear_position_cache(position_id, position_seniority.position.job_family_id)
            
            logger.info(f"Updated seniority level {seniority_id} for position {position_id}")
            return position_seniority
        except PositionSeniority.DoesNotExist:
            raise HttpError(404, "Position seniority level not found")
        except SeniorityLevel.DoesNotExist:
            raise HttpError(400, "Seniority level not found")

    @http_delete('/positions/{position_id}/seniority-levels/{seniority_id}', response={204: None}, permissions=[ScopePermission('jobs:d')])
    def delete_position_seniority_level(self, position_id: UUID, seniority_id: UUID):
        """ Removes a seniority level from a position. """
        success = self.job_service.delete_position_seniority_level(position_id, seniority_id)
        
        if not success:
            raise HttpError(404, "Position seniority level not found")
        
        # Invalidate caches (get position to find family_id)
        position = get_object_or_404(Position, id=position_id)
        JobsCacheService.clear_position_cache(position_id, position.job_family_id)
        
        logger.info(f"Deleted seniority level {seniority_id} from position {position_id}")
        return 204, None

    @http_get('/positions/{position_id}/career-progression', response=List[PositionSeniorityOut], permissions=[ScopePermission('jobs:r')])
    def get_position_career_progression(self, position_id: UUID):
        """ Returns the career progression structure for a position. """
        get_object_or_404(Position, id=position_id)
        return self.job_service.get_position_career_progression(position_id)

    # ===== PROFESSIONAL CATEGORIES (grille légale 7x4) =====

    @http_get('/professional-categories', response=List[ProfessionalCategoryOut], permissions=[ScopePermission('jobs:r')])
    def list_professional_categories(self):
        """ Grille des catégories professionnelles (7 classes x 4 échelons). """
        return list(ProfessionalCategory.objects.all().order_by('classe', 'echelon'))

    @http_post('/professional-categories', response={201: ProfessionalCategoryOut}, permissions=[ScopePermission('jobs:w')])
    def create_professional_category(self, data: ProfessionalCategoryCreateIn):
        """ Ajoute une classe/échelon à la grille. """
        category = ProfessionalCategory.objects.create(**data.model_dump())
        return 201, category

    @http_patch('/professional-categories/{category_id}', response=ProfessionalCategoryOut, permissions=[ScopePermission('jobs:u')])
    def update_professional_category(self, category_id: UUID, data: ProfessionalCategoryUpdateIn):
        """ Modifie une classe/échelon (libellé, application, actif). """
        category = get_object_or_404(ProfessionalCategory, id=category_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        category.save()
        return category

    @http_post('/professional-categories/reset', response={200: dict}, permissions=[ScopePermission('jobs:a')])
    def reset_professional_categories(self):
        """ Recharge la grille légale depuis la fixture (7 classes x 4 échelons). """
        from hr.jobs.services.init import init_professional_categories
        count = init_professional_categories()
        return {"status": "success", "reset_count": count}

