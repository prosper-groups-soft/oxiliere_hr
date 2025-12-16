from typing import Optional
from hr.banking.models import BankAccountHistory


class BankAccountHistoryReaderService:
    """
    Reader for BankAccountHistory.
    """

    @staticmethod
    def list_history_for_account(account_id: int):
        return BankAccountHistory.objects.filter(
            bank_account_id=account_id
        ).order_by("-created_at")

    @staticmethod
    def list_history_for_employee(employee_id: int):
        return BankAccountHistory.objects.filter(
            bank_account__employee_id=employee_id
        ).order_by("-created_at")

    @staticmethod
    def get_history(history_id: int) -> Optional[BankAccountHistory]:
        return BankAccountHistory.objects.filter(id=history_id).first()