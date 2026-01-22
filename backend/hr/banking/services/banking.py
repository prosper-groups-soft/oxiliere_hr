import logging
from uuid import UUID
from typing import Dict, Any

from django.db import transaction
from django.utils import timezone

from hr.banking.models import (
    Bank,
    BankAccount,
    BankAccountHistory
)
from hr.banking.enums import BankAccountAction


logger = logging.getLogger(__name__)


class BankingService:
    """
    Unified service for managing Banks and Bank Accounts.
    Covers creation, updates, verification, and lifecycle management.
    """
    
    # --- Bank Management ---

    @transaction.atomic
    def create_bank(self, data: Dict[str, Any]) -> Bank:
        """Create a new Bank institution."""
        bank = Bank(**data)
        bank.full_clean()
        bank.save()
        logger.info(f"Bank created: {bank.name} ({bank.code})")
        return bank

    @transaction.atomic
    def update_bank(self, bank_id: UUID, data: Dict[str, Any]) -> Bank:
        """Update generic Bank details."""
        bank = Bank.objects.get(id=bank_id)
        for field, value in data.items():
            if hasattr(bank, field):
                setattr(bank, field, value)
        bank.full_clean()
        bank.save()
        logger.info(f"Bank updated: {bank.id}")
        return bank

    @transaction.atomic
    def delete_bank(self, bank_id: UUID):
        """Delete a bank (soft delete if configured, else hard delete)."""
        bank = Bank.objects.get(id=bank_id)
        bank.delete()
        logger.info(f"Bank deleted: {bank_id}")

    # --- Bank Account Management ---

    @transaction.atomic
    def create_bank_account(self, employee_id: UUID, bank_id: UUID, account_data: Dict[str, Any], actor=None):
        """
        Creates a new bank account and logs the history.
        Ensures that if it's the first account for a currency, it becomes primary.
        """
        # Check if this is the first account for this currency
        currency = account_data.get('currency')
        if not currency:
            # Default to model default if not provided, but usually required in data
            currency = BankAccount._meta.get_field('currency').default

        existing_accounts = BankAccount.objects.filter(
            employee_id=employee_id, 
            currency=currency
        ).exists()

        is_primary = account_data.get('is_primary', not existing_accounts)

        # If we want this to be primary, we must unset others first
        if is_primary:
            BankAccount.objects.filter(
                employee_id=employee_id, 
                currency=currency,
                is_primary=True
            ).update(is_primary=False)

        account = BankAccount.objects.create(
            employee_id=employee_id,
            bank_id=bank_id,
            is_primary=is_primary,
            created_by=actor,
            **account_data
        )

        # Log History
        self._log_history(account, BankAccountAction.CREATED, actor)
        
        logger.info(f"Bank account created for employee {employee_id} at bank {bank_id}")
        return account

    @transaction.atomic
    def update_account(self, account_id: UUID, data: Dict[str, Any], actor=None) -> BankAccount:
        """
        Update account details with audit logging.
        """
        account = BankAccount.objects.select_for_update().get(id=account_id)
        changed_fields = {}
        
        # Prevent direct changes to sensitive flags via generic update
        restricted_fields = {'is_primary', 'verified', 'verified_at', 'employee', 'bank'}
        
        for field, value in data.items():
            if field in restricted_fields:
                continue
            
            if hasattr(account, field):
                old_val = getattr(account, field)
                if old_val != value:
                    changed_fields[field] = {'old': str(old_val), 'new': str(value)}
                    setattr(account, field, value)

        if changed_fields:
            account.full_clean()
            account.save()
            self._log_history(
                account, 
                BankAccountAction.UPDATED, 
                actor, 
                changed_fields=changed_fields,
                notes=data.get('notes')
            )
        
        if actor:
            account.updated_by = actor
            account.save(update_fields=['updated_by'])  
        
        return account

    @transaction.atomic
    def verify_account(self, account_id: UUID, actor=None):
        """Marks an account as verified for payroll processing."""
        account = BankAccount.objects.get(id=account_id)
        if not account.verified:
            account.verified = True
            account.verified_at = timezone.now()
            if actor:
                account.updated_by = actor
            account.save(update_fields=['verified', 'verified_at', 'updated_at', 'updated_by'])
            self._log_history(account, BankAccountAction.VERIFIED, actor)
        return account

    @transaction.atomic
    def unverify_account(self, account_id: UUID, actor=None):
        """Revokes verification status."""
        account = BankAccount.objects.get(id=account_id)
        if account.verified:
            account.verified = False
            account.verified_at = None
            if actor:
                account.updated_by = actor
            account.save(update_fields=['verified', 'verified_at', 'updated_at', 'updated_by'])
            self._log_history(account, BankAccountAction.UNVERIFIED, actor)
        return account

    @transaction.atomic
    def set_primary_account(self, account_id: UUID, actor=None):
        """Switches the primary account for a specific currency."""
        account = BankAccount.objects.get(id=account_id)
        
        if not account.is_primary:
            # Unset current primary for the same currency
            BankAccount.objects.filter(
                employee=account.employee,
                currency=account.currency,
                is_primary=True
            ).update(is_primary=False)

            account.is_primary = True
            if actor:
                account.updated_by = actor
            account.save(update_fields=['is_primary', 'updated_at', 'updated_by'])
            self._log_history(account, BankAccountAction.SET_PRIMARY, actor)
        
        return account

    @transaction.atomic
    def activate_account(self, account_id: UUID, actor=None):
        """Activates a suspended account."""
        account = BankAccount.objects.get(id=account_id)
        if not account.is_active:
            account.is_active = True
            if  actor:
                account.updated_by = actor
            account.save(update_fields=['is_active', 'updated_at', 'updated_by'])
            self._log_history(account, BankAccountAction.ACTIVATED, actor)
        return account

    @transaction.atomic
    def deactivate_account(self, account_id: UUID, actor=None):
        """Deactivates/Suspends a bank account."""
        account = BankAccount.objects.get(id=account_id)
        if account.is_active:
            account.is_active = False
            if actor:
                account.updated_by = actor
            account.save(update_fields=['is_active', 'updated_at', 'updated_by'])
            self._log_history(account, BankAccountAction.DEACTIVATED, actor)
        return account

    @transaction.atomic
    def delete_account(self, account_id: UUID, actor=None):
        """
        Deletes a bank account. 
        Logs the deletion in history before removing the record 
        (if using soft delete, it actually keeps record but marks delete).
        """
        account = BankAccount.objects.get(id=account_id)
        if actor:
            account.updated_by = actor
        account.delete()
        self._log_history(account, BankAccountAction.DELETED, actor)

    def _log_history(self, account, action, actor, changed_fields=None, notes=None):
        """Internal helper to create audit history."""
        BankAccountHistory.objects.create(
            bank_account=account,
            action=action,
            changed_by=actor,
            changed_fields=changed_fields or {},
            notes=notes
        )

    def generate_payroll_export(self, bank_code: str = None, currency: str = "CDF"):
        """
        Generates the data ready for a mass transfer.
        Filters only verified and active accounts.
        """
        queryset = BankAccount.objects.filter(
            verified=True,
            is_active=True,
            currency=currency
        ).select_related('employee', 'bank')

        if bank_code:
            queryset = queryset.filter(bank__code=bank_code)

        data = []
        for acc in queryset:
            data.append({
                "matricule": acc.employee.matricule,
                "full_name": f"{acc.employee.last_name} {acc.employee.middle_name} {acc.employee.first_name}",
                "bank_name": acc.bank.name,
                "bank_code": acc.bank.code,
                "branch_code": acc.branch_code or "00000",
                "account_number": acc.account_number,
                "currency": acc.currency,
                "amount": 0.0,  # To be filled by Payroll module
                "reason": "SALAIRE DU MOIS"
            })
        
        return data