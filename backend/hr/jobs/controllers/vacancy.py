import logging
from uuid   import UUID
from typing import Optional
from ninja.errors import HttpError
from ninja       import Query
from injector    import inject
from ninja_extra import (
    api_controller, 
    http_get, 
    http_post, 
    http_patch, 
    http_delete, 
    ControllerBase
)
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra,
    PaginatedResponseSchema
)
from oxutils.permissions.perms import ScopePermission

from hr.jobs.models  import Vacancy
from hr.jobs.schemas import (
    VacancyOut,
    VacancyCreateIn,
    VacancyUpdateIn,
    VacancyFilter
)
from hr.jobs.services.vacancy import VacancyService


logger = logging.getLogger(__name__)


@api_controller('/vacancies', tags=['Vacancies'])
class VacancyController(ControllerBase):
    """ Manages job vacancies - open positions that need to be filled. """

    @inject
    def __init__(self, vacancy_service: VacancyService):
        self.vacancy_service = vacancy_service

    @http_get('', response=PaginatedResponseSchema[VacancyOut], permissions=[ScopePermission('jobs:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_vacancies(
        self,
        filters: VacancyFilter = Query(...)
    ):
        """ 
        Retrieves paginated list of vacancies with optional filtering.
        Supports search by position name and filtering by priority/status.
        """
        return self.vacancy_service.list_vacancies(filters=filters)

    @http_get('/{vacancy_id}', response=VacancyOut, permissions=[ScopePermission('jobs:r')])
    def get_vacancy(self, vacancy_id: UUID):
        """ Retrieves a single vacancy by ID. """
        vacancy = self.vacancy_service.get_vacancy(vacancy_id)
        if not vacancy:
            raise HttpError(404, "Vacancy not found")
        return vacancy

    @http_post('', response={201: VacancyOut}, permissions=[ScopePermission('jobs:w')])
    def create_vacancy(self, data: VacancyCreateIn):
        """ Creates a new vacancy. """
        try:
            # Get current user ID from request context if available
            created_by_id = None
            if hasattr(self.context, 'request') and hasattr(self.context.request, 'user'):
                user = self.context.request.user
                if hasattr(user, 'id'):
                    created_by_id = user.id

            vacancy = self.vacancy_service.create_vacancy(
                position_id=data.position_id,
                priority=data.priority,
                status=data.status,
                opened_date=data.opened_date.isoformat() if data.opened_date else None,
                target_date=data.target_date.isoformat() if data.target_date else None,
                reason=data.reason,
                created_by_id=created_by_id
            )
            return 201, vacancy
        except ValueError as e:
            raise HttpError(400, str(e))
        except Exception as e:
            logger.error(f"Error creating vacancy: {e}")
            raise HttpError(500, "Failed to create vacancy")

    @http_patch('/{vacancy_id}', response=VacancyOut, permissions=[ScopePermission('jobs:u')])
    def update_vacancy(self, vacancy_id: UUID, data: VacancyUpdateIn):
        """ Updates an existing vacancy (partial update). """
        try:
            vacancy = self.vacancy_service.update_vacancy(
                vacancy_id=vacancy_id,
                position_id=data.position_id,
                priority=data.priority,
                status=data.status,
                opened_date=data.opened_date.isoformat() if data.opened_date else None,
                target_date=data.target_date.isoformat() if data.target_date else None,
                reason=data.reason,
                filled_date=data.filled_date.isoformat() if data.filled_date else None
            )
            return vacancy
        except ValueError as e:
            raise HttpError(400, str(e))
        except Exception as e:
            logger.error(f"Error updating vacancy {vacancy_id}: {e}")
            raise HttpError(500, "Failed to update vacancy")

    @http_delete('/{vacancy_id}', response={204: None}, permissions=[ScopePermission('jobs:d')])
    def delete_vacancy(self, vacancy_id: UUID):
        """ Soft deletes a vacancy. """
        success = self.vacancy_service.delete_vacancy(vacancy_id)
        if not success:
            raise HttpError(404, "Vacancy not found")
        return 204, None

    @http_post('/{vacancy_id}/close', response=VacancyOut, permissions=[ScopePermission('jobs:u')])
    def close_vacancy(self, vacancy_id: UUID, transition_id: Optional[UUID] = None):
        """ Marks a vacancy as filled. """
        try:
            vacancy = self.vacancy_service.close_vacancy(vacancy_id, transition_id)
            return vacancy
        except ValueError as e:
            raise HttpError(404, str(e))
        except Exception as e:
            logger.error(f"Error closing vacancy {vacancy_id}: {e}")
            raise HttpError(500, "Failed to close vacancy")
