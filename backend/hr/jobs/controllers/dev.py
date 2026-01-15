import logging
from injector import inject
from uuid import UUID
from typing import List

from ninja.pagination import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    ControllerBase,
)

from oxutils.pagination.cursor import CursorPagination

# Schemas
from hr.jobs.schemas import (
    TrainingOut,
    TrainingRecordIn
)

# Services
from hr.jobs.services import DevelopmentService


logger = logging.getLogger(__name__)


@api_controller('/development', tags=['Skill & Training'])
class DevelopmentController(ControllerBase):
    """
    ORCHESTRATION LAYER - SKILLS & TRAINING
    
    Manages the professional development lifecycle:
    - Recording new certifications
    - Monitoring expiration dates
    - Skill matrix aggregation
    """

    @inject
    def __init__(self, dev_service: DevelopmentService):
        self.dev_service = dev_service

    @http_post('/training/{employee_id}', response={201: TrainingOut})
    def add_training_record(self, employee_id: UUID, data: TrainingRecordIn):
        """
        Logs a completed or ongoing training session for an employee.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Recording training '{data.name}' for employee {employee_id}")

        training = self.dev_service.record_training(
            employee_id=employee_id,
            **data.model_dump() # Injecte name, institute, dates, location, etc.
        )
        return 201, training

    @http_get('/expirations/upcoming', response=List[TrainingOut])
    @paginate(CursorPagination)
    def list_upcoming_expirations(self, days: int = 30):
        """
        Compliance Monitoring: Returns certifications expiring within N days.
        Used by HR to plan renewal campaigns.
        """
        return self.dev_service.get_upcoming_expirations(days=days)

    @http_get('/expirations/expired', response=List[TrainingOut])
    @paginate(CursorPagination)
    def list_expired_certifications(self):
        """
        Critical Risk View: Lists all certifications that have already expired.
        """
        return self.dev_service.get_expired_certifications()

    @http_get('/skills-matrix/{employee_id}', response=dict)
    def get_employee_skills_profile(self, employee_id: UUID):
        """
        Returns a consolidated view of an employee's professional profile:
        Current seniority, active certifications, and experience areas.
        """
        return self.dev_service.get_employee_skills_matrix(employee_id)

