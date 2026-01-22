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

    @staticmethod
    @transaction.atomic
    def consume(employee, year: int, days: Decimal, leave_request=None, actor=None):
        """
        Consumes leave days using FIFO:
            1. Non-expired carry-over (oldest first)
            2. Annual balance of the given year
        Added logging for audit trail and decimal precision safety.
        """
        remaining = Decimal(str(days))
        total_to_consume = remaining

        # 1. Carry-over FIRST
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

        # 2. Annual balance SECOND
        if remaining > 0:
            balance = LeaveBalance.objects.select_for_update().get(
                employee=employee, year=year
            )
            if balance.remaining_days < remaining:
                raise ValidationError(f"Insufficient balance for year {year}")
            
            balance.used_days += remaining
            balance.save(update_fields=["used_days"])

        # 3. LOG TRANSACTION
        LeaveTransaction.objects.create(
            employee=employee,
            year=year,
            amount=-total_to_consume, # Negative for consumption
            transaction_type=LeaveTransactionTypes.CONSUME,
            leave_request=leave_request,
            created_by=actor,
            reason=f"Consumption of {total_to_consume} days for period in {year}"
        )

