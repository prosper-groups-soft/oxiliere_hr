import uuid
import uuid6
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog

from hr.models import BaseAuditableModel
from hr.jobs.models import Position, Department
from .enums import ApplicationStatus, InterviewType
from hr.utils import normalize_names


class JobOffer(BaseAuditableModel):
    """
    Represents a job offer published by the company.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # Relationships with the Jobs module
    target_position = models.ForeignKey(
        Position, 
        on_delete=models.PROTECT, 
        related_name='job_offers',
        help_text=_("The position template on which this offer is based.")
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='job_offers'
    )
    
    # Offer content
    description = models.TextField()
    requirements = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, default="Remote")
    
    # Publication management
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Internal tracking
    recruiter = models.ForeignKey(
        "hr_employees.Employee", 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="managed_offers"
    )
    
    # --- LIMITS AND QUOTAS ---
    slots = models.PositiveIntegerField(
        default=1, 
        help_text=_("Number of open positions available for this job offer.")
    )
    max_applications = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text=_("Maximum number of applications accepted (optional).")
    )

    class Meta:
        db_table = "recr_job_offer"
        ordering = ["-created_at"]
        verbose_name = _("Job Offer")
        verbose_name_plural = _("Job Offers")

    def clean(self):
        if self.title:
            self.title = self.title.strip().title()
            
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        
        # Logical validation of dates
        if self.end_date and self.published_at:
            if self.end_date < self.published_at.date():
                from django.core.exceptions import ValidationError
                raise ValidationError(_("End date cannot be earlier than the publication date."))


    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            self.slug = slugify(f"{self.title}-{str(uuid6.uuid7())[:8]}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.department.name})"


class Candidate(BaseAuditableModel):
    """
    Represents a profile in the talent pool.
    """
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    
    class Meta:
        db_table = "recr_candidate"
        verbose_name = _("Candidate")
        verbose_name_plural = _("Candidates")
    
    def clean(self):
        super().clean()
        self.__dict__.update(normalize_names(
            first_name=self.first_name,
            middle_name=self.middle_name,
            last_name=self.last_name
        ))
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Application(BaseAuditableModel):
    """
    Intersection model: Application of a candidate to a specific job offer.
    """

    job_offer = models.ForeignKey(
        JobOffer, 
        on_delete=models.CASCADE, 
        related_name='applications'
    )
    candidate = models.ForeignKey(
        Candidate, 
        on_delete=models.CASCADE, 
        related_name='applications'
    )
    
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    cover_letter = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='recruitment/resumes/%Y/%m/')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recr_application"
        ordering = ["-applied_at"]
        unique_together = ('job_offer', 'candidate')
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")

    def __str__(self):
        return f"{self.candidate} -> {self.job_offer.title}"


class Interview(BaseAuditableModel):
    """
    Tracking of direct interactions (interviews).
    """
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='interviews'
    )
    interviewer = models.ForeignKey(
        "hr_employees.Employee", 
        on_delete=models.CASCADE, 
        related_name='interviews_to_conduct'
    )
    interview_type = models.CharField(
        max_length=20, 
        choices=InterviewType.choices, 
        default=InterviewType.VIDEO
    )
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    
    # Assessment
    notes = models.TextField(blank=True, null=True, help_text=_("Internal notes and impressions."))
    score = models.IntegerField(
        null=True, 
        blank=True, 
        help_text=_("Overall score from 1 to 5")
    )
    
    class Meta:
        db_table = "recr_interview"
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"{self.get_interview_type_display()} - {self.application.candidate}"


# --- AUDIT LOG REGISTRATION ---

auditlog.register(JobOffer)
auditlog.register(Candidate)
auditlog.register(Application)
auditlog.register(Interview)

