from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from utils_mixins.models import BaseModelMixin
from .enums import AccountType, Currency, BankAccountAction
from utils_mixins.fn import enum_to_choices


class Bank(BaseModelMixin):
    """Model representing a bank institution."""
    
    name = models.CharField(
        max_length=255, 
        verbose_name="Nom de la banque"
    )
    code = models.CharField(
        max_length=10, 
        unique=True, 
        verbose_name="Code banque"
    )
    swift_code = models.CharField(
        max_length=11, 
        blank=True, 
        null=True, 
        verbose_name="Code SWIFT"
    )
    country = models.CharField(
        max_length=100, 
        default="République Démocratique du Congo", 
        verbose_name="Pays"
    )
    country_code = models.CharField(
        max_length=3, 
        default="CD", 
        verbose_name="Code pays"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Actif"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Banque"
        verbose_name_plural = "Banques"

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()
        if self.code:
            self.code = self.code.strip().upper()
        if self.swift_code:
            self.swift_code = self.swift_code.strip().upper()
            if len(self.swift_code) not in [8, 11]:
                raise ValidationError(
                    "Le code SWIFT doit contenir 8 ou 11 caractères."
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class BankAccount(BaseModelMixin):
    """Bank account linked to an employee."""

    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='bank_accounts',
        verbose_name="Employé"
    )
    bank = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        related_name='accounts',
        verbose_name="Banque"
    )
    account_number = models.CharField(
        max_length=50, 
        verbose_name="Numéro de compte"
    )
    account_name = models.CharField(
        max_length=255, 
        verbose_name="Nom du titulaire du compte"
    )
    account_type = models.CharField(
        max_length=20, 
        choices=enum_to_choices(AccountType), 
        default=AccountType.CHECKING.value, 
        verbose_name="Type de compte"
    )
    currency = models.CharField(
        max_length=3, 
        choices=enum_to_choices(Currency), 
        default=Currency.CDF.value, 
        verbose_name="Devise"
    )
    iban = models.CharField(
        max_length=34, 
        blank=True, 
        null=True, 
        verbose_name="IBAN"
    )
    is_primary = models.BooleanField(default=False, verbose_name="Compte principal")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    verified = models.BooleanField(default=False, verbose_name="Vérifié")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Vérifié le")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        ordering = ["-is_primary", "-created_at"]
        verbose_name = "Compte bancaire"
        verbose_name_plural = "Comptes bancaires"
        unique_together = [('bank', 'account_number', 'currency')]
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'currency'],
                condition=models.Q(is_primary=True),
                name='unique_primary_account_per_employee_currency'
            )
        ]

    def clean(self):
        # Clean account number
        if self.account_number:
            self.account_number = re.sub(r'[^0-9]', '', self.account_number.strip())
            if not self.account_number:
                raise ValidationError(
                    "Le numéro de compte doit contenir au moins un chiffre."
                )

        # Clean account name
        if self.account_name:
            self.account_name = self.account_name.strip().title()

        # Clean IBAN
        if self.iban:
            self.iban = re.sub(r'[^A-Z0-9]', '', self.iban.strip().upper())
            if not (15 <= len(self.iban) <= 34):
                raise ValidationError("L'IBAN doit contenir entre 15 et 34 caractères.")

        # Validate account name consistency
        if self.employee_id and self.account_name:
            employee_full_name = f"{self.employee.first_name} {self.employee.last_name}".title()

            valid_names = {
                employee_full_name,
                f"{self.employee.last_name} {self.employee.first_name}".title(),
                self.employee.first_name.title(),
                self.employee.last_name.title(),
            }

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        indicator = " (Principal)" if self.is_primary else ""
        return f"{self.employee} - {self.bank.name} - {self.currency} {self.account_number}{indicator}"


class BankAccountHistory(models.Model):
    """Tracks changes performed on a bank account."""

    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Compte bancaire"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True
    )

    action = models.CharField(
        max_length=50,
        choices=enum_to_choices(BankAccountAction)
    )

    changed_fields = models.JSONField(default=dict, verbose_name="Champs modifiés")
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Historique compte bancaire"
        verbose_name_plural = "Historiques comptes bancaires"

    def __str__(self):
        return f"{self.bank_account} - {self.get_action_display()} - {self.created_at}"

