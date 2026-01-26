from typing     import Tuple
from .employee  import EmployeeController
from .family    import EmployeeFamilyController
from .lifecycle import EmployeeLifecycleController
from .records   import EmployeeRecordController
from .safety    import EmployeeSafetyController


def get_all_ctrls_employees() -> Tuple:
    """
    Returns all controller classes related to employee management and workflows.
    """
    return (
        EmployeeController,
        EmployeeFamilyController,
        EmployeeLifecycleController,
        EmployeeRecordController,
        EmployeeSafetyController,
    )


__all__ = [
    'EmployeeController',
    'EmployeeFamilyController',
    'EmployeeLifecycleController',
    'EmployeeRecordController',
    'EmployeeSafetyController'
]