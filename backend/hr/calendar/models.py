from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from hr.models import BaseAuditableModel

from hr.enums import CountryCode
from .enums import (
    CalendarEventType,
    CalendarEventRecurrence,
    CalendarEventStatus,
)

from hr.utils import get_country_codes
from .utils import generate_event_code


class CalendarEvent(BaseAuditableModel):
    """
    Events affecting the work schedule and payroll.
    Includes Public Holidays and Company Closings.
    """

    name = models.CharField(max_length=200, verbose_name=_("Event Name"))
    code = models.CharField(
        max_length=100, 
        unique=True, 
        default=generate_event_code,
        verbose_name=_("Event Code")
    )
    event_type = models.CharField(
        max_length=50, 
        choices=CalendarEventType.choices, 
        default=CalendarEventType.OTHER, 
        verbose_name=_("Event Type")
    )
    
    # Scope
    country_code = models.CharField(
        max_length=2,
        choices=get_country_codes(),
        default=CountryCode.DRC,
        null=True,
        blank=True,
        verbose_name=_("Country Code"),
        help_text=_("If set, applies only to this country. If empty, applies globally.")
    )
    
    # Timing
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
    start_time = models.TimeField(null=True, blank=True, verbose_name=_("Start Time"))
    end_time = models.TimeField(null=True, blank=True, verbose_name=_("End Time"))
    
    # Impact
    is_workable = models.BooleanField(
        default=False, 
        verbose_name=_("Is Workable"),
        help_text=_("If false, this is a non-working day (e.g., Public Holiday).")
    )
    recurrent = models.CharField(
        max_length=50, 
        choices=CalendarEventRecurrence.choices, 
        default=CalendarEventRecurrence.NONE, 
        verbose_name=_("Recurrence")
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
        unique_together = ('name', 'start_date', 'event_type')
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

