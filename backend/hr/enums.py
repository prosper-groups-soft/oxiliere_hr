from enum import Enum


class DegreeEnum(str, Enum):
    BREVET = "brevet"
    DIPLOMA = "diploma"
    LICENSE = "license"
    MASTER = "master"
    PHD = "phd"
    NOT_SPECIFIED = 'not specified'


class GenderStatus(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NOT_SPECIFIED = "not specified"


class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOW = "widow"


class EmployeeStatus(str, Enum):
    PERMANENT_WORKER = "permanent worker"
    LABOR_TECHNICIAN = "labor technician"
    LABOR_WORKER = "labor worker"


class RelationshipType(str, Enum):
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    FRIEND = "friend"
    SPOUSE = "spouse"
    OTHER = "other"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    HOLIDAY = "holiday"


class UpdateAttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"


class CalendarEventType(str, Enum):
    HOLIDAY = "holiday"
    MEETING = "meeting"
    TRAINING = "training"
    BIRTHDAY = "birthday"
    DEADLINE = "deadline"
    OTHER = "other"


class PaymentType(str, Enum):
    FIXED = "fixed"
    HOURLY = "hourly"


class ContractType(str, Enum):
    CDI = "cdi"
    CDD = "cdd"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    TEMPORARY = "temporary"


class PaymentPeriod(str, Enum):
    DAILY = "DAILY daily"
    PER_TASK = "per_task"
    MONTHLY = "monthly"


class PayslipStatus(str, Enum):
    CONFIRMED = "confirmed"
    PAID = "paid"
    CANCELED = "canceled"
    REVIEW = "review"
