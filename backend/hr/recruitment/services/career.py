import logging
from django.db import transaction
from hr.jobs.models import EmployeePositionHistory


logger = logging.getLogger(__name__)


class CareerService:
    """
    Service responsible for managing job assignments and career progression.
    Located within the JOBS module.
    """

    @transaction.atomic
    def assign_initial_position(self, employee, position_id, org_unit_id, start_date):
        """
        Creates the first position history record for a new employee.
        """
        history = EmployeePositionHistory.objects.create(
            employee=employee,
            position_id=position_id,
            org_unit_id=org_unit_id,
            start_date=start_date,
            is_current=True
        )
        logger.info(
            f"[CareerService] Initial position assigned to employee {employee.email}"
        )
        return history

