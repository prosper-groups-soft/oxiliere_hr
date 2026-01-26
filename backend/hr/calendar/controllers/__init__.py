from typing import Tuple
from .calendar import CalendarController


def get_all_ctrls_calendar() -> Tuple:
    """Get all calendar controllers."""
    return (
        CalendarController,
    )

