import logging
from django.db import transaction
from hr.recruitment.models import Application
from hr.employees.models import Employee
from hr.enums import ApplicationStatus
from .career import CareerService


logger = logging.getLogger(__name__)


class HiringService:
    """
    Service responsible for converting accepted candidates into active employees
    and initializing their career within the organization.
    """

    def __init__(self, career_service: CareerService):
        self.career_service = career_service

    @transaction.atomic
    def hire_candidate(self, application_id, start_date, actor=None):
        """
        Converts an accepted application into a real employee.
        """
        application = Application.objects.select_related(
            'candidate',
            'job_offer'
        ).get(id=application_id)

        candidate = application.candidate
        offer = application.job_offer

        # 1. Create the employee record from the candidate profile
        employee = Employee.objects.create(
            first_name=candidate.first_name,
            middle_name=candidate.middle_name,
            last_name=candidate.last_name,
            email=candidate.email,
            personal_phone=candidate.phone,
            # An employee identifier (e.g. employee number) is often generated automatically
        )

        # 2. Assign the initial position using the Jobs module CareerService
        # The position and department are defined by the job offer
        self.career_service.assign_initial_position(
            employee=employee,
            position_id=offer.target_position.id,
            department_id=offer.department.id,
            start_date=start_date
        )

        # 3. Finalize the application
        application.status = ApplicationStatus.ACCEPTED
        application.save()

        # 4. Handle hiring quotas and automatic job offer closure
        # Count how many candidates have been successfully hired (ACCEPTED) for this offer
        hired_count = Application.objects.filter(
            job_offer=offer, 
            status=ApplicationStatus.ACCEPTED
        ).count()

        # If the number of hires reaches or exceeds the available slots, close the offer
        if offer.slots and hired_count >= offer.slots:
            offer.is_active = False
            offer.is_published = False
            offer.save()
            logger.info(
                f"[HIRE] Job offer '{offer.title}' has been closed. "
                f"Hiring quota reached: {hired_count}/{offer.slots} slots filled."
            )

        logger.info(
            f"[HIRE] {candidate.full_name} is now an employee (ID: {employee.id})"
        )
        return employee

