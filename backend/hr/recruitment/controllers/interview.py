import logging
from typing   import List
from injector import inject
from ninja.pagination import paginate
from oxutils.permissions.perms import ScopePermission
from oxutils.pagination.cursor import CursorPagination

from ninja_extra import (
    api_controller,
    http_post,
    http_get,
    http_patch,
    ControllerBase,
)
from django.core.exceptions import ValidationError

from hr.recruitment.schemas import (
    InterviewScheduleIn,
    InterviewFeedbackIn,
    InterviewOut,
)

from hr.recruitment.services import InterviewService


logger = logging.getLogger(__name__)


@api_controller('/recruitment/interviews', tags=['Recruitment - Interviews'])
class InterviewController(ControllerBase):
    """
    Handles interview scheduling and feedback submission.
    Acts as a thin API layer delegating business logic to InterviewService.
    """

    @inject
    def __init__(self, interview_service: InterviewService):
        self.interview_service = interview_service

    @http_get('/', response=List[InterviewOut], permissions=[ScopePermission('recruitment:r')])
    @paginate(CursorPagination)
    def list_interviews(self):
        """
        Lists all interviews.
        """
        logger.info("[API] Listing all interviews")
        return self.interview_service.get_all_interviews()

    @http_post('/', response={201: InterviewOut}, permissions=[ScopePermission('recruitment:w')])
    @inject
    def schedule_new_interview(self, data: InterviewScheduleIn):
        """
        Schedules a new interview and transitions the application
        to the INTERVIEW status.
        """
        logger.info(
            f"[API] Scheduling interview for application {data.application_id} "
            f"(interviewer={data.interviewer_id}, type={data.interview_type})"
        )

        try:
            interview = self.interview_service.schedule_interview(
                application_id=data.application_id,
                interviewer_id=data.interviewer_id,
                scheduled_at=data.scheduled_at,
                interview_type=data.interview_type,
                # Pass remaining optional fields (e.g. duration_minutes)
                **data.model_dump(
                    exclude={
                        'application_id',
                        'interviewer_id',
                        'scheduled_at',
                        'interview_type',
                    }
                )
            )
            return 201, interview

        except ValidationError as e:
            logger.warning(
                f"[API] Validation error while scheduling interview "
                f"for application {data.application_id}: {e}"
            )
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.error(
                f"[API] Unexpected error while scheduling interview "
                f"for application {data.application_id}: {e}",
                exc_info=True,
            )
            return self.create_response(
                {"detail": "An unexpected error occurred."},
                status_code=500,
            )

    @http_patch('/{interview_id}/feedback', response=InterviewOut, permissions=[ScopePermission('recruitment:u')])
    def submit_interview_feedback(self, interview_id: int, data: InterviewFeedbackIn):
        """
        Records the interview score and qualitative feedback
        after the interview has been conducted.
        """
        logger.info(
            f"[API] Submitting feedback for interview {interview_id} "
            f"(score={data.score})"
        )

        try:
            return self.interview_service.submit_feedback(
                interview_id=interview_id,
                score=data.score,
                notes=data.notes,
            )

        except ValidationError as e:
            logger.warning(
                f"[API] Validation error while submitting feedback "
                f"for interview {interview_id}: {e}"
            )
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.error(
                f"[API] Unexpected error while submitting feedback "
                f"for interview {interview_id}: {e}",
                exc_info=True,
            )
            return self.create_response(
                {"detail": "An unexpected error occurred."},
                status_code=500,
            )

