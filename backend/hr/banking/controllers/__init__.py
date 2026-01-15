from typing import Tuple
from .banking import BankingController


def get_all_banking_ctrls() -> Tuple:
    """Get all banking controllers."""
    return (
        BankingController,
    )


__all__ = [
    "BankingController",
]

