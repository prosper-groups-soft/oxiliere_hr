from django.utils.translation import gettext_lazy as _
from django.db import models
from django.apps import apps
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from auditlog.registry import auditlog
from django.db.models import Q, UniqueConstraint

from hr.models.base import BaseAuditableModel
from .enums import PositionLevel, OrgUnitType, TransitionType


class JobFamily(BaseAuditableModel):
    """ High-level functional career category (e.g., Engineering, HR, Finance). """
    name = models.CharField(
        max_length=255, 
        verbose_name=_("Family Name")
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Description")
    )

    class Meta:
        db_table = "jobs_job_family"
        ordering = ["name"]
        verbose_name = _("Job Family")
        verbose_name_plural = _("Job Families")

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def __str__(self):
        return self.name


class Position(BaseAuditableModel):
    """ 
    Specific role within a Job Family. Seniority levels are now linked via PositionSeniority.
    This allows employees to progress through levels within the same position.
    """
    job_family = models.ForeignKey(
        JobFamily, 
        on_delete=models.CASCADE, 
        related_name="positions",
        help_text="The job family this position belongs to."
    )
    org_unit = models.ForeignKey(
        'OrgUnit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions",
        verbose_name=_("Organizational Unit"),
        help_text="The org unit this position is attached to."
    )
    name = models.CharField(
        max_length=100,
        help_text="Title of the position (e.g., Software Engineer, Recruiter)."
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Job Description")
    )
    requirements = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Requirements"),
        help_text="List of specific requirements for this position"
    )
    skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Key Skills"),
        help_text="List of key skills with levels, e.g. [{'name': 'React', 'level': 3}]"
    )

    class Meta:
        db_table = "jobs_position"
        ordering = ["job_family__name", "name"]
        constraints = [
            UniqueConstraint(
                fields=['job_family', 'name'],
                condition=Q(deleted__isnull=True),
                name='unique_active_position'
            ),
        ]
        verbose_name = _("Position")

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def __str__(self):
        return self.name


class ProfessionalCategory(BaseAuditableModel):
    """
    Grille des catégories professionnelles (catalogue.md §6).

    7 classes x 4 échelons définies par le Décret n° 25/22 :
    - Classe 1 : Manœuvre ordinaire → Classe 7 : Cadre supérieur
    - Principe de tension salariale 1:10 : le salaire max de la grille
      (Classe 7, Échelon 4) = SMIG mensuel x 10.

    Source de vérité des classes/échelons — `SeniorityLevel` et
    `PositionSeniority` y référencent via FK (migration depuis hr_payroll).
    """
    classe = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name=_("Classe"),
        help_text=_("Classe professionnelle RDC (1-7).")
    )
    echelon = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name=_("Échelon"),
        help_text=_("Échelon dans la classe (1-4).")
    )
    label = models.CharField(
        max_length=120,
        verbose_name=_("Libellé"),
        help_text=_("Libellé de la classe (ex. Manœuvre ordinaire, Cadre moyen).")
    )
    application = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Application"),
        help_text=_("Profil de personnel concerné (ex. Personnel non qualifié).")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("La classe/échelon est applicable pour les nouveaux contrats.")
    )

    class Meta:
        db_table = "jobs_professional_category"
        verbose_name = _("Catégorie professionnelle")
        verbose_name_plural = _("Catégories professionnelles")
        ordering = ['classe', 'echelon']
        constraints = [
            UniqueConstraint(
                fields=['classe', 'echelon'],
                condition=Q(deleted__isnull=True),
                name='unique_jobs_professional_category_class_echelon'
            )
        ]

    def __str__(self):
        return f"Classe {self.classe} — Échelon {self.echelon} ({self.label})"


