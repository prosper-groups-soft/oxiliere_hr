from enum import Enum


class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


class LeaveType(str, Enum):
    ANNUAL = "Annual Leave"             # Standard annual leave
    SICK = "Sick Leave"                 # Leave due to illness
    MATERNITY = "Maternity Leave"       # Leave for maternity
    PATERNITY = "Paternity Leave"       # Leave for paternity
    UNPAID = "Unpaid Leave"             # Leave without pay
    COMPENSATORY = "Compensatory Leave" # Time-off for extra hours worked
    BEREAVEMENT = "Bereavement Leave"   # Leave due to death in family
    OTHER = "Other Leave"               # Any other type of leave
    
