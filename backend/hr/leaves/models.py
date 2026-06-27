from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog

from hr.employees.models import Employee
from hr.models.base import BaseAuditableModel
from .enums import (
    LeaveCategory, 
    LeaveStatus, 
    CircumstanceType, 
    LeaveTransactionTypes
)
from hr.enums import CountryCode

from hr.utils.core import get_country_codes


# --- HR CONFIGURATION ---

class LeavePolicy(BaseAuditableModel):
    """ Global annual leave configuration and base entitlements. """
    name = models.CharField(
        max_length=100,
        verbose_name=_("Policy Name")
    )
    country_code = models.CharField(
        max_length=2,
        choices=get_country_codes(),
        default=CountryCode.DRC,
        unique=True,
        verbose_name=_("Country")
    )
    
    # Base number of days (e.g., 18 days or 30 days per year)
    standard_annual_days = models.PositiveIntegerField(
        default=18,
        verbose_name=_("Standard Annual Days"),
        help_text=_("Base number of annual leave days granted per year.")
    )

    allows_carry_over = models.BooleanField(
        default=False,
        verbose_name=_("Allows Carry-over")
    )
    max_carry_over_days = models.PositiveIntegerField(
        default=10, 
        verbose_name=_("Max Carry-over Days"),
        help_text=_("Maximum unused days that can be moved to the next year.")
    )
    carry_over_expiration_month = models.PositiveIntegerField(
        default=3,
        verbose_name=_("Expiration Month"),
        help_text=_("Month (1-12) when carried-over days expire (e.g., 3 for March).")
    )

    # Limites de demande
    max_consecutive_days = models.PositiveIntegerField(
        default=30,
        verbose_name=_("Max Consecutive Days"),
        help_text=_("Maximum consecutive working days allowed per request.")
    )
    notice_period_days = models.PositiveIntegerField(
        default=15,
        verbose_name=_("Notice Period Days"),
        help_text=_("Minimum advance notice required for leave requests.")
    )

    class Meta:
        db_table = "leav_leave_policy"
        verbose_name = _("Leave Policy")
        verbose_name_plural = _("Leave Policies")
        constraints = [
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
    Rules for granting additional leave days based on years of service. 
    Example: +1 day after 3 years, +2 days after 5 years.
    """
    policy = models.ForeignKey(
        LeavePolicy,
        on_delete=models.CASCADE,
        related_name="seniority_rules",
        verbose_name=_("Policy")
    )
    years_of_service = models.PositiveIntegerField(
        verbose_name=_("Years of Service"),
        help_text=_("Required length of service to trigger bonus days.")
    )
    bonus_days = models.PositiveIntegerField(
        verbose_name=_("Bonus Days"),
        help_text=_("Extra leave days granted for this seniority level.")
    )

    class Meta:
        db_table = "leav_seniority_rule"
        verbose_name = _("Seniority Rule")
        verbose_name_plural = _("Seniority Rules")
        ordering = ['years_of_service']
        constraints = [
            models.UniqueConstraint(
                fields=['policy', 'years_of_service'], 
                name="unique_seniority_per_policy"
            )
        ]


class CircumstanceLeaveRule(BaseAuditableModel):
    """ Entitlements for special leave categories (e.g., Marriage, Bereavement). """
    policy = models.ForeignKey(
        LeavePolicy, 
        on_delete=models.CASCADE,
        verbose_name=_("Policy")
    )
    type = models.CharField(
        max_length=50,
        choices=CircumstanceType.choices,
        verbose_name=_("Leave Type")
    )
    duration_days = models.PositiveIntegerField(
        verbose_name=_("Duration (Days)")
    )
    is_paid = models.BooleanField(
        default=True,
        verbose_name=_("Paid Leave")
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Optional description for this leave type (e.g., 'Mariage de l\'employé')")
    )

    class Meta:
        db_table = "leav_circumstance_leave_rule"
        verbose_name = _("Special Leave Rule")
        verbose_name_plural = _("Special Leave Rules")
        unique_together = ("policy", "type")
        indexes = [
            models.Index(fields=['policy', 'type']),
        ]


# --- BALANCE TRACKING ---

class LeaveBalance(BaseAuditableModel):
    """ Individual employee leave entitlements and usage for a specific year. """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="balances",
        verbose_name=_("Employee")
    )
    year = models.PositiveIntegerField(
        verbose_name=_("Year")
    )

    base_entitlement = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("Base Entitlement"),
        help_text=_("Standard days granted (may be prorated).")
    )
    seniority_bonus = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("Seniority Bonus")
    )

    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("Used Days")
    )

    @property
    def total_granted(self):
        return self.base_entitlement + self.seniority_bonus

    @property
    def remaining_days(self):
        return self.total_granted - self.used_days

    class Meta:
        db_table = "leav_leave_balance"
        verbose_name = _("Leave Balance")
        verbose_name_plural = _("Leave Balances")
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
            models.CheckConstraint(
                condition=models.Q(base_entitlement__gte=0),
                name="positive_base_entitlement"
            )
        ]


class LeaveCarryOver(BaseAuditableModel):
    """ Tracks leave days moved from a previous year and their expiration. """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="carry_overs",
        verbose_name=_("Employee")
    )

    source_year = models.PositiveIntegerField(
        verbose_name=_("Source Year"),
        help_text=_("Year from which these days originated.")
    )

    days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("Carried Days")
    )

    used_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Used Carried Days")
    )

    expires_at = models.DateField(
        verbose_name=_("Expiration Date")
    )

    class Meta:
        db_table = "leav_leave_carry_over"
        verbose_name = _("Leave Carry-over")
        verbose_name_plural = _("Leave Carry-overs")
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


# --- TRANSACTIONS & REQUESTS ---

class LeaveRequest(BaseAuditableModel):
    """ Formal request for leave submitted by an employee. """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_requests",
        verbose_name=_("Employee")
    )
    category = models.CharField(
        max_length=20,
        choices=LeaveCategory.choices,
        verbose_name=_("Category"),
        help_text=_("Annual or Special/Circumstance leave.")
    )
    
    circumstance_type = models.CharField(
        max_length=50,
        choices=CircumstanceType.choices,
        null=True,
        blank=True,
        verbose_name=_("Special Type"),
        help_text=_("Required if category is Special Leave.")
    )
    
    start_date = models.DateField(
        verbose_name=_("Start Date")
    )
    end_date = models.DateField(
        verbose_name=_("End Date")
    )
    
    requested_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Requested Days"),
        help_text=_("Total effective days excluding holidays and weekends.")
    )
    
    status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING,
        verbose_name=_("Status")
    )
    
    attachment = models.FileField(
        upload_to='leave_proofs/%Y/',
        null=True,
        blank=True,
        verbose_name=_("Supporting Document"),
        help_text=_("Proof for special leave requests (e.g., certificates).")
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name=_("Comments")
    )

    class Meta:
        db_table = "leav_leave_request"
        verbose_name = _("Leave Request")
        verbose_name_plural = _("Leave Requests")
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F('start_date')),
                name="leave_start_before_end"
            ),
            models.CheckConstraint(
                condition=models.Q(requested_days__gt=0),
                name="positive_requested_days"
            )
        ]


class LeaveRecall(BaseAuditableModel):
    """ Record of an employee being requested to return to work before leave ends. """
    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name="recalls",
        verbose_name=_("Leave Request")
    )

    recall_date = models.DateField(
        verbose_name=_("Recall Date"),
        help_text=_("Date on which the employee resumed work.")
    )

    reason = models.TextField(
        verbose_name=_("Reason"),
        help_text=_("Official justification for the recall.")
    )

    recalled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="leave_recalls",
        verbose_name=_("Authorized By")
    )

    class Meta:
        db_table = "leav_leave_recall"
        verbose_name = _("Leave Recall")
        verbose_name_plural = _("Leave Recalls")
        indexes = [
            models.Index(fields=['leave_request', 'recall_date']),
        ]


class LeaveTransaction(BaseAuditableModel):
    """ Detailed log of all leave balance movements (Accruals, Usage, Returns). """
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name="leave_transactions",
        verbose_name=_("Employee")
    )
    
    year = models.PositiveIntegerField(
        verbose_name=_("Affected Year")
    )
    
    amount = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name=_("Amount"),
        help_text=_("Negative for usage, positive for accruals/refunds.")
    )
    
    transaction_type = models.CharField(
        max_length=20, 
        choices=LeaveTransactionTypes.choices,
        verbose_name=_("Type")
    )
    
    leave_request = models.ForeignKey(
        'LeaveRequest', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        verbose_name=_("Related Request")
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name=_("Remarks")
    )

    class Meta:
        db_table = "leav_leave_transaction"
        verbose_name = _("Leave Transaction")
        verbose_name_plural = _("Leave Transactions")
        indexes = [
            models.Index(fields=['employee', 'year']),
            models.Index(fields=['transaction_type']),
        ]


# --- Audit log registration ---
auditlog.register(LeavePolicy)
auditlog.register(SeniorityRule)
auditlog.register(CircumstanceLeaveRule)
auditlog.register(LeaveBalance)
auditlog.register(LeaveRequest)
auditlog.register(LeaveRecall)
auditlog.register(LeaveTransaction)

