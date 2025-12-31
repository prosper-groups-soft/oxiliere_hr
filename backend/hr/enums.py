from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _



class DegreeEnum(TextChoices):
    BREVET = "brevet", _('brevet')
    DIPLOMA = "diploma", _('diploma')
    LICENSE = "license", _('license')
    MASTER = "master", _('master')
    PHD = "phd", _('phd')
    NOT_SPECIFIED = 'not specified', _('not specified')


class GenderStatus(TextChoices):
    MALE = "male", _('male')
    FEMALE = "female", _('female')
    NOT_SPECIFIED = "not specified", _('not specified')


class MaritalStatus(TextChoices):
    SINGLE = "single", _('single')
    MARRIED = "married", _('married')
    DIVORCED = "divorced", _('divorced')
    WIDOW = "widow", _('widow')


class EmployeeStatus(TextChoices):
    PERMANENT_WORKER = "pw", _('permanent worker')
    COLLABORATOR = "col", _('collaborator')
    CONSULTANT = "con", _('consultant')
    INTERNSHIP = "int", _('internship')
    FREELANCE = "fre", _('freelance')
    TEMPORARY = "tmp", _('temporary')


class RelationshipType(TextChoices):
    PARENT = "parent", _('parent')
    CHILD = "child", _('child')
    SIBLING = "sibling", _('sibling')
    FRIEND = "friend", _('friend')
    SPOUSE = "spouse", _('spouse')
    OTHER = "other", _('other')


class AttendanceStatus(TextChoices):
    PRESENT = "present", _('present')
    ABSENT = "absent", _('absent')
    LATE = "late", _('late')
    EXCUSED = "excused", _('excused')
    HOLIDAY = "holiday", _('holiday')


class UpdateAttendanceStatus(TextChoices):
    PRESENT = "present", _('present')
    ABSENT = "absent", _('absent')
    EXCUSED = "excused", _('excused')


class CalendarEventType(TextChoices):
    HOLIDAY = "holiday", _('holiday')
    MEETING = "meeting", _('meeting')
    TRAINING = "training", _('training')
    BIRTHDAY = "birthday", _('birthday')
    DEADLINE = "deadline", _('deadline')
    OTHER = "other", _('other')


class PaymentType(TextChoices):
    FIXED = "fixed", _('fixed')
    HOURLY = "hourly", _('hourly')


class ContractType(TextChoices):
    CDI = "cdi", _('cdi')
    CDD = "cdd", _('cdd')
    INTERNSHIP = "internship", _('internship')
    FREELANCE = "freelance", _('freelance')
    TEMPORARY = "temporary", _('temporary')


class PaymentPeriod(TextChoices):
    DAILY = "daily", _('daily')
    PER_TASK = "per_task", _('per task')
    MONTHLY = "monthly", _('monthly')


class PayslipStatus(TextChoices):
    CONFIRMED = "confirmed", _('confirmed')
    PAID = "paid", _('paid')
    CANCELED = "canceled", _('canceled')
    REVIEW = "review", _('review')
