import re
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from auditlog.registry import auditlog

from hr.models import BaseAuditableModel
from .enums import (
    AccountType,
    BankAccountAction,
)
from hr.enums import ( 
    Currency, 
    CountryCode,
)


class Bank(BaseAuditableModel):
    """
    Represents a financial institution or mobile money provider.
    
    Stores standardized banking information including SWIFT codes and country data.
    Used to validate and group employee bank accounts.
    """
    
    name = models.CharField(max_length=255, verbose_name=_("Bank Name"))
    code = models.CharField(max_length=10, unique=True, verbose_name=_("Bank Code"))
    swift_code = models.CharField(max_length=11, blank=True, null=True, verbose_name=_("SWIFT Code"))
    
    # Practical flags for payroll processing
    is_mobile_money = models.BooleanField(default=False, verbose_name=_("Is Mobile Money Provider"))
    country_code = models.CharField(max_length=3, choices=CountryCode.choices, default=CountryCode.DRC, verbose_name=_("Country Code"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        db_table = "bank_institution"
        ordering = ["name"]
        verbose_name = _("Bank")
        verbose_name_plural = _("Banks")

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()
        if self.code:
            self.code = self.code.strip().upper()
        if self.swift_code:
            self.swift_code = self.swift_code.strip().upper()
            if not self.is_mobile_money and len(self.swift_code) not in [8, 11]:
                raise ValidationError(_("Standard banks must have 8 or 11 characters SWIFT code."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class BankAccount(BaseAuditableModel):
    """
    Represents an employee's bank account for salary payment.
    
    An employee can have multiple accounts (e.g., in different currencies),
    but only one can be marked as 'Primary' per currency (enforced by constraints).
    Includes verification status and IBAN support.
    """

    employee = models.ForeignKey(
        'hr_employees.Employee',
        on_delete=models.CASCADE,
        related_name='bank_accounts',
        verbose_name=_("Employee")
    )
    bank = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        related_name='accounts',
        verbose_name=_("Bank")
    )
    
    # Specific fields for mass transfer (Rawbank/TMB/OHADA standards)
    branch_code = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("Branch Code"))
    account_number = models.CharField(max_length=50, verbose_name=_("Account Number"))
    account_name = models.CharField(max_length=255, verbose_name=_("Account Holder Name"))
    
    account_type = models.CharField(
        max_length=20, 
        choices=AccountType.choices, 
        default=AccountType.CHECKING, 
        verbose_name=_("Account Type")
    )
    currency = models.CharField(
        max_length=3, 
        choices=Currency.choices, 
        default=Currency.CDF, 
        verbose_name=_("Currency")
    )
    
    iban = models.CharField(max_length=34, blank=True, null=True, verbose_name=_("IBAN"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Primary Account"))
    
    # Verification & Compliance
    verified = models.BooleanField(default=False, verbose_name=_("Verified"))
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Verified At"))
    document_proof = models.FileField(upload_to='banking/proofs/', null=True, blank=True, verbose_name=_("RIB/Proof Document"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    class Meta:
        db_table = "bank_account"
        ordering = ["-is_primary", "-created_at"]
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")
        unique_together = [('bank', 'account_number', 'currency')]
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'currency'],
                condition=models.Q(is_primary=True),
                name='unique_primary_account_per_employee_currency'
            )
        ]

    def clean(self):
        # 1. Formatting account number (remove spaces/special chars)
        if self.account_number:
            self.account_number = re.sub(r'[^0-9A-Z]', '', self.account_number.strip().upper())

        # 2. Capitalize account name for bank matching
        if self.account_name:
            self.account_name = self.account_name.strip().upper()

        # 3. Handle verification date
        if self.verified and not self.verified_at:
            self.verified_at = timezone.now()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        indicator = " [PRIMARY]" if self.is_primary else ""
        return f"{self.employee} - {self.bank.name} ({self.currency}){indicator}"


class BankAccountHistory(BaseAuditableModel):
    """
    Historical log of changes made to a bank account.
    
    This model provides a detailed audit trail for sensitive operations such as
    creation, updates, verification, and status changes (activation/deactivation).
    It works alongside 'auditlog' but focuses on business-logic specific actions.
    """

    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_("Bank Account")
    )
    action = models.CharField(max_length=50, choices=BankAccountAction.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True
    )
    changed_fields = models.JSONField(default=dict, verbose_name=_("Changed Data"))
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "bank_account_history"
        ordering = ["-created_at"]
        verbose_name = _("Bank Account History")
        verbose_name_plural = _("Bank Account Histories")


# --- AUDIT LOG REGISTRATION ---

auditlog.register(Bank)
auditlog.register(BankAccount)
auditlog.register(BankAccountHistory)
