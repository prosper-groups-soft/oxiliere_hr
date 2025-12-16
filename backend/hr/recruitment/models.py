from django.db import models
from django.utils.text import slugify
import uuid
from utils_mixins.models import BaseModelMixin
from django.utils.translation import gettext_lazy as _


class JobOffer(BaseModelMixin):
    title = models.CharField(
        max_length=255
    )
    slug = models.SlugField(
        max_length=255, 
        unique=True, 
        blank=True
    )
    company = models.CharField(
        max_length=255
    )
    location = models.CharField(
        max_length=255
    )
    category = models.ForeignKey(
        "hr.jobs.models.JobCategory", 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='jobs'
    )
    description = models.TextField()
    requirements = models.TextField()
    salary_range = models.CharField(
        max_length=100, 
        blank=True, 
        null=True
    )
    posted_by = models.CharField(
        max_length=255
    )
    is_published = models.BooleanField(
        default=False
    )
    published_at = models.DateTimeField(
        null=True, 
        blank=True
    )
    end_date = models.DateField(
        null=True, 
        blank=True
    )
    is_active = models.BooleanField(
        default=True
    )
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"

    
    def clean(self):
        # Formatage des champs textuels pour standardiser la casse
        if self.title:
            self.title = self.title.strip().title()
        if self.company:
            self.company = self.company.strip().title()
        if self.location:
            self.location = self.location.strip().title()
        if self.posted_by:
            self.posted_by = self.posted_by.strip().title()

    
    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            # Générer un slug à partir du titre avec une valeur aléatoire
            random_string = str(uuid.uuid4()).split('-')[0]  # Prendre la première partie de l'UUID
            self.slug = slugify(f"{self.title}-{random_string}")
        super().save(*args, **kwargs)
        

    def __str__(self):
        return self.title


class Application(BaseModelMixin):
    PENDING = 'pending'
    REVIEW = 'review'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (REVIEW, 'Review'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected')
    ]
    job_offer = models.ForeignKey(
        JobOffer, 
        on_delete=models.CASCADE, 
        related_name='applications'
    )
    applicant_name = models.CharField(
        max_length=255
    )
    applicant_email = models.EmailField()
    applicant_phone = models.CharField(
        max_length=20
    )
    cover_letter = models.TextField()
    resume = models.FileField(
        upload_to='resumes/'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-applied_at"]
        unique_together = ('job_offer', 'applicant_email')
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"

    def clean(self):
        # Formatage des champs textuels pour standardiser la casse
        if self.applicant_name:
            self.applicant_name = self.applicant_name.strip().title()
        if self.applicant_email:
            self.applicant_email = self.applicant_email.strip().lower()
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.applicant_name} - {self.job_offer.title}"
