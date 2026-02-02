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
    """ Manages professional development, certification monitoring, and skill aggregation. """

    @inject
    def __init__(self, dev_service: DevelopmentService):
        self.dev_service = dev_service

    @http_post('/training/{employee_id}', response={201: TrainingOut})
    def add_training_record(self, employee_id: UUID, data: TrainingRecordIn):
        """ Logs a professional training session or certification for an employee. """
        logger.info(f"Recording training '{data.name}' for employee {employee_id}")

        training = self.dev_service.record_training(
            employee_id=employee_id,
            **data.model_dump()
        )
        return 201, training

    @http_get('/expirations/upcoming', response=List[TrainingOut])
    @paginate(CursorPagination)
    def list_upcoming_expirations(self, days: int = 30):
        """ Identifies certifications approaching their expiry date. """
        return self.dev_service.get_upcoming_expirations(days=days)

    @http_get('/expirations/expired', response=List[TrainingOut])
    @paginate(CursorPagination)
    def list_expired_certifications(self):
        """ Lists all certifications that are no longer valid. """
        return self.dev_service.get_expired_certifications()

    @http_get('/skills-matrix/{employee_id}', response=dict)
    def get_employee_skills_profile(self, employee_id: UUID):
        """ Provides a summary of an employee's professional profile and active skills. """
        return self.dev_service.get_employee_skills_matrix(employee_id)

