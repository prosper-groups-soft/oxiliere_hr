from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class TimeSheetStatus(TextChoices):
    PRESENT = "PRESENT", _("Present")
    ABSENT = "ABSENT", _("Absent")
    LATE = "LATE", _("Late")
    PARTIAL = "PARTIAL", _("Partial Absence")
    EXCUSED = "EXCUSED", _("Excused")
    ON_LEAVE = "ON_LEAVE", _("On Leave")
    HOLIDAY = "HOLIDAY", _("Public Holiday")


class PunchType(TextChoices):
    WORK = "WORK", _("Work")
    BREAK = "BREAK", _("Break")
    MISSION = "MISSION", _("External Mission")
    PERSONAL = "PERSONAL", _("Personal Leave")


class RecurrenceType(TextChoices):
    NONE = "NONE", _("None")
    WEEKLY = "WEEKLY", _("Weekly")
    BIWEEKLY = "BIWEEKLY", _("Biweekly")
    MONTHLY = "MONTHLY", _("Monthly")
    QUARTERLY = "QUARTERLY", _("Quarterly")
