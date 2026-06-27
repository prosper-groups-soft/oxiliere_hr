from __future__ import annotations
import logging
from datetime import date, timedelta
from typing import List

from django.db.models import Q

from hr.attendance.models import (
    TimeSheet,
    EmploymentScheme,
    ShiftAssignment,
    ShiftDetail,
)
from hr.employees.models import Employee
from hr.attendance.schemas import (
    DailyViewFilter,
    DailyViewEntryOut,
)
from hr.attendance.services import (
    AttendanceService,
    AttendanceCacheService,
)
from hr.attendance.services.scheduling import SchedulingService
from hr.calendar.services import CalendarService
from hr.jobs.models import EmployeePositionHistory


logger = logging.getLogger(__name__)


class DailyViewService:
    """
    Service responsible for building the enriched daily attendance view.
    Encapsulates all business logic previously in the controller's get_daily_view.
    """

    @staticmethod
    def build_daily_view(filters: DailyViewFilter) -> List[DailyViewEntryOut]:
        """
        Builds the enriched daily attendance view for a given date.
        """
        # 1. Ensure the daily register exists
        register = AttendanceService.get_or_create_daily_register(filters.date)

        # 2. Find all employees with an active scheme for this date
        employee_ids = DailyViewService._get_active_employee_ids(filters.date)
        employees = Employee.objects.filter(id__in=employee_ids).only(
            'id', 'first_name', 'last_name', 'middle_name', 'profile_photo'
        )

        # 3. Pre-fetch current positions for org unit info
        positions = DailyViewService._get_positions_by_employee(employee_ids)

        country_code = getattr(employees.first(), 'nationality', 'CD') if employees else 'CD'
        is_holiday = CalendarService.is_non_working_day(filters.date, country_code)

        entries = []
        for emp in employees:
            entry = DailyViewService._build_entry(
                emp, filters.date, register, positions
            )

            # Apply client-side filters
            if not DailyViewService._passes_filters(entry, filters):
                continue

            entries.append(entry)

        return entries

    @staticmethod
    def _get_active_employee_ids(target_date: date) -> List:
        """Returns distinct employee IDs with an active scheme for the given date."""
        active_schemes = EmploymentScheme.objects.filter(
            is_active=True,
            valid_from__lte=target_date,
        ).filter(
            Q(valid_until__gte=target_date) | Q(valid_until__isnull=True)
        )
        return list(active_schemes.values_list('employee_id', flat=True).distinct())

    @staticmethod
    def _get_positions_by_employee(employee_ids: List):
        """Pre-fetches current positions for all given employees."""
        return {
            p.employee_id: p
            for p in EmployeePositionHistory.objects.filter(
                employee_id__in=employee_ids,
                is_current=True
            ).select_related('org_unit', 'position')
        }

    @staticmethod
    def _build_entry(emp, target_date, register, positions) -> DailyViewEntryOut:
        """Builds a single DailyViewEntryOut for one employee."""
        # Get or create timesheet
        timesheet, _ = TimeSheet.objects.get_or_create(
            employee=emp,
            register=register,
        )

        # Get punches via the timesheet (TimePunch → timesheet FK)
        punches = list(timesheet.punches.all().order_by('start_at'))

        check_in, check_out = None, None
        check_in_at, check_out_at = None, None
        check_in_punch_id, check_out_punch_id = None, None
        is_manual = False

        if punches:
            first = punches[0]
            last = punches[-1]
            check_in_at = first.start_at
            check_in = first.start_at.strftime('%H:%M') if first.start_at else None
            check_in_punch_id = first.id
            if last.end_at:
                check_out_at = last.end_at
                check_out = last.end_at.strftime('%H:%M')
            check_out_punch_id = last.id
            is_manual = any(getattr(p, 'is_manual_entry', False) for p in punches)

        # Get expected schedule & source info
        schedule = SchedulingService.get_expected_schedule(emp, target_date)
        expected_in = None
        expected_out = None
        expected_break = None
        is_working_day = False
        schedule_name = None
        schedule_source = "none"

        if schedule is None:
            # Check why: holiday or no scheme?
            country_code = getattr(emp, 'nationality', 'CD')
            if CalendarService.is_non_working_day(target_date, country_code):
                schedule_source = "holiday"
            # else stays "none" (no active scheme or non-working day)
        else:
            is_working_day = schedule.is_working_day

            if schedule.start_time:
                expected_in = (
                    schedule.start_time.strftime('%H:%M')
                    if hasattr(schedule.start_time, 'strftime')
                    else str(schedule.start_time)
                )
            if schedule.end_time:
                expected_out = (
                    schedule.end_time.strftime('%H:%M')
                    if hasattr(schedule.end_time, 'strftime')
                    else str(schedule.end_time)
                )
            if schedule.break_duration:
                try:
                    expected_break = int(schedule.break_duration.total_seconds() / 60)
                except (AttributeError, ValueError):
                    expected_break = None

            # Determine source: override (ShiftAssignment) or policy
            has_override = ShiftAssignment.objects.filter(
                employee=emp, date=target_date
            ).exists()
            if has_override:
                schedule_source = "override"
                schedule_name = schedule.policy.name if schedule.policy else None
            else:
                schedule_source = "policy"
                scheme = SchedulingService.get_active_scheme_for_date(emp, target_date)
                if scheme and scheme.override_policy and \
                   scheme.override_valid_from and scheme.override_valid_from <= target_date and \
                   (scheme.override_valid_until is None or scheme.override_valid_until >= target_date):
                    schedule_name = scheme.override_policy.name
                elif scheme:
                    schedule_name = scheme.policy.name

        # Compute anomalies
        anomalies = DailyViewService._compute_anomalies(schedule, timesheet, check_in)

        # Position / org unit
        pos = positions.get(emp.id)
        org_unit_id = pos.org_unit.id if pos and pos.org_unit else None
        org_unit_name = pos.org_unit.name if pos and pos.org_unit else None
        job_title = pos.position.name if pos and pos.position else None

        # Lock status
        is_locked = timesheet.register.is_finalized
        lock_date = AttendanceCacheService.get_lock_date()
        if lock_date and timesheet.register.date <= lock_date:
            is_locked = True

        return DailyViewEntryOut(
            id=timesheet.id or 0,
            employee_id=emp.id,
            employee_name=emp.full_name or f"{emp.first_name or ''} {emp.last_name or ''}".strip(),
            first_name=emp.first_name,
            last_name=emp.last_name,
            avatar_url=emp.profile_photo.url if emp.profile_photo else None,
            job_title=job_title,
            org_unit_id=org_unit_id,
            org_unit_name=org_unit_name,
            register_date=target_date,
            check_in=check_in,
            check_out=check_out,
            check_in_at=check_in_at,
            check_out_at=check_out_at,
            check_in_punch_id=check_in_punch_id,
            check_out_punch_id=check_out_punch_id,
            is_manual_entry=is_manual,
            expected_in=expected_in,
            expected_out=expected_out,
            expected_break_duration=expected_break,
            is_working_day=schedule.is_working_day if schedule else False,
            schedule_name=schedule_name,
            schedule_source=schedule_source,
            recorded_work=timesheet.recorded_work,
            recorded_break=timesheet.recorded_break,
            overtime=timesheet.overtime,
            shortfall=timesheet.shortfall,
            status=timesheet.status,
            remarks=timesheet.remarks or None,
            is_locked=is_locked,
            is_finalized=timesheet.register.is_finalized,
            anomalies=anomalies,
        )

    @staticmethod
    def _compute_anomalies(schedule, timesheet, check_in) -> list[str]:
        """Computes anomaly flags for a single employee entry."""
        anomalies = []
        if schedule and getattr(schedule, 'is_working_day', False):
            if timesheet.status == 'ABSENT' and not check_in:
                anomalies.append("Absence non justifiée")
            elif timesheet.status == 'LATE':
                anomalies.append("Retard détecté")
            if timesheet.recorded_work > timedelta(hours=16):
                anomalies.append("Travail excessif détecté")
        return anomalies

    @staticmethod
    def _passes_filters(entry: DailyViewEntryOut, filters: DailyViewFilter) -> bool:
        """Applies in-memory search/org_unit/status filters to an entry."""
        if filters.search:
            q = filters.search.lower()
            if q not in entry.employee_name.lower():
                return False
        if filters.org_unit:
            org_unit_id_str = str(entry.org_unit_id) if entry.org_unit_id else None
            if (org_unit_id_str != filters.org_unit
                    and entry.org_unit_name != filters.org_unit):
                return False
        if filters.status:
            if entry.status.upper() != filters.status.upper():
                return False
        return True
