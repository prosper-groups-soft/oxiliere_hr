from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction
import re

from utils_mixins.models import BaseModelMixin


class Bank(BaseModelMixin):
    """Model representing a bank institution"""
    name = models.CharField(max_length=255, verbose_name="Nom de la banque")
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
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
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
            # Validate SWIFT code format (8 or 11 characters)
            if len(self.swift_code) not in [8, 11]:
                raise ValidationError("Le code SWIFT doit contenir 8 ou 11 caractères.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class BankAccount(BaseModelMixin):
    """Model representing a bank account for an employee"""
    ACCOUNT_TYPES = [
        ('CHECKING', 'Compte courant'),
        ('SAVINGS', 'Compte épargne'),
        ('SALARY', 'Compte salaire'),
        ('OTHER', 'Autre'),
    ]
    
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
        choices=ACCOUNT_TYPES,
        default='CHECKING',
        verbose_name="Type de compte"
    )
    iban = models.CharField(
        max_length=34,
        blank=True,
        null=True,
        verbose_name="IBAN"
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Compte principal"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    verified = models.BooleanField(
        default=False,
        verbose_name="Vérifié"
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Vérifié le"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes"
    )
    
    class Meta:
        ordering = ["-is_primary", "-created_at"]
        verbose_name = "Compte bancaire"
        verbose_name_plural = "Comptes bancaires"
        unique_together = [
            ('bank', 'account_number'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['employee'],
                condition=models.Q(is_primary=True),
                name='unique_primary_account_per_employee'
            )
        ]
    
    def clean(self):
        # Clean account number
        if self.account_number:
            self.account_number = re.sub(r'[^0-9]', '', self.account_number.strip())
            if not self.account_number:
                raise ValidationError("Le numéro de compte doit contenir au moins un chiffre.")
        
        # Clean account name
        if self.account_name:
            self.account_name = self.account_name.strip().title()
        
        # Clean IBAN
        if self.iban:
            self.iban = re.sub(r'[^A-Z0-9]', '', self.iban.strip().upper())
            if len(self.iban) < 15 or len(self.iban) > 34:
                raise ValidationError("L'IBAN doit contenir entre 15 et 34 caractères.")
        
        # Validate that account name matches employee name
        if self.employee and self.account_name:
            employee_full_name = f"{self.employee.first_name} {self.employee.last_name}".title()
            if self.account_name.lower() != employee_full_name.lower():
                # Allow some flexibility in name matching
                employee_names = [
                    employee_full_name,
                    f"{self.employee.last_name} {self.employee.first_name}".title(),
                    self.employee.first_name.title(),
                    self.employee.last_name.title()
                ]
                if not any(name.lower() == self.account_name.lower() for name in employee_names):
                    raise ValidationError(
                        f"Le nom du titulaire du compte doit correspondre au nom de l'employé: {employee_full_name}"
                    )
    
    @transaction.atomic
    def set_as_primary(self):
        """Set this account as primary and unset others"""
        # Unset other primary accounts for this employee
        BankAccount.objects.filter(
            employee=self.employee,
            is_primary=True
        ).exclude(id=self.id).update(is_primary=False)
        
        # Set this account as primary
        self.is_primary = True
        self.save(update_fields=['is_primary'])
    
    def verify_account(self, verified_by=None):
        """Mark account as verified"""
        from django.utils import timezone
        self.verified = True
        self.verified_at = timezone.now()
        if verified_by:
            self.updated_by = verified_by
        self.save(update_fields=['verified', 'verified_at', 'updated_by'])
    
    def unverify_account(self, updated_by=None):
        """Mark account as unverified"""
        self.verified = False
        self.verified_at = None
        if updated_by:
            self.updated_by = updated_by
        self.save(update_fields=['verified', 'verified_at', 'updated_by'])
    
    def save(self, *args, **kwargs):
        self.clean()
        
        # Auto-set as primary if it's the first account for this employee
        if not self.pk and not BankAccount.objects.filter(employee=self.employee).exists():
            self.is_primary = True
        
        super().save(*args, **kwargs)
        
        # If this account is set as primary, unset others
        if self.is_primary:
            BankAccount.objects.filter(
                employee=self.employee,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
    
    def __str__(self):
        primary_indicator = " (Principal)" if self.is_primary else ""
        return f"{self.employee} - {self.bank.name} - {self.account_number}{primary_indicator}"


class BankAccountHistory(models.Model):
    """Model to track changes to bank accounts"""
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Compte bancaire"
    )
    action = models.CharField(
        max_length=50,
        choices=[
            ('CREATED', 'Créé'),
            ('UPDATED', 'Modifié'),
            ('VERIFIED', 'Vérifié'),
            ('UNVERIFIED', 'Non vérifié'),
            ('ACTIVATED', 'Activé'),
            ('DEACTIVATED', 'Désactivé'),
            ('SET_PRIMARY', 'Défini comme principal'),
        ],
        verbose_name="Action"
    )
    changed_fields = models.JSONField(
        default=dict,
        verbose_name="Champs modifiés"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Créé par"
    )
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Historique compte bancaire"
        verbose_name_plural = "Historiques comptes bancaires"
    
    def __str__(self):
        return f"{self.bank_account} - {self.get_action_display()} - {self.created_at}"