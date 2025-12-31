from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from hr.employees.models import Employee
<<<<<<< HEAD
from utils_mixins.models import BaseModelMixin
from utils_mixins.fn import enum_to_choices
from .choices import LeaveStatus, LeaveType
=======
from oxutils.models import BaseModelMixin
from .enums import LeaveStatus, LeaveType
>>>>>>> d9d914b (add: oxiliere tenant)


class Leave(BaseModelMixin):
    """
    Represents a leave request in the system.
    """

    applicable_to = models.ManyToManyField(
        Employee,
        through="LeaveEmployee",
        related_name="leaves",
        verbose_name="Applicable Employees",
        blank=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leaves",
        verbose_name="Approved By",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    reason = models.TextField(null=True, blank=True, verbose_name="Reason")

    everyone = models.BooleanField(default=False, verbose_name="Applies to Everyone")
    paid = models.BooleanField(default=False, verbose_name="Paid")

    leave_type = models.CharField(
        max_length=50,
        choices=LeaveType.choices,
        default=LeaveType.ANNUAL.value,
        verbose_name="Leave Type",
    )

    status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING.value,
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Leave"
        verbose_name_plural = "Leaves"
        ordering = ["-start_date"]
        constraints = [
            # Ensure start_date is before or equal to end_date
            models.CheckConstraint(
                condition=models.Q(start_date__lte=models.F("end_date")),
                name="leave_start_before_end",
            ),
            # Ensure approved leaves have approver and approval date, others do not
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status=LeaveStatus.APPROVED.value,
                        approved_by__isnull=False,
                        approved_at__isnull=False
                    ) |
                    models.Q(
                        status__in=[
                            LeaveStatus.PENDING.value,
                            LeaveStatus.REJECTED.value,
                            LeaveStatus.CANCELLED.value,
                        ],
                        approved_by__isnull=True,
                        approved_at__isnull=True
                    )
                ),
                name="leave_approval_consistency",
            )
        ]
        indexes = [
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["everyone"]),
        ]

    def clean(self):
        """Validate start/end dates and approval consistency."""
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date must be before or equal to end date.")

        if self.status == LeaveStatus.APPROVED.value:
            if not self.approved_by or not self.approved_at:
                raise ValidationError("Approved leave must have approver and approval date.")

        if self.everyone and self.applicable_to.exists():
            raise ValidationError("Leave cannot be set to 'everyone' while also having specific employees.")

    @property
    def total_days(self) -> int:
        """Returns the total number of calendar days of the leave."""
        return (self.end_date - self.start_date).days + 1

    def __str__(self) -> str:
        return f"{LeaveType(self.leave_type).name} ({self.start_date} → {self.end_date})"


class LeaveEmployee(BaseModelMixin):
    """
    Through model linking Employees to Leaves.
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="employee_leaves",
        verbose_name="Employee",
    )
    leave = models.ForeignKey(
        Leave,
        on_delete=models.CASCADE,
        related_name="leaves_employees",
        verbose_name="Leave",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name="Created By",
    )

    class Meta:
        verbose_name = "Leave Assignment"
        verbose_name_plural = "Leave Assignments"
        indexes = [
            models.Index(fields=["employee", "leave"]),
            models.Index(fields=["employee"]),
            models.Index(fields=["leave"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["leave", "employee"],
                name="unique_leave_employee"
            )
        ]

    def __str__(self) -> str:
        return f"{self.employee} → {self.leave}"
