from enum import Enum


class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class LeaveType(str, Enum):
    ANNUAL = "annual Leave"             # Standard annual leave
    SICK = "sick Leave"                 # Leave due to illness
    MATERNITY = "maternity Leave"       # Leave for maternity
    PATERNITY = "paternity Leave"       # Leave for paternity
    UNPAID = "unpaid Leave"             # Leave without pay
    COMPENSATORY = "compensatory Leave" # Time-off for extra hours worked
    BEREAVEMENT = "bereavement Leave"   # Leave due to death in family
    OTHER = "other Leave"               # Any other type of leave
    
