from typing       import Tuple
from .attendance  import AttendanceController
from .registry    import RegistryController
from .scheduling  import SchedulingController
from .maintenance import MaintenanceController
from .validation  import ValidationController


def get_all_ctrls_attendance() -> Tuple:
    """
    Returns a tuple containing all the API controllers related to 
    attendance management.
    """
    return (
        AttendanceController,
        RegistryController,
        SchedulingController,
        MaintenanceController,
        ValidationController
    )


__all__ = [
    'AttendanceController',
    'RegistryController',
    'SchedulingController',
    'MaintenanceController',
    'ValidationController'
]

