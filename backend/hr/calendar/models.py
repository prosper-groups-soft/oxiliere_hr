from django.db import models
from django.core.exceptions   import ValidationError
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog
from hr.models.base import BaseAuditableModel

from hr.enums import CountryCode
from .enums   import (
    CalendarEventType,
    CalendarEventRecurrence,
    CalendarEventStatus,
)

from hr.utils.core import get_country_codes
from .utils import generate_event_code


class CalendarEvent(BaseAuditableModel):
    """ Special dates affecting work schedules, payroll, and company operations. """

    name = models.CharField(
        max_length=200, 
        verbose_name=_("Event Name"),
        help_text=_("Common name of the holiday or company event.")
    )
    code = models.CharField(
        max_length=100, 
        unique=True, 
        default=generate_event_code,
        verbose_name=_("Event Code"),
        help_text=_("Unique identifier for scheduling logic.")
    )
    event_type = models.CharField(
        max_length=50, 
        choices=CalendarEventType.choices, 
        default=CalendarEventType.OTHER, 
        verbose_name=_("Event Type"),
        help_text=_("Category of the event (e.g., Public Holiday, Closing).")
    )
    
    country_code = models.CharField(
        max_length=2,
        choices=get_country_codes(),
        default=CountryCode.DRC,
        null=True,
        blank=True,
        verbose_name=_("Country"),
        help_text=_("Determines if the event applies to a specific country or the entire group.")
    )
    
    start_date = models.DateField(
        verbose_name=_("Start Date"),
        help_text=_("First day of the event.")
    )
    end_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("End Date"),
        help_text=_("Leave empty for single-day events.")
    )
    start_time = models.TimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Start Time")
    )
    end_time = models.TimeField(
        null=True, 
        blank=True, 
        verbose_name=_("End Time")
    )
    
    is_workable = models.BooleanField(
        default=False, 
        verbose_name=_("Workable"),
        help_text=_("If disabled, this is considered a non-working day.")
    )
    recurrent = models.CharField(
        max_length=50, 
        choices=CalendarEventRecurrence.choices, 
        default=CalendarEventRecurrence.NONE, 
        verbose_name=_("Recurrence"),
        help_text=_("Frequency for repeating the event (e.g., Yearly).")
    )
    
    description = models.TextField(
        null=True, 
        blank=True, 
        verbose_name=_("Description")
    )
    status = models.CharField(
        max_length=50, 
        choices=CalendarEventStatus.choices, 
        default=CalendarEventStatus.PENDING, 
        verbose_name=_("Status")
    )

    class Meta:
        db_table = "cale_event" 
        verbose_name = _("Calendar Event")
        verbose_name_plural = _("Calendar Events")
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'start_date', 'event_type'],
                condition=models.Q(deleted__isnull=True),
                name='unique_calendar_event'
            ),
        ]
        ordering = ['start_date', 'start_time']

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError(_("End date cannot be before start date."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.end_date:
            return f"{self.name} ({self.start_date} - {self.end_date})"
        return f"{self.name} ({self.start_date})"


# --- Audit log registration ---
auditlog.register(CalendarEvent)

