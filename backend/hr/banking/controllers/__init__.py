from typing import Any
from .banking import BankingController


def get_all_ctrls_banking() -> tuple[type[Any], ...]:
    """Get all banking controllers."""
    return (
        BankingController,
    )


__all__ = [
    "BankingController",
]

