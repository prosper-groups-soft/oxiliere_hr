from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class CalendarEventType(TextChoices):
    PUBLIC_HOLIDAY = "PUBLIC_HOLIDAY", _("Public Holiday") # Holiday
    COMPANY_EVENT = "COMPANY_EVENT", _("Company Event")    # Event
    DEADLINE = "DEADLINE", _("Deadline")                   # Deadline
    ANNIVERSARY = "ANNIVERSARY", _("Anniversary")          # Anniversary
    LEAVE = "LEAVE", _("Leave/Absence")                    # Leave
    OTHER = "OTHER", _("Other")                            # Other


class CalendarEventRecurrence(TextChoices):
    NONE = "NONE", _("None")
    DAILY = "DAILY", _("Daily")
    WEEKLY = "WEEKLY", _("Weekly")
    MONTHLY = "MONTHLY", _("Monthly")
    YEARLY = "YEARLY", _("Yearly")


class CalendarEventStatus(TextChoices):
    PENDING = "PENDING", _("Pending")
    APPROVED = "APPROVED", _("Approved")
    REJECTED = "REJECTED", _("Rejected")
    CANCELLED = "CANCELLED", _("Cancelled")
    TAKEN = "TAKEN", _("Taken / Archived")

