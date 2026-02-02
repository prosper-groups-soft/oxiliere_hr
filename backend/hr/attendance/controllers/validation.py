import logging
from uuid import UUID
from injector import inject

from ninja_extra import (
    api_controller,
    http_post,
    ControllerBase
)

from django.shortcuts import get_object_or_404

from hr.attendance.schemas import (
    TimesheetValidationIn,
    TimesheetValidationOut
)
from hr.attendance.models import TimeSheet
from hr.attendance.services import ValidationService


logger = logging.getLogger(__name__)


@api_controller('/attendance/validation', tags=['Validation'])
class ValidationController(ControllerBase):
    """ HR tools for quality control and attendance data auditing. """

    @inject
    def __init__(self, validation_service: ValidationService):
        self.validation_service = validation_service

    @http_post('/check-timesheet', response={200: TimesheetValidationOut})
    def validate_timesheet(self, data: TimesheetValidationIn):
        """ Validates a timesheet for consistency, overlapping punches, and policy compliance. """
        logger.info(
            "Timesheet validation requested",
            extra={"timesheet_id": data.timesheet_id}
        )

        timesheet = get_object_or_404(TimeSheet, id=data.timesheet_id)
        errors = self.validation_service.validate_punch_sequence(timesheet)

        is_valid = len(errors) == 0
        warnings = []

        timesheet_summary = {
            "date": timesheet.register.date.isoformat(),
            "employee_id": str(timesheet.employee_id),
            "employee_name": f"{timesheet.employee.first_name} {timesheet.employee.last_name}",
            "total_work": str(timesheet.recorded_work),
            "total_break": str(timesheet.recorded_break),
            "overtime": str(timesheet.overtime),
            "shortfall": str(timesheet.shortfall),
            "status": timesheet.status
        }

        logger.info(
            "Timesheet validation completed",
            extra={
                "timesheet_id": data.timesheet_id,
                "is_valid": is_valid,
                "error_count": len(errors)
            }
        )

        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "timesheet_summary": timesheet_summary
        }

