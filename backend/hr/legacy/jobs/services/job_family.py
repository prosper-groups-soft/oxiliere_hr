from typing import Optional
from hr.jobs.models import JobFamily
from django.db import transaction


# -----------------------------------------------------------
# JobFamily Services
# -----------------------------------------------------------
class JobFamilyWriterService:
    """
    Writer for JobFamily: creation, update and deletion operations.
    Business rules:
      - name is normalized (strip/title).
      - creation raises on duplicate name (DB unique will also enforce).
    """

    @staticmethod
    @transaction.atomic
    def create(name: str, description: str = "") -> JobFamily:
        """
        Create a JobFamily.
        """
        name = name.strip().title()
        jf = JobFamily(name=name, description=description)
        jf.full_clean(exclude=None)  # model level cleaning/validation
        jf.save()
        return jf

    @staticmethod
    @transaction.atomic
    def update(job_family_id: int, **kwargs) -> JobFamily:
        """
        Update fields on a JobFamily.
        Accepts name and description.
        """
        try:
            jf = JobFamily.objects.get(id=job_family_id)
        except JobFamily.DoesNotExist:
            raise ValueError(f"JobFamily {job_family_id} not found")

        if "name" in kwargs and kwargs["name"]:
            kwargs["name"] = kwargs["name"].strip().title()

        for field, value in kwargs.items():
            if hasattr(jf, field):
                setattr(jf, field, value)
        jf.full_clean(exclude=None)
        jf.save()
        return jf

    @staticmethod
    @transaction.atomic
    def delete(job_family_id: int) -> None:
        """
        Delete a JobFamily. If positions exist, deletion will cascade (or
        raise depending on model on_delete). Use with caution.
        """
        jf = JobFamily.objects.get(id=job_family_id)
        jf.delete()


class JobFamilyReaderService:
    """
    Reader for JobFamily: retrieval and listing operations.
    """

    @staticmethod
    def get(job_family_id: int) -> Optional[JobFamily]:
        return JobFamily.objects.filter(id=job_family_id).first()

    @staticmethod
    def list_all():
        return JobFamily.objects.all()

    @staticmethod
    def search_by_name(query: str):
        return JobFamily.objects.filter(
            name__icontains=query.strip()
        ).order_by("name")

