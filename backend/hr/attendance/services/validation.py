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
    """ Ensures attendance data integrity and detects punch anomalies. """

    @staticmethod
    def validate_punch_sequence(timesheet: TimeSheet) -> list[str]:
        """ Analyzes the sequence of punches for logical errors or overlaps. """
        errors = []
        punches = AttendanceCacheService.get_punches_for_date(
            timesheet.employee, 
            timesheet.register.date
        )
        
        if not punches:
            return []

        last_punch = None
        for punch in punches:
            if last_punch and last_punch.end_at and punch.start_at < last_punch.end_at:
                errors.append(
                    _("Overlap detected between {last_type} and {current_type} at {time}.").format(
                        last_type=last_punch.get_punch_type_display(),
                        current_type=punch.get_punch_type_display(),
                        time=punch.start_at.strftime("%H:%M")
                    )
                )

            if punch != punches[-1] and not punch.end_at:
                errors.append(
                    _("Incomplete segment found: {type} started at {time} has no end time.").format(
                        type=punch.get_punch_type_display(),
                        time=punch.start_at.strftime("%H:%M")
                    )
                )
            
            last_punch = punch

        if timesheet.recorded_work > timedelta(hours=16):
            errors.append(_("Total recorded work exceeds 16 hours. Please verify for errors."))

        schedule = SchedulingService.get_expected_schedule(timesheet.employee, timesheet.register.date)
        if schedule and schedule.break_duration:
            if timesheet.recorded_break > schedule.break_duration:
                excess = timesheet.recorded_break - schedule.break_duration
                errors.append(
                    _("Break exceedance detected: {duration} extra minutes.")
                    .format(duration=excess.seconds // 60)
                )
        
        country_code = getattr(timesheet.employee, 'nationality', 'CD')
        if CalendarService.is_non_working_day(timesheet.register.date, country_code) and timesheet.recorded_work > timedelta(0):
            errors.append(_("Work recorded on a Public Holiday. Verify overtime eligibility."))

        return errors

    @staticmethod
    def detect_orphaned_punches(employee, target_date) -> bool:
        """ Detects if punches exist for dates without an active employment scheme. """
        scheme = SchedulingService.get_active_scheme_for_date(employee, target_date)
        punches = AttendanceCacheService.get_punches_for_date(employee, target_date)
        return bool(punches) and not scheme

    @staticmethod
    def can_modify_attendance(timesheet: TimeSheet) -> bool:
        """ Verifies if attendance records can still be modified based on locks and finalization. """        
        lock_date = AttendanceCacheService.get_lock_date()
        if lock_date and timesheet.register.date <= lock_date:
            return False
            
        return not timesheet.register.is_finalized

    @staticmethod
    def validate_geo_location(employee, emp_lat, emp_lon):
        """ Validates if the punch location is within the allowed work site radius. """
        if emp_lat is None or emp_lon is None:
            raise ValidationError(_("GPS coordinates are required to punch."))

        work_site = employee.work_site
        if not work_site:
            logger.warning(f"Employee {employee.id} has no assigned work site.")
            return

        distance = calculate_geo_distance(
            float(emp_lat), float(emp_lon), 
            float(work_site.latitude), float(work_site.longitude)
        )

        if distance > work_site.allowed_radius:
            raise ValidationError(
                _("Location error: You are {dist}m away from your designated work site. "
                "Maximum allowed is {max_dist}m.")
                .format(dist=int(distance), max_dist=work_site.allowed_radius)
            )

