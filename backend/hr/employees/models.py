from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from auditlog.registry import auditlog

from hr.models import BaseAuditableModel, AddressMixin
from hr.enums import (
    GenderStatus, 
    CountryCode,
)

from .enums import (
    AcademicLevel,
    MaritalStatus,
    RelationshipType,
    EmployeeStatus,
    DocumentType,
)
from hr.utils.core import get_country_codes, normalize_names


class WorkSite(BaseAuditableModel):
    """ Physical work location for employees. """
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    allowed_radius = models.PositiveIntegerField(default=100)

    class Meta:
        db_table = "empl_work_site"
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class Employee(BaseAuditableModel):
    """ Main employee profile for identifying workforce. """
    work_site = models.ForeignKey(
        WorkSite, on_delete=models.SET_NULL, null=True,
        help_text=_("Primary work location."),
        related_name="employees"
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
        help_text=_("Associated system user account.")
    )

    # Identifiers
    matricule = models.CharField(
        max_length=16,
        unique=True,
        help_text=_("Unique staff ID.")
    )
    first_name = models.CharField(max_length=75)
    middle_name = models.CharField(max_length=75, blank=True, null=True)
    last_name = models.CharField(max_length=75)
    
    # Personal details
    gender = models.CharField(
        choices=GenderStatus.choices,
        default=GenderStatus.NOT_SPECIFIED,
        max_length=20
    )
    birthdate = models.DateField(
        null=True, 
        blank=True,
        help_text=_("Date of birth for age and legal checks.")
    )
    nationality = models.CharField(
        max_length=2,
        choices=get_country_codes(),
        default=CountryCode.DRC,
        null=True,
        blank=True,
        help_text=_("ISO country code.")
    )
    marital_status = models.CharField(
        choices=MaritalStatus.choices,
        default=MaritalStatus.SINGLE,
        max_length=20,
        help_text=_("Marital status for benefits calculation.")
    )

    # Contact
    email = models.EmailField(
        unique=True, 
        null=True, 
        blank=True,
        help_text=_("Professional email address.")
    )
    phone = models.CharField(
        max_length=15, 
        null=True, 
        blank=True,
        help_text=_("Contact phone number.")
    )

    # Career lifecycle
    hire_date = models.DateField(
        default=timezone.now,
        help_text=_("Official hiring date.")
    )
    termination_date = models.DateField(
        null=True, 
        blank=True, 
        help_text=_("Last day of employment.")
    )
    
    # System flags
    is_active = models.BooleanField(
        default=True,
        help_text=_("Global active state in the system.")
    )
    can_connect = models.BooleanField(
        default=True,
        help_text=_("Allows access to the employee portal.")
    )
    description = models.TextField(
        null=True, 
        blank=True,
        help_text=_("Additional HR notes.")
    )

    class Meta:
        db_table = "empl_employee"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['matricule']),
            models.Index(fields=['email']),
            models.Index(fields=['last_name', 'first_name']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.matricule})"

    def clean(self):
        super().clean()
        self.__dict__.update(normalize_names(
            first_name=self.first_name,
            middle_name=self.middle_name,
            last_name=self.last_name
        ))

        if self.termination_date and self.hire_date:
            if self.termination_date < self.hire_date:
                raise ValidationError({
                    "termination_date": _("Termination date cannot be earlier than hire date.")
                })
                
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def current_address(self):
        if hasattr(self, 'prefetched_current_address'):
            return self.prefetched_current_address[0] if self.prefetched_current_address else None
        return self.addresses.filter(is_current=True).first()

    @property
    def all_addresses(self):
        if hasattr(self, 'prefetched_all_addresses'):
            return self.prefetched_all_addresses
        return self.addresses.all()

    @property
    def current_status(self):
        if hasattr(self, 'prefetched_current_status'):
            return self.prefetched_current_status[0] if self.prefetched_current_status else None
        return self.status_history.order_by('-created_at').first()

    @property
    def all_status_history(self):
        if hasattr(self, 'prefetched_all_status_history'):
            return self.prefetched_all_status_history
        return self.status_history.all()


class StatusHistory(BaseAuditableModel):
    """ History of employment status changes. """
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="status_history"
    )
    status = models.CharField(
        choices=EmployeeStatus.choices,
        max_length=30,
        help_text=_("Professional status (Active, Suspended, etc.).")
    )
    start_date = models.DateField(help_text=_("Effective date for this status."))
    end_date = models.DateField(
        null=True, 
        blank=True, 
        help_text=_("End date for temporary statuses.")
    )
    reason = models.TextField(
        null=True, 
        blank=True, 
        help_text=_("Context for the status change.")
    )

    class Meta:
        db_table = "empl_status_history"
        ordering = ['-start_date']
        verbose_name_plural = "Status Histories"


