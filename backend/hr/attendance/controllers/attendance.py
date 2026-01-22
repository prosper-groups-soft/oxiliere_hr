import logging
from typing import List
from uuid import UUID

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from ninja import Query
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    paginate,
    ControllerBase,
)

from oxutils.pagination.cursor import CursorPagination

from hr.employees.models import Employee
from hr.attendance.models import TimeSheet
from hr.attendance.schemas import (
    PunchCreateIn,
    PunchOut,
    TimeSheetOut,
    TimeSheetFilter,
    CanModifyOut,
)

from hr.attendance.services import AttendanceService, ValidationService
from injector import inject


logger = logging.getLogger(__name__)


@api_controller('/attendance', tags=['Attendance & Timesheets'])
class AttendanceController(ControllerBase):
    """
    API controller responsible for attendance operations:
    - Punch in / punch out
    - Timesheet listing
    - Timesheet modification eligibility checks
    """

    @inject
    def __init__(
        self,
        attendance_service: AttendanceService,
        validation_service: ValidationService,
    ):
        # Inject domain services (business logic stays outside the controller)
        self.attendance_service = attendance_service
        self.validation_service = validation_service

    # Punch creation (clock-in / clock-out)
    # -----------------------------------------------------------------
    @http_post('/punch', response={201: PunchOut})
    def create_punch(self, data: PunchCreateIn):
        """
        Create a punch (clock-in or clock-out) for the authenticated employee.
        """
        # Retrieve the authenticated user
        actor = self.context.request.user

        # Trace incoming punch request (low-level, non-critical)
        logger.debug(
            "Punch request received",
            extra={
                "user_id": actor.id,
                "timestamp": data.timestamp,
                "punch_type": data.punch_type,
                "is_manual": data.is_manual,
            },
        )

        # Resolve employee linked to the authenticated user
        employee = get_object_or_404(Employee, user=actor)

        try:
            # Delegate punch processing to the attendance service
            punch = self.attendance_service.process_punch(
                employee=employee,
                timestamp=data.timestamp,
                punch_type=data.punch_type,
                is_manual=data.is_manual,
            )

            # Business-level success log
            logger.info(
                "Punch successfully processed",
                extra={
                    "employee_id": employee.id,
                    "punch_id": punch.id,
                    "punch_type": punch.punch_type,
                    "timestamp": punch.timestamp,
                },
            )

            return 201, punch

        except ValidationError as e:
            # Expected business rule violation (no stack trace needed)
            logger.warning(
                "Punch validation failed",
                extra={
                    "employee_id": employee.id,
                    "error": e.message,
                },
            )
            return self.create_response(
                {"detail": str(e.message)},
                status_code=400,
            )

        except Exception:
            # Unexpected error → full stack trace for observability
            logger.exception(
                "Unexpected error while processing punch",
                extra={"employee_id": employee.id},
            )
            raise

    # Timesheet listing (paginated)
    # -----------------------------------------------------------------
    @http_get('/timesheets', response=List[TimeSheetOut])
    @paginate(CursorPagination)
    def list_timesheets(self, filters: TimeSheetFilter = Query(...)):
        """
        Return a paginated list of timesheets based on filter criteria.
        """
        # Log filter usage for debugging and audit purposes
        logger.debug(
            "Timesheet list requested",
            extra={"filters": filters.model_dump()},
        )

        # Optimize query to avoid N+1 issues
        qs = TimeSheet.objects.select_related(
            'employee',
            'register',
        ).all()

        # Apply filter logic encapsulated in the schema
        return filters.filter(qs)

    # Timesheet modification eligibility
    # -----------------------------------------------------------------
    @http_get('/timesheets/{timesheet_id}/can-modify', response=CanModifyOut)
    def check_modification_status(self, timesheet_id: UUID):
        """
        Determine whether a timesheet can still be modified according
        to business rules (period closure, validation state, etc.).
        """
        # Trace access to modification check endpoint
        logger.debug(
            "Checking timesheet modification rights",
            extra={"timesheet_id": str(timesheet_id)},
        )

        # Load the target timesheet
        timesheet = get_object_or_404(TimeSheet, id=timesheet_id)

        # Delegate decision logic to the validation service
        can_modify, reason = self.validation_service.can_modify_attendance(
            timesheet.employee,
            timesheet.register_date,
        )

        # Log the outcome for audit and traceability
        logger.info(
            "Timesheet modification check completed",
            extra={
                "timesheet_id": str(timesheet_id),
                "employee_id": timesheet.employee.id,
                "can_modify": can_modify,
                "reason": reason,
            },
        )

        return {
            "can_modify": can_modify,
            "reason": reason,
        }
