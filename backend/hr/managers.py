from __future__ import annotations

from datetime import timedelta, date
from django.db.models import Sum
from django.db.models import Manager
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.transaction import atomic




class AttendanceManager(Manager):

    def compute_overtime_and_undertime(self, employee, start_date: date, end_date: date) -> timedelta:
        """
        Calculate the total overtime and undertime for a given date range.
        """
        totals = self.filter(
            date__gte=start_date,
            date__lte=end_date,
            entries__employee=employee
        ).aggregate(
            total_overtime=Sum('entries__overtime'),
            total_undertime=Sum('entries__undertime')
        )

        total_overtime = totals['total_overtime'] or timedelta()
        total_undertime = totals['total_undertime'] or timedelta()

        return total_overtime, total_undertime
