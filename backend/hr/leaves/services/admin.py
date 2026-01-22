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
    """
    Service for HR administrators to manually adjust leave balances and carry-overs.
    """

    @staticmethod
    @transaction.atomic
    def adjust_balance(employee, year: int, amount: Decimal, reason: str, hr_user):
        """
        Manually adjust an employee's annual balance.
        'amount' can be positive (credit) or negative (debit).
        """
        balance = LeaveBalance.objects.select_for_update().get(
            employee=employee, year=year
        )

        # If the adjustment is negative (withdrawing days),
        # verify that the employee has enough days to avoid a negative balance.
        if amount < 0 and (balance.remaining_days + amount) < 0:
            raise ValidationError(f"Cannot deduct {abs(amount)} days. Employee only has {balance.remaining_days} left.")

        # We adjust the 'base_entitlement' field.
        # Alternatively, a separate adjustment transaction could be used.
        # For simplicity, we modify the entitlement directly.
        balance.base_entitlement += amount
        balance.save(update_fields=["base_entitlement"])

        # 4. LOG TRANSACTION
        return LeaveTransaction.objects.create(
            employee=employee,
            year=year,
            amount=amount,
            transaction_type=LeaveTransactionTypes.ADJUST,
            reason=f"Manual HR Adjustment: {reason}",
            created_by=hr_user
        )

    @staticmethod
    @transaction.atomic
    def adjust_carry_over(employee, source_year: int, amount: Decimal, reason: str, hr_user, new_expiration=None):
        """
        Manually adjust or create a carry-over record for an employee.
        - source_year: The year the leave was earned (usually year - 1).
        - amount: The number of days to ADD to the carry-over.
        - new_expiration: Optional date to extend the validity of these days.
        """
        # Target the destination year (source_year + 1)
        target_year = source_year + 1
        
        carry_over, created = LeaveCarryOver.objects.select_for_update().get_or_create(
            employee=employee,
            source_year=source_year,
            defaults={
                'days': Decimal("0.00"),
                'used_days': Decimal("0.00"),
                'expires_at': date(target_year, 3, 31) # Default expiration if created
            }
        )

        if new_expiration:
            carry_over.expires_at = new_expiration

        # Increase the total carry-over days
        carry_over.days += amount
        
        if carry_over.days < 0:
            raise ValidationError("Carry-over days cannot be negative.")
            
        carry_over.save()

        # LOG TRANSACTION
        return LeaveTransaction.objects.create(
            employee=employee,
            year=target_year,
            amount=amount,
            transaction_type=LeaveTransactionTypes.ADJUST, # Or a specific CARRY_OVER_ADJUST type
            reason=f"Manual Carry-over Adjustment (Source {source_year}): {reason}",
            created_by=hr_user
        )

