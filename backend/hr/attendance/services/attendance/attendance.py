from datetime import datetime
import random
import string
from __future__ import annotations
from typing import List
from django.utils import timezone
from hr.attendance.models import (
    Attendance,
    AttendanceEntry,
)
from hr.employees.models import Employee


class AttendanceWriterService:
    """
    Service for creating, updating, and closing Attendance sheets.
    """

    @staticmethod
    def create_sheet(date: datetime.date, name: str | None = None) -> Attendance:
        """
        Create a new Attendance sheet for the given date.
        Generates a code automatically.
        """
        attendance = Attendance(date=date, name=name)
        attendance.code = AttendanceWriterService.generate_code()
        attendance.save()
        return attendance

    @staticmethod
    def generate_code() -> str:
        """
        Generate a lightweight random code for Attendance.
        Format: DDMMYY-XXXXXX
        """
        date_part = timezone.now().strftime("%d%m%y")
        random_part = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        return f"{date_part}-{random_part}"

    @staticmethod
    def close_sheet(attendance: Attendance):
        """
        Mark the given Attendance sheet as closed.
        """
        attendance.closed = True
        attendance.save()

    @staticmethod
    def bulk_create_entries(attendance: Attendance, employees: List[Employee]):
        """
        Create AttendanceEntry records for a list of employees in bulk.
        Check-in time is set to the current time.
        """
        entries = [
            AttendanceEntry(attendance=attendance, employee=e, check_in_time=timezone.now().time())
            for e in employees
        ]
        AttendanceEntry.objects.bulk_create(entries)


class AttendanceReaderService:
    """
    Service for reading Attendance sheets and related entries.
    """

    @staticmethod
    def get_by_date(date: datetime.date) -> Attendance | None:
        """
        Return the Attendance sheet for the given date, or None if not found.
        """
        return Attendance.objects.filter(date=date).first()

    @staticmethod
    def list_all_closed() -> list[Attendance]:
        """
        Return all Attendance sheets marked as closed, ordered by date descending.
        """
        return Attendance.objects.filter(closed=True).order_by("-date")

    @staticmethod
    def list_entries(attendance: Attendance, employee_name: str | None = None, status: str | None = None):
        """
        Return AttendanceEntry queryset for a sheet.
        Optional filters: employee name contains, status.
        """
        qs = attendance.entries.select_related("employee")
        if employee_name:
            qs = qs.filter(employee__name__icontains=employee_name)
        if status:
            qs = qs.filter(status=status)
        return qs

    @staticmethod
    def list_by_date_range(start_date: datetime.date, end_date: datetime.date):
        """
        Return Attendance sheets within a given date range (inclusive).
        """
        return Attendance.objects.filter(date__range=[start_date, end_date])
