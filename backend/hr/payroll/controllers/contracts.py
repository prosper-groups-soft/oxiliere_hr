import logging
from typing   import List
from uuid     import UUID
from injector import inject

from django.core.exceptions import ValidationError
from ninja import Query
from ninja.pagination import paginate
from ninja_extra      import (
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

from hr.payroll.models  import EmployeeContract, ContractAdjustment
from hr.payroll.schemas import (
    EmployeeContractCreateIn,
    EmployeeContractOut,
    EmployeeContractUpdateIn,
    EmployeeContractListFilterIn,
    ContractAdjustmentCreateIn,
    ContractAdjustmentUpdateIn,
    ContractPayElementListOut,
    PayElementOut,
)
from hr.payroll.services.contracts import EmployeeContractService
from hr.payroll.services.adjustments import AdjustmentManagementService
# Cache integration
from hr.services.cache_helpers import cache_api_response


logger = logging.getLogger(__name__)


@api_controller('/payroll/contracts', tags=['Employee Contracts'])
class EmployeeContractController(ControllerBase):
    """
    Employee contract controller.

    Manages employee compensation agreements:
    - Contract creation / termination
    - Salary adjustments
    - Remuneration type changes (fixed, hourly, net-to-gross)
    - Payment period management
    - Contract history and audit trail
    """

    @inject
    def __init__(self, contract_service: EmployeeContractService, adjustment_service: AdjustmentManagementService):
        self.contract_service = contract_service
        self.adjustment_service = adjustment_service

    @http_get('/', response=PaginatedResponseSchema[EmployeeContractOut], permissions=[ScopePermission('payroll:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    @cache_api_response(timeout=60*60, key_prefix="employee_contracts_list", user_specific=False)
    def list_contracts(self, filters: EmployeeContractListFilterIn = Query(...)):  # type: ignore[reportCallIssue]
        """
        List employee contracts with filtering options.
        
        Supports filtering by:
        - Employee
        - Active status
        - Remuneration type (FIXED, HOURLY)
        - Contract type (CDI, CDD, FREELANCE, INTERN)
        - Date range
        """
        logger.debug("[Contracts] Listing contracts", extra={"filters": filters.model_dump()})

        qs = EmployeeContract.objects.select_related(
            'employee',
            'employee__user',
        ).all()

        # Apply filter logic
        return filters.filter(qs)

    @http_get('/{contract_id}', response=EmployeeContractOut, permissions=[ScopePermission('payroll:r')])
    @cache_api_response(timeout=60*60*24, key_prefix="contract_detail", user_specific=False)
    def get_contract_detail(self, contract_id: UUID):
        """
        Retrieve full details of a specific contract.
        Includes all terms, salary info, and activation status.
        """
        logger.debug("[Contracts] Getting contract detail", extra={"contract_id": contract_id})

        try:
            contract = self.contract_service.get_contract_by_id(contract_id)
            return contract

        except EmployeeContract.DoesNotExist:
            logger.warning("[Contracts] Contract not found", extra={"contract_id": contract_id})
            return self.create_response(
                {"detail": "Contract not found"},
                status_code=404,
            )

    @http_get('/employee/{employee_id}/active', response=EmployeeContractOut)
    @cache_api_response(timeout=60*60*24, key_prefix="active_contract_employee", user_specific=False)
    def get_active_contract(self, employee_id: UUID):
        """
        Retrieve the currently active contract for an employee.
        Returns the contract marked as is_active=True.
        If no active contract exists, returns 404.
        """
        logger.debug("[Contracts] Getting active contract", extra={"employee_id": employee_id})

        try:
            contract = self.contract_service.get_active_contract(employee_id)
            return contract

        except EmployeeContract.DoesNotExist:
            logger.info("[Contracts] No active contract found", extra={"employee_id": employee_id})
            return self.create_response(
                {"detail": "No active contract found for this employee"},
                status_code=404,
            )

    @http_get('/employee/{employee_id}/history', response=List[EmployeeContractOut])
    @cache_api_response(timeout=60*60*24, key_prefix="contract_history_employee", user_specific=False)
    def get_contract_history(self, employee_id: UUID):
        """
        Retrieve full contract history for an employee.
        Returns all contracts (active and inactive) ordered by start date.
        """
        logger.debug("[Contracts] Getting contract history", extra={"employee_id": employee_id})

        contracts = self.contract_service.get_employee_contract_history(employee_id)
        return contracts

    @http_post('/', response={201: EmployeeContractOut}, permissions=[ScopePermission('payroll:w')])
    def create_contract(self, data: EmployeeContractCreateIn):
        """
        Create a new employment contract for an employee.
        Automatically marks previous active contracts as inactive.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Contracts] Creating contract", extra={"actor": actor})

        try:
            contract = self.contract_service.create_contract(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info(
                "[Contracts] Contract created successfully",
                extra={"contract_id": contract.id, "employee_id": contract.employee_id},
            )
            return 201, contract

        except ValidationError as e:
            logger.warning("[Contracts] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

        except Exception as e:
            logger.exception("[Contracts] Unexpected error during contract creation")
            return self.create_response(
                {"detail": "An unexpected error occurred"},
                status_code=500,
            )

    @http_patch('/{contract_id}', response=EmployeeContractOut, permissions=[ScopePermission('payroll:u')])
    def update_contract(self, contract_id: UUID, data: EmployeeContractUpdateIn):
        """
        Update an existing employment contract.
        
        Allows updating:
        - Base salary
        - Hourly rate
        - Remuneration type
        - Payment period
        - Contract dates
        - Currency
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Contracts] Updating contract", extra={"contract_id": contract_id, "actor": actor})

        try:
            contract = self.contract_service.update_contract(
                contract_id=contract_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            logger.info("[Contracts] Contract updated successfully", extra={"contract_id": contract_id})
            return contract

        except EmployeeContract.DoesNotExist:
            logger.warning("[Contracts] Contract not found", extra={"contract_id": contract_id})
            return self.create_response(
                {"detail": "Contract not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Contracts] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{contract_id}/deactivate', response=EmployeeContractOut, permissions=[ScopePermission('payroll:u')])
    def deactivate_contract(self, contract_id: UUID):
        """
        Deactivate a contract (mark end date as today).
        Used when an employee's employment is terminated.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Contracts] Deactivating contract", extra={"contract_id": contract_id, "actor": actor})

        try:
            contract = self.contract_service.deactivate_contract(
                contract_id=contract_id,
                actor=actor,
            )
            logger.info("[Contracts] Contract deactivated", extra={"contract_id": contract_id})
            return contract

        except EmployeeContract.DoesNotExist:
            logger.warning("[Contracts] Contract not found", extra={"contract_id": contract_id})
            return self.create_response(
                {"detail": "Contract not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Contracts] Cannot deactivate contract", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_delete('/{contract_id}')
    def delete_contract(self, contract_id: UUID):
        """
        Delete a contract.
        Only allowed for draft contracts that haven't generated payslips.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Contracts] Deleting contract", extra={"contract_id": contract_id, "actor": actor})

        try:
            self.contract_service.delete_contract(
                contract_id=contract_id,
                actor=actor,
            )
            logger.info("[Contracts] Contract deleted", extra={"contract_id": contract_id})
            return {"message": "Contract deleted successfully"}

        except EmployeeContract.DoesNotExist:
            logger.warning("[Contracts] Contract not found", extra={"contract_id": contract_id})
            return self.create_response(
                {"detail": "Contract not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Contracts] Cannot delete contract", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== S10 — ÉLÉMENTS DE PAIE DU CONTRAT =====

    @http_get('/{contract_id}/pay-elements', response=ContractPayElementListOut, permissions=[ScopePermission('payroll:r')])
    def list_pay_elements(self, contract_id: UUID):
        """
        S10 — Liste les éléments de paie récurrents d'un contrat avec résumé brut estimé.

        Conforme à la doc s10-elements-paie-contrat.md :
        - éléments actifs et inactifs (toggle S10)
        - base_salary + total fixes = brut estimé
        """
        logger.debug("[Contracts] Listing pay elements", extra={"contract_id": contract_id})

        try:
            contract = self.contract_service.get_contract_by_id(contract_id)
        except EmployeeContract.DoesNotExist:
            return self.create_response({"detail": "Contract not found"}, status_code=404)

        assignments = self.adjustment_service.get_contract_adjustments(contract_id)

        # Construction de la réponse S10 (pas d'alias traversants en sérialisation)
        elements = []
        total_fixed = 0
        for assignment in assignments:
            adj = assignment.adjustment
            amount = assignment.custom_amount if assignment.custom_amount is not None else adj.amount
            value_type = adj.calculation_mode
            if value_type == 'FIXED' and amount:
                total_fixed += amount

            elements.append({
                'id': assignment.id,
                'catalog_code': adj.code,
                'label': adj.name,
                'value_type': value_type,
                'amount': amount,
                'custom_amount': assignment.custom_amount,
                'custom_percentage': assignment.custom_percentage,
                'catalog_percentage': adj.percentage,
                'is_active': assignment.is_active,
                'is_taxable': adj.is_taxable,
                'recurrence': 'monthly',
                'start_period': assignment.start_date,
                'end_period': assignment.end_date,
            })

        base_salary = contract.base_salary or 0
        estimated_gross = base_salary + total_fixed

        return {
            'contract_id': contract.id,
            'employee': contract.employee,
            'contract_type': contract.contract_type,
            'base_salary': base_salary,
            'elements': elements,
            'estimated_gross': estimated_gross,
        }

    @http_post('/{contract_id}/pay-elements', response={201: PayElementOut}, permissions=[ScopePermission('payroll:w')])
    def add_pay_element(self, contract_id: UUID, data: ContractAdjustmentCreateIn):
        """
        S10 — Ajoute un élément du catalogue (PayrollAdjustment) à un contrat.

        Le contrat est imposé par l'URL ; le payload accepte un `contract`
        mais le service verrouille sur contract_id de la route (cohérence).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Contracts] Adding pay element", extra={"contract_id": contract_id, "actor": actor})

        payload = data.model_dump()
        payload['contract'] = contract_id

        try:
            assignment = self.adjustment_service.create_contract_adjustment(
                data=payload,
                actor=actor,
            )
            logger.info("[Contracts] Pay element added", extra={"assignment_id": assignment.id})

            adj = assignment.adjustment
            return 201, {
                'id': assignment.id,
                'catalog_code': adj.code,
                'label': adj.name,
                'value_type': adj.calculation_mode,
                'amount': assignment.custom_amount if assignment.custom_amount is not None else adj.amount,
                'custom_amount': assignment.custom_amount,
                'custom_percentage': assignment.custom_percentage,
                'catalog_percentage': adj.percentage,
                'is_active': assignment.is_active,
                'is_taxable': adj.is_taxable,
                'recurrence': 'monthly',
                'start_period': assignment.start_date,
                'end_period': assignment.end_date,
            }

        except ValidationError as e:
            logger.warning("[Contracts] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{contract_id}/pay-elements/{element_id}', response=PayElementOut, permissions=[ScopePermission('payroll:u')])
    def update_pay_element(self, contract_id: UUID, element_id: UUID, data: ContractAdjustmentUpdateIn):
        """
        S10 — Modifie un élément de paie du contrat (montant négocié, dates, statut).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Contracts] Updating pay element", extra={"element_id": element_id, "contract_id": contract_id})

        try:
            assignment = self.adjustment_service.update_contract_adjustment(
                adjustment_id=element_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )

            # Vérifier que l'élément appartient bien au contrat de l'URL
            if str(assignment.contract_id) != str(contract_id):
                return self.create_response(
                    {"detail": "Pay element does not belong to this contract"},
                    status_code=404,
                )

            adj = assignment.adjustment
            return {
                'id': assignment.id,
                'catalog_code': adj.code,
                'label': adj.name,
                'value_type': adj.calculation_mode,
                'amount': assignment.custom_amount if assignment.custom_amount is not None else adj.amount,
                'custom_amount': assignment.custom_amount,
                'custom_percentage': assignment.custom_percentage,
                'catalog_percentage': adj.percentage,
                'is_active': assignment.is_active,
                'is_taxable': adj.is_taxable,
                'recurrence': 'monthly',
                'start_period': assignment.start_date,
                'end_period': assignment.end_date,
            }

        except ContractAdjustment.DoesNotExist:
            logger.warning("[Contracts] Pay element not found", extra={"element_id": element_id})
            return self.create_response({"detail": "Pay element not found"}, status_code=404)

        except ValidationError as e:
            logger.warning("[Contracts] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_delete('/{contract_id}/pay-elements/{element_id}', permissions=[ScopePermission('payroll:d')])
    def delete_pay_element(self, contract_id: UUID, element_id: UUID):
        """
        S10 — Supprime un élément de paie du contrat (règle 4 : confirmation + motif).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Contracts] Deleting pay element", extra={"element_id": element_id, "contract_id": contract_id})

        try:
            assignment = self.adjustment_service.get_contract_adjustment(element_id)

            # Vérifier que l'élément appartient bien au contrat de l'URL
            if str(assignment.contract_id) != str(contract_id):
                return self.create_response(
                    {"detail": "Pay element does not belong to this contract"},
                    status_code=404,
                )

            self.adjustment_service.delete_contract_adjustment(
                adjustment_id=element_id,
                actor=actor,
            )
            logger.info("[Contracts] Pay element deleted", extra={"element_id": element_id})
            return {"message": "Pay element deleted successfully"}

        except ContractAdjustment.DoesNotExist:
            logger.warning("[Contracts] Pay element not found", extra={"element_id": element_id})
            return self.create_response({"detail": "Pay element not found"}, status_code=404)

        except ValidationError as e:
            logger.warning("[Contracts] Cannot delete pay element", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

