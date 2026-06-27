import uuid6
from django.db    import models
from django.utils import timezone
from auditlog.registry import auditlog
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from hr.models.base import BaseAuditableModel
from hr.jobs.models import Position, Vacancy
from .enums         import (
    ApplicationStatus,
    CandidatePriority,
    CandidateSource,
    InterviewType,
    InterviewStatus,
    JobOfferStatus,
)
from hr.enums import GenderStatus
from hr.utils.core  import normalize_names

    
class JobOffer(BaseAuditableModel):
    """
    Represents a job offer published by the company.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # Relationships with the Jobs module
    target_positions = models.ManyToManyField(
        Position,
        related_name='job_offers',
        help_text=_("The position templates on which this offer is based.")
    )
    vacancies = models.ManyToManyField(
        Vacancy,
        related_name='job_offers',
        blank=True,
        help_text=_("The vacancies this job offer is addressing.")
    )

    # Offer content
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=255, default="Remote")

    # Status
    status = models.CharField(
        max_length=20,
        choices=JobOfferStatus.choices,
        default=JobOfferStatus.DRAFT
    )

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
    position_slots = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Mapping of position_id -> number of slots for each position.")
    )
    max_applications = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text=_("Maximum number of applications accepted (optional).")
    )
    evaluation_template = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Evaluation criteria per position: {position_id: [{source, name, weight}, ...]}.")
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
        return f"{self.title}"

    @property
    def total_candidates(self):
        """Total number of applications for this job offer."""
        return self.applications.count()

    @property
    def in_pipeline(self):
        """Number of applications in active pipeline (not rejected/withdrawn)."""
        from .enums import ApplicationStatus
        return self.applications.exclude(
            status__in=[ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN]
        ).count()

    @property
    def interviews_count(self):
        """Number of interviews scheduled for applications of this job offer."""
        from django.db.models import Count
        return Interview.objects.filter(
            application__job_offer=self
        ).count()

    @property
    def offers_sent(self):
        """Number of accepted applications (actual hires)."""
        from .enums import ApplicationStatus
        return self.applications.filter(
            status=ApplicationStatus.ACCEPTED
        ).count()

    @property
    def offers_made(self):
        """Number of applications that received an offer (OFFER status)."""
        from .enums import ApplicationStatus
        return self.applications.filter(
            status=ApplicationStatus.OFFER
        ).count()


class Candidate(BaseAuditableModel):
    """
    Represents a profile in the talent pool.
    """
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, default="")
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    profile_photo = models.ImageField(
        upload_to='candidate_photos/%Y/%m/',
        null=True,
        blank=True,
        help_text=_("Candidate profile photo")
    )
    resume = models.FileField(
        upload_to='candidate_resumes/%Y/%m/',
        blank=True,
        null=True,
        help_text=_("Candidate resume/CV")
    )
    gender = models.CharField(
        max_length=15,
        choices=GenderStatus.choices,
        default=GenderStatus.NOT_SPECIFIED,
        blank=True,
        help_text=_("Candidate gender identity")
    )
    source = models.CharField(
        max_length=20,
        choices=CandidateSource.choices,
        default=CandidateSource.DIRECT
    )
    priority = models.CharField(
        max_length=10,
        choices=CandidatePriority.choices,
        default=CandidatePriority.MEDIUM
    )
    location = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    experience = models.CharField(max_length=255, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)
    technical_score = models.PositiveSmallIntegerField(blank=True, null=True)
    experience_score = models.PositiveSmallIntegerField(blank=True, null=True)
    communication_score = models.PositiveSmallIntegerField(blank=True, null=True)
    culture_score = models.PositiveSmallIntegerField(blank=True, null=True)
    
    class Meta:
        db_table = "recr_candidate"
        verbose_name = _("Candidate")
        verbose_name_plural = _("Candidates")
    
    def clean(self):
        super().clean()
        normalized_names = normalize_names(
            first_name=self.first_name,
            middle_name=self.middle_name,
            last_name=self.last_name
        )
        self.first_name = normalized_names.get("first_name", self.first_name)
        self.middle_name = normalized_names.get("middle_name", self.middle_name)
        self.last_name = normalized_names.get("last_name", self.last_name)
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Application(BaseAuditableModel):
    """
    Intersection model: Application of a candidate to a specific job offer.
    A candidate may apply to multiple positions within the same job offer.
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
    target_position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications',
        help_text=_("The specific position within the offer this application targets.")
    )

    priority = models.CharField(
        max_length=10,
        choices=CandidatePriority.choices,
        default=CandidatePriority.MEDIUM,
    )

    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    scores = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Evaluation scores: {criterion_name: score_value}.")
    )
    evaluation_notes = models.TextField(blank=True, null=True)

    # --- OFFER DETAILS ---
    salary_min = models.PositiveIntegerField(null=True, blank=True, help_text=_("Minimum salary for the offer."))
    salary_max = models.PositiveIntegerField(null=True, blank=True, help_text=_("Maximum salary for the offer."))
    salary_currency = models.CharField(max_length=3, default='USD', help_text=_("Currency code (USD, EUR, CDF, etc.)"))
    offer_start_date = models.DateField(null=True, blank=True, help_text=_("Expected start date for the offer."))

    class Meta:
        db_table = "recr_application"
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(
                fields=['job_offer', 'candidate', 'target_position'],
                condition=models.Q(target_position__isnull=False, deleted__isnull=True),
                name='unique_active_application_per_position'
            ),
            models.UniqueConstraint(
                fields=['job_offer', 'candidate'],
                condition=models.Q(target_position__isnull=True, deleted__isnull=True),
                name='unique_active_application_no_position'
            ),
        ]
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
    location = models.CharField(max_length=255, blank=True, null=True, help_text=_("Physical location or meeting room."))
    video_link = models.URLField(blank=True, null=True, help_text=_("Link to the video conference."))
    notes = models.TextField(
        blank=True, null=True,
        help_text=_("Internal notes about the interview (preparation, context)")
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=InterviewStatus.choices,
        default=InterviewStatus.SCHEDULED,
        help_text=_("Current status of the interview.")
    )
    
    # Assessment
    feedback = models.TextField(
        blank=True, null=True,
        help_text=_("Qualitative feedback and appreciation")
    )
    strengths = models.JSONField(
        default=list, blank=True,
        help_text=_("Points forts détectés")
    )
    weaknesses = models.JSONField(
        default=list, blank=True,
        help_text=_("Axes d'amélioration")
    )
    would_hire = models.BooleanField(
        null=True, blank=True,
        help_text=_("Recommandation d'embauche")
    )
    next_steps = models.TextField(
        blank=True, null=True,
        help_text=_("Prochaines étapes conseillées")
    )
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


# --- Audit log registration ---
auditlog.register(JobOffer)
auditlog.register(Candidate)
auditlog.register(Application)
auditlog.register(Interview)

