import logging
from hr.recruitment.models import Interview, Application
from hr.enums import ApplicationStatus


logger = logging.getLogger(__name__)


class InterviewService:
    """
    Service responsible for managing interviews,
    including scheduling and feedback submission.
    """

    def schedule_interview(
        self,
        application_id,
        interviewer_id,
        scheduled_at,
        interview_type,
        **kwargs
    ):
        """
        Schedules an interview and automatically updates the application status.
        """
        application = Application.objects.get(id=application_id)
        
        # 1. Interview creation
        interview = Interview.objects.create(
            application=application,
            interviewer_id=interviewer_id,
            scheduled_at=scheduled_at,
            interview_type=interview_type,
            **kwargs
        )
        
        # 2. Automatic application status update
        if application.status != ApplicationStatus.INTERVIEW:
            application.status = ApplicationStatus.INTERVIEW
            application.save()
            
        logger.info(
            f"Interview ({interview_type}) scheduled for candidate {application.candidate}"
        )
        return interview

    def submit_feedback(self, interview_id, score, notes):
        """
        Records the outcome of an interview.
        """
        interview = Interview.objects.get(id=interview_id)
        interview.score = score
        interview.notes = notes
        interview.save()
        return interview

