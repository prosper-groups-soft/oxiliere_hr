import logging
from injector import inject

from ninja_extra import (
    api_controller,
    http_post,
    ControllerBase
)

from hr.attendance.schemas import (
    MaintenanceDateIn,
    ClosePunchesOut,
    FlagAbsencesOut
)
from hr.attendance.models   import TimePunch, TimeSheet
from hr.employees.models    import Employee
from hr.attendance.services import (
    AutoClosingService,
)


logger = logging.getLogger(__name__)


@api_controller('/attendance/maintenance', tags=['Maintenance'])
class MaintenanceController(ControllerBase):
    """ HR administration endpoints for maintaining attendance data integrity. """

    @inject
    def __init__(self, autoclosing_service: AutoClosingService):
        self.autoclosing_service = autoclosing_service

    @http_post('/close-pending-punches', response={200: ClosePunchesOut})
    def close_pending_punches(self, data: MaintenanceDateIn):
        """ Automatically closes all open punches for a given date. """
        logger.info(
            "Closing pending punches requested",
            extra={"date": data.date}
        )

        open_punches_before = TimePunch.objects.filter(
            timesheet__register__date=data.date,
            end_at__isnull=True
        ).select_related('timesheet__employee')

        affected_employee_ids = set(
            punch.timesheet.employee_id 
            for punch in open_punches_before
        )
        
        closed_count = open_punches_before.count()

        self.autoclosing_service.close_pending_punches(data.date)

        affected_employees = []
        if affected_employee_ids:
            affected_employees = list(
                Employee.objects.filter(id__in=affected_employee_ids)
            )

        details = [
            {
                "employee_id": str(punch.timesheet.employee_id),
                "punch_id": str(punch.id),
                "started_at": punch.start_at.isoformat()
            }
            for punch in open_punches_before
        ]

        logger.info(
            "Pending punches closed successfully",
            extra={
                "date": data.date,
                "closed_count": closed_count,
                "affected_employees": len(affected_employees)
            }
        )

        return {
            "closed_count": closed_count,
            "affected_employees": affected_employees,
            "details": details
        }

    @http_post('/flag-absences', response={200: FlagAbsencesOut})
    def flag_unrecorded_absences(self, data: MaintenanceDateIn):
        """ Identifies and flags employees who are expected to work but have no punches. """
        logger.info(
            "Flagging unrecorded absences requested",
            extra={"date": data.date}
        )

        timesheets_before = TimeSheet.objects.filter(
            register__date=data.date
        ).count()

        self.autoclosing_service.flag_unrecorded_absences(data.date)

        timesheets_after = TimeSheet.objects.filter(
            register__date=data.date
        ).select_related('employee')

        flagged_count = timesheets_after.count() - timesheets_before

        newly_flagged = list(timesheets_after.order_by('-created_at')[:flagged_count])
        
        absent_employees = [ts.employee for ts in newly_flagged]

        details = [
            {
                "employee_id": str(ts.employee_id),
                "timesheet_id": str(ts.id),
                "status": ts.status
            }
            for ts in newly_flagged
        ]

        logger.info(
            "Absences flagged successfully",
            extra={
                "date": data.date,
                "flagged_count": flagged_count,
                "absent_employees": len(absent_employees)
            }
        )

        return {
            "flagged_count": flagged_count,
            "absent_employees": absent_employees,
            "details": details
        }

