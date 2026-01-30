from __future__ import annotations
from datetime import date, timedelta
from uuid import UUID
from django.db.models import Sum, Count, Q
from hr.attendance.models import TimeSheet, TimeSheetStatus
# Cache integration
from hr.services.cache_helpers import cache_query


class AttendanceSummaryService:
    """
    Service providing aggregated attendance metrics for payroll and reporting.
    Optimized to minimize database hits using conditional aggregation and Redis caching.
    """

    @staticmethod
    @cache_query(timeout=3600, key_args=(0, 1, 2)) # Cache during 1h based on ID, start, end
    def get_attendance_summary(employee_id: UUID, start_date: date, end_date: date) -> dict:
        """
        Calculates worked days, hours, and overtime breakdown in a single optimized query.
        Results are cached in Redis to prevent redundant heavy aggregations.
        
        Priority Logic:
        - Status PRESENT/PARTIAL/LATE count as worked days and regular hours.
        - Status HOLIDAY counts specifically towards holiday overtime.
        - ABSENT status is counted separately for payroll deductions.
        """
        
        # Single database hit using conditional aggregation
        summary = TimeSheet.objects.filter(
            employee_id=employee_id,
            register__date__range=(start_date, end_date)
        ).aggregate(
            worked_days=Count('id', filter=Q(status__in=[
                TimeSheetStatus.PRESENT, TimeSheetStatus.PARTIAL, TimeSheetStatus.LATE
            ])),
            absence_days=Count('id', filter=Q(status=TimeSheetStatus.ABSENT)),
            total_work=Sum('recorded_work', filter=Q(status__in=[
                TimeSheetStatus.PRESENT, TimeSheetStatus.PARTIAL, TimeSheetStatus.LATE
            ])),
            std_overtime=Sum('overtime', filter=Q(status__in=[
                TimeSheetStatus.PRESENT, TimeSheetStatus.PARTIAL, TimeSheetStatus.LATE
            ])),
            hld_overtime=Sum('overtime', filter=Q(status=TimeSheetStatus.HOLIDAY))
        )

        def to_hours(td: timedelta | None) -> float:
            """Converts timedelta objects to decimal hours (rounded to 2 units)."""
            if not td: return 0.0
            return round(td.total_seconds() / 3600.0, 2)

        # Return structured data for JSON serialization or Payroll processing
        return {
            'regular_days': summary['worked_days'] or 0,
            'absence_days': summary['absence_days'] or 0,
            'total_worked_hours': to_hours(summary['total_work']),
            'overtime_hours_standard': to_hours(summary['std_overtime']),
            'overtime_hours_holiday': to_hours(summary['hld_overtime']),
        }

