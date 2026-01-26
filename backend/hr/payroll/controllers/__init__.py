"""
Payroll Module Controllers

Exports all payroll API controllers for registration in the main router.
"""

from .configuration import PayrollConfigurationController
from .contracts     import EmployeeContractController
from .payslips      import PayrollRunController
from .advances      import SalaryAdvanceController
from .adjustments   import PayrollAdjustmentsController


def get_all_ctrls_payroll():
    """
    Returns a tuple of all controllers related to payroll management for API routing registration.
    """
    return (
        PayrollConfigurationController,
        EmployeeContractController,
        PayrollRunController,
        SalaryAdvanceController,
        PayrollAdjustmentsController,
    )


__all__ = [
    'PayrollConfigurationController',
    'EmployeeContractController',
    'PayrollRunController',
    'SalaryAdvanceController',
    'PayrollAdjustmentsController',
]