class SeniorityLevel(BaseAuditableModel):
    """ 
    Dynamic definition of seniority levels with requirements.
    Allows customization of the 9 standard levels per organization.
    """
    level = models.CharField(
        max_length=20,
        choices=PositionLevel,
        unique=True,
        verbose_name=_("Position Level")
    )
    rank = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_("Hierarchy Rank"),
        help_text="Numeric rank for ordering (1=lowest, 9=highest)"
    )
    label = models.CharField(
        max_length=100,
        verbose_name=_("Display Label")
    )
    requirements = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Requirements"),
        help_text="List of requirements/prerequisites for this level"
    )
    # Classe professionnelle RDC (catalogue.md §6 : 7 classes, 1 = Manœuvre, 7 = Cadre supérieur)
    # FK vers la grille des catégories professionnelles (ligne échelon=1 = classe de base).
    professional_category = models.ForeignKey(
        ProfessionalCategory,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="seniority_levels",
        verbose_name=_("Catégorie professionnelle"),
        help_text=_("Classe RDC (1-7) de la grille des catégories professionnelles.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    class Meta:
        db_table = "jobs_seniority_level"
        ordering = ["rank"]
        verbose_name = _("Seniority Level Definition")
        verbose_name_plural = _("Seniority Level Definitions")

    @property
    def classe(self) -> int | None:
        """ Classe (1-7) dérivée de la grille — rétro-compat API. """
        return self.professional_category.classe if self.professional_category else None

    def __str__(self):
        return f"{self.label} ({self.level})"


class PositionSeniority(BaseAuditableModel):
    """
    Links a Position to available SeniorityLevels with specific salary ranges.
    Allows progression through levels within the same position.
    """
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name="seniority_levels",
        verbose_name=_("Position")
    )
    seniority_level = models.ForeignKey(
        SeniorityLevel,
        on_delete=models.PROTECT,
        verbose_name=_("Seniority Level")
    )
    salary_min = models.PositiveIntegerField(
        verbose_name=_("Minimum Salary for this level")
    )
    salary_max = models.PositiveIntegerField(
        verbose_name=_("Maximum Salary for this level")
    )
    # Échelon dans la grille (1-4) — progression intra-classe (catalogue.md §6)
    echelon = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name=_("Échelon"),
        help_text=_("Échelon (1-4) de la grille des catégories professionnelles.")
    )
    # Ligne exacte (classe, échelon) de la grille des catégories professionnelles
    professional_category = models.ForeignKey(
        ProfessionalCategory,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="position_seniorities",
        verbose_name=_("Catégorie professionnelle"),
        help_text=_("Ligne (classe, échelon) de la grille des catégories professionnelles.")
    )
    rank = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_("Progression Rank"),
        help_text=_("Order within career ladder (1=first, highest=last)")
    )
    next_level = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="previous_level",
        verbose_name=_("Next Level in Progression")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    class Meta:
        db_table = "jobs_position_seniority"
        ordering = ["position", "rank"]
        constraints = [
            UniqueConstraint(
                fields=['position', 'seniority_level'],
                condition=Q(deleted__isnull=True),
                name='unique_position_seniority'
            ),
        ]
        verbose_name = _("Position Seniority Level")
        verbose_name_plural = _("Position Seniority Levels")

    def clean(self):
        if self.salary_min > self.salary_max:
            raise ValidationError(_("Salary min cannot exceed salary max"))

        # Tension salariale légale 1:10 — le salaire max d'un échelon ne peut pas
        # dépasser 10× le SMIG mensuel actif (prévention des grilles abusives).
        # Import différé pour éviter la dépendance circulaire (pattern EmployeeContract.clean()).
        if self.salary_max and self.salary_max > 0:
            SMIGConfiguration = apps.get_model('hr_payroll', 'SMIGConfiguration')
            smig = SMIGConfiguration.objects.filter(is_active=True).first()
            if smig and smig.monthly_rate:
                ceiling = smig.monthly_rate * 10
                if self.salary_max > ceiling:
                    raise ValidationError(
                        _(f"Salary max ({self.salary_max} FC) cannot exceed 10× the active monthly SMIG ({ceiling} FC).")
                    )

    def __str__(self):
        return f"{self.position.name} - {self.seniority_level.label} (FC{self.salary_min:,}-{self.salary_max:,})"


class OrgUnit(BaseAuditableModel):
    """ 
    Organizational unit - represents any structural entity in the company hierarchy.
    Can be a department, division, team, function, branch, or project.
    """
    name = models.CharField(
        max_length=100, 
        verbose_name=_("Unit Name")
    )
    type = models.CharField(
        max_length=20,
        choices=OrgUnitType.choices,
        default=OrgUnitType.DEPARTMENT,
        verbose_name=_("Unit Type")
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="sub_units",
        verbose_name=_("Parent Unit")
    )
    manager = models.ForeignKey(
        "hr_employees.Employee", 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="units_managed",
        verbose_name=_("Unit Manager")
    )
    affoint = models.ForeignKey(
        "hr_employees.Employee", 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="units_deputized",
        verbose_name=_("Adjoint/Deputy")
    )
    authorized_headcount = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Authorized Headcount")
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Mission Description")
    )

    class Meta:
        db_table = "jobs_orgunit"
        ordering = ["name"]
        verbose_name = _("Organizational Unit")
        verbose_name_plural = _("Organizational Units")

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    @property
    def employee_count(self) -> int:
        """Returns the number of employees currently assigned to this unit."""
        return self.position_history.filter(is_current=True).count()

    @property
    def total_employee_count(self) -> int:
        """Returns the total number of employees in this unit and all sub-units."""
        count = self.employee_count
        for sub_unit in self.sub_units.all():
            count += sub_unit.total_employee_count
        return count


