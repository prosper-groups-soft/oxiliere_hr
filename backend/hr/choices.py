from django.db import models


class DegreeChoices(models.TextChoices):
    BREVET = "brevet", "Brevet"
    DIPLOMA = "diploma", "Diploma"
    LICENSE = "license", "License"
    MASTER = "master", "Master"
    PHD = "phd", "PhD"
    NOT_SPECIFIED = "not specified", "Not Specified"


class GenderChoices(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    NOT_SPECIFIED = "not specified", "Not Specified"


class MaritalStatusChoices(models.TextChoices):
    SINGLE = "single", "Single"
    MARRIED = "married", "Married"
    DIVORCED = "divorced", "Divorced"
    WIDOW = "widow", "Widow"


class EmployeeStatusChoices(models.TextChoices):
    PERMANENT_WORKER = "permanent worker", "Permanent Worker"
    LABOR_TECHNICIAN = "labor technician", "Labor Technician"
    LABOR_WORKER = "labor worker", "Labor Worker"


class RelationshipTypeChoices(models.TextChoices):
    PARENT = "parent", "Parent"
    CHILD = "child", "Child"
    SIBLING = "sibling", "Sibling"
    FRIEND = "friend", "Friend"
    SPOUSE = "spouse", "Spouse"
    OTHER = "other", "Other"


class AttendanceStatusChoices(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"
    EXCUSED = "excused", "Excused"
    HOLIDAY = "holiday", "Holiday"


class UpdateAttendanceStatusChoices(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    EXCUSED = "excused", "Excused"


class CalendarEventTypeChoices(models.TextChoices):
    HOLIDAY = "holiday", "Holiday"
    MEETING = "meeting", "Meeting"
    TRAINING = "training", "Training"
    BIRTHDAY = "birthday", "Birthday"
    DEADLINE = "deadline", "Deadline"
    OTHER = "other", "Other"


class PaymentTypeChoices(models.TextChoices):
    FIXED = "fixed", "Fixed"
    HOURLY = "hourly", "Hourly"


class ContractTypeChoices(models.TextChoices):
    CDI = "cdi", "CDI"
    CDD = "cdd", "CDD"
    INTERNSHIP = "internship", "Internship"
    FREELANCE = "freelance", "Freelance"
    TEMPORARY = "temporary", "Temporary"


class PaymentPeriodChoices(models.TextChoices):
    DAILY = "daily", "Daily"
    PER_TASK = "per_task", "Per Task"
    MONTHLY = "monthly", "Monthly"


class PayslipStatusChoices(models.TextChoices):
    CONFIRMED = "confirmed", "Confirmed"
    PAID = "paid", "Paid"
    CANCELED = "canceled", "Canceled"
    REVIEW = "review", "Review"

