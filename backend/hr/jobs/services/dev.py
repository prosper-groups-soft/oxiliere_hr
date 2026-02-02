from datetime import date
import logging
from uuid import UUID
from typing import Optional, Dict, Any
from django.utils import timezone
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from hr.jobs.models import Training
from hr.employees.models import Employee


logger = logging.getLogger(__name__)


class DevelopmentService:
    """ Manages employee skills development, profesional certifications, and training records. """

    def record_training(
        self,
        employee_id: UUID,
        name: str,
        institute: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        location: Optional[str] = None,
        description: Optional[str] = None
    ) -> Training:
        """ Logs a new training session or certification for an employee. """
        employee = get_object_or_404(Employee, id=employee_id)
        
        training = Training.objects.create(
            employee=employee,
            name=name,
            institute=institute,
            start_date=start_date or timezone.now().date(),
            end_date=end_date,
            location=location,
            description=description
        )
        
        logger.info(f"Training '{name}' recorded for {employee.full_name}")
        return training

    def get_upcoming_expirations(self, days: int = 30) -> QuerySet[Training]:
        """ Identifies certifications that require renewal within the specified timeframe. """
        today = timezone.now().date()
        limit_date = today + timezone.timedelta(days=days)
        
        return Training.objects.filter(
            expiry_date__range=[today, limit_date]
        ).select_related('employee', 'employee__user').order_by('expiry_date')

    def get_expired_certifications(self) -> QuerySet[Training]:
        """ Lists all certifications that have passed their validity period. """
        return Training.objects.filter(
            expiry_date__lt=timezone.now().date()
        ).select_related('employee').order_by('-expiry_date')

    def get_employee_skills_matrix(self, employee_id: UUID) -> Dict[str, Any]:
        """ Aggregates an employee's training history and current certification status. """
        employee = get_object_or_404(Employee, id=employee_id)
        trainings = Training.objects.filter(employee=employee)
        today = timezone.now().date()

        return {
            "employee": employee.full_name,
            "active_certifications": trainings.filter(
                expiry_date__gt=today
            ).count() + trainings.filter(expiry_date__isnull=True, end_date__isnull=False).count(),
            "expired_count": trainings.filter(expiry_date__lte=today).count(),
            "history": trainings.all()
        }

