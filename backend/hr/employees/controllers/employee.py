import logging
from injector  import inject
from uuid      import UUID
from typing    import Optional
from ninja     import Query
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from ninja.pagination import paginate
from ninja       import File
from ninja.files import UploadedFile
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
from hr.services.cache_helpers import cache_api_response

# Schemas
from hr.employees.schemas import (
    EmployeeOut,
    EmployeeFullProfileOut,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeFilterIn,
    EmployeeAddressCreate,
    EmployeeContractInfoUpdateIn,
)

# Services
from hr.employees.services import (
    EmployeeProfileService,
    EmployeeQueryService,
    EmployeeAddressService,
    EmployeeCacheService,
)
from hr.employees.models import Employee
from hr.payroll.services.contracts import EmployeeContractService
from hr.jobs.services import CareerService


logger = logging.getLogger(__name__)


@api_controller('/employees', tags=['Employee Core'])
class EmployeeController(ControllerBase):
    """ API endpoints for employee profile and identity management. """

    @inject
    def __init__(
        self,
        profile_service: EmployeeProfileService,
        query_service: EmployeeQueryService,
        address_service: EmployeeAddressService,
        cache_service: EmployeeCacheService,
        contract_service: EmployeeContractService,
        career_service: CareerService,
    ):
        self.profile_service = profile_service
        self.query_service = query_service
        self.address_service = address_service
        self.cache_service = cache_service
        self.contract_service = contract_service
        self.career_service = career_service

    @http_get('', response=PaginatedResponseSchema[EmployeeOut], permissions=[ScopePermission('employees:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_employees(
        self, 
        filters: EmployeeFilterIn = Query(...),
        ordering: Optional[str] = Query(None, description="Sort by: name, -name, hire_date, -hire_date, status, -status")
    ):
        """ Returns a filtered list of all employees in the directory. """
        logger.info(f"[API] Accessing workforce directory with filters: {filters}, ordering: {ordering}")

        # Optimized base queryset:
        # select_related + prefetch_related are centralized in the service
        qs = self.query_service.get_base_queryset()

        # Applies dynamic Q-object filtering defined in the schema
        qs = filters.filter(qs).distinct()
        
        # Apply ordering/sorting
        qs = filters.apply_ordering(qs, ordering)
        
        return qs

    @http_post('/', response={201: EmployeeOut, 409: dict}, permissions=[ScopePermission('employees:w')])
    def onboard_employee(self, data: EmployeeCreate):
        """ Initiates the onboarding journey for a new staff member. """
        
        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Onboarding initiated by {actor}")

        try:
            employee = self.profile_service.onboard_employee(
                data=data.model_dump(),
                actor=actor,
            )
            return 201, employee
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)}
            logger.warning(f"[API] Validation error during onboarding: {error_dict}")
            
            # Si c'est une erreur d'email déjà existant, retourner 409 Conflict
            # ValidationError met les valeurs dans des listes
            error_code = error_dict.get('code', [None])[0] if isinstance(error_dict.get('code'), list) else error_dict.get('code')
            if error_code == 'EMAIL_ALREADY_EXISTS':
                message = error_dict.get('message', ['Email already assigned.'])[0] if isinstance(error_dict.get('message'), list) else error_dict.get('message')
                return 409, {
                    'error': 'EMAIL_ALREADY_EXISTS',
                    'message': message,
                    'field': 'email'
                }
            
            return self.create_response(error_dict, status_code=400)

    @http_get('/{employee_id}', response=EmployeeFullProfileOut, permissions=[ScopePermission('employees:r')])
    @cache_api_response(timeout=60*60*24, key_prefix="employee_detail", user_specific=False)
    def get_employee_detail(self, employee_id: UUID):
        """ Retrieves full HR dossier and history for a specific employee. """
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

    @http_patch('/{employee_id}/assign-user/{user_id}', response={200: dict}, permissions=[ScopePermission('employees:u')])
    def link_user(self, employee_id: UUID, user_id: UUID):
        """ Connects a system user account to an employee profile. """
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

    @http_post('/{employee_id}/revoke-user', permissions=[ScopePermission('employees:u')])
    def revoke_user(self, employee_id: UUID):
        """Revokes portal access for this employee."""
        actor = getattr(self.context.request, 'user', None)
        self.profile_service.unlink_user_account(employee_id=employee_id, actor=actor)
        return 200, {"message": "Access revoked successfully."}

    @http_patch('/{employee_id}/personal-info', response={200: EmployeeOut}, permissions=[ScopePermission('employees:u')])
    def update_personal_info(self, employee_id: UUID, data: EmployeeUpdate):
        """ Updates core identification and civil status data. """
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

        # Invalidate the cached data and API responses for this specific employee
        self.cache_service.clear_employee_cache(employee)

        return 200, updated_employee

    @http_post('/{employee_id}/upload-photo', response={200: EmployeeOut}, permissions=[ScopePermission('employees:u')])
    def upload_profile_photo(
        self,
        employee_id: UUID,
        file: File[UploadedFile],
    ):
        """
        Uploads a profile photo for the employee.

        The photo is stored directly in the employee.profile_photo field.
        """
        employee = get_object_or_404(Employee, id=employee_id)
        actor = getattr(self.context.request, 'user', None)

        logger.info(f"[API] Uploading profile photo for {employee.matricule}")

        try:
            # Service handles the update
            self.profile_service.update_profile_photo(
                employee=employee,
                file=file,
                actor=actor
            )

            # Return the updated employee
            return 200, self.query_service.get_employee_by_id(employee_id)

        except ValidationError as e:
            logger.warning(f"[API] Validation error uploading photo: {e}")
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.exception(f"[API] Unexpected error uploading photo for {employee_id}")
            return self.create_response(
                {"detail": "An unexpected error occurred while uploading the photo"},
                status_code=500
            )

    @http_post('/{employee_id}/address', response={201: dict}, permissions=[ScopePermission('employees:u')])
    def add_employee_address(self, employee_id: UUID, data: EmployeeAddressCreate):
        """ Adds a residential address for the employee (during onboarding). """
        actor = getattr(self.context.request, 'user', None)
        employee = get_object_or_404(Employee, id=employee_id)

        logger.info(f"[API] Adding address for employee {employee.matricule}")

        try:
            # Use register_move to create the address with is_current=True
            address = self.address_service.register_move(
                employee=employee,
                data=data.model_dump(exclude_unset=True),
                actor=actor
            )

            logger.info(f"[API] Address created successfully for {employee.matricule}")
            return 201, {
                "id": str(address.id),
                "message": "Address added successfully"
            }

        except ValidationError as e:
            logger.warning(f"[API] Validation error adding address: {e}")
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.exception(f"[API] Unexpected error adding address for {employee_id}")
            return self.create_response(
                {"detail": "An unexpected error occurred while adding the address"},
                status_code=500
            )

    @http_delete('/{employee_id}', response={204: None, 404: dict}, permissions=[ScopePermission('employees:d')])
    def delete_employee(self, employee_id: UUID):
        """ 
        Supprime un employé et toutes ses données associées.
        Utilisé pour le rollback en cas d'échec d'onboarding.
        """
        employee = get_object_or_404(Employee, id=employee_id)
        
        logger.warning(f"[API] Deleting employee {employee.matricule} (rollback onboarding)")
        
        try:
            self.profile_service.delete_employee(employee)
            return 204, None
                
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.exception(f"[API] Error deleting employee {employee_id}")
            return self.create_response(
                {"detail": f"Failed to delete employee: {str(e)}"},
                status_code=500
            )

    @http_patch('/{employee_id}/contract-info', response={200: EmployeeOut}, permissions=[ScopePermission('employees:u')])
    def update_contract_info(self, employee_id: UUID, data: EmployeeContractInfoUpdateIn):
        """ 
        Orchestrates the update of both employment terms (contract) 
        and career positioning (position, seniority).
        """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee record not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Contract info update for {employee.matricule} by {actor}")

        try:
            self.profile_service.update_contract_and_career(
                employee=employee,
                data=data.model_dump(exclude_unset=True),
                actor=actor
            )

            # Invalidate cache
            self.cache_service.clear_employee_cache(employee)
            
            # Return updated employee
            return 200, self.query_service.get_employee_by_id(employee_id)

        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.exception(f"[API] Unexpected error updating contract info for {employee_id}")
            return self.create_response({"detail": str(e)}, status_code=500)

