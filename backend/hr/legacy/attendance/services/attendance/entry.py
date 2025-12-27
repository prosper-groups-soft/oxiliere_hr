from datetime import datetime, time, timedelta
from hr.attendance.models import (
    Attendance, 
    AttendanceEntry
)
from hr.employees.models import Employee


class AttendanceEntryReaderService:
    """
    Service for reading single employee attendance entries.
    - Search, filter by employee, status, date, or leave.
    - Aggregate durations (total hours, overtime, etc.).
    """

    @staticmethod
    def get_for_employee(
        attendance: Attendance, 
        employee: Employee
    ) -> AttendanceEntry | None:
        return attendance.entries.filter(employee=employee).first()

    @staticmethod
    def filter_entries(
        start_date: datetime.date,
        end_date: datetime.date,
        employee_name: str | None = None,
        status: str | None = None,
    ):
        qs = AttendanceEntry.objects.select_related("employee", "attendance").filter(
            attendance__date__range=[start_date, end_date]
        )
        if employee_name:
            qs = qs.filter(employee__name__icontains=employee_name)
        if status:
            qs = qs.filter(status=status)
        return qs


class AttendanceEntryWriterService:
    """
    Service for creating/updating individual AttendanceEntry records.
    - Compute durations, overtime, undertime based on schedule.
    - Validate closed periods.
    - Apply business rules (lateness, absence policies, leave integration).
    """

    @staticmethod
    def create_entry(
        attendance: Attendance, 
        employee: Employee, 
        check_in: time, 
        check_out: time | None = None
    ) -> AttendanceEntry:
        entry = AttendanceEntry(
            attendance=attendance, 
            employee=employee, 
            check_in_time=check_in, 
            check_out_time=check_out
        )
        AttendanceEntryWriterService.recalculate_entry(entry)
        entry.save()
        return entry

    @staticmethod
    def recalculate_entry(
        entry: AttendanceEntry, 
        scheduled_hours: timedelta | None = None
    ) -> None:
        total, overtime, undertime = entry.recalc_durations(scheduled_hours)
        entry.total_hours = total
        entry.overtime = overtime
        entry.undertime = undertime

    @staticmethod
    def update_status(entry: AttendanceEntry, status: str):
        entry.status = status
        entry.save()

