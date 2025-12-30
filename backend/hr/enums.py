from enum import Enum
from utils_mixins.mixins_cls import EnumValuesMixin


class DegreeEnum(str, EnumValuesMixin, Enum):
    BREVET = "brevet"
    DIPLOMA = "diploma"
    LICENSE = "license"
    MASTER = "master"
    PHD = "phd"
    NOT_SPECIFIED = 'not specified'


class GenderStatus(str, EnumValuesMixin, Enum):
    MALE = "male"
    FEMALE = "female"
    NOT_SPECIFIED = "not specified"


class MaritalStatus(str, EnumValuesMixin, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOW = "widow"


class EmployeeStatus(str, EnumValuesMixin, Enum):
    PERMANENT_WORKER = "permanent worker"
    LABOR_TECHNICIAN = "labor technician"
    LABOR_WORKER = "labor worker"


class RelationshipType(str, EnumValuesMixin, Enum):
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    FRIEND = "friend"
    SPOUSE = "spouse"
    OTHER = "other"


class AttendanceStatus(str, EnumValuesMixin, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    HOLIDAY = "holiday"


class UpdateAttendanceStatus(str, EnumValuesMixin, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"


class CalendarEventType(str, EnumValuesMixin, Enum):
    HOLIDAY = "holiday"
    MEETING = "meeting"
    TRAINING = "training"
    BIRTHDAY = "birthday"
    DEADLINE = "deadline"
    OTHER = "other"


class PaymentType(str, EnumValuesMixin, Enum):
    FIXED = "fixed"
    HOURLY = "hourly"


class ContractType(str, EnumValuesMixin, Enum):
    CDI = "cdi"
    CDD = "cdd"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    TEMPORARY = "temporary"


class PaymentPeriod(str, EnumValuesMixin, Enum):
    DAILY = "DAILY daily"
    PER_TASK = "per_task"
    MONTHLY = "monthly"


class PayslipStatus(str, EnumValuesMixin, Enum):
    CONFIRMED = "confirmed"
    PAID = "paid"
    CANCELED = "canceled"
    REVIEW = "review"
