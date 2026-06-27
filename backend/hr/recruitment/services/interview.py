import logging
from hr.recruitment.models import Interview, Application
from hr.recruitment.enums import ApplicationStatus


logger = logging.getLogger(__name__)


class InterviewService:
    """
    Service responsible for managing interviews,
    including scheduling and feedback submission.
    """

    def get_all_interviews(self):
        """
        Returns all interviews, ordered by most recent first.
        """
        return Interview.objects.select_related(
            'application', 'application__candidate', 'application__target_position', 'interviewer'
        ).order_by('-scheduled_at')

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

    def submit_feedback(self, interview_id, score, feedback=None, strengths=None, weaknesses=None, would_hire=None, next_steps=None, status=None):
        """
        Records the outcome of an interview.
        Now supports structured feedback fields.
        """
        interview = Interview.objects.get(id=interview_id)
        interview.score = score
        if feedback is not None:
            interview.feedback = feedback
        if strengths is not None:
            interview.strengths = strengths
        if weaknesses is not None:
            interview.weaknesses = weaknesses
        if would_hire is not None:
            interview.would_hire = would_hire
        if next_steps is not None:
            interview.next_steps = next_steps
        if status:
            interview.status = status
        interview.save()
        return interview

    def update_interview(self, interview_id, **kwargs):
        """
        Updates an existing interview's mutable fields.
        Only updates fields that are explicitly provided (not None).
        """
        interview = Interview.objects.get(id=interview_id)

        update_fields = []
        for field in ('interviewer_id', 'scheduled_at', 'interview_type', 'duration_minutes', 'notes', 'location', 'video_link', 'status'):
            if field in kwargs and kwargs[field] is not None:
                setattr(interview, field, kwargs[field])
                update_fields.append(field)

        if update_fields:
            interview.save(update_fields=update_fields)
            logger.info(
                f"Interview {interview_id} updated: {', '.join(update_fields)}"
            )

        return interview

