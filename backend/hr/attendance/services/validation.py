from __future__ import annotations
import logging
from datetime   import timedelta
from django.core.exceptions   import ValidationError
from django.utils.translation import gettext_lazy as _
from hr.attendance.models import TimeSheet
from hr.calendar.services import CalendarService
from hr.utils.geo import calculate_geo_distance
from .scheduling  import SchedulingService
# Cache integration
from .cache import AttendanceCacheService


logger = logging.getLogger(__name__)


class ValidationService:
    """
    Service dedicated to ensuring data integrity and detecting 
    anomalies in employee punches.
    """

    @staticmethod
    def validate_punch_sequence(timesheet: TimeSheet) -> list[str]:
        """
        Analyzes the sequence of punches for a specific timesheet to find logical errors.
        Uses cached punches and schedules to speed up validation.
        """
        errors = []
        
        # 1. Optimization: Use the cache service for punches
        punches = AttendanceCacheService.get_punches_for_date(
            timesheet.employee, 
            timesheet.register.date
        )
        
        if not punches:
            # Note: Being absent isn't necessarily a "validation error" in itself, 
            # but for a manual validation check, it's a useful indicator.
            return []

        last_punch = None
        for punch in punches:
            # A. Overlap detection (Chronological integrity)
            if last_punch and last_punch.end_at and punch.start_at < last_punch.end_at:
                errors.append(
                    _("Overlap detected between {last_type} and {current_type} at {time}.").format(
                        last_type=last_punch.get_punch_type_display(),
                        current_type=punch.get_punch_type_display(),
                        time=punch.start_at.strftime("%H:%M")
                    )
                )

            # B. Unclosed segments detection (except for the very last punch of an ongoing day)
            if punch != punches[-1] and not punch.end_at:
                errors.append(
                    _("Incomplete segment found: {type} started at {time} has no end time.").format(
                        type=punch.get_punch_type_display(),
                        time=punch.start_at.strftime("%H:%M")
                    )
                )
            
            last_punch = punch

        # 2. Excessive duration check (Health & Safety/Error detection)
        if timesheet.recorded_work > timedelta(hours=16):
            errors.append(_("Total recorded work exceeds 16 hours. Please verify for errors."))

        # 3. Break duration anomalies
        schedule = SchedulingService.get_expected_schedule(timesheet.employee, timesheet.register.date)
        if schedule and schedule.break_duration:
            # If they punched a manual break that is longer than the policy
            if timesheet.recorded_break > schedule.break_duration:
                excess = timesheet.recorded_break - schedule.break_duration
                errors.append(
                    _("Break exceedance detected: {duration} extra minutes.")
                    .format(duration=excess.seconds // 60)
                )
        
        # 4. Non-working day check (Policy compliance)
        country_code = getattr(timesheet.employee, 'nationality', 'CD')
        is_non_working_day = CalendarService.is_non_working_day(
            timesheet.register.date, 
            country_code
        )
        if is_non_working_day and timesheet.recorded_work > timedelta(0):
            errors.append(_("Work recorded on a Public Holiday. Verify overtime eligibility."))

        return errors

    @staticmethod
    def detect_orphaned_punches(employee, target_date) -> bool:
        """
        Detects if an employee has punches but no active contract/policy (EmploymentScheme).
        """
        scheme = SchedulingService.get_active_scheme_for_date(employee, target_date)
        punches = AttendanceCacheService.get_punches_for_date(employee, target_date)

        return bool(punches) and not scheme

    @staticmethod
    def can_modify_attendance(timesheet: TimeSheet) -> bool:
        """
        Centralized safety check. 
        Returns False if the record is Locked by Payroll or Finalized by HR.
        """        
        # Rule 1: Global Archive Lock (High Performance Cache check)
        lock_date = AttendanceCacheService.get_lock_date()
        if lock_date and timesheet.register.date <= lock_date:
            return False
            
        # Rule 2: Daily Register Finalization
        if timesheet.register.is_finalized:
            return False

        return True

    @staticmethod
    def validate_geo_location(employee, emp_lat, emp_lon):
        """
        Validates if the employee's current GPS position is within their work site's radius.
        """
        # 1. Verify if the coordinates have been provided by the front-end
        if emp_lat is None or emp_lon is None:
            raise ValidationError(_("GPS coordinates are required to punch."))

        # 2. Retrieve the employee's work site
        work_site = employee.work_site
        if not work_site:
            # If no work site is defined, we can either block or allow.
            # Here, for caution, we allow but log.
            logger.warning(f"Employee {employee.id} has no assigned work site.")
            return

        # 3. Calculate the actual distance
        distance = calculate_geo_distance(
            float(emp_lat), float(emp_lon), 
            float(work_site.latitude), float(work_site.longitude)
        )

        # 4. Compare with the site's allowed radius
        if distance > work_site.allowed_radius:
            raise ValidationError(
                _("Location error: You are {dist}m away from your designated work site. "
                "Maximum allowed is {max_dist}m.")
                .format(dist=int(distance), max_dist=work_site.allowed_radius)
            )

