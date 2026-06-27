import logging
from decimal  import Decimal
from datetime import date
from typing   import Dict, Any, Optional
from uuid     import UUID
from django.utils import timezone

from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db.models       import QuerySet
from datetime import timedelta

from hr.payroll.models   import EmployeeContract
from hr.employees.models import Employee


logger = logging.getLogger(__name__)


class EmployeeContractService:
    """
    Manages employee employment contracts.

    Responsibilities:
    - Create new employment contracts
    - Update contract terms (salary, remuneration type, dates)
    - Deactivate contracts (employee termination via end_date)
    - Query contract history and current status
    - Contracts are considered "active" when: start_date <= today AND (end_date IS NULL OR end_date >= today)
    - Audit trail with actor tracking
    """

    @classmethod
    def _is_currently_active_filter(cls):
        today = timezone.localdate()
        return Q(start_date__lte=today) & (Q(end_date__isnull=True) | Q(end_date__gte=today))

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
        Automatically terminates any currently active contract by setting its end_date.
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

        # Validate dates
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date:
            if start_date >= end_date:
                logger.warning("[Contracts] Invalid date range")
                raise ValidationError("start_date must be before end_date")

        today = timezone.localdate()
        active_filter = Q(employee_id=employee.id) & Q(start_date__lte=today) & (Q(end_date__isnull=True) | Q(end_date__gte=today))
        previous_active = EmployeeContract.objects.filter(active_filter)
        if previous_active.exists():
            effective_end = (start_date - timedelta(days=1)) if start_date else today
            logger.info(
                "[Contracts] Terminating previous contracts",
                extra={"employee_id": employee.id, "count": previous_active.count()}
            )
            previous_active.update(end_date=effective_end)

        # Create contract
        contract = EmployeeContract.objects.create(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            remuneration_type=data.get('remuneration_type', 'FIXED'),
            base_salary=data.get('base_salary'),
            hourly_rate=data.get('hourly_rate'),
            currency=data.get('currency', 'CDF'),
            contract_type=data.get('contract_type', 'CDI'),
            payment_period=data.get('payment_period', 'MONTHLY'),
            salary_base_type=data.get('salary_base_type', 'GROSS'),
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

        # Validate and update salary fields
        if 'base_salary' in data:
            base_salary = data['base_salary']
            if base_salary is not None:
                val = Decimal(str(base_salary))
                if val <= 0:
                    raise ValidationError("Base salary must be positive")
                contract.base_salary = val

        if 'hourly_rate' in data:
            hourly_rate = data['hourly_rate']
            if hourly_rate is not None:
                val = Decimal(str(hourly_rate))
                if val <= 0:
                    raise ValidationError("Hourly rate must be positive")
                contract.hourly_rate = val

        # Update other fields
        if 'start_date' in data:
            contract.start_date = data['start_date']
        if 'end_date' in data:
            # If setting a new end_date, ensure it doesn't conflict with existing active status
            if data['end_date'] and data['end_date'] < timezone.localdate():
                # Ending in the past is a termination
                pass
            contract.end_date = data['end_date']
        if 'remuneration_type' in data:
            contract.remuneration_type = data['remuneration_type']
        if 'payment_period' in data:
            contract.payment_period = data['payment_period']
        if 'salary_base_type' in data:
            contract.salary_base_type = data['salary_base_type']
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
        Sets end_date to today if not already set.
        Also marks the employee as inactive.
        """
        logger.debug("[Contracts] Deactivating contract", extra={"contract_id": contract_id})

        contract = EmployeeContract.objects.get(id=contract_id)

        # Check if already ended
        if contract.end_date and contract.end_date < date.today():
            logger.warning("[Contracts] Contract already terminated", extra={"contract_id": contract_id})
            raise ValidationError("Contract is already terminated")

        # Set end_date to today if not already set
        if not contract.end_date:
            contract.end_date = date.today()

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
        Active = start_date <= today AND (end_date IS NULL OR end_date >= today)
        """
        logger.debug("[Contracts] Getting active contract", extra={"employee_id": employee_id})

        return EmployeeContract.objects.select_related(
            'employee',
            'employee__user',
        ).get(
            Q(employee_id=employee_id) & cls._is_currently_active_filter()
        )

    @classmethod
    def get_latest_contract(cls, employee_id: UUID) -> Optional[EmployeeContract]:
        """
        Get the latest contract for an employee (newest start_date first).
        """
        logger.debug("[Contracts] Getting latest contract", extra={"employee_id": employee_id})

        return EmployeeContract.objects.select_related(
            'employee',
            'employee__user',
        ).filter(
            employee_id=employee_id
        ).order_by('-start_date').first()

    @classmethod
    def get_employee_contract_history(cls, employee_id: UUID) -> QuerySet:
        """
        Get complete contract history for an employee.
        Returns all contracts ordered by start date (newest first).
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
        if contract.remuneration_type == 'HOURLY':
            return contract.hourly_rate.amount if contract.hourly_rate else Decimal('0')
        return contract.base_salary.amount if contract.base_salary else Decimal('0')

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
            Q(employee_id=employee_id) & cls._is_currently_active_filter()
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
            qs = qs.filter(cls._is_currently_active_filter())

        return qs.select_related('employee', 'employee__user')
