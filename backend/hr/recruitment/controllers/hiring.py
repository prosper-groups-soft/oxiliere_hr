import logging
from injector import inject
from django.core.exceptions import ValidationError
from ninja_extra import (
    api_controller, 
    http_post, 
    ControllerBase
)

# Schemas
from hr.recruitment.schemas import HireCandidateIn

# Output schema from the Employee module for consistency
from hr.employees.schemas import EmployeeOut

# Services
from hr.recruitment.services import HiringService


logger = logging.getLogger(__name__)


@api_controller('/recruitment/hiring', tags=['Recruitment - Hiring'])
class HiringController(ControllerBase):
    """
    Handles the final step of the recruitment process.
    Converts an accepted application into a real employee record
    and initializes the employee's career history.
    """

    @inject
    def __init__(self, hiring_service: HiringService):
        self.hiring_service = hiring_service

    @http_post('/{application_id}/execute', response={201: EmployeeOut})
    def hire_candidate(self, application_id: int, data: HireCandidateIn):
        """
        Final action of the recruitment workflow:
        transforms an accepted application into a real employee record
        and creates the initial position history.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info(
            f"[API] Finalizing hiring process for application {application_id} "
            f"by {actor}"
        )

        try:
            employee = self.hiring_service.hire_candidate(
                application_id=application_id,
                start_date=data.start_date,
                actor=actor,
            )
            logger.info(
                f"[API] Hiring completed successfully for application {application_id} "
                f"(employee_id={employee.id})"
            )
            return 201, employee

        except ValidationError as e:
            logger.warning(
                f"[API] Validation error during hiring process "
                f"for application {application_id}: {e}"
            )
            return self.create_response({"detail": str(e)}, status_code=400)

        except Exception as e:
            logger.error(
                f"[API] Critical error during hiring process "
                f"for application {application_id}: {e}",
                exc_info=True,
            )
            return self.create_response(
                {"detail": "Hiring process failed."},
                status_code=500,
            )

