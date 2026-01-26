import logging
from uuid import UUID
from decimal import Decimal
from datetime import date
from django.db import transaction
from django.core.exceptions import ValidationError

from hr.payroll.models import PayrollAdjustment, EmployeeAdjustment
from hr.employees.models import Employee


logger = logging.getLogger(__name__)


class AdjustmentManagementService:
    """
    Service for managing payroll adjustments and their application to employees.
    
    Responsibilities:
    - Create and update adjustment types (templates)
    - Apply adjustments to specific employees
    - Validate adjustment configurations
    - Track adjustment history
    """

    # ===== ADJUSTMENT TYPE MANAGEMENT =====

    @classmethod
    def get_adjustment_type(cls, adjustment_id: UUID) -> PayrollAdjustment:
        """
        Retrieve a specific adjustment type by ID.
        
        Args:
            adjustment_id: UUID of the adjustment type
            
        Returns:
            PayrollAdjustment instance
            
        Raises:
            PayrollAdjustment.DoesNotExist: If not found
        """
        logger.debug("[AdjustmentService] Getting adjustment type", extra={"adjustment_id": adjustment_id})
        return PayrollAdjustment.objects.get(id=adjustment_id)

    @classmethod
    @transaction.atomic
    def create_adjustment_type(cls, data: dict, actor=None) -> PayrollAdjustment:
        """
        Create a new adjustment type template.
        
        Args:
            data: Dictionary with adjustment details (name, type, calculation_mode, etc.)
            actor: User creating the adjustment
            
        Returns:
            Created PayrollAdjustment instance
            
        Raises:
            ValidationError: If data is invalid
        """
        logger.info(
            "[AdjustmentService] Creating adjustment type",
            extra={"name": data.get('name'), "type": data.get('adjustment_type')},
        )

        # Validation
        if not data.get('name'):
            raise ValidationError("Adjustment name is required")
        
        if not data.get('adjustment_type'):
            raise ValidationError("Adjustment type is required")

        # Create adjustment
        adjustment = PayrollAdjustment.objects.create(**data)
        logger.info(
            "[AdjustmentService] Adjustment type created",
            extra={"adjustment_id": adjustment.id, "name": adjustment.name},
        )

        return adjustment

    @classmethod
    @transaction.atomic
    def update_adjustment_type(cls, adjustment_id: UUID, data: dict, actor=None) -> PayrollAdjustment:
        """
        Update an adjustment type.
        
        Args:
            adjustment_id: UUID of adjustment to update
            data: Dictionary with fields to update
            actor: User making the update
            
        Returns:
            Updated PayrollAdjustment instance
            
        Raises:
            PayrollAdjustment.DoesNotExist: If not found
            ValidationError: If data is invalid
        """
        logger.info("[AdjustmentService] Updating adjustment type", extra={"adjustment_id": adjustment_id})

        adjustment = PayrollAdjustment.objects.get(id=adjustment_id)

        # Update allowed fields
        allowed_fields = ['name', 'adjustment_type', 'calculation_mode', 'amount', 'percentage', 'is_mandatory', 'is_active']
        for field in allowed_fields:
            if field in data:
                setattr(adjustment, field, data[field])

        adjustment.save()
        logger.info("[AdjustmentService] Adjustment type updated", extra={"adjustment_id": adjustment_id})

        return adjustment

    @classmethod
    @transaction.atomic
    def delete_adjustment_type(cls, adjustment_id: UUID, actor=None) -> None:
        """
        Delete an adjustment type (only if no employee adjustments exist).
        
        Args:
            adjustment_id: UUID of adjustment to delete
            actor: User deleting the adjustment
            
        Raises:
            PayrollAdjustment.DoesNotExist: If not found
            ValidationError: If employee adjustments exist
        """
        logger.info("[AdjustmentService] Deleting adjustment type", extra={"adjustment_id": adjustment_id})

        adjustment = PayrollAdjustment.objects.get(id=adjustment_id)

        # Check if any employee adjustments use this type
        employee_count = EmployeeAdjustment.objects.filter(adjustment=adjustment).count()
        if employee_count > 0:
            raise ValidationError(f"Cannot delete: {employee_count} employee adjustments use this type")

        adjustment_name = adjustment.name
        adjustment.delete()
        logger.info("[AdjustmentService] Adjustment type deleted", extra={"name": adjustment_name})

    # ===== EMPLOYEE ADJUSTMENT MANAGEMENT =====

    @classmethod
    def get_employee_adjustments(cls, employee_id: UUID) -> list[EmployeeAdjustment]:
        """
        Get all adjustments for a specific employee.
        
        Args:
            employee_id: UUID of employee
            
        Returns:
            List of EmployeeAdjustment instances
        """
        logger.debug("[AdjustmentService] Getting employee adjustments", extra={"employee_id": employee_id})

        return EmployeeAdjustment.objects.filter(
            employee_id=employee_id
        ).select_related('adjustment').order_by('-start_date')

    @classmethod
    def get_employee_adjustment(cls, adjustment_id: UUID) -> EmployeeAdjustment:
        """
        Retrieve a specific employee adjustment by ID.
        
        Args:
            adjustment_id: UUID of the employee adjustment
            
        Returns:
            EmployeeAdjustment instance
            
        Raises:
            EmployeeAdjustment.DoesNotExist: If not found
        """
        logger.debug("[AdjustmentService] Getting employee adjustment", extra={"adjustment_id": adjustment_id})

        return EmployeeAdjustment.objects.select_related('adjustment').get(id=adjustment_id)

    @classmethod
    @transaction.atomic
    def create_employee_adjustment(cls, data: dict, actor=None) -> EmployeeAdjustment:
        """
        Apply an adjustment to a specific employee.
        
        Args:
            data: Dictionary with employee_id, adjustment_id, amount, dates, etc.
            actor: User creating the adjustment
            
        Returns:
            Created EmployeeAdjustment instance
            
        Raises:
            ValidationError: If data is invalid
        """
        logger.info(
            "[AdjustmentService] Creating employee adjustment",
            extra={"employee_id": data.get('employee'), "adjustment_id": data.get('adjustment')},
        )

        # Validate employee exists
        employee_id = data.get('employee')
        if not employee_id:
            raise ValidationError("Employee is required")

        try:
            Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            raise ValidationError("Employee not found")

        # Validate adjustment exists
        adjustment_id = data.get('adjustment')
        if not adjustment_id:
            raise ValidationError("Adjustment type is required")

        try:
            PayrollAdjustment.objects.get(id=adjustment_id)
        except PayrollAdjustment.DoesNotExist:
            raise ValidationError("Adjustment type not found")

        # Validate dates if provided
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date must be before end date")

        # Create employee adjustment
        adjustment = EmployeeAdjustment.objects.create(**data)
        logger.info(
            "[AdjustmentService] Employee adjustment created",
            extra={"adjustment_id": adjustment.id, "employee_id": employee_id},
        )

        return adjustment

    @classmethod
    @transaction.atomic
    def update_employee_adjustment(cls, adjustment_id: UUID, data: dict, actor=None) -> EmployeeAdjustment:
        """
        Update an employee adjustment.
        
        Args:
            adjustment_id: UUID of adjustment to update
            data: Dictionary with fields to update
            actor: User making the update
            
        Returns:
            Updated EmployeeAdjustment instance
            
        Raises:
            EmployeeAdjustment.DoesNotExist: If not found
            ValidationError: If data is invalid
        """
        logger.info("[AdjustmentService] Updating employee adjustment", extra={"adjustment_id": adjustment_id})

        adjustment = EmployeeAdjustment.objects.get(id=adjustment_id)

        # Validate dates if provided
        start_date = data.get('start_date') or adjustment.start_date
        end_date = data.get('end_date') or adjustment.end_date

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date must be before end date")

        # Update allowed fields
        allowed_fields = ['start_date', 'end_date', 'custom_amount', 'is_active']
        for field in allowed_fields:
            if field in data:
                setattr(adjustment, field, data[field])

        adjustment.save()
        logger.info("[AdjustmentService] Employee adjustment updated", extra={"adjustment_id": adjustment_id})

        return adjustment

    @classmethod
    @transaction.atomic
    def delete_employee_adjustment(cls, adjustment_id: UUID, actor=None) -> None:
        """
        Remove an adjustment from an employee.
        
        Args:
            adjustment_id: UUID of adjustment to delete
            actor: User deleting the adjustment
            
        Raises:
            EmployeeAdjustment.DoesNotExist: If not found
        """
        logger.info("[AdjustmentService] Deleting employee adjustment", extra={"adjustment_id": adjustment_id})

        adjustment = EmployeeAdjustment.objects.get(id=adjustment_id)

        emp_id = adjustment.employee_id
        adj_type = adjustment.adjustment_id

        adjustment.delete()
        logger.info(
            "[AdjustmentService] Employee adjustment deleted",
            extra={"employee_id": emp_id, "adjustment_id": adj_type},
        )

    # ===== ACTIVE ADJUSTMENTS FOR PAYROLL =====

    @classmethod
    def get_active_adjustments_for_employee(
        cls,
        employee_id: UUID,
        payroll_date: date,
    ) -> list[EmployeeAdjustment]:
        """
        Get active adjustments for an employee on a specific payroll date.
        
        Args:
            employee_id: UUID of employee
            payroll_date: The payroll period date
            
        Returns:
            List of active EmployeeAdjustment instances
        """
        logger.debug(
            "[AdjustmentService] Getting active adjustments for payroll",
            extra={"employee_id": employee_id, "payroll_date": payroll_date},
        )

        from django.db.models import Q
        
        return EmployeeAdjustment.objects.filter(
            Q(employee_id=employee_id) &
            Q(is_active=True) &
            Q(start_date__lte=payroll_date) &
            (Q(end_date__isnull=True) | Q(end_date__gte=payroll_date))
        ).select_related('adjustment').order_by('created_at')

    @classmethod
    def calculate_adjustment_amount(
        cls,
        employee_adjustment: EmployeeAdjustment,
        gross_salary: Decimal = None,
    ) -> Decimal:
        """
        Calculate the actual amount for an adjustment.
        
        Args:
            employee_adjustment: The EmployeeAdjustment instance
            gross_salary: Gross salary if percentage-based calculation needed
            
        Returns:
            Decimal amount to apply
        """
        # If custom amount is set, use it
        if employee_adjustment.custom_amount:
            return employee_adjustment.custom_amount

        # Otherwise, calculate based on adjustment type
        adjustment = employee_adjustment.adjustment

        if adjustment.calculation_mode == 'FIXED_AMOUNT' and adjustment.amount:
            return adjustment.amount

        if adjustment.calculation_mode == 'PERCENTAGE' and adjustment.percentage and gross_salary:
            percentage = Decimal(str(adjustment.percentage)) / Decimal('100')
            return (gross_salary * percentage).quantize(Decimal('0.01'))

        return Decimal('0.00')
