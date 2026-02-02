from hr.leaves.models import (
    LeaveBalance, 
    LeaveTransaction, 
    LeaveCarryOver
)
from hr.leaves.enums import LeaveTransactionTypes
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
from datetime import date


class LeaveAdminService:
    """ Provides HR administrators with tools for manual leave balance and carry-over adjustments. """

    @staticmethod
    @transaction.atomic
    def adjust_balance(employee, year: int, amount: Decimal, reason: str, hr_user):
        """
        Manually modifies an employee's annual leave entitlement.
        Accrues or deducts days based on the provided amount and records the change.
        """
        balance = LeaveBalance.objects.select_for_update().get(
            employee=employee, year=year
        )

        if amount < 0 and (balance.remaining_days + amount) < 0:
            raise ValidationError(f"Insufficient days to process a deduction of {abs(amount)}.")

        balance.base_entitlement += amount
        balance.save(update_fields=["base_entitlement"])

        return LeaveTransaction.objects.create(
            employee=employee,
            year=year,
            amount=amount,
            transaction_type=LeaveTransactionTypes.ADJUST,
            reason=f"HR Adjustment: {reason}",
            created_by=hr_user
        )

    @staticmethod
    @transaction.atomic
    def adjust_carry_over(employee, source_year: int, amount: Decimal, reason: str, hr_user, new_expiration=None):
        """
        Manually creates or modifies a leave carry-over record for an employee.
        Adjusts the number of days moved from the previous year.
        """
        target_year = source_year + 1
        
        carry_over, created = LeaveCarryOver.objects.select_for_update().get_or_create(
            employee=employee,
            source_year=source_year,
            defaults={
                'days': Decimal("0.00"),
                'used_days': Decimal("0.00"),
                'expires_at': date(target_year, 3, 31)
            }
        )

        if new_expiration:
            carry_over.expires_at = new_expiration

        carry_over.days += amount
        
        if carry_over.days < 0:
            raise ValidationError("Carry-over balance cannot be negative.")
            
        carry_over.save()

        return LeaveTransaction.objects.create(
            employee=employee,
            year=target_year,
            amount=amount,
            transaction_type=LeaveTransactionTypes.ADJUST,
            reason=f"Carry-over Adjustment (Earned {source_year}): {reason}",
            created_by=hr_user
        )

