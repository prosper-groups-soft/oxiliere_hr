from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from auditlog.registry import auditlog

from hr.models import BaseAuditableModel
from .enums import PositionLevel


class JobFamily(BaseAuditableModel):
    """ Engineering, HR, Finance, etc. """
    name = models.CharField(
        max_length=255, 
        unique=True,
        help_text="Name of the job family (e.g., Engineering, Human Resources)."
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Brief description of the roles and responsibilities within this family."
    )

    class Meta:
        db_table = "jobs_job_family"
        ordering = ["name"]
        verbose_name = "Job Family"
        verbose_name_plural = "Job Families"

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def __str__(self):
        return self.name


class Position(BaseAuditableModel):
    """ Seniority levels within a JobFamily. """
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
        help_text="Seniority or hierarchical level of the position."
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Specific requirements or details about this role."
    )

    class Meta:
        db_table = "jobs_position"
        ordering = ["job_family__name", "level", "name"]
        # Prevents having "Senior Developer" twice in the same family
        unique_together = ('job_family', 'name', 'level')

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"


class Department(BaseAuditableModel):
    """ Functional units with hierarchical support. """
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Official name of the department."
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="sub_departments",
        help_text="Parent department for hierarchical structure (e.g., Marketing under Global Ops)."
    )
    manager = models.ForeignKey(
        "hr_employees.Employee", 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="department_managed",
        help_text="The employee leading this department."
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Purpose and focus of this department."
    )

    class Meta:
        db_table = "jobs_department"
        ordering = ["name"]

    def __str__(self):
        return self.name


class EmployeePositionHistory(BaseAuditableModel):
    """ Tracks career path. """
    employee = models.ForeignKey(
        "hr_employees.Employee",
        on_delete=models.CASCADE,
        related_name="position_history",
        help_text="The employee associated with this career record."
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT, # Protect position from deletion if used in history
        related_name="employee_histories",
        help_text="The position held by the employee during this period."
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="employee_position_histories",
        help_text="The department where the employee worked during this period."
    )
    start_date = models.DateField(
        default=timezone.now,
        help_text="Date when the employee started in this position."
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Date when the employee left this position. Leave blank if still active."
    )
    is_current = models.BooleanField(
        default=True,
        help_text="Indicates if this is the employee's current active position."
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes about the employee's performance or role changes."
    )

    class Meta:
        db_table = "jobs_employee_position_history"
        ordering = ["-start_date"]
        verbose_name = "Employee Position History"
        verbose_name_plural = "Employee Position Histories"

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")

    def save(self, *args, **kwargs):
        self.clean()
        if self.is_current:
            # Automatically close the previous position if this one is marked as 'current'
            EmployeePositionHistory.objects.filter(
                employee=self.employee, 
                is_current=True
            ).exclude(id=self.id).update(is_current=False, end_date=timezone.now().date())
        super().save(*args, **kwargs)


class Training(BaseAuditableModel):
    """ Certifications and skills development. """
    employee = models.ForeignKey(
        "hr_employees.Employee",
        on_delete=models.CASCADE,
        related_name="trainings",
        help_text="The employee who attended the training."
    )
    name = models.CharField(
        max_length=255,
        help_text="Name of the training or certification."
    )
    institute = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="The organization or institution that provided the training."
    )
    start_date = models.DateField(
        default=timezone.now,
        help_text="Start date of the training session."
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Completion date of the training."
    )
    location = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Physical or virtual location where the training took place."
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Brief summary of skills acquired or certification details."
    )
    expiry_date = models.DateField(
        null=True, 
        blank=True,
        help_text=_("Date when this certification or training expires.")
    )

    class Meta:
        db_table = "jobs_training"
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.name} - {self.employee.full_name}"

    def clean(self):
            super().clean()
            if self.expiry_date and self.start_date and self.expiry_date <= self.start_date:
                raise ValidationError(_("Expiry date must be after the start date."))


# --- AUDIT LOG REGISTRATION ---

auditlog.register(JobFamily)
auditlog.register(Position)
auditlog.register(Department)
auditlog.register(EmployeePositionHistory)
auditlog.register(Training)

