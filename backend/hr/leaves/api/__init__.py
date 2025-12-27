from .leaves import LeaveAPI
from .leave_employees import LeaveEmployeeAPI


def get_all_leaves_apis():
    return (
        LeaveAPI,
        LeaveEmployeeAPI
    )
    
