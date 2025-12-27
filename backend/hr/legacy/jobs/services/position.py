from django.db import transaction
from django.core.exceptions import ValidationError
from hr.jobs.models import Position, JobFamily
from typing import Optional, Iterable



# -----------------------------------------------------------------------
# Position Reader / Writer services
# -----------------------------------------------------------------------
class PositionWriterService:
    """
    Writer for Position: creation, update, delete, and bulk operations.
    Business rules:
      - name normalized
      - level must be one of Position.LEVEL_CHOICES
      - job_family must exist
    """

    @staticmethod
    @transaction.atomic
    def create(
        name: str, 
        job_family: JobFamily, 
        level: str = Position.LEVEL_JUNIOR, 
        description: str = ""
    ) -> Position:
        """
        Create a Position under a JobFamily.
        """
        if level not in dict(Position.LEVEL_CHOICES):
            raise ValidationError(f"Invalid level '{level}' for Position.")
        name = name.strip().title()
        pos = Position(
            name=name, 
            job_family=job_family,
            level=level, 
            description=description
        )
        pos.full_clean()
        pos.save()
        return pos

    @staticmethod
    @transaction.atomic
    def update(position_id: int, **kwargs) -> Position:
        """
        Update a Position. Allowed: name, job_family, level, description.
        """
        try:
            pos = Position.objects.get(id=position_id)
        except Position.DoesNotExist:
            raise ValueError(f"Position {position_id} not found")

        if "name" in kwargs and kwargs["name"]:
            kwargs["name"] = kwargs["name"].strip().title()

        if "level" in kwargs and kwargs["level"] not in dict(Position.LEVEL_CHOICES):
            raise ValidationError(f"Invalid level '{kwargs['level']}' for Position.")

        for field, value in kwargs.items():
            if hasattr(pos, field):
                setattr(pos, field, value)

        pos.full_clean()
        pos.save()
        return pos

    @staticmethod
    @transaction.atomic
    def delete(position_id: int) -> None:
        """
        Delete a Position. If EmployeePositionHistory references it, 
        DB constraints will apply.
        Prefer soft-deleting or preventing deletion if referenced.
        """
        pos = Position.objects.get(id=position_id)
        pos.delete()

    @staticmethod
    def bulk_create(positions: Iterable[dict]) -> list[Position]:
        """
        Bulk create positions. Each dict requires: name, job_family (instance), 
        level (optional), description (optional).
        Returns list of created Position instances.
        """
        created = []
        for p in positions:
            created.append(PositionWriterService.create(
                name=p["name"],
                job_family=p["job_family"],
                level=p.get("level", Position.LEVEL_JUNIOR),
                description=p.get("description", "")
            ))
        return created


class PositionReaderService:
    """
    Reader for Position: get, list and search.
    """

    @staticmethod
    def get(position_id: int) -> Optional[Position]:
        return Position.objects.filter(
            id=position_id
        ).select_related("job_family").first()

    @staticmethod
    def list_all():
        return Position.objects.select_related("job_family").all()

    @staticmethod
    def list_by_family(job_family_id: int):
        return Position.objects.filter(
            job_family_id=job_family_id
        ).order_by("level", "name")

    @staticmethod
    def search(query: str):
        return Position.objects.filter(name__icontains=query.strip())