class EmployeePositionHistory(BaseAuditableModel):
    """ Records an employee's career progression and organization unity assignments. """
    employee = models.ForeignKey(
        "hr_employees.Employee",
        on_delete=models.CASCADE,
        related_name="position_history",
        verbose_name=_("Employee")
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="employee_histories",
        verbose_name=_("Position held")
    )
    seniority_level = models.ForeignKey(
        SeniorityLevel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="employee_histories",
        verbose_name=_("Seniority Level at Assignment")
    )
    salary_at_assignment = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Salary at Assignment"),
        help_text="Captured salary when this position was assigned"
    )
    org_unit = models.ForeignKey(
        OrgUnit,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="position_history",
        verbose_name=_("Assigned Unit")
    )
    start_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Start Date")
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("End Date")
    )
    is_current = models.BooleanField(
        default=True,
        verbose_name=_("Current Position")
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Assignment Notes")
    )

    class Meta:
        db_table = "jobs_employee_position_history"
        ordering = ["-start_date"]
        unique_together = ('employee', 'position', 'seniority_level', 'is_current')
        verbose_name = _("Position History")
        verbose_name_plural = _("Position Histories")

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError(_("End date cannot be before start date."))

    def save(self, *args, **kwargs):
        self.clean()
        if self.is_current:
            EmployeePositionHistory.objects.filter(
                employee=self.employee, 
                is_current=True
            ).exclude(id=self.id).update(is_current=False, end_date=timezone.now().date())
        super().save(*args, **kwargs)


class EmployeeTransition(BaseAuditableModel):
    """ Records a specific career movement event (promotion, transfer, hire, offboard). """
    employee = models.ForeignKey(
        "hr_employees.Employee",
        on_delete=models.CASCADE,
        related_name="transitions",
        verbose_name=_("Employee")
    )
    transition_type = models.CharField(
        max_length=20,
        choices=TransitionType,
        verbose_name=_("Transition Type")
    )
    from_position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transitions_from",
        verbose_name=_("From Position")
    )
    from_seniority_level = models.ForeignKey(
        SeniorityLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transitions_from",
        verbose_name=_("From Seniority Level")
    )
    to_position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transitions_to",
        verbose_name=_("To Position")
    )
    to_seniority_level = models.ForeignKey(
        SeniorityLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transitions_to",
        verbose_name=_("To Seniority Level")
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name=_("Transition Date")
    )
    reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Reason/Notes")
    )

    class Meta:
        db_table = "jobs_employee_transition"
        ordering = ["-date", "-created_at"]
        verbose_name = _("Employee Transition")
        verbose_name_plural = _("Employee Transitions")

    def __str__(self):
        return f"{self.employee} - {self.get_transition_type_display()} ({self.date})"


class Training(BaseAuditableModel):
    """ Professional certifications and corporate training records. """
    employee = models.ForeignKey(
        "hr_employees.Employee",
        on_delete=models.CASCADE,
        related_name="trainings",
        verbose_name=_("Employee")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Training Name")
    )
    institute = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name=_("Training Institution")
    )
    start_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Start Date")
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("End Date")
    )
    location = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name=_("Location")
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Content Summary")
    )
    expiry_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("Expiry Date")
    )

    class Meta:
        db_table = "jobs_training"
        ordering = ["-start_date"]
        verbose_name = _("Training")
        indexes = [
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.name} - {self.employee.full_name}"

    def clean(self):
            super().clean()
            if self.expiry_date and self.start_date and self.expiry_date <= self.start_date:
                raise ValidationError(_("Expiry date must be after the start date."))


class Vacancy(BaseAuditableModel):
    """ Records open job positions that need to be filled. """
    class Priority(models.TextChoices):
        HIGH = 'HIGH', _('High')
        MEDIUM = 'MEDIUM', _('Medium')
        LOW = 'LOW', _('Low')

    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        RECRUITMENT = 'RECRUITMENT', _('External Recruitment')
        CANCELLED = 'CANCELLED', _('Cancelled')
        FILLED = 'FILLED', _('Filled')

    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='vacancies',
        verbose_name=_('Position')
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name=_('Priority')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name=_('Status')
    )
    opened_date = models.DateField(
        default=timezone.now,
        verbose_name=_('Opened Date')
    )
    target_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Target Fill Date')
    )
    reason = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Reason/Notes')
    )
    filled_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Filled Date')
    )
    filled_by_transition = models.ForeignKey(
        EmployeeTransition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filled_vacancy',
        verbose_name=_('Filled By Transition')
    )

    class Meta:
        db_table = "jobs_vacancy"
        ordering = ['-opened_date', '-priority']
        verbose_name = _('Vacancy')
        verbose_name_plural = _('Vacancies')
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['opened_date']),
        ]

    def __str__(self):
        return f"{self.position.name} - {self.get_status_display()}"


# --- Audit log registration ---
auditlog.register(JobFamily)
auditlog.register(Position)
auditlog.register(SeniorityLevel)
auditlog.register(OrgUnit)
auditlog.register(EmployeePositionHistory)
auditlog.register(EmployeeTransition)
auditlog.register(Training)
auditlog.register(Vacancy)
auditlog.register(ProfessionalCategory)

