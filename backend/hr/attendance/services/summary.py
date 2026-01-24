from datetime import date, timedelta
from uuid import UUID
from django.db.models import Sum
from hr.attendance.models import (
    TimeSheet, 
    TimeSheetStatus
)


class AttendanceSummaryService:
    """
    Provides aggregated attendance data for a given period.
    Centralizes query logic to avoid direct model access from other modules.
    """

    @staticmethod
    def get_attendance_summary(employee_id: UUID, start_date: date, end_date: date):
        """
        Calculates worked days and overtime hours for an employee in a specific period.
        """
        # Filter timesheets for the employee and period
        period_sheets = TimeSheet.objects.filter(
            employee_id=employee_id,
            register__date__range=(start_date, end_date)
        )

        # 1. Worked Days (Status is PRESENT, PARTIAL, or LATE)
        worked_days = period_sheets.filter(
            status__in=[TimeSheetStatus.PRESENT, TimeSheetStatus.PARTIAL, TimeSheetStatus.LATE]
        ).count()

        # 2. Total Worked Hours (recorded_work duration)
        total_worked_td = period_sheets.filter(
            status__in=[TimeSheetStatus.PRESENT, TimeSheetStatus.PARTIAL, TimeSheetStatus.LATE]
        ).aggregate(total=Sum('recorded_work'))['total'] or timedelta()

        # 3. Overtime Hours Categorization
        # - Tier 1 & 2 (Standard Workdays)
        standard_overtime = period_sheets.filter(
            status__in=[TimeSheetStatus.PRESENT, 
            TimeSheetStatus.PARTIAL, 
            TimeSheetStatus.LATE]
        ).aggregate(total=Sum('overtime'))['total'] or timedelta()

        # - Tier Holiday (Holidays or Off-days)
        holiday_overtime = period_sheets.filter(
            status__in=[TimeSheetStatus.HOLIDAY]
        ).aggregate(total=Sum('overtime'))['total'] or timedelta()

        # Convert to decimal hours
        def to_hours(td):
            return round(td.total_seconds() / 3600.0, 2)

        return {
            'regular_days': worked_days,
            'total_worked_hours': to_hours(total_worked_td),
            'overtime_hours_standard': to_hours(standard_overtime),
            'overtime_hours_holiday': to_hours(holiday_overtime),
            'absence_days': period_sheets.filter(status=TimeSheetStatus.ABSENT).count()
        }

