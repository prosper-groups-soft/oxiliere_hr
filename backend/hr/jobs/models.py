from django.db import models
from django.db import transaction
from django.utils import timezone
from utils_mixins.models import BaseModelMixin
from utils_mixins.fn import enum_to_choices
from .enums import PositionLevel


class JobFamily(BaseModelMixin):
    """
    Represents a family of related positions within the company.
    Examples: Engineering, HR, Finance.

    Purpose:
    - Organizes positions into logical career paths.
    - Simplifies reporting and career tracking.

    Notes:
    - Only stores structural data: name and description.
    - Business rules (e.g., allowed positions per family) handled in services.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Job Family"
        verbose_name_plural = "Job Families"

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def __str__(self):
        return self.name


class Position(BaseModelMixin):
    """
    Represents a job position inside a JobFamily, with a defined seniority level.

    The `level` attribute represents the seniority or career stage:
        - TRAINEE: Entry-level training or internship
        - APPRENTICE: Practical learning with mentoring
        - JUNIOR: First independent work experience
        - INTERMEDIATE: Solid experience, some autonomy
        - SENIOR: Advanced expertise, mentoring others
        - LEAD: Leads a small team or project
        - MANAGER: Manages a team or functional area
        - DIRECTOR: Manages multiple teams or departments
        - EXECUTIVE: Strategic leadership role
    """
    job_family = models.ForeignKey(
        JobFamily,
        on_delete=models.CASCADE,
        related_name="positions"
    )
    name = models.CharField(max_length=100)
    level = models.CharField(
        max_length=20,
        choices=enum_to_choices(PositionLevel),
        default=PositionLevel.JUNIOR.value,
        help_text="Seniority level of the position."
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["job_family__name", "level", "name"]

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def __str__(self):
        return f"{self.name} ({self.get_level_display()}) in {self.job_family}"


class Department(BaseModelMixin):
    """
    Represents a company department.
    
    Purpose:
    - Groups employees into functional units.
    - Can be used in reporting and career history.
    
    Notes:
    - The 'manager' field links to the employee managing the department.
    - Business rules (e.g., only one manager per department) handled in services.
    """
    manager = models.ForeignKey(
        "hr.employees.models.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="department_managed",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)


    class Meta:
        ordering = ["name"]

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def __str__(self):
        return self.name


class EmployeePositionHistory(BaseModelMixin):
    """
    Tracks an employee's positions and departments over time.

    Fields:
    - employee → The employee.
    - position → The position held, includes level and JobFamily.
    - department → Optional department.
    - start_date / end_date → Duration in the role.
    - description → Optional notes (projects, responsibilities).

    Purpose:
    - Maintains full career history for an employee.
    - Used for promotions, reporting, and HR analytics.

    Notes:
    - Business rules such as overlapping positions, promotions,
      or level validation should be enforced in service layer.
    """

    employee = models.ForeignKey(
        "hr.employees.models.Employee",
        on_delete=models.CASCADE,
        related_name="position_history",
        help_text="The employee who held this position."
    )

    position = models.ForeignKey(
        "hr.jobs.models.Position",
        on_delete=models.CASCADE,
        related_name="employee_histories",
        help_text="Position held by the employee."
    )

    department = models.ForeignKey(
        "hr.jobs.models.Department",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employee_position_histories",
        help_text="Department where the employee worked during this period."
    )

    start_date = models.DateField(
        default=timezone.now,
        help_text="Start date of the position."
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date of the position. Null if currently held."
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description or notes about the employee's role or responsibilities."
    )

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Employee Position History"
        verbose_name_plural = "Employee Position Histories"

    def __str__(self):
        end_str = self.end_date.strftime("%Y-%m-%d") if self.end_date else "Present"
        return f"{self.employee} - {self.position.name} ({self.position.get_level_display()}) from {self.start_date} to {end_str}"


class Training(BaseModelMixin):
    """
    Represents a training, certification, or course attended by an employee.

    Fields:
    - employee → Employee attending the training.
    - name → Training or course name.
    - institute → Training provider.
    - start_date / end_date → Training duration.
    - location → Training location.
    - description → Optional notes.

    Purpose:
    - Tracks employee skill development and certifications.
    - Used for HR reporting, promotions, and skills management.

    Notes:
    - Business rules like overlapping training periods should be enforced in service layer.
    """
    employee = models.ForeignKey(
        "hr.employees.models.Employee",
        on_delete=models.CASCADE,
        related_name="trainings"
    )
    name = models.CharField(max_length=255)
    institute = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-start_date"]

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.employee})"

