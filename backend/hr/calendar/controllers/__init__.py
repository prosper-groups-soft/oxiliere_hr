from typing import Any
from .calendar import CalendarController


def get_all_ctrls_calendar() -> tuple[type[Any], ...]:
    """Get all calendar controllers."""
    return (
        CalendarController,
    )

