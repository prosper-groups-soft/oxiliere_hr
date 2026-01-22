from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class TimeSheetStatus(TextChoices):
    PRESENT = "PRESENT", _("Present")
    ABSENT = "ABSENT", _("Absent")
    LATE = "LATE", _("Late")
    PARTIAL = "PARTIAL", _("Partial Absence") # New: present but did not complete required hours
    EXCUSED = "EXCUSED", _("Excused")
    ON_LEAVE = "ON_LEAVE", _("On Leave")
    HOLIDAY = "HOLIDAY", _("Public Holiday")


class PunchType(TextChoices):
    WORK = "WORK", _("Work")
    BREAK = "BREAK", _("Break")
    MISSION = "MISSION", _("External Mission")  # E.g., client meeting
    PERSONAL = "PERSONAL", _("Personal Leave")  # For "Personal Reason"

