import json
import logging
from pathlib import Path
from typing    import Dict, Any
from uuid      import UUID

from django.db    import transaction
from django.utils import timezone
from django.db.models.deletion import ProtectedError
from django.core.exceptions import ValidationError

from core.services.crud import BaseCRUDService
from hr.banking.models  import (
    Bank,
    BankAccount,
    BankAccountHistory
)
from hr.banking.enums import BankAccountAction, AccountStatus


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
        try:
            bank = self.bank_crud.get(id=bank_id)
            self.bank_crud.delete(instance=bank)
            logger.info(f"Bank deleted: {bank_id}")
        except ProtectedError:
            account_count = BankAccount.objects.filter(bank_id=bank_id).count()
            raise ValidationError(
                f"Impossible de supprimer cette institution : {account_count} compte(s) bancaire(s) "
                f"y sont rattaché(s). Veuillez d'abord supprimer ou réaffecter ces comptes."
            )

    def _read_fixture_entries(self) -> list[dict]:
        """Read and parse the initial_banks.json fixture file."""
        fixture_path = Path(__file__).resolve().parent.parent / "fixtures" / "initial_banks.json"
        with open(fixture_path, encoding="utf-8") as f:
            fixtures = json.load(f)

        entries = []
        for item in fixtures:
            fields = item["fields"]
            entries.append({
                "name": fields["name"],
                "code": fields["code"],
                "swift_code": fields.get("swift_code", "") or "",
                "is_mobile_money": fields.get("is_mobile_money", False),
                "country_code": fields.get("country_code", "CD"),
            })
        return entries

    def list_seedable_banks(self) -> list[dict]:
        """
        Returns the list of institutions available in the fixture,
        annotated with whether they already exist in the database.
        """
        entries = self._read_fixture_entries()
        existing_codes = set(Bank.objects.values_list('code', flat=True))
        for entry in entries:
            entry["exists"] = entry["code"] in existing_codes
        return entries

    @transaction.atomic
    def seed_default_banks(self, codes: list[str] | None = None) -> dict:
        """
        Bulk-create default DRC financial institutions from the fixture file.
        Deduplicates by 'code'. Optionally filter by codes to seed only selected ones.
        Returns a summary of created vs skipped.
        """
        entries = self._read_fixture_entries()

        if codes:
            entries = [e for e in entries if e["code"] in codes]

        existing_codes = set(Bank.objects.values_list('code', flat=True))
        created = []
        skipped = []

        for entry in entries:
            if entry["code"] in existing_codes:
                skipped.append(entry["name"])
                continue

            # Sanitize: if swift_code is empty or invalid for a standard bank, clear it
            swift = (entry.get("swift_code") or "").strip()
            if not swift:
                entry["swift_code"] = None
            elif not entry.get("is_mobile_money") and len(swift) not in (8, 11):
                logger.warning(f"Clearing invalid SWIFT code '{swift}' for {entry['name']}")
                entry["swift_code"] = None

            bank = Bank(**entry)
            bank.full_clean()
            bank.save()
            created.append(entry["name"])
            existing_codes.add(entry["code"])

        logger.info(
            f"Seed banks: {len(created)} created, {len(skipped)} already exist."
        )
        return {
            "created": created,
            "created_count": len(created),
            "skipped": skipped,
            "skipped_count": len(skipped),
        }

    # --- Bank Account Management ---

    @transaction.atomic
    def create_bank_account(self, employee_id: UUID, bank_id: UUID, account_data: Dict[str, Any], actor=None):
        """ Sets up a new payment account for an employee. """
        currencies = account_data.get('currencies', ['USD'])
        default_currency = account_data.get('default_currency', 'USD')

        # Ensure default_currency is in currencies
        if default_currency not in currencies:
            currencies = currencies + [default_currency]

        existing_accounts = self.account_crud.exists(
            employee_id=employee_id
        )

        is_primary = account_data.get('is_primary', not existing_accounts)

        if is_primary:
            BankAccount.objects.filter(
                employee_id=employee_id,
                is_primary=True
            ).update(is_primary=False)

        account_data['employee_id'] = employee_id
        account_data['bank_id'] = bank_id
        account_data['currencies'] = currencies
        account_data['default_currency'] = default_currency
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
        
        restricted_fields = {'verified_at', 'employee', 'bank'}
        
        for field, value in data.items():
            if field in restricted_fields:
                continue
            
            # Map foreign key fields
            if field == 'employee_id':
                if value and (account.employee_id != value):
                    changed_fields['employee'] = {'old': str(account.employee_id), 'new': str(value)}
                    account.employee_id = value
                    if actor:
                        account.updated_by = actor
                    account.save(update_fields=['employee_id', 'updated_by'])
                continue
            
            if field == 'bank_id':
                if value and (str(account.bank_id) != str(value)):
                    changed_fields['bank'] = {'old': str(account.bank_id), 'new': str(value)}
                    account.bank_id = value
                    if actor:
                        account.updated_by = actor
                    account.save(update_fields=['bank_id', 'updated_by'])
                continue
            
            if field == 'is_primary':
                if account.is_primary != value:
                    # Unset other primaries for this employee first
                    BankAccount.objects.filter(
                        employee_id=account.employee_id,
                        is_primary=True
                    ).exclude(id=account.id).update(is_primary=False)
                    changed_fields['is_primary'] = {'old': str(account.is_primary), 'new': str(value)}
                    account.is_primary = value
                    account.save(update_fields=['is_primary'])
                continue

            if field == 'status':
                if account.status != value:
                    changed_fields['status'] = {'old': str(account.status), 'new': str(value)}
                    account.status = value
                    # Manage verified_at based on status
                    if value == AccountStatus.VERIFIED:
                        account.verified_at = timezone.now()
                    elif value in (AccountStatus.PENDING, AccountStatus.REJECTED):
                        account.verified_at = None
                    account.save(update_fields=['status', 'verified_at'])
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
        if account.status != AccountStatus.VERIFIED:
            account.status = AccountStatus.VERIFIED
            account.verified_at = timezone.now()
            if actor:
                account.updated_by = actor
            account.save(update_fields=['status', 'verified_at', 'updated_at', 'updated_by'])
            self._log_history(account, BankAccountAction.VERIFIED, actor)
        return account

    @transaction.atomic
    def unverify_account(self, account_id: UUID, actor=None):
        """ Revokes the validation status of a payment account. """
        account = self.account_crud.get(id=account_id)
        if account.status == AccountStatus.VERIFIED:
            account.status = AccountStatus.PENDING
            account.verified_at = None
            if actor:
                account.updated_by = actor
            account.save(update_fields=['status', 'verified_at', 'updated_at', 'updated_by'])
            self._log_history(account, BankAccountAction.UNVERIFIED, actor)
        return account

    @transaction.atomic
    def set_primary_account(self, account_id: UUID, actor=None):
        """ Designates the main account for salary distribution. """
        account = self.account_crud.get(id=account_id)
        
        if not account.is_primary:
            BankAccount.objects.filter(
                employee=account.employee,
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
        if account.status == AccountStatus.BLOCKED:
            account.status = AccountStatus.PENDING
            if actor:
                account.updated_by = actor
            account.save(update_fields=['status', 'updated_at', 'updated_by'])
            self._log_history(account, BankAccountAction.ACTIVATED, actor)
        return account

    @transaction.atomic
    def deactivate_account(self, account_id: UUID, actor=None):
        """ Suspends a bank account from further payroll processing. """
        account = self.account_crud.get(id=account_id)
        if account.status != AccountStatus.BLOCKED:
            account.status = AccountStatus.BLOCKED
            if actor:
                account.updated_by = actor
            account.save(update_fields=['status', 'updated_at', 'updated_by'])
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
            status=AccountStatus.VERIFIED,
            default_currency=currency
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
                "currency": acc.default_currency,
                "amount": 0.0,
                "reason": "SALAIRE DU MOIS"
            })
        
        return data

