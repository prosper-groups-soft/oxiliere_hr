import logging
from injector import inject
from uuid import UUID
from typing import List

from django.core.exceptions import ValidationError
from ninja import Query
from ninja.pagination import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)
from oxutils.pagination.cursor import CursorPagination

# Schemas
from hr.employees.schemas import (
    EmployeeOut,
    EmployeeFullProfileOut,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeFilterIn,
)

# Services
from hr.employees.services import (
    EmployeeProfileService,
    EmployeeQueryService,
)


logger = logging.getLogger(__name__)


@api_controller('/employees', tags=['Employee Core'])
class EmployeeController(ControllerBase):
    """
    ORCHESTRATION LAYER

    This controller exposes the primary Employee API.
    It is responsible for:
    - HTTP validation (Ninja / Pydantic)
    - Authentication context access
    - Delegation to domain services

    All business rules (matricule generation, lifecycle transitions,
    audit tracking) live in the service layer — not here.
    """

    @inject
    def __init__(
        self,
        profile_service: EmployeeProfileService,
        query_service: EmployeeQueryService,
    ):
        """
        Dependency injection of domain services.

        profile_service:
            - Write-side use cases (onboarding, updates)
        query_service:
            - Read-side optimized queries (prefetch, filtering)
        """
        self.profile_service = profile_service
        self.query_service = query_service

    @http_get('/', response=List[EmployeeOut])
    @paginate(CursorPagination)
    def list_employees(self, filters: EmployeeFilterIn = Query(...)):
        """
        Provides a global workforce directory with advanced filtering
        (status, department, dates, etc.).
        """
        logger.info("[API] Accessing workforce directory with filters.")

        # Optimized base queryset:
        # select_related + prefetch_related are centralized in the service
        qs = self.query_service.get_base_queryset()

        # Applies dynamic Q-object filtering defined in the schema
        return filters.filter(qs).distinct()

    @http_post('/', response={201: EmployeeOut})
    def onboard_employee(self, data: EmployeeCreate):
        """
        Starts the employee's professional journey (Onboarding).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Onboarding initiated by {actor}")

        employee = self.profile_service.onboard_employee(
            data=data.model_dump(),
            actor=actor,
        )
        return 201, employee

    @http_get('/{employee_id}', response=EmployeeFullProfileOut)
    def get_employee_detail(self, employee_id: UUID):
        """
        Provides a 360-degree HR view of a specific employee:
        - Identity
        - Address history
        - Emergency contacts
        - Education
        - Status timeline
        """
        logger.debug(f"[API] Retrieving full employee dossier: {employee_id}")

        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            logger.warning(
                f"[API] Resource not found: Employee UUID {employee_id}"
            )
            return self.create_response(
                "Employee record not found",
                status_code=404,
            )

        return employee

    @http_patch('/{employee_id}/assign-user/{user_id}', response={200: dict})
    def link_user(self, employee_id: UUID, user_id: UUID):
        """
        Admin Link: Totally delegates retrieval and logic to the service.
        """
        actor = getattr(self.context.request, 'user', None)
        
        try:
            # We only pass the identifiers now
            employee = self.profile_service.assign_user_account(
                employee_id=employee_id, 
                user_id=user_id, 
                actor=actor
            )
            
            return 200, {
                "message": "Link successful.",
                "employee": employee.matricule,
                "user_id": user_id
            }
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{employee_id}/revoke-user', response={200: dict})
    def revoke_user(self, employee_id: UUID):
        """Revokes portal access for this employee."""
        actor = getattr(self.context.request, 'user', None)
        self.profile_service.unlink_user_account(employee_id=employee_id, actor=actor)
        return 200, {"message": "Access revoked successfully."}

    @http_patch('/{employee_id}/personal-info', response=EmployeeOut)
    def update_personal_info(self, employee_id: UUID, data: EmployeeUpdate):
        """
        Updates civil status, contact details, or identity attributes.
        """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            logger.warning(
                f"[API] Update aborted: Target {employee_id} does not exist."
            )
            return self.create_response(
                "Employee record not found",
                status_code=404,
            )

        actor = getattr(self.context.request, 'user', None)
        logger.info(
            f"[API] Personal data update for {employee.matricule} "
            f"by actor {actor}"
        )

        updated_employee = self.profile_service.update_personal_info(
            employee=employee,
            data=data.model_dump(exclude_unset=True),
            actor=actor,
        )
        return updated_employee

