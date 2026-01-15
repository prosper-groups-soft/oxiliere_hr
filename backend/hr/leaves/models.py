from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog

from hr.employees.models import Employee
from hr.models import BaseAuditableModel
from hr.enums import (
    LeaveCategory, 
    LeaveStatus, 
    CircumstanceType, 
    CountryCode
)
from hr.utils import get_country_codes


# --- HR CONFIGURATION ---

class LeavePolicy(BaseAuditableModel):
    """
    Global annual leave configuration.
    Defines the base foundation for all employees.
    """
    name = models.CharField(max_length=100)
    country_code = models.CharField(
        max_length=2,
        choices=get_country_codes(),
        default=CountryCode.DRC,
        unique=True
    )
    
    # Base number of days (e.g., 18 days or 30 days per year)
    standard_annual_days = models.PositiveIntegerField(
        default=18,
        help_text=_("Number of base annual leave days per year.")
    )

    # --- Carry-over Configuration ---
    allows_carry_over = models.BooleanField(default=False)
    max_carry_over_days = models.PositiveIntegerField(
        default=10, 
        help_text=_("Maximum number of days an employee can carry over to the next year.")
    )
    carry_over_expiration_month = models.PositiveIntegerField(
        default=3,
        help_text=_("Month (1–12) when carry-over expires, e.g. 3 = March 31 of the following year.")
    )

    class Meta:
        db_table = "leav_leave_policy"
        verbose_name_plural = "Leave Policies"
        constraints = [
            # Valid expiration month (January to December)
            models.CheckConstraint(
                condition=models.Q(
                    carry_over_expiration_month__gte=1,
                    carry_over_expiration_month__lte=12
                ),
                name="valid_expiration_month"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.country_code})"


class SeniorityRule(BaseAuditableModel):
    """
    Rules for granting bonus days based on seniority.
    Example: +1 day after 3 years, +2 days after 5 years.
    """
    policy = models.ForeignKey(
        LeavePolicy,
        on_delete=models.CASCADE,
        related_name="seniority_rules"
    )
    years_of_service = models.PositiveIntegerField(
        help_text=_("Required years of service.")
    )
    bonus_days = models.PositiveIntegerField(
        help_text=_("Additional leave days granted.")
    )

    class Meta:
        db_table = "leav_seniority_rule"
        ordering = ['years_of_service']
        constraints = [
            # Prevent duplicate seniority rules for the same policy
            models.UniqueConstraint(
                fields=['policy', 'years_of_service'], 
                name="unique_seniority_per_policy"
            )
        ]


class CircumstanceLeaveRule(BaseAuditableModel):
    """
    Defines the fixed duration for each type of special (circumstance) leave.
    Configured by HR.
    """
    policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=50,
        choices=CircumstanceType.choices
    )
    duration_days = models.PositiveIntegerField()
    is_paid = models.BooleanField(default=True)

    class Meta:
        db_table = "leav_circumstance_leave_rule"
        unique_together = ("policy", "type")
        indexes = [
            models.Index(fields=['policy', 'type']),
        ]


# --- BALANCE TRACKING (ENTITLEMENTS) ---

class LeaveBalance(BaseAuditableModel):
    """
    Employee leave balance for a given year.
    Manages annual expiration and prorated calculation upon hire date.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="balances"
    )
    year = models.PositiveIntegerField()

    # Calculated at creation (prorated if starting mid-year)
    base_entitlement = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    seniority_bonus = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    # Days already used
    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    @property
    def total_granted(self):
        return self.base_entitlement + self.seniority_bonus

    @property
    def remaining_days(self):
        return self.total_granted - self.used_days

    class Meta:
        db_table = "leav_leave_balance"
        unique_together = ("employee", "year")
        indexes = [
            models.Index(fields=['employee', 'year']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    used_days__lte=models.F('base_entitlement') + models.F('seniority_bonus')
                ),
                name="used_days_within_limit"
            ),
            # Entitlement cannot be negative
            models.CheckConstraint(
                condition=models.Q(base_entitlement__gte=0),
                name="positive_base_entitlement"
            )
        ]


class LeaveCarryOver(BaseAuditableModel):
    """
    Represents leave days carried over from a previous year for an employee,
    tracking usage and expiration.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="carry_overs"
    )

    source_year = models.PositiveIntegerField(
        help_text=_("Year from which the leave was carried over.")
    )

    days = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    used_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0")
    )

    expires_at = models.DateField()

    class Meta:
        db_table = "leav_leave_carry_over"
        unique_together = ("employee", "source_year")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(used_days__lte=models.F('days')),
                name="carryover_used_days_within_limit"
            ),
            models.CheckConstraint(
                condition=models.Q(days__gt=0),
                name="positive_carryover_days"
            )
        ]


# --- TRANSACTIONS (REQUESTS) ---

class LeaveRequest(BaseAuditableModel):
    """
    Leave request (annual or special/circumstance).
    Supports splitting across multiple records if needed.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )
    category = models.CharField(
        max_length=20,
        choices=LeaveCategory.choices
    )
    
    # For special (circumstance) leave
    circumstance_type = models.CharField(
        max_length=50,
        choices=CircumstanceType.choices,
        null=True,
        blank=True
    )
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Number of effective leave days (excluding public holidays, weekends, closures)
    requested_days = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    
    status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING
    )
    
    # Supporting document (mandatory for special leave)
    attachment = models.FileField(
        upload_to='leave_proofs/%Y/',
        null=True,
        blank=True
    )
    
    comment = models.TextField(blank=True)

    class Meta:
        db_table = "leav_leave_request"
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        constraints = [
            # End date must be on or after start date
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F('start_date')),
                name="leave_start_before_end"
            ),
            # Requested days must be positive
            models.CheckConstraint(
                condition=models.Q(requested_days__gt=0),
                name="positive_requested_days"
            )
        ]


class LeaveRecall(BaseAuditableModel):
    """
    Manages employee recall from leave.
    Triggers re-crediting of unused leave days.
    """
    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name="recalls"
    )

    recall_date = models.DateField(
        help_text=_("Date on which the employee must return to work.")
    )

    reason = models.TextField(
        help_text=_("Reason for recalling the employee.")
    )

    recalled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="leave_recalls",
        help_text=_("User who initiated the recall.")
    )

    class Meta:
        db_table = "leav_leave_recall"
        indexes = [
            models.Index(fields=['leave_request', 'recall_date']),
        ]


# --- CALENDAR ---

class PublicHoliday(BaseAuditableModel):
    """Statutory public holidays."""
    name = models.CharField(max_length=100)
    date = models.DateField()
    country_code = models.CharField(
        max_length=2,
        choices=get_country_codes(),
        default=CountryCode.DRC
    )
    is_recurring = models.BooleanField(default=True)

    class Meta:
        db_table = "leav_public_holiday"
        indexes = [
            models.Index(fields=['date', 'country_code']),
        ]
        constraints = [
            # A public holiday must be unique per date and country
            models.UniqueConstraint(
                fields=['date', 'country_code'],
                name="unique_holiday_per_country_date"
            )
        ]


class CompanyClosing(BaseAuditableModel):
    """Exceptional company-wide closing days."""
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = "leav_company_closing"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F('start_date')),
                name="closing_start_before_end"
            )
        ]


# --- AUDIT LOG REGISTRATION ---

auditlog.register(LeavePolicy)
auditlog.register(SeniorityRule)
auditlog.register(CircumstanceLeaveRule)
auditlog.register(LeaveBalance)
auditlog.register(LeaveRequest)
auditlog.register(LeaveRecall)
auditlog.register(PublicHoliday)
auditlog.register(CompanyClosing)

