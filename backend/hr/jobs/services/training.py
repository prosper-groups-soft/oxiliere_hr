from typing import Optional
from django.db import transaction
from django.db import models
from django.core.exceptions import ValidationError
from hr.jobs.models import Training
from hr.employees.models import Employee


class TrainingWriter:
    """
    Writer for Training: create, update, delete training records.
    Validations:
      - date coherence (start_date <= end_date)
      - optional overlap checks can be enabled
    """

    @staticmethod
    @transaction.atomic
    def create(employee: Employee, name: str, institute: str, start_date, end_date, location: str, description: str = "", allow_overlap: bool = True) -> Training:
        """
        Create a Training record for an employee. By default overlap is allowed.
        """
        if start_date and end_date and start_date > end_date:
            raise ValidationError("start_date must be <= end_date for Training.")

        if not allow_overlap:
            # simple overlap check against other trainings for the employee
            if Training.objects.filter(employee=employee).filter(models.Q(start_date__lte=end_date) & models.Q(end_date__gte=start_date)).exists():
                raise ValidationError(
                    "Training period overlaps another training for the same employee."
                )

        tr = Training(
            employee=employee,
            name=name.strip().title(),
            institute=institute.strip(),
            start_date=start_date,
            end_date=end_date,
            location=location.strip(),
            description=description
        )
        tr.full_clean()
        tr.save()
        return tr

    @staticmethod
    @transaction.atomic
    def update(training_id: int, **kwargs) -> Training:
        tr = Training.objects.get(id=training_id)
        if "start_date" in kwargs or "end_date" in kwargs:
            start_date = kwargs.get("start_date", tr.start_date)
            end_date = kwargs.get("end_date", tr.end_date)
            if start_date and end_date and start_date > end_date:
                raise ValidationError("start_date must be <= end_date for Training.")

        for field, value in kwargs.items():
            if hasattr(tr, field):
                setattr(tr, field, value)
        tr.full_clean()
        tr.save()
        return tr

    @staticmethod
    @transaction.atomic
    def delete(training_id: int) -> None:
        tr = Training.objects.get(id=training_id)
        tr.delete()


class TrainingReader:
    """
    Reader for Training: retrieval and listing.
    """

    @staticmethod
    def get(training_id: int) -> Optional[Training]:
        return Training.objects.filter(id=training_id).select_related("employee").first()

    @staticmethod
    def list_for_employee(employee_id: int):
        return Training.objects.filter(employee_id=employee_id).order_by("-start_date")

    @staticmethod
    def search(employee_id: int = None, institute: str = None, name: str = None):
        qs = Training.objects.all()
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if institute:
            qs = qs.filter(institute__icontains=institute)
        if name:
            qs = qs.filter(name__icontains=name)
        return qs