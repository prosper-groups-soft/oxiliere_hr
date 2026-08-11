import logging
from typing   import List
from uuid     import UUID
from injector import inject

from django.core.exceptions import ValidationError
from ninja import Query, Schema, Body
from ninja.pagination import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra,
    PaginatedResponseSchema
)
from oxutils.permissions.perms import ScopePermission
from hr.services.cache_helpers import cache_api_response

from hr.payroll.models import SalaryAdvance, AdvanceDeductionConfiguration
from hr.payroll.schemas import (
    SalaryAdvanceCreateIn,
    SalaryAdvanceOut,
    SalaryAdvanceUpdateIn,
    SalaryAdvanceDetailOut,
    AdvanceDeductionConfigurationCreateIn,
    AdvanceDeductionConfigurationOut,
    AdvanceDeductionConfigurationUpdateIn,
    RepaymentRecordOut,
    AdvanceBalanceOut,
    AdvanceListFilterIn,
)
from hr.payroll.services.advances.advances_mgmt import AdvanceManagementService


logger = logging.getLogger(__name__)


class AdvanceRejectIn(Schema):
    """Body schema for rejecting an advance — reason is mandatory."""
    reason: str


@api_controller('/payroll/advances', tags=['Salary Advances'])
class SalaryAdvanceController(ControllerBase):
    """
    SALARY ADVANCES CONTROLLER

    Manages employee salary advances:
    - Request and approve salary advances
    - Configure advance deduction terms
    - Track advance repayment
    - Multi-advance priority management
    - Advance balance and repayment history
    """

    @inject
    def __init__(self, advance_service: AdvanceManagementService):
        self.advance_service = advance_service

    # ===== SALARY ADVANCES =====

    @http_get('/', response=PaginatedResponseSchema[SalaryAdvanceOut], permissions=[ScopePermission('payroll:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_advances(self, filters: AdvanceListFilterIn = Query(...)):
        """
        List salary advances with filtering.
        
        Supports filtering by:
        - Employee
        - Status (PENDING, APPROVED, ACTIVE, CLOSED)
        - Advance type
        - Date range
        """
        logger.debug("[Advances] Listing advances", extra={"filters": filters.model_dump()})

        qs = SalaryAdvance.objects.select_related(
            'employee',
            'requested_by',
            'approved_by',
        ).prefetch_related(
            'employee__position_history__position',
            'employee__position_history__org_unit',
        ).all().order_by('-requested_date')

        # Apply filters
        return filters.filter(qs)

    @http_get('/employee/{employee_id}/active', response=List[SalaryAdvanceOut], permissions=[ScopePermission('payroll:r')])
    def list_active_advances(self, employee_id: UUID):
        """
        List all active (ACTIVE status) advances for an employee.
        Returns advances that are currently deductible from payroll.
        """
        logger.debug("[Advances] Listing active advances", extra={"employee_id": employee_id})

        advances = self.advance_service.get_active_advances(employee_id)
        return advances

    @http_get('/employee/{employee_id}/history', response=List[SalaryAdvanceOut], permissions=[ScopePermission('payroll:r')])
    def list_advance_history(self, employee_id: UUID):
        """
        List complete advance history for an employee.
        Returns all advances (active and closed) ordered by request date.
        """
        logger.debug("[Advances] Listing advance history", extra={"employee_id": employee_id})

        advances = self.advance_service.get_employee_advance_history(employee_id)
        return advances

    @http_get('/{advance_id}/balance', response=AdvanceBalanceOut, permissions=[ScopePermission('payroll:r')])
    def get_advance_balance(self, advance_id: UUID):
        """
        Get current balance information for an advance.
        
        Returns:
        - Total amount requested
        - Total repaid
        - Remaining balance
        - Estimated repayment date
        """
        logger.debug("[Advances] Getting advance balance", extra={"advance_id": advance_id})

        try:
            balance = self.advance_service.get_advance_balance(advance_id)
            return balance

        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Advance not found", extra={"advance_id": advance_id})
            return self.create_response(
                {"detail": "Advance not found"},
                status_code=404,
            )

    @http_post('/', response={201: SalaryAdvanceOut}, permissions=[ScopePermission('payroll:w')])
    def request_salary_advance(self, data: SalaryAdvanceCreateIn):
        """
        Create a new salary advance request.
        Initial status is PENDING, must be approved before activation.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Advances] Creating advance request", extra={"actor": actor})

        try:
            advance = self.advance_service.create_advance(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info(
                "[Advances] Advance created",
                extra={"advance_id": advance.id, "employee_id": advance.employee_id},
            )
            return 201, advance

        except ValidationError as e:
            logger.warning("[Advances] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/{advance_id}/submit', response=SalaryAdvanceOut, permissions=[ScopePermission('payroll:w')])
    def submit_salary_advance(self, advance_id: UUID):
        """
        Submit a draft advance request.
        Transitions status from DRAFT to PENDING (enters the approval queue).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Advances] Submitting advance", extra={"advance_id": advance_id, "actor": actor})

        try:
            advance = self.advance_service.submit_advance(
                advance_id=advance_id,
                actor=actor,
            )
            logger.info("[Advances] Advance submitted", extra={"advance_id": advance_id})
            return advance

        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Advance not found", extra={"advance_id": advance_id})
            return self.create_response(
                {"detail": "Advance not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Advances] Cannot submit advance", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{advance_id}/approve', response=SalaryAdvanceOut, permissions=[ScopePermission('payroll:a')])
    def approve_salary_advance(self, advance_id: UUID):
        """
        Approve a pending salary advance request.
        Transitions status from PENDING to APPROVED.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Advances] Approving advance", extra={"advance_id": advance_id, "actor": actor})

        try:
            advance = self.advance_service.approve_advance(
                advance_id=advance_id,
                actor=actor,
            )
            logger.info("[Advances] Advance approved", extra={"advance_id": advance_id})
            return advance

        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Advance not found", extra={"advance_id": advance_id})
            return self.create_response(
                {"detail": "Advance not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Advances] Cannot approve advance", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{advance_id}/activate', response=SalaryAdvanceOut, permissions=[ScopePermission('payroll:a')])
    def activate_salary_advance(self, advance_id: UUID):
        """
        Activate an approved advance request.
        Transitions status from APPROVED to ACTIVE (deductible).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Advances] Activating advance", extra={"advance_id": advance_id, "actor": actor})

        try:
            advance = self.advance_service.activate_advance(
                advance_id=advance_id,
                actor=actor,
            )
            logger.info("[Advances] Advance activated", extra={"advance_id": advance_id})
            return advance

        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Advance not found", extra={"advance_id": advance_id})
            return self.create_response(
                {"detail": "Advance not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Advances] Cannot activate advance", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{advance_id}/reject', response=SalaryAdvanceOut, permissions=[ScopePermission('payroll:a')])
    def reject_advance(self, advance_id: UUID, data: AdvanceRejectIn = Body(...)):
        """
        Reject a pending salary advance request.
        
        Transitions status from PENDING to REJECTED.
        The reason is mandatory and stored in rejection_reason.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Advances] Rejecting advance", extra={"advance_id": advance_id, "reason": data.reason})

        try:
            advance = self.advance_service.reject_advance(
                advance_id=advance_id,
                reason=data.reason,
                actor=actor,
            )
            logger.info("[Advances] Advance rejected", extra={"advance_id": advance_id})
            return advance

        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Advance not found", extra={"advance_id": advance_id})
            return self.create_response(
                {"detail": "Advance not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Advances] Cannot reject advance", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{advance_id}', response=SalaryAdvanceOut, permissions=[ScopePermission('payroll:u')])
    def update_advance(self, advance_id: UUID, data: SalaryAdvanceUpdateIn):
        """
        Update an advance (only PENDING advances can be modified).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Advances] Updating advance", extra={"advance_id": advance_id})

        try:
            advance = self.advance_service.update_advance(
                advance_id=advance_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return advance

        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Advance not found", extra={"advance_id": advance_id})
            return self.create_response(
                {"detail": "Advance not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Advances] Cannot update advance", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_get('/{advance_id}', response=SalaryAdvanceDetailOut, permissions=[ScopePermission('payroll:r')])
    def get_salary_advance_detail(self, advance_id: UUID):
        """
        Get a salary advance by its ID.
        """
        logger.debug("[Advances] Getting salary advance by ID", extra={"advance_id": advance_id})
        try:
            advance = self.advance_service.get_advance_detail(advance_id)
            return advance
        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Salary advance not found", extra={"advance_id": advance_id})
            return self.create_response(
                {"detail": "Salary advance not found"},
                status_code=404,
            )   

    # ===== ADVANCE DEDUCTION CONFIGURATION =====

    @http_get('/deduction-configs/', response=List[AdvanceDeductionConfigurationOut], permissions=[ScopePermission('payroll:r')])
    def list_deduction_configs(self):
        """
        List all advance deduction configurations.
        """
        logger.debug("[Advances] Listing all deduction configurations")
        configs = self.advance_service.list_all_advance_configurations()
        return configs

    @http_get('/{advance_id}/configuration', response=AdvanceDeductionConfigurationOut, permissions=[ScopePermission('payroll:r')])
    def get_advance_configuration(self, advance_id: UUID):
        """
        Retrieve deduction configuration for a specific advance.
        
        Returns:
        - Salary base (GROSS or NET)
        - Tax timing (BEFORE_TAX or AFTER_TAX)
        - Deduction window (ALL_MONTHS or CUSTOM_PERIOD)
        - Priority order for multi-advance deduction
        """
        logger.debug("[Advances] Getting advance configuration", extra={"advance_id": advance_id})

        try:
            config = self.advance_service.get_advance_configuration(advance_id)
            return config

        except AdvanceDeductionConfiguration.DoesNotExist:
            logger.warning("[Advances] Configuration not found", extra={"advance_id": advance_id})
            return self.create_response(
                {"detail": "Configuration not found"},
                status_code=404,
            )

    @http_post('/deduction-configs/', response={201: AdvanceDeductionConfigurationOut}, permissions=[ScopePermission('payroll:w')])
    def configure_advance_deduction(self, data: AdvanceDeductionConfigurationCreateIn):
        """
        Create or update deduction configuration for an advance.
        
        Defines how the advance will be deducted from payroll:
        - Base salary (gross or net)
        - Tax impact timing
        - Custom deduction window
        - Priority among multiple advances
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Advances] Creating configuration", extra={"advance_id": data.advance})

        try:
            config = self.advance_service.create_advance_configuration(
                advance_id=data.advance,
                data=data.model_dump(),
                actor=actor,
            )
            logger.info("[Advances] Configuration created", extra={"advance_id": data.advance})
            return 201, config

        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Advance not found", extra={"advance_id": data.advance})
            return self.create_response(
                {"detail": "Advance not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Advances] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{advance_id}/configuration', response=AdvanceDeductionConfigurationOut)
    def update_configuration(self, advance_id: UUID, data: AdvanceDeductionConfigurationUpdateIn):
        """
        Update deduction configuration for an advance.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Advances] Updating configuration", extra={"advance_id": advance_id})

        try:
            config = self.advance_service.update_advance_configuration(
                advance_id=advance_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return config

        except AdvanceDeductionConfiguration.DoesNotExist:
            logger.warning("[Advances] Configuration not found", extra={"advance_id": advance_id})
            return self.create_response(
                {"detail": "Configuration not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Advances] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== REPAYMENT HISTORY =====

    @http_get('/{advance_id}/repayments', response=List[RepaymentRecordOut])
    def list_repayment_history(self, advance_id: UUID):
        """
        List all repayment records for a salary advance.
        Shows the repayment schedule and amounts deducted per payslip.
        """
        logger.debug("[Advances] Listing repayment history", extra={"advance_id": advance_id})

        try:
            repayments = self.advance_service.get_repayment_history(advance_id)
            return repayments

        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Advance not found", extra={"advance_id": advance_id})
            return self.create_response(
                {"detail": "Advance not found"},
                status_code=404,
            )