class EmployeeDocument(BaseAuditableModel):
    """ Repository for legal and professional documents. """
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="documents"
    )
    document_type = models.CharField(
        choices=DocumentType.choices, 
        default=DocumentType.OTHER,
        max_length=50
    )
    document_number = models.CharField(
        max_length=50, 
        blank=True, 
        help_text=_("Identification or reference number.")
    )
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(
        null=True, 
        blank=True, 
        help_text=_("Validity end date.")
    )
    file = models.FileField(
        upload_to="employee_docs/%Y/%m/",
        help_text=_("Digital scan of the document.")
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Confirms digital copy matches the original.")
    )
    issuing_authority = models.CharField(
        max_length=150, 
        blank=True, 
        null=True,
        help_text=_("Entity that issued the document.")
    )

    class Meta:
        db_table = "empl_employee_document"
        indexes = [
            models.Index(fields=['document_type', 'expiry_date']),
            models.Index(fields=['employee', 'document_type']),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.employee.last_name}"


class EmployeeAddress(AddressMixin):
    """ Employee residential and work addresses. """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE, 
        related_name="addresses"
    )
    is_current = models.BooleanField(
        default=True,
        help_text=_("Set as the primary mailing address.")
    )
    move_in_date = models.DateField(null=True, blank=True)
    move_out_date = models.DateField(
        null=True, 
        blank=True,
        help_text=_("Date of departure from this address.")
    )
    
    class Meta:
        db_table = "empl_employee_address"
        indexes = [
            models.Index(fields=["employee", "is_current"]),
        ]
        
    def clean(self):
        super().clean()
        if self.move_in_date and self.move_out_date:
            if self.move_out_date < self.move_in_date:
                raise ValidationError(_("Move out date cannot be before move in date."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class EmergencyContact(BaseAuditableModel):
    """ Contacts to notify in case of an incident. """
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="emergency_contacts"
    )
    first_name = models.CharField(max_length=75, null=True, blank=True)
    middle_name = models.CharField(max_length=75, null=True, blank=True)
    last_name = models.CharField(max_length=75, null=True, blank=True)
    phone = models.CharField(
        max_length=15,
        help_text=_("Direct phone line for emergencies.")
    )
    relation = models.CharField(
        choices=RelationshipType.choices, 
        default=RelationshipType.OTHER,
        max_length=20
    )
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text=_("Call order (1 is primary).")
    )

    class Meta:
        db_table = "empl_emergency_contact"
        ordering = ["priority", "last_name"]
        constraints = [
            models.UniqueConstraint(fields=['employee', 'priority'], name='unique_priority_per_employee')
        ]

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
        

class EmployeeChild(BaseAuditableModel):
    """ Information on children for family benefits. """
    parent = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="children"
    )
    first_name = models.CharField(max_length=75, null=True, blank=True)
    middle_name = models.CharField(max_length=75, null=True, blank=True)
    last_name = models.CharField(max_length=75, null=True, blank=True)
    gender = models.CharField(
        choices=GenderStatus.choices, 
        default=GenderStatus.NOT_SPECIFIED,
        max_length=20
    )
    birthdate = models.DateField()
    is_dependent = models.BooleanField(
        default=True,
        help_text=_("Legal dependent status for benefits.")
    )

    class Meta:
        db_table = "empl_employee_child"
        ordering = ["first_name", "-birthdate"]
        verbose_name_plural = "Children"

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
        

class EmployeeEducation(BaseAuditableModel):
    """ Academic and professional training background. """
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="educations"
    )
    institute = models.CharField(
        max_length=255,
        help_text=_("University or training center name.")
    )
    degree = models.CharField(
        choices=AcademicLevel.choices,
        default=AcademicLevel.NOT_SPECIFIED,
        max_length=50
    )
    major = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text=_("Field of study.")
    )
    start_year = models.PositiveSmallIntegerField(help_text=_("Year of start."))
    end_year = models.PositiveSmallIntegerField(help_text=_("Year of completion."))
    location = models.CharField(
        max_length=255,
        help_text=_("Institute city and country.")
    )

    class Meta:
        db_table = "empl_employee_education"
        ordering = ["-end_year", "degree"]
        unique_together = ("employee", "degree", "institute")

    def clean(self):
        super().clean()
        self.institute = self.institute.strip().upper()
        self.major = self.major.strip().title()
        self.location = self.location.strip()

        if self.start_year and self.end_year and self.start_year > self.end_year:
            raise ValidationError({"end_year": _("End year must be after start year.")})
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)        


# --- Audit log registration ---
auditlog.register(Employee)
auditlog.register(StatusHistory)
auditlog.register(EmployeeDocument)
auditlog.register(EmployeeAddress)
auditlog.register(EmergencyContact)
auditlog.register(EmployeeChild)
auditlog.register(EmployeeEducation)

