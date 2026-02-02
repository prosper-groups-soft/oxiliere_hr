import logging
from uuid   import UUID
from typing import Dict, Any

from django.db    import transaction
from django.utils import timezone

from core.services.crud import BaseCRUDService
from hr.banking.models import (
    Bank,
    BankAccount,
    BankAccountHistory
)
from hr.banking.enums import BankAccountAction


logger = logging.getLogger(__name__)


# --- Internal CRUD Helpers ---
class BankCRUD(BaseCRUDService):
    model = Bank


class BankAccountCRUD(BaseCRUDService):
    model = BankAccount


class BankingService:
    """ Unified management of banks and employee payment accounts. """
    
    def __init__(self):
        self.bank_crud = BankCRUD()
        self.account_crud = BankAccountCRUD()

    # --- Bank Management ---

    @transaction.atomic
    def create_bank(self, data: Dict[str, Any]) -> Bank:
        """ Registers a new financial institution in the system. """
        bank = self.bank_crud.create(data=data)
        bank.full_clean()
        bank.save()
        
        logger.info(f"Bank created: {bank.name} ({bank.code})")
        return bank

    @transaction.atomic
    def update_bank(self, bank_id: UUID, data: Dict[str, Any]) -> Bank:
        """ Updates the metadata for an existing bank. """
        bank = self.bank_crud.get(id=bank_id)
        self.bank_crud.update(instance=bank, data=data)
        
        logger.info(f"Bank updated: {bank.id}")
        return bank

    @transaction.atomic
    def delete_bank(self, bank_id: UUID):
        """ Removes a bank provider from the catalog. """
        bank = self.bank_crud.get(id=bank_id)
        self.bank_crud.delete(instance=bank)
        logger.info(f"Bank deleted: {bank_id}")

    # --- Bank Account Management ---

    @transaction.atomic
    def create_bank_account(self, employee_id: UUID, bank_id: UUID, account_data: Dict[str, Any], actor=None):
        """ Sets up a new payment account for an employee. """
        currency = account_data.get('currency')
        if not currency:
            currency = BankAccount._meta.get_field('currency').default

        existing_accounts = self.account_crud.exists(
            employee_id=employee_id, 
            currency=currency
        )

        is_primary = account_data.get('is_primary', not existing_accounts)

        if is_primary:
            BankAccount.objects.filter(
                employee_id=employee_id, 
                currency=currency,
                is_primary=True
            ).update(is_primary=False)

        account_data['employee_id'] = employee_id
        account_data['bank_id'] = bank_id
        account_data['is_primary'] = is_primary
        account_data['created_by'] = actor
        
        account = self.account_crud.create(data=account_data)
        self._log_history(account, BankAccountAction.CREATED, actor)
        
        logger.info(f"Bank account created for employee {employee_id}")
        return account

    @transaction.atomic
    def update_account(self, account_id: UUID, data: Dict[str, Any], actor=None) -> BankAccount:
        """ Modifies existing bank account details with full audit tracing. """
        account = BankAccount.objects.select_for_update().get(id=account_id)
        changed_fields = {}
        
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
        """ Formally validates a bank account for payroll use. """
        account = self.account_crud.get(id=account_id)
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
        """ Revokes the validation status of a payment account. """
        account = self.account_crud.get(id=account_id)
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
        """ Designates the main account for salary distribution in a specific currency. """
        account = self.account_crud.get(id=account_id)
        
        if not account.is_primary:
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
        """ Restores a suspended bank account to active status. """
        account = self.account_crud.get(id=account_id)
        if not account.is_active:
            account.is_active = True
            if  actor:
                account.updated_by = actor
            account.save(update_fields=['is_active', 'updated_at', 'updated_by'])
            self._log_history(account, BankAccountAction.ACTIVATED, actor)
        return account

    @transaction.atomic
    def deactivate_account(self, account_id: UUID, actor=None):
        """ Suspends a bank account from further payroll processing. """
        account = self.account_crud.get(id=account_id)
        if account.is_active:
            account.is_active = False
            if actor:
                account.updated_by = actor
            account.save(update_fields=['is_active', 'updated_at', 'updated_by'])
            self._log_history(account, BankAccountAction.DEACTIVATED, actor)
        return account

    @transaction.atomic
    def delete_account(self, account_id: UUID, actor=None):
        """ Formally removes a bank account record from the system. """
        account = self.account_crud.get(id=account_id)
        if actor:
            account.updated_by = actor
        
        self._log_history(account, BankAccountAction.DELETED, actor)
        self.account_crud.delete(instance=account)

    def _log_history(self, account, action, actor, changed_fields=None, notes=None):
        """ Internal helper to record banking modifications. """
        BankAccountHistory.objects.create(
            bank_account=account,
            action=action,
            changed_by=actor,
            changed_fields=changed_fields or {},
            notes=notes
        )

    def generate_payroll_export(self, bank_code: str = None, currency: str = "CDF"):
        """ Compiles verified and active account data for mass bank transfers. """
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
                "amount": 0.0,
                "reason": "SALAIRE DU MOIS"
            })
        
        return data

