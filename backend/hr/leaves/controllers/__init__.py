from typing import Tuple
from .config import LeaveConfigController
from .leave_batch import LeaveBatchController
from .leave import LeaveController


def get_all_leaves_ctrls() -> Tuple:
    """
    Returns a tuple of all controllers related to leave management for API routing registration.
    """
    return (
        LeaveController,
        LeaveBatchController,
        LeaveConfigController,
    )


__all__ = [
    'LeaveConfigController',
    'LeaveBatchController',
    'LeaveController',
]

