from typing     import Any
from .employee  import EmployeeController
from .family    import EmployeeFamilyController
from .lifecycle import EmployeeLifecycleController
from .records   import EmployeeRecordController
from .safety    import EmployeeSafetyController
from .worksite  import WorkSiteController
from .account   import UserController
from .career    import EmployeeCareerController


def get_all_ctrls_employees() -> tuple[type[Any], ...]:
    """
    Returns all controller classes related to employee management and workflows.
    """
    return (
        EmployeeController,
        EmployeeFamilyController,
        EmployeeLifecycleController,
        EmployeeRecordController,
        EmployeeSafetyController,
        WorkSiteController,
        UserController,
        EmployeeCareerController,
    )


__all__ = [
    'EmployeeController',
    'EmployeeFamilyController',
    'EmployeeLifecycleController',
    'EmployeeRecordController',
    'EmployeeSafetyController',
    'WorkSiteController',
    'UserController',
    'EmployeeCareerController',
]

