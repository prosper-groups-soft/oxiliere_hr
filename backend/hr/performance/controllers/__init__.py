"""Performance Module Controllers

Exports all performance API controllers for registration in the main router.
"""

from typing import Any
from .reviews import PerformanceReviewController


def get_all_ctrls_performance() -> tuple[type[Any], ...]:
    """Returns a tuple of all controllers related to performance management."""
    return (
        PerformanceReviewController,
    )


__all__ = [
    'PerformanceReviewController',
]
