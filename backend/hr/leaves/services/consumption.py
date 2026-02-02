from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.db.models import F

from hr.leaves.models import (
    LeaveCarryOver, 
    LeaveBalance, 
    LeaveTransaction
)

from hr.leaves.enums import LeaveTransactionTypes


class LeaveConsumptionService:
    """ Manages the order and logic of leave day deduction. """

    @staticmethod
    @transaction.atomic
    def consume(employee, year: int, days: Decimal, leave_request=None, actor=None):
        """
        Deducts leave days following the official priority:
        1. Non-expired carry-over days from previous years (first to expire).
        2. Standard annual entitlement for the current year.
        Records the transaction for audit purposes.
        """
        remaining = Decimal(str(days))
        total_to_consume = remaining

        # 1. Deduct from non-expired carry-overs first
        carry_overs = LeaveCarryOver.objects.select_for_update().filter(
            employee=employee,
            expires_at__gte=timezone.now().date(),
            days__gt=F('used_days')
        ).order_by("expires_at")

        for co in carry_overs:
            available = co.days - co.used_days
            consumed = min(available, remaining)
            
            co.used_days += consumed
            co.save(update_fields=["used_days"])
            remaining -= consumed
            if remaining <= 0: break

        # 2. Deduct remaining days from the current year's annual balance
        if remaining > 0:
            balance = LeaveBalance.objects.select_for_update().get(
                employee=employee, year=year
            )
            if balance.remaining_days < remaining:
                raise ValidationError(f"Insufficient leave balance for {year}")
            
            balance.used_days += remaining
            balance.save(update_fields=["used_days"])

        # 3. Log the consumption transaction
        LeaveTransaction.objects.create(
            employee=employee,
            year=year,
            amount=-total_to_consume,
            transaction_type=LeaveTransactionTypes.CONSUME,
            leave_request=leave_request,
            created_by=actor,
            reason=f"Usage of {total_to_consume} leave days"
        )

