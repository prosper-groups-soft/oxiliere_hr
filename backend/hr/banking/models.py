import re
from django.db   import models
from django.conf import settings
from django.core.exceptions   import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from auditlog.registry import auditlog

from hr.models.base import BaseAuditableModel
from .enums   import AccountType, AccountStatus, BankAccountAction
from hr.enums import Currency, CountryCode


class Bank(BaseAuditableModel):
    """ Financial institutions and mobile money payment providers. """
    
    name = models.CharField(
        max_length=255, 
        verbose_name=_("Bank Name"),
        help_text=_("Official name of the financial institution.")
    )
    code = models.CharField(
        max_length=10, 
        verbose_name=_("Bank Code"),
        help_text=_("Unique identifier for payroll processing.")
    )
    swift_code = models.CharField(
        max_length=11, 
        blank=True, 
        null=True, 
        verbose_name=_("SWIFT Code"),
        help_text=_("Standard international BIC/SWIFT code.")
    )
    is_mobile_money = models.BooleanField(
        default=False, 
        verbose_name=_("Mobile Money"),
        help_text=_("Enable for telco-based wallet providers.")
    )
    logo = models.ImageField(
        upload_to='banking/logos/', 
        null=True, 
        blank=True,
        verbose_name=_("Logo"),
        help_text=_("Brand logo of the financial institution.")
    )
    country_code = models.CharField(
        max_length=3, 
        choices=CountryCode.choices, 
        default=CountryCode.DRC, 
        verbose_name=_("Country"),
        help_text=_("Country of operation for this bank.")
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name=_("Active")
    )

    class Meta:
        db_table = "bank_institution"
        ordering = ["name"]
        verbose_name = _("Bank")
        verbose_name_plural = _("Banks")
        constraints = [
            models.UniqueConstraint(
                fields=['code'],
                condition=models.Q(deleted__isnull=True),
                name='unique_bank_code'
            ),
        ]

    def clean(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = self.code.strip().upper()
        if self.swift_code:
            self.swift_code = self.swift_code.strip().upper()
            if not self.is_mobile_money and len(self.swift_code) not in [8, 11]:
                raise ValidationError(_("Standard banks must have 8 or 11 characters SWIFT code."))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class BankAccount(BaseAuditableModel):
    """ Employee bank and payment account details for salary distribution. """

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
        verbose_name=_("Bank"),
        help_text=_("The institution where the account is held.")
    )
    branch_code = models.CharField(
        max_length=10, 
        blank=True, 
        null=True, 
        verbose_name=_("Branch Code"),
        help_text=_("Specific code for the local bank branch.")
    )
    account_number = models.CharField(
         max_length=50, 
         verbose_name=_("Account Number"),
         help_text=_("The bank account or phone number for transfers.")
    )
    account_name = models.CharField(
        max_length=255, 
        verbose_name=_("Account Holder"),
        help_text=_("Full name as registered at the bank.")
    )
    account_type = models.CharField(
        max_length=20, 
        choices=AccountType.choices, 
        default=AccountType.CHECKING, 
        verbose_name=_("Type"),
        help_text=_("Category of account (e.g., Checking, Savings).")
    )
    currencies = models.JSONField(
        default=list,
        verbose_name=_("Currencies"),
        help_text=_("List of supported currencies (e.g., ['USD', 'CDF']).")
    )
    default_currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.USD,
        verbose_name=_("Default Currency"),
        help_text=_("Primary display currency for this account.")
    )
    iban = models.CharField(
        max_length=34, 
        blank=True, 
        null=True, 
        verbose_name=_("IBAN"),
        help_text=_("International Bank Account Number if required.")
    )
    is_primary = models.BooleanField(
        default=False, 
        verbose_name=_("Primary"),
        help_text=_("Mark as the main account for salary payments.")
    )
    status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.PENDING,
        verbose_name=_("Status"),
        help_text=_("Verification status of the account.")
    )
    verified_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Verified At")
    )
    document_proof = models.FileField(
        upload_to='banking/proofs/', 
        null=True, 
        blank=True, 
        verbose_name=_("RIB/Proof Document"),
        help_text=_("Official document certifying account ownership.")
    )
    notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_("Notes")
    )

    class Meta:
        db_table = "bank_account"
        ordering = ["-is_primary", "-created_at"]
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")
        constraints = [
            models.UniqueConstraint(
                fields=['bank', 'account_number'],
                condition=models.Q(deleted__isnull=True),
                name='unique_bank_account_number'
            ),
            models.UniqueConstraint(
                fields=['employee'],
                condition=models.Q(is_primary=True, deleted__isnull=True),
                name='unique_primary_account_per_employee'
            ),
        ]

    def clean(self):
        if self.account_number:
            self.account_number = re.sub(r'[^0-9A-Z]', '', self.account_number.strip().upper())
        if self.account_name:
            self.account_name = self.account_name.strip().upper()
        if self.status == AccountStatus.VERIFIED and not self.verified_at:
            self.verified_at = timezone.now()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        indicator = " [PRIMARY]" if self.is_primary else ""
        return f"{self.employee} - {self.bank.name} ({self.default_currency}){indicator}"


class BankAccountHistory(BaseAuditableModel):
    """ Audit record of changes to employee banking information. """

    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_("Bank Account")
    )
    action = models.CharField(
        max_length=50, 
        choices=BankAccountAction.choices,
        verbose_name=_("Action")
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_("Performed By")
    )
    changed_fields = models.JSONField(
        default=dict, 
        verbose_name=_("Changes")
    )
    notes = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Notes")
    )

    class Meta:
        db_table = "bank_account_history"
        ordering = ["-created_at"]
        verbose_name = _("Account History")
        verbose_name_plural = _("Account Histories")


# --- Audit log registration ---
auditlog.register(Bank)
auditlog.register(BankAccount)
auditlog.register(BankAccountHistory)
