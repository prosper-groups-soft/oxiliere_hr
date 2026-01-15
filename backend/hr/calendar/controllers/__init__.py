from typing import Tuple
from .calendar import CalendarController


def get_all_calendar_ctrls() -> Tuple:
    """Get all calendar controllers."""
    return (
        CalendarController,
    )

