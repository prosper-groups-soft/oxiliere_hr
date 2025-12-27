from typing import Optional
from django.db import transaction, models
from hr.banking.models import Bank


class BankWriterService:
    """
    Writer service for Bank model.
    Responsibility: create/update/delete Banks with data normalization 
    and model validation.
    """

    @staticmethod
    @transaction.atomic
    def create_bank(
        name: str, 
        code: str, 
        swift_code: Optional[str] = None,
        country: Optional[str] = None, 
        country_code: Optional[str] = None,
        is_active: bool = True
    ) -> Bank:
        """
        Create and return a Bank instance after cleaning/validation.
        """
        bank = Bank(
            name=(name or "").strip().title(),
            code=(code or "").strip().upper(),
            swift_code=(swift_code or None),
            country=(country or Bank._meta.get_field("country").default),
            country_code=(country_code or Bank._meta.get_field("country_code").default),
            is_active=is_active
        )
        bank.full_clean()
        bank.save()
        return bank

    @staticmethod
    @transaction.atomic
    def update_bank(bank_id: int, **kwargs) -> Bank:
        """
        Update a Bank. Accepts name, code, swift_code, country, country_code, is_active.
        """
        try:
            bank = Bank.objects.get(id=bank_id)
        except Bank.DoesNotExist:
            raise ValueError(f"Bank {bank_id} not found")

        if "name" in kwargs and kwargs["name"]:
            kwargs["name"] = kwargs["name"].strip().title()
        if "code" in kwargs and kwargs["code"]:
            kwargs["code"] = kwargs["code"].strip().upper()
        if "swift_code" in kwargs and kwargs["swift_code"]:
            kwargs["swift_code"] = kwargs["swift_code"].strip().upper()

        for field, value in kwargs.items():
            if hasattr(bank, field):
                setattr(bank, field, value)

        bank.full_clean()
        bank.save()
        return bank

    @staticmethod
    @transaction.atomic
    def delete_bank(bank_id: int) -> None:
        """
        Delete a bank. Caller should ensure no critical external references exist.
        """
        bank = Bank.objects.get(id=bank_id)
        bank.delete()


class BankReaderService:
    """
    Reader service for Bank model: retrieval and search helpers.
    """

    @staticmethod
    def get_bank(bank_id: int) -> Optional[Bank]:
        return Bank.objects.filter(id=bank_id).first()

    @staticmethod
    def list_banks(active_only: bool = False):
        qs = Bank.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return qs

    @staticmethod
    def search_banks(query: str):
        q = (query or "").strip()
        return Bank.objects.filter(
            models.Q(name__icontains=q) | models.Q(code__icontains=q)
        ).order_by("name")

