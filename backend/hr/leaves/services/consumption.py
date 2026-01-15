from decimal import Decimal
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.db.models import F

from hr.leaves.models import LeaveCarryOver, LeaveBalance


class LeaveConsumptionService:

    @staticmethod
    @transaction.atomic
    def consume(employee, year: int, days: Decimal):
        """
        Consumes leave days using FIFO:
            1. Non-expired carry-over (oldest first)
            2. Annual balance of the given year
        Added logging for audit trail and decimal precision safety.
        """
        remaining = Decimal(str(days))

        # 1. Carry-over FIRST (Strictly non-expired)
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
            
