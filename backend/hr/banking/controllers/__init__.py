from typing import Tuple
from .banking import BankingController


def get_all_ctrls_banking() -> Tuple:
    """Get all banking controllers."""
    return (
        BankingController,
    )


__all__ = [
    "BankingController",
]

