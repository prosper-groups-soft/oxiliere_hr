import logging
from injector import inject
from uuid   import UUID
from typing import List
from ninja  import Query

from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_delete,
    ControllerBase,
)
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra,
    PaginatedResponseSchema
)
from oxutils.permissions.perms import ScopePermission

# Schemas
from hr.jobs.schemas import (
    TransitionOut,
    TransitionCreateIn,
    TransitionUpdateIn,
    TransitionFilter
)

# Services
from hr.jobs.services.transition import TransitionService


logger = logging.getLogger(__name__)


@api_controller('/transitions', tags=['Employee Transitions'])
class TransitionController(ControllerBase):
    """ Manages employee career transitions (promotions, transfers, hires, offboards). """

    @inject
    def __init__(self, transition_service: TransitionService):
        self.transition_service = transition_service

    @http_get('', response=PaginatedResponseSchema[TransitionOut], permissions=[ScopePermission('jobs:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_transitions(
        self,
        filters: TransitionFilter = Query(...)  # type: ignore[reportCallIssue]
    ):
        """ Retrieves all employee tra        "reportCallIssue": falsensitions with optional filtering and search. """
        logger.info(f"Listing transitions with filters: {filters}")
        return self.transition_service.list_transitions(filters)

    @http_get('/{transition_id}', response=TransitionOut, permissions=[ScopePermission('jobs:r')])
    def get_transition(self, transition_id: UUID):
        """ Retrieves a specific transition by ID. """
        transition = self.transition_service.get_transition(transition_id)
        if not transition:
            return self.create_response({"detail": "Transition not found"}, status_code=404)
        return transition

    @http_get('/employee/{employee_id}', response=List[TransitionOut], permissions=[ScopePermission('jobs:r')])
    def get_employee_transitions(self, employee_id: UUID):
        """ Retrieves all transitions for a specific employee. """
        logger.info(f"Getting transitions for employee {employee_id}")
        return self.transition_service.get_employee_transitions(employee_id)

    @http_post('', response={201: TransitionOut}, permissions=[ScopePermission('jobs:w')])
    def create_transition(self, data: TransitionCreateIn):
        """ Creates a new employee transition/movement. """
        logger.info(f"Creating {data.transition_type} transition for employee {data.employee_id}")

        try:
            transition = self.transition_service.create_transition(
                employee_id=data.employee_id,
                transition_type=data.transition_type,
                from_position_id=data.from_position_id,
                from_seniority_level_id=data.from_seniority_level_id,
                to_position_id=data.to_position_id,
                to_seniority_level_id=data.to_seniority_level_id,
                date=data.date,
                reason=data.reason
            )
            return 201, transition
        except ValueError as e:
            logger.error(f"Failed to create transition: {str(e)}")
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.error(f"Unexpected error creating transition: {str(e)}")
            return self.create_response({"detail": "Failed to create transition"}, status_code=500)

    @http_patch('/{transition_id}', response=TransitionOut, permissions=[ScopePermission('jobs:u')])
    def update_transition(self, transition_id: UUID, data: TransitionUpdateIn):
        """ Updates an existing transition. """
        logger.info(f"Updating transition {transition_id}")

        try:
            transition = self.transition_service.update_transition(
                transition_id=transition_id,
                transition_type=data.transition_type,
                from_position_id=data.from_position_id,
                from_seniority_level_id=data.from_seniority_level_id,
                to_position_id=data.to_position_id,
                to_seniority_level_id=data.to_seniority_level_id,
                date=data.date,
                reason=data.reason
            )
            return transition
        except ValueError as e:
            logger.error(f"Failed to update transition: {str(e)}")
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.error(f"Unexpected error updating transition: {str(e)}")
            return self.create_response({"detail": "Failed to update transition"}, status_code=500)

    @http_delete('/{transition_id}', response={204: None}, permissions=[ScopePermission('jobs:d')])
    def delete_transition(self, transition_id: UUID):
        """ Deletes a transition record. """
        logger.info(f"Deleting transition {transition_id}")

        success = self.transition_service.delete_transition(transition_id)
        if not success:
            return self.create_response({"detail": "Transition not found"}, status_code=404)

        return 204, None

