from .employees import EmployeeAPI, EmployeeAddressAPI
from .children import EmployeeChildrenAPI
from .education import EmployeeEducationAPI
from .emergency_contact import EmployeeEmergencyContactAPI


def get_all_employee_api():
    return (
        EmployeeAPI,
        EmployeeAddressAPI,
        EmployeeChildrenAPI,
        EmployeeEducationAPI,
        EmployeeEmergencyContactAPI,
    )
