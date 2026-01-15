from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from hr.models import BaseAuditableModel
from hr.enums import (
    CalendarEventType, 
    CalendarEventRecurrence, 
    CalendarEventStatus
)


class CalendarEvent(BaseAuditableModel):
    """
    Events affecting the work schedule and payroll.
    """
    name = models.CharField(max_length=200, verbose_name=_("Event Name"))
    code = models.CharField(max_length=100, unique=True, verbose_name=_("Event Code"))
    event_type = models.CharField(
        max_length=50, 
        choices=CalendarEventType.choices, 
        default=CalendarEventType.OTHER, 
        verbose_name=_("Event Type")
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
        if not self.code and self.name:
            import uuid
            self.code = f"EVT-{uuid.uuid4().hex[:8].upper()}"
            
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError(_("End date cannot be before start date."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.end_date:
            return f"{self.name} ({self.start_date} - {self.end_date})"
        return f"{self.name} ({self.start_date})"


class CalendarSettings(BaseAuditableModel):
    """
    Global calendar and work-week configuration.
    """
    show_anniversaries = models.BooleanField(default=True)
    show_deadlines = models.BooleanField(default=True)
    
    # Critical for payroll calculations
    work_days_per_week = models.PositiveSmallIntegerField(
        default=6, 
        verbose_name=_("Standard Work Days/Week")
    )

    class Meta:
        db_table = "cale_setting"  # Table name with 4-char prefix
        verbose_name = _("Calendar Settings")

    def save(self, *args, **kwargs):
        # Singleton pattern
        if not self.pk and CalendarSettings.objects.exists():
            raise ValidationError(_("Only one settings instance is allowed."))
        super().save(*args, **kwargs)

