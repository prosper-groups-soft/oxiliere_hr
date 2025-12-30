from django.conf import settings
from django.db import models
from hr.employees.models import Employee
from utils_mixins.models import BaseModelMixin
from utils_mixins.fn import enum_to_choices
from .enums import LeaveStatus, LeaveType


class Leave(BaseModelMixin):
    applicable_to = models.ManyToManyField(
        Employee,
        through="LeaveEmployee",
        related_name="leaves",
        verbose_name="Employés concernés",
        blank=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="approved_leaves",
        verbose_name="Approuvé par",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    reason = models.TextField(
        null=True,
        blank=True,
        verbose_name="Raison",
    )

    everyone = models.BooleanField(
        default=False,
        verbose_name="Applicable à tout le monde",
    )

    paid = models.BooleanField(
        default=False,
        verbose_name="Payé",
    )

    leave_type = models.CharField(
        max_length=50,
        choices=enum_to_choices(LeaveType),
        default=LeaveType.ANNUAL.value,
        verbose_name="Type de congé",
    )

    status = models.CharField(
        max_length=20,
        choices=enum_to_choices(LeaveStatus),
        default=LeaveStatus.PENDING.value,
        verbose_name="Statut",
    )


    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(start_date__lte=models.F("end_date")),
                name="leave_start_before_end",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status=LeaveStatus.APPROVED.value,
                        approved_by__isnull=False,
                        approved_at__isnull=False
                    ) |
                    models.Q(status__in=[
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

    def total_days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{LeaveType(self.leave_type).name} ({self.start_date} → {self.end_date})"


class LeaveEmployee(BaseModelMixin):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="employee_leaves",
        verbose_name="Employé",
    )
    leave = models.ForeignKey(
        Leave,
        on_delete=models.CASCADE,
        related_name="leaves_employees",
        verbose_name="Congé",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name="Créé par",
    )

    class Meta:
        unique_together = ["employee", "leave"]
        verbose_name = "Affectation de congé"
        verbose_name_plural = "Affectations de congés"
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

    def __str__(self):
        return f"{self.employee} → {self.leave}"
