from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from auditlog.registry import auditlog

from hr.models import BaseAuditableModel
from .enums import PositionLevel


class JobFamily(BaseAuditableModel):
    """ High-level functional career category (e.g., Engineering, HR, Finance). """
    name = models.CharField(
        max_length=255, 
        unique=True,
        verbose_name=_("Family Name")
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Description")
    )

    class Meta:
        db_table = "jobs_job_family"
        ordering = ["name"]
        verbose_name = _("Job Family")
        verbose_name_plural = _("Job Families")

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def __str__(self):
        return self.name


class Position(BaseAuditableModel):
    """ Specific role and seniority level within a Job Family. """
    job_family = models.ForeignKey(
        JobFamily, 
        on_delete=models.CASCADE, 
        related_name="positions",
        help_text="The job family this position belongs to."
    )
    name = models.CharField(
        max_length=100,
        help_text="Title of the position (e.g., Software Engineer, Recruiter)."
    )
    level = models.CharField(
        max_length=20,
        choices=PositionLevel,
        default=PositionLevel.JUNIOR,
        verbose_name=_("Seniority Level")
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Job Description")
    )

    class Meta:
        db_table = "jobs_position"
        ordering = ["job_family__name", "level", "name"]
        unique_together = ('job_family', 'name', 'level')
        verbose_name = _("Position")

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"


class Department(BaseAuditableModel):
    """ Organizational unit or functional department. """
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name=_("Department Name")
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="sub_departments",
        verbose_name=_("Parent Department")
    )
    manager = models.ForeignKey(
        "hr_employees.Employee", 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="department_managed",
        verbose_name=_("Department Manager")
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Mission Description")
    )

    class Meta:
        db_table = "jobs_department"
        ordering = ["name"]
        verbose_name = _("Department")

    def __str__(self):
        return self.name


class EmployeePositionHistory(BaseAuditableModel):
    """ Records an employee's career progression and departmental assignments. """
    employee = models.ForeignKey(
        "hr_employees.Employee",
        on_delete=models.CASCADE,
        related_name="position_history",
        verbose_name=_("Employee")
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name="employee_histories",
        verbose_name=_("Position held")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="employee_position_histories",
        verbose_name=_("Assigned Department")
    )
    start_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Start Date")
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("End Date")
    )
    is_current = models.BooleanField(
        default=True,
        verbose_name=_("Current Position")
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Assignment Notes")
    )

    class Meta:
        db_table = "jobs_employee_position_history"
        ordering = ["-start_date"]
        verbose_name = _("Position History")
        verbose_name_plural = _("Position Histories")

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError(_("End date cannot be before start date."))

    def save(self, *args, **kwargs):
        self.clean()
        if self.is_current:
            EmployeePositionHistory.objects.filter(
                employee=self.employee, 
                is_current=True
            ).exclude(id=self.id).update(is_current=False, end_date=timezone.now().date())
        super().save(*args, **kwargs)


class Training(BaseAuditableModel):
    """ Professional certifications and corporate training records. """
    employee = models.ForeignKey(
        "hr_employees.Employee",
        on_delete=models.CASCADE,
        related_name="trainings",
        verbose_name=_("Employee")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Training Name")
    )
    institute = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name=_("Training Institution")
    )
    start_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Start Date")
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("End Date")
    )
    location = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name=_("Location")
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Content Summary")
    )
    expiry_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("Expiry Date")
    )

    class Meta:
        db_table = "jobs_training"
        ordering = ["-start_date"]
        verbose_name = _("Training")
        indexes = [
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.name} - {self.employee.full_name}"

    def clean(self):
            super().clean()
            if self.expiry_date and self.start_date and self.expiry_date <= self.start_date:
                raise ValidationError(_("Expiry date must be after the start date."))


# --- Audit log registration ---
auditlog.register(JobFamily)
auditlog.register(Position)
auditlog.register(Department)
auditlog.register(EmployeePositionHistory)
auditlog.register(Training)

