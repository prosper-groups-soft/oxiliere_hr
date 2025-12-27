from typing import Optional, Dict, Any
from django.utils import timezone
from django.db import transaction
from hr.employees.models import Employee
from hr.banking.models import (
    Bank, 
    BankAccount, 
    BankAccountHistory
)
import re


class BankAccountWriterService:
    """
    Writer service for BankAccount. Encapsulates business workflows:
      - create account (with optional mark primary)
      - update account (with history)
      - set primary (atomic)
      - verify/unverify
      - activate/deactivate
      - remove account (delete)
    Each method records BankAccountHistory entries.
    """

    @staticmethod
    def _record_history(
        bank_account: BankAccount, 
        action: str, 
        changed_fields: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None, 
        user: Optional[Any] = None
    ) -> BankAccountHistory:
        """
        Create a BankAccountHistory row describing an action.
        """
        history = BankAccountHistory.objects.create(
            bank_account=bank_account,
            action=action,
            changed_fields=changed_fields or {},
            notes=notes,
            created_by=user
        )
        return history

    @staticmethod
    @transaction.atomic
    def create_account(
        employee: Employee, 
        bank: Bank, 
        account_number: str, 
        account_name: str,
        account_type: str = "CHECKING", 
        iban: Optional[str] = None,
        is_primary: bool = False, 
        verify: bool = False, 
        created_by: Optional[Any] = None,
        notes: Optional[str] = None
    ) -> BankAccount:
        """
        Create a BankAccount and optionally mark as primary and/or verified.
        Enforces unique constraints and performs model validation.
        """
        acct = BankAccount(
            employee=employee,
            bank=bank,
            account_number=account_number,
            account_name=account_name,
            account_type=account_type,
            iban=iban,
            is_primary=is_primary,
            verified=verify
        )

        acct.full_clean()
        acct.save()

        # If requested, mark as primary using service logic (atomic)
        if is_primary:
            BankAccountWriterService.set_primary(acct.id, actor=created_by)

        # If requested to verify, set verified fields
        if verify:
            BankAccountWriterService.verify_account(acct.id, verified_by=created_by)

        BankAccountWriterService._record_history(
            acct, action="CREATED",
            changed_fields={"account_number": acct.account_number},
            notes=notes,
            user=created_by
        )
        return acct

    @staticmethod
    @transaction.atomic
    def update_account(
        account_id: int, 
        actor: Optional[Any] = None, 
        **kwargs
    ) -> BankAccount:
        """
        Update a BankAccount. Returns updated account and records history.
        Allowed modifiable fields: bank, account_number, account_name, 
        account_type, iban, is_active, notes
        Changing is_primary should go through set_primary.
        """
        acct = BankAccount.objects.select_for_update().get(id=account_id)
        changed = {}
        disallowed_primary = {"is_primary"}

        for field, value in kwargs.items():
            if field in disallowed_primary:
                continue
            if hasattr(acct, field):
                old = getattr(acct, field)
                if old != value:
                    changed[field] = {"old": old, "new": value}
                    setattr(acct, field, value)

        acct.full_clean()
        acct.save()

        # If caller requested to set primary, but provided in kwargs, 
        # ignore; use set_primary method instead.
        BankAccountWriterService._record_history(
            acct, 
            action="UPDATED", 
            changed_fields=changed or {}, 
            notes=kwargs.get("notes"), 
            user=actor
        )
        return acct

    @staticmethod
    @transaction.atomic
    def set_primary(account_id: int, actor: Optional[Any] = None) -> BankAccount:
        """
        Atomically set given account as primary for its employee and unset others.
        """
        acct = BankAccount.objects.select_for_update().get(id=account_id)
        # Unset other primaries for this employee
        BankAccount.objects.filter(
            employee=acct.employee, 
            is_primary=True
        ).exclude(id=acct.id).update(is_primary=False)
        # Set this one
        if not acct.is_primary:
            acct.is_primary = True
            acct.save(update_fields=["is_primary"])
        BankAccountWriterService._record_history(
            acct, 
            action="SET_PRIMARY", 
            changed_fields={"is_primary": True}, 
            user=actor
        )
        return acct

    @staticmethod
    @transaction.atomic
    def verify_account(account_id: int, verified_by: Optional[Any] = None) -> BankAccount:
        """
        Mark an account verified (sets verified=True and verified_at).
        """
        acct = BankAccount.objects.select_for_update().get(id=account_id)
        acct.verified = True
        acct.verified_at = timezone.now()
        if verified_by:
            acct.updated_by = verified_by
        acct.save(update_fields=["verified", "verified_at", "updated_by"])
        BankAccountWriterService._record_history(
            acct, 
            action="VERIFIED", 
            changed_fields={"verified": True}, 
            user=verified_by
        )
        return acct

    @staticmethod
    @transaction.atomic
    def unverify_account(account_id: int, actor: Optional[Any] = None) -> BankAccount:
        """
        Mark an account unverified.
        """
        acct = BankAccount.objects.select_for_update().get(id=account_id)
        acct.verified = False
        acct.verified_at = None
        if actor:
            acct.updated_by = actor
        acct.save(update_fields=["verified", "verified_at", "updated_by"])
        BankAccountWriterService._record_history(
            acct, 
            action="UNVERIFIED", 
            changed_fields={"verified": False}, 
            user=actor
        )
        return acct

    @staticmethod
    @transaction.atomic
    def activate_account(account_id: int, actor: Optional[Any] = None) -> BankAccount:
        acct = BankAccount.objects.select_for_update().get(id=account_id)
        acct.is_active = True
        if actor:
            acct.updated_by = actor
        acct.save(update_fields=["is_active", "updated_by"])
        BankAccountWriterService._record_history(
            acct, 
            action="ACTIVATED", 
            user=actor
        )
        return acct

    @staticmethod
    @transaction.atomic
    def deactivate_account(account_id: int, actor: Optional[Any] = None) -> BankAccount:
        acct = BankAccount.objects.select_for_update().get(id=account_id)
        acct.is_active = False
        if actor:
            acct.updated_by = actor
        acct.save(update_fields=["is_active", "updated_by"])
        BankAccountWriterService._record_history(
            acct, 
            action="DEACTIVATED", 
            user=actor
        )
        return acct

    @staticmethod
    @transaction.atomic
    def delete_account(account_id: int, actor: Optional[Any] = None) -> None:
        acct = BankAccount.objects.get(id=account_id)
        BankAccountWriterService._record_history(
            acct, 
            action="DEACTIVATED", 
            changed_fields={}, 
            user=actor, 
            notes="Deleted"
        )
        acct.delete()


class BankAccountReaderService:
    """
    Reader service for BankAccount: retrieval and queries.
    """

    @staticmethod
    def get_account(account_id: int) -> Optional[BankAccount]:
        return BankAccount.objects.filter(
            id=account_id
        ).select_related("employee", "bank").first()

    @staticmethod
    def list_accounts_for_employee(employee_id: int):
        return BankAccount.objects.filter(
            employee_id=employee_id
        ).select_related("bank").order_by("-is_primary", "-created_at")

    @staticmethod
    def list_accounts_for_bank(bank_id: int):
        return BankAccount.objects.filter(
            bank_id=bank_id
        ).select_related("employee").order_by("-is_primary", "-created_at")

    @staticmethod
    def find_by_account_number(bank_id: int, account_number: str) -> Optional[BankAccount]:
        num = re.sub(r'[^0-9]', '', (account_number or "").strip())
        return BankAccount.objects.filter(
            bank_id=bank_id, 
            account_number=num
        ).first()

    @staticmethod
    def get_primary_account(employee_id: int) -> Optional[BankAccount]:
        return BankAccount.objects.filter(
            employee_id=employee_id, 
            is_primary=True
        ).first()


