from typing      import Tuple
from .attendance import AttendanceController
from .registry   import RegistryController
from .scheduling import SchedulingController


def get_all_attendance_ctrls() -> Tuple:
    """
    Returns a tuple containing all the API controllers related to attendance management.
    """
    return (
        AttendanceController,
        RegistryController,
        SchedulingController
    )


__all__ = [
    'AttendanceController',
    'RegistryController',
    'SchedulingController'
]

