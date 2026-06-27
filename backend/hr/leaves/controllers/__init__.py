from typing import Any
from .config import LeaveConfigController
from .leave_batch import LeaveBatchController
from .leave import LeaveController
from .admin import LeaveAdminController


def get_all_ctrls_leaves() -> tuple[type[Any], ...]:
    """
    Returns a tuple of all controllers related to leave management for API routing registration.
    """
    return (
        LeaveController,
        LeaveBatchController,
        LeaveConfigController,
        LeaveAdminController,
    )


__all__ = [
    'LeaveConfigController',
    'LeaveBatchController',
    'LeaveController',
    'LeaveAdminController',
]

