import logging
from typing   import List
from uuid     import UUID
from injector import inject

from django.core.exceptions import ValidationError
from ninja import Query
from ninja.pagination import paginate
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

from hr.payroll.models import PayrollAdjustment, ContractAdjustment
from hr.payroll.schemas import (
    PayrollAdjustmentCreateIn,
    PayrollAdjustmentOut,
    PayrollAdjustmentUpdateIn,
    ContractAdjustmentCreateIn,
    ContractAdjustmentOut,
    ContractAdjustmentUpdateIn,
    AdjustmentListFilterIn,
    ContractAdjustmentListFilterIn,
)
from hr.payroll.services.adjustments import AdjustmentManagementService
from hr.payroll.services import PayrollInitService


logger = logging.getLogger(__name__)


@api_controller('/payroll/adjustments', tags=['Payroll Adjustments'])
class PayrollAdjustmentsController(ControllerBase):
    """
    Payroll adjustments controller.

    Manages manual adjustments to payroll:
    - Create and manage bonuses and deductions
    - Apply adjustments to employee contracts (ContractAdjustment)
    - Configure mandatory vs optional adjustments
    - Track adjustment history and audit trail
    """

    @inject
    def __init__(self, adjustment_service: AdjustmentManagementService, init_service: PayrollInitService):
        self.adjustment_service = adjustment_service
        self.init_service = init_service

    # ===== PAYROLL ADJUSTMENT TYPES =====

    @http_post('/reset/', response={200: dict}, permissions=[ScopePermission('payroll:a')])
    def reset_adjustments(self):
        """
        Réinitialise le catalogue d'éléments de paie depuis la fixture
        (payroll_adjustments.json) — ne touche pas aux autres paramètres.
        """
        logger.info("[Adjustments] Resetting adjustment types from fixture")
        try:
            count = self.init_service.reset_adjustments()
            return {"status": "success", "reset_count": count}
        except Exception as e:
            logger.error("[Adjustments] Error resetting adjustment types", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=500)

    @http_get('/types', response=PaginatedResponseSchema[PayrollAdjustmentOut], permissions=[ScopePermission('payroll:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    @cache_api_response(timeout=60*60*24, key_prefix="adjustment_types_list", user_specific=False)
    def list_adjustment_types(self, filters: AdjustmentListFilterIn = Query(...)):
        """
        List all adjustment types (bonuses, deductions, special payments).
        
        Supports filtering by:
        - Type (BONUS, DEDUCTION, SPECIAL_PAYMENT)
        - Is mandatory
        - Active status
        """
        logger.debug("[Adjustments] Listing adjustment types", extra={"filters": filters.model_dump()})

        qs = PayrollAdjustment.objects.all().order_by('name')

        # Apply filters
        return filters.filter(qs)

    @http_get('/{adjustment_id}', response=PayrollAdjustmentOut, permissions=[ScopePermission('payroll:r')])
    def get_adjustment_type(self, adjustment_id: UUID):
        """
        Retrieve details of a specific adjustment type.
        """
        logger.debug("[Adjustments] Getting adjustment type", extra={"adjustment_id": adjustment_id})

        try:
            adjustment = self.adjustment_service.get_adjustment_type(adjustment_id)
            return adjustment

        except PayrollAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Type not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Adjustment type not found"},
                status_code=404,
            )

    @http_post('/types', response={201: PayrollAdjustmentOut}, permissions=[ScopePermission('payroll:w')])
    def create_adjustment(self, data: PayrollAdjustmentCreateIn):
        """
        Create a new adjustment type (bonus, deduction, special payment).
        
        Example:
        - "Performance Bonus" - BONUS type, 5% of salary
        - "Professional Tax" - DEDUCTION type, mandatory
        - "End of Year Bonus" - SPECIAL_PAYMENT type, 13th month
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Creating adjustment type", extra={"actor": actor})

        try:
            adjustment = self.adjustment_service.create_adjustment_type(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info(
                "[Adjustments] Adjustment type created",
                extra={"adjustment_id": adjustment.id, "adjustment_name": adjustment.name},
            )
            return 201, adjustment

        except ValidationError as e:
            logger.warning("[Adjustments] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{adjustment_id}', response=PayrollAdjustmentOut, permissions=[ScopePermission('payroll:u')])
    def update_adjustment(self, adjustment_id: UUID, data: PayrollAdjustmentUpdateIn):
        """
        Update an adjustment type definition.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Updating adjustment type", extra={"adjustment_id": adjustment_id})

        try:
            adjustment = self.adjustment_service.update_adjustment_type(
                adjustment_id=adjustment_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return adjustment

        except PayrollAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Type not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Adjustment type not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Adjustments] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_delete('/{adjustment_id}', permissions=[ScopePermission('payroll:d')])
    def delete_adjustment_type(self, adjustment_id: UUID):
        """
        Delete an adjustment type (only if no contract adjustments exist).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Deleting adjustment type", extra={"adjustment_id": adjustment_id})

        try:
            self.adjustment_service.delete_adjustment_type(
                adjustment_id=adjustment_id,
                actor=actor,
            )
            logger.info("[Adjustments] Adjustment type deleted", extra={"adjustment_id": adjustment_id})
            return {"message": "Adjustment type deleted successfully"}

        except PayrollAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Type not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Adjustment type not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Adjustments] Cannot delete type", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== CONTRACT ADJUSTMENTS (S10) =====

    @http_get('/contracts/', response=PaginatedResponseSchema[ContractAdjustmentOut], permissions=[ScopePermission('payroll:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_contract_adjustments(self, filters: ContractAdjustmentListFilterIn = Query(...)):
        """
        List contract adjustments (elements de paie du contrat) with filtering.

        Supports filtering by:
        - Contract
        - Employee (denormalized)
        - Adjustment type
        - Effective date range
        - Active status
        """
        logger.debug("[Adjustments] Listing contract adjustments", extra={"filters": filters.model_dump()})

        qs = ContractAdjustment.objects.select_related(
            'employee',
            'contract',
            'adjustment',
        ).all().order_by('-start_date')

        # Apply filters
        return filters.filter(qs)

    @http_get('/contracts/{contract_id}/adjustments/', response=List[ContractAdjustmentOut], permissions=[ScopePermission('payroll:r')])
    def list_contract_specific_adjustments(self, contract_id: UUID):
        """
        List all adjustments for a specific contract.
        """
        logger.debug("[Adjustments] Listing adjustments for contract", extra={"contract_id": contract_id})

        adjustments = self.adjustment_service.get_contract_adjustments(contract_id)
        return adjustments

    @http_get('/employees/{employee_id}/', response=List[ContractAdjustmentOut], permissions=[ScopePermission('payroll:r')])
    def list_employee_specific_adjustments(self, employee_id: UUID):
        """
        List all adjustments for a specific employee (active contract).
        """
        logger.debug("[Adjustments] Listing adjustments for employee", extra={"employee_id": employee_id})

        adjustments = self.adjustment_service.get_employee_adjustments(employee_id)
        return adjustments

    @http_get('/employee-adjustments/{adjustment_id}', response=ContractAdjustmentOut, permissions=[ScopePermission('payroll:r')])
    def get_employee_adjustment(self, adjustment_id: UUID):
        """
        Retrieve details of a specific contract adjustment assignment.
        """
        logger.debug("[Adjustments] Getting adjustment", extra={"adjustment_id": adjustment_id})

        try:
            adjustment = self.adjustment_service.get_contract_adjustment(adjustment_id)
            return adjustment

        except ContractAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Adjustment not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Contract adjustment not found"},
                status_code=404,
            )

    @http_post('/employee-adjustments', response={201: ContractAdjustmentOut}, permissions=[ScopePermission('payroll:w')])
    def assign_adjustment_to_contract(self, data: ContractAdjustmentCreateIn):
        """
        Apply a catalog element to a specific contract (S10).

        Example:
        - Apply "Prime de performance" to John Doe's contract: 50,000 CDF
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Applying adjustment to contract", extra={"actor": actor})

        try:
            adjustment = self.adjustment_service.create_contract_adjustment(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info(
                "[Adjustments] Adjustment applied",
                extra={"contract_id": adjustment.contract_id, "adjustment_type": adjustment.adjustment_id},
            )
            return 201, adjustment

        except ValidationError as e:
            logger.warning("[Adjustments] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/employee/{adjustment_id}', response=ContractAdjustmentOut)
    def update_employee_adjustment(self, adjustment_id: UUID, data: ContractAdjustmentUpdateIn):
        """
        Update a contract adjustment (amount, percentage, dates, status).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Updating contract adjustment", extra={"adjustment_id": adjustment_id})

        try:
            adjustment = self.adjustment_service.update_contract_adjustment(
                adjustment_id=adjustment_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return adjustment

        except ContractAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Adjustment not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Contract adjustment not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Adjustments] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_delete('/employee/{adjustment_id}')
    def delete_employee_adjustment(self, adjustment_id: UUID):
        """
        Remove an adjustment from a contract.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Deleting contract adjustment", extra={"adjustment_id": adjustment_id})

        try:
            self.adjustment_service.delete_contract_adjustment(
                adjustment_id=adjustment_id,
                actor=actor,
            )
            logger.info("[Adjustments] Adjustment removed", extra={"adjustment_id": adjustment_id})
            return {"message": "Adjustment removed successfully"}

        except ContractAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Adjustment not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Contract adjustment not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Adjustments] Cannot delete adjustment", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)
