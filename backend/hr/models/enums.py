from enum import Enum



class DegreeEnum(str, Enum):
    BREVET = 'B'
    DIMPLOMA = 'C'
    LICENSE = 'L'
    MASTER = 'M'
    PHD = 'Doctorat'


class GenderStatus(str, Enum):
    MALE = 'M'
    FEMALE = 'F'


class MaritalStatus(str, Enum):
    SINGLE = 'S'
    MARRIED = 'M'
    DIVORCED = 'D'
    WIDOW = 'W'


class EmployeeStatus(str, Enum):
    PERMANENT_WORKER = 'OW'
    LABOR_TECHNICIAN = 'LT'
    LABOR_WORKER = 'LW'


class RelationshipType(str, Enum):
    PARENT = 'P'
    CHILD = 'C'
    SIBLING = 'S'
    FRIEND = 'F'
    WIFE = 'W'
    OTHER = 'O'


class AttendanceStatus(str, Enum):
    PRESENT = 'P'
    ABSENT = 'A'
    LATE = 'L'
    EXCUSED = 'E'
    HOLIDAY = 'H'


class UpdateAttendanceStatus(str, Enum):
    PRESENT = 'P'
    ABSENT = 'A'
    EXCUSED = 'E'


class LeaveType(str, Enum):
    AN = 'AN'
    SI = 'SI'
    MA = 'MA'
    PE = 'PE'
    OT = 'OT'


class CalendarEventType(str, Enum):
    HOLIDAY = 'H'
    MEETING = 'M'
    TRAINING = 'T'
    BIRTHDAY = 'B'
    DEADLINE = 'D'
    OTHER = 'O'


class PaymentType(str, Enum):
    FIXED = 'FIXED'
    HOURLY = 'HOURLY'


class ContractType(str, Enum):
    CDI = 'CDI'
    CDD = 'CDD'
    INTERNSHIP = 'INTERNSHIP'
    FREELANCE = 'FREELANCE'
    TEMPORARY = 'TEMPORARY'


class PaymentPeriod(str, Enum):
    DAILY = 'DAILY'
    PER_TASK = 'PER_TASK'
    MONTHLY = 'MONTHLY'



class PayslipStatus(str, Enum):
    CONFIRMED = 'confirmed'
    PAID = 'paid'
    CANCELED = 'canceled'
    REVIEW = 'review'
