import logging
from decimal  import Decimal
from datetime import date
from typing   import Dict, Any
from uuid     import UUID

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models       import QuerySet

from hr.payroll.models   import EmployeeContract
from hr.employees.models import Employee


logger = logging.getLogger(__name__)


class EmployeeContractService:
    """
    Manages employee employment contracts.
    
    Responsibilities:
    - Create new employment contracts
    - Update contract terms (salary, remuneration type, dates)
    - Deactivate contracts (employee termination)
    - Query contract history and current status
    - Audit trail with actor tracking
    """
    """
    EMPLOYEE CONTRACT SERVICE

    Manages employee employment contracts:
    - Contract creation and termination
    - Salary and compensation tracking
    - Remuneration type management
    - Contract history and audit trail
    """

    # ===== CRUD OPERATIONS =====

    @classmethod
    def get_contract_by_id(cls, contract_id: UUID) -> EmployeeContract:
        """
        Retrieve a contract by ID.
        """
        logger.debug("[Contracts] Getting contract by ID", extra={"contract_id": contract_id})

        return EmployeeContract.objects.select_related(
            'employee',
            'employee__user',
        ).get(id=contract_id)

    @classmethod
    @transaction.atomic
    def create_contract(cls, data: Dict[str, Any], actor=None) -> EmployeeContract:
        """
        Create a new employment contract for an employee.
        Automatically marks previous active contracts as inactive when a new contract is created.
        """
        logger.debug("[Contracts] Creating contract", extra={"data": data, "actor": actor})

        # Validate employee exists
        try:
            employee = Employee.objects.get(id=data.get('employee_id'))
        except Employee.DoesNotExist:
            logger.warning(
                "[Contracts] Employee not found",
                extra={"employee_id": data.get('employee_id')}
            )
            raise ValidationError(f"Employee {data.get('employee_id')} not found")

        # Validate amount
        amount = Decimal(str(data.get('amount', 0)))
        if amount <= 0:
            logger.warning("[Contracts] Invalid amount", extra={"amount": amount})
            raise ValidationError("Contract amount must be positive")

        # Validate dates
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                logger.warning("[Contracts] Invalid date range")
                raise ValidationError("start_date must be before end_date")

        # Deactivate previous active contracts for this employee
        if data.get('is_active', True):
            previous_active = EmployeeContract.objects.filter(
                employee_id=employee.id,
                is_active=True
            )
            if previous_active.exists():
                logger.info(
                    "[Contracts] Deactivating previous contracts",
                    extra={"employee_id": employee.id, "count": previous_active.count()}
                )
                previous_active.update(is_active=False)

        # Create contract
        contract = EmployeeContract.objects.create(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            remuneration_type=data.get('remuneration_type', 'FIXED'),
            amount=amount,
            currency=data.get('currency', 'CDF'),
            contract_type=data.get('contract_type', 'CDI'),
            payment_period=data.get('payment_period', 'MONTHLY'),
            is_active=data.get('is_active', True),
            created_by=actor,
        )

        logger.info(
            "[Contracts] Contract created",
            extra={"contract_id": contract.id, "employee_id": employee.id}
        )
        return contract

    @classmethod
    @transaction.atomic
    def update_contract(
        cls,
        contract_id: UUID,
        data: Dict[str, Any],
        actor=None
    ) -> EmployeeContract:
        """
        Update an existing employment contract.
        
        Allows updating:
        - Salary/rate (amount)
        - Remuneration type
        - Payment period
        - Contract dates
        - Currency
        """
        logger.debug("[Contracts] Updating contract", extra={"contract_id": contract_id})

        contract = EmployeeContract.objects.get(id=contract_id)

        # Validate amount if provided
        if 'amount' in data:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                raise ValidationError("Contract amount must be positive")
            contract.amount = amount

        # Update other fields
        if 'start_date' in data:
            contract.start_date = data['start_date']
        if 'end_date' in data:
            contract.end_date = data['end_date']
        if 'remuneration_type' in data:
            contract.remuneration_type = data['remuneration_type']
        if 'payment_period' in data:
            contract.payment_period = data['payment_period']
        if 'currency' in data:
            contract.currency = data['currency']
        if 'contract_type' in data:
            contract.contract_type = data['contract_type']

        contract.updated_by = actor
        contract.save()

        logger.info("[Contracts] Contract updated", extra={"contract_id": contract_id})
        return contract

    @classmethod
    @transaction.atomic
    def deactivate_contract(cls, contract_id: UUID, actor=None) -> EmployeeContract:
        """
        Deactivate a contract (employee termination).
        Sets is_active=False and optionally sets end_date if not already set.
        """
        logger.debug("[Contracts] Deactivating contract", extra={"contract_id": contract_id})

        contract = EmployeeContract.objects.get(id=contract_id)

        if not contract.is_active:
            logger.warning("[Contracts] Contract already inactive", extra={"contract_id": contract_id})
            raise ValidationError("Contract is already inactive")

        # Set end_date to today if not already set
        if not contract.end_date:
            contract.end_date = date.today()

        contract.is_active = False
        contract.updated_by = actor
        contract.save()

        logger.info("[Contracts] Contract deactivated", extra={"contract_id": contract_id})
        return contract

    @classmethod
    @transaction.atomic
    def delete_contract(cls, contract_id: UUID, actor=None) -> None:
        """
        Delete a contract (hard delete).
        Only allowed for contracts that haven't generated payslips.
        """
        logger.debug("[Contracts] Deleting contract", extra={"contract_id": contract_id})

        contract = EmployeeContract.objects.get(id=contract_id)

        # Check if contract has associated payslips
        if hasattr(contract, 'payslips') and contract.payslips.exists():
            logger.warning(
                "[Contracts] Cannot delete contract with payslips",
                extra={"contract_id": contract_id}
            )
            raise ValidationError(
                "Cannot delete contract that has generated payslips. Deactivate instead."
            )

        contract_id_log = contract.id
        contract.delete()

        logger.info("[Contracts] Contract deleted", extra={"contract_id": contract_id_log})

    # ===== QUERY OPERATIONS =====

    @classmethod
    def get_active_contract(cls, employee_id: UUID) -> EmployeeContract:
        """
        Get the currently active contract for an employee.
        """
        logger.debug("[Contracts] Getting active contract", extra={"employee_id": employee_id})

        return EmployeeContract.objects.select_related(
            'employee',
            'employee__user',
        ).get(
            employee_id=employee_id,
            is_active=True,
        )

    @classmethod
    def get_employee_contract_history(cls, employee_id: UUID) -> QuerySet:
        """
        Get complete contract history for an employee.
        Returns all contracts (active and inactive) ordered by start date (newest first).
        """
        logger.debug("[Contracts] Getting contract history", extra={"employee_id": employee_id})

        # Verify employee exists
        Employee.objects.get(id=employee_id)

        return EmployeeContract.objects.filter(
            employee_id=employee_id,
        ).select_related(
            'employee',
            'employee__user',
        ).order_by('-start_date')

    @classmethod
    def get_current_salary(cls, employee_id: UUID) -> Decimal:
        """
        Get the current salary/rate from the active contract.
        """
        logger.debug("[Contracts] Getting current salary", extra={"employee_id": employee_id})

        contract = cls.get_active_contract(employee_id)
        return contract.amount

    @classmethod
    def get_contract_on_date(cls, employee_id: UUID, target_date: date) -> EmployeeContract:
        """
        Get the contract that was active on a specific date.
        Useful for historical payroll calculations.
        """
        logger.debug(
            "[Contracts] Getting contract on date",
            extra={"employee_id": employee_id, "date": target_date}
        )

        from django.db.models import Q

        return EmployeeContract.objects.get(
            Q(employee_id=employee_id) &
            Q(start_date__lte=target_date) &
            (Q(end_date__isnull=True) | Q(end_date__gte=target_date))
        )

    @classmethod
    def count_active_contracts(cls, employee_id: UUID) -> int:
        """
        Count active contracts for an employee (should be 0 or 1).
        """
        logger.debug("[Contracts] Counting active contracts", extra={"employee_id": employee_id})

        return EmployeeContract.objects.filter(
            employee_id=employee_id,
            is_active=True,
        ).count()

    @classmethod
    def get_contracts_by_remuneration_type(
        cls,
        remuneration_type: str,
        is_active_only: bool = True
    ) -> QuerySet:
        """
        Get all contracts of a specific remuneration type.
        """
        logger.debug(
            "[Contracts] Getting contracts by remuneration",
            extra={"type": remuneration_type, "active_only": is_active_only}
        )

        qs = EmployeeContract.objects.filter(
            remuneration_type=remuneration_type,
        )

        if is_active_only:
            qs = qs.filter(is_active=True)

        return qs.select_related('employee', 'employee__user')

