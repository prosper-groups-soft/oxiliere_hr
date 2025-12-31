import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from hr.employees.models import Employee
from utils_mixins.models import BaseModelMixin
from hr.choices import (
    PaymentType, 
    PaymentPeriod, 
    ContractType,
    PayslipStatus
)
from django.core.exceptions import ValidationError
from utils_mixins.fn import enum_to_choices
from .enums import PaymentMethod, BonusTypes



#
#   from hr.caches import get_attendance_settings
#   return get_attendance_settings()
#


class Salary(BaseModelMixin):
    code = models.CharField(
        max_length=16,
        unique=True,
        verbose_name="Code (automatique)",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="salaries",
        verbose_name="Employé"
    )
    payment_type = models.CharField(
        max_length=6,
        choices=[
            (PaymentType.FIXED.value, 'Salaire fixe'),
            (PaymentType.HOURLY.value, 'Paiement à l\'heure'),
        ],
        default=PaymentType.FIXED,
        verbose_name="Type de paiement"
    )
    payment_period = models.CharField(
        max_length=10,
        choices=[
            (PaymentPeriod.DAILY.value, 'Journalier'),
            (PaymentPeriod.PER_TASK.value, 'A la tâche'),
            (PaymentPeriod.MONTHLY.value, 'Mensuel'),
        ],
        default=PaymentPeriod.MONTHLY.value,
        verbose_name="Type de période"
    )
    contract_type = models.CharField(
        max_length=20,
        choices=[
            (ContractType.CDI.value, 'Contrat à Durée Indéterminée'),
            (ContractType.CDD.value, 'Contrat à Durée Déterminée'),
            (ContractType.INTERNSHIP.value, 'Stage'),
            (ContractType.FREELANCE.value, 'Freelance'),
            (ContractType.TEMPORARY.value, 'Contrat Temporaire'),
        ],
        default=ContractType.CDD.value,
        verbose_name="Type de contrat",
    )
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Salaire de base"
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Taux horaire"
    )
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin (si applicable)"
    )
    deduct_late = models.BooleanField(
        default=False, 
        verbose_name="Déduire les retards"
    )
    pay_overtime = models.BooleanField(
        default=False, 
        verbose_name="Payer les heures supplémentaires"
    )
    allow_advance = models.BooleanField(
        default=False, 
        verbose_name="Permettre les avances sur salaire"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Contrat actif"
    )
    comments = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Commentaires"
    )

    def clean(self):
        # Validation simple : cohérence des dates
        if self.contract_type != ContractType.CDI and self.end_date is None:
            raise ValidationError(
                "La date de fin est obligatoire pour un contrat non CDI."
            )

        if self.contract_type != ContractType.CDI and self.start_date >= self.end_date:
            raise ValidationError("La date de début doit être inférieure à la date de fin.")

        # Normalisation simple
        if self.comments:
            self.comments = self.comments.strip()

    def __str__(self):
        return f"Contract of {self.employee} ({self.contract_type})"

    class Meta:
        verbose_name = "Salaire ou paiement horaire"
        verbose_name_plural = "Salaires et paiements horaires"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['employee'],
                condition=models.Q(is_active=True),
                name='unique_active_contract_per_employee'
            )
        ]


class SalaryLog(BaseModelMixin):
    salary = models.ForeignKey(
        Salary,
        on_delete=models.DO_NOTHING,
        related_name='salary_logs',
        verbose_name="Salary"
    )
    payslip = models.ForeignKey(
        "hr.Payslip",
        on_delete=models.DO_NOTHING,
        related_name='salary_logs',
        verbose_name="Payslip"
    )
    start_date = models.DateField(verbose_name="Start date")
    end_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="End date"
    )
    
    total_payment = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Total payment"
    )
    total_contributions = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Total social contributions"
    )
    total_bonus = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Total bonus"
    )
    social_contributions = models.ManyToManyField(
        'SocialContribution',
        related_name='salary_logs',
        blank=True,
        verbose_name="Social contributions"
    )
    overtime_payment = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Overtime payment"
    )
    overtime_hours = models.DurationField(
        null=True, 
        blank=True, 
        verbose_name="Overtime hours"
    )
    undertime_hours = models.DurationField(
        null=True, 
        blank=True, 
        verbose_name="Undertime hours"
    )
    bonus = models.ManyToManyField(
        'Bonus',
        related_name='salary_logs',
        blank=True,
        verbose_name="Bonus"
    )
    salary_advance = models.ForeignKey(
        'RepaymentLog',
        on_delete=models.SET_NULL,
        related_name='salary_logs',
        null=True,
        blank=True,
        verbose_name="Salary advance"
    )
    payment_method = models.CharField(
        max_length=50,
        choices=enum_to_choices(PaymentMethod),
        default=PaymentMethod.CASH.value,
        verbose_name="Payment method"
    )
    payment_reference = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Payment reference"
    )
    hours_worked = models.DurationField(
        null=True, 
        blank=True, 
        verbose_name="Worked hours"
    )
    is_paid = models.BooleanField(default=False, verbose_name="Paid")
    paid_at = models.DateTimeField(null=True, blank=True)
    
    confirmed = models.BooleanField(default=False, verbose_name="Confirmed")
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    comments = models.TextField(null=True, blank=True, verbose_name="Comments")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def attendance_settings(self):
        from hr.caches import get_attendance_settings
        return get_attendance_settings()

    def __str__(self):
        return f"Payment log for {self.salary.employee} ({self.start_date} - {self.end_date})"

    class Meta:
        verbose_name = "Payment log"
        verbose_name_plural = "Payment logs"
        unique_together = ('salary', 'payslip')


class Bonus(BaseModelMixin):
    applicable_to = models.ManyToManyField(
        Employee,
        related_name='bonuses',
        verbose_name="Applicable à",
        through='BonusEmployee',
    )
    name = models.CharField(
        max_length=100, 
        verbose_name="Nom du bonus", 
        blank=True, 
        null=True
    )
    bonus_type = models.CharField(
        max_length=100, 
        choices=enum_to_choices(BonusTypes),
        verbose_name="Type de bonus"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Montant"
    )
    always_apply = models.BooleanField(default=False, verbose_name="Toujours applicable")
    everyone = models.BooleanField(default=False, verbose_name="Appliquer à tout le monde")
    start_date = models.DateField(verbose_name="Date de début", null=True, blank=True)
    end_date = models.DateField(verbose_name="Date de fin", null=True, blank=True)
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    def clean(self):
        """Format the name and description fields."""
        if self.name:
            self.name = self.name.strip().title()
        if self.description:
            self.description = self.description.strip()

    def save(self, *args, **kwargs):
        """Set default name if not provided."""
        if not self.name:
            self.name = timezone.now().strftime("%d/%m/%Y") + " - " + self.bonus_type
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bonus_type} : {self.amount}"

    class Meta:
        verbose_name = "Bonus"
        verbose_name_plural = "Bonus"


class BonusEmployee(BaseModelMixin):
    """
    Pure relationship model between Bonus and Employee.
    """

    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='bonus_employees',
        verbose_name="Employé"
    )

    bonus = models.ForeignKey(
        'Bonus',
        on_delete=models.CASCADE,
        related_name='bonus_employees',
        verbose_name="Bonus"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='bonus_employees_created_by',
        verbose_name="Créé par"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} ← {self.bonus}"

    class Meta:
        verbose_name = "Employé – Bonus"
        verbose_name_plural = "Employés – Bonus"
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'bonus'],
                name='unique_employee_bonus'
            )
        ]


class SalaryAdvance(BaseModelMixin):
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.PROTECT,
        related_name='salary_advances',
        verbose_name="Employee"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Advance amount"
    )

    repayment_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Repayment percentage"
    )

    is_repaid = models.BooleanField(
        default=False,
        verbose_name="Fully repaid"
    )

    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name="Comments"
    )

    def __str__(self):
        return f"Salary advance {self.amount} for {self.employee}"

    @property
    def repayment_amount(self):
        if not self.repayment_percentage:
            return None
        return (self.amount * self.repayment_percentage) / 100

    class Meta:
        verbose_name = "Salary advance"
        verbose_name_plural = "Salary advances"
        ordering = ['-created_at']



class RepaymentLog(BaseModelMixin):
    salary_advance = models.ForeignKey(
        'SalaryAdvance',
        on_delete=models.CASCADE,
        related_name='repayment_logs',
        verbose_name="Salary advance"
    )

    date = models.DateField(
        auto_now_add=True,
        verbose_name="Repayment date"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Repaid amount"
    )

    sold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Remaining amount"
    )

    def __str__(self):
        return f"Repayment of {self.amount} for advance {self.salary_advance_id}"

    class Meta:
        verbose_name = "Repayment log"
        verbose_name_plural = "Repayment logs"
        ordering = ['-date']


class Payslip(BaseModelMixin):
    employees = models.ManyToManyField(
        Employee,
        related_name="payslips",
        verbose_name="Employés inclus"
    )
    code: str = models.CharField(max_length=16)
    start_date = models.DateField(verbose_name="Début de la période")
    end_date = models.DateField(verbose_name="Fin de la période")
    payment_period = models.CharField(
        max_length=10,
        choices=[
            (PaymentPeriod.DAILY.value, 'Journalier'),
            (PaymentPeriod.PER_TASK.value, 'A la tâche'),
            (PaymentPeriod.MONTHLY.value, 'Mensuel'),
        ],
        default=PaymentPeriod.MONTHLY,
        verbose_name="Type de période"
    )
    paid_date = models.DateTimeField(null=True)
    confirmed_date = models.DateTimeField(null=True)
    canceled_date = models.DateTimeField(null=True)

    status = models.CharField(
        max_length=15,
        choices=[
            (PayslipStatus.CONFIRMED.value, 'Confirmée'),
            (PayslipStatus.PAID.value, 'Payée'),
            (PayslipStatus.CANCELED.value, 'Annulée'),
            (PayslipStatus.REVIEW.value, 'En révision'),
        ],
        default=PayslipStatus.REVIEW,
        verbose_name="État de la fiche de paie"
    )

    class Meta:
        ordering = ["-start_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"FICHE-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_eligible_employees(self):
        eligible_employees = Employee.objects.filter(
            salaries__payment_period=self.payment_period,
            salaries__is_active=True,
        ).filter(
            models.Q(salaries__contract_type=ContractType.CDI) | 
            models.Q(salaries__end_date__gte=self.start_date)
        ).exclude(
            payslips=self
        )
        return eligible_employees

    def get_period_days(self) -> int:
        periods = {
            PaymentPeriod.MONTHLY: 30,
            PaymentPeriod.DAILY: 1,
            PaymentPeriod.PER_TASK: 1
        }
        return periods.get(self.payment_period, 30)


class PaymentState(models.Model):
    salary = models.OneToOneField(
        Salary, 
        on_delete=models.CASCADE, 
        related_name="payment_state",
        verbose_name="Contrat de salaire"
    )
    next_payment_date = models.DateField(
        verbose_name="Prochaine date de paiement"
    )
    last_period = models.DateField(
        null=True, blank=True,
        verbose_name="Dernière période de paiement"
    )
    payment_cycles = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de paiements exécutés"
    )
    has_next = models.BooleanField(
        default=True, 
        verbose_name="Y a-t-il un prochain paiement ?"
    )
    
    class Meta:
        ordering = ["next_payment_date"]

    def calculate_next_payment_date(self):
        """Calcule la prochaine date de paiement en fonction du payment_period"""
        start_date = self.salary.start_date
        period = self.salary.payment_period
        next_date = self.next_payment_date or start_date

        if period == PaymentPeriod.MONTHLY:
            next_date = start_date + relativedelta(months=self.payment_cycles + 1)
        # elif period == PaymentPeriod.WEEKLY:
        #     next_date = start_date + relativedelta(weeks=self.payment_cycles + 1)
        elif period == PaymentPeriod.DAILY:
            next_date = start_date + relativedelta(days=self.payment_cycles + 1)
        
        self.next_payment_date = next_date

    def update_has_next(self):
        """Met à jour has_next en fonction de Salary.end_date"""
        end_date = self.salary.end_date

        if self.salary.contract_type == ContractType.CDI:
            self.has_next = True
        elif end_date and self.next_payment_date >= end_date:
            self.has_next = False
        else:
            self.has_next = True

    def update_next_payment(self):
        """Met à jour la prochaine date de paiement après un paiement"""
        if not self.has_next:
            return

        self.last_period = self.next_payment_date
        self.payment_cycles += 1
        self.calculate_next_payment_date()
        self.update_has_next()
        self.save()

    def save(self, *args, **kwargs):
        """Initialisation de la prochaine date de paiement et de has_next"""
        if self._state.adding:
            self.calculate_next_payment_date()
        self.update_has_next()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PaymentState ({self.salary.employee}) - Prochain paiement : {self.next_payment_date} - Actif: {self.has_next}"


class SocialContribution(BaseModelMixin):
    name = models.CharField(max_length=100, verbose_name="Nom de la cotisation")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, 
        verbose_name="Montant", null=True)
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, 
        verbose_name="Pourcentage (%)", null=True, blank=True
    )
    applicable_to = models.ManyToManyField(
        'Employee',
        related_name='social_contributions',
        verbose_name="Applicable à",
        through="ContributionEmployee",
    )
    always_apply = models.BooleanField(
        default=False,
        verbose_name="Toujours applicable"
    )
    everyone = models.BooleanField(
        default=False,
        verbose_name="Appliquer à tout le monde"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Statut actif/inactif"
    )
    
    def clean(self):
        # Formatage du nom pour standardiser la casse
        if self.name:
            self.name = self.name.strip().title()
            
    start_date = models.DateField(
        verbose_name="Date de début",
        null=True, blank=True
    )
    end_date = models.DateField(
        verbose_name="Date de fin",
        null=True, blank=True
    )
    
    class Meta:
        ordering = ["name", "-is_active"]
    description = models.TextField(
        null=True, blank=True,
        verbose_name="Description"
    )

    def add_employees(self, employee_ids, created_by_user, check_on_everyone=True):
        if check_on_everyone:
            self.check_on_everyone()

        if employee_ids is None or len(employee_ids) == 0:
            return []
        
        existing_employee_ids = self.contribution_employees.values_list('employee__id', flat=True)
        new_employee_ids = [emp_id for emp_id in employee_ids if emp_id not in existing_employee_ids]
        new_employees = Employee.objects.filter(id__in=new_employee_ids)
        contribution_employee_instances = [
            ContributionEmployee(
                employee=employee,
                contribution=self,
                created_by=created_by_user
            )
            for employee in new_employees
        ]
        
        ContributionEmployee.objects.bulk_create(contribution_employee_instances)
        return new_employee_ids
    

    def remove_employees(self, employee_ids, created_by_user, check_on_everyone=True):
        if check_on_everyone:
            self.check_on_everyone()

        if employee_ids is None or len(employee_ids) == 0:
            return []
        
        existing_employee_ids = self.contribution_employees.values_list('employee__id', flat=True)
        existed_ids = [emp_id for emp_id in employee_ids if emp_id in existing_employee_ids]
        self.contribution_employees.filter(employee__id__in=existed_ids).delete()
        return existed_ids
    
    def reset(self, created_by_user):
        self.everyone = False
        self.contribution_employees.all().delete()
        self.updated_by = created_by_user
        self.save(
            update_fields=['everyone', 'updated_by']
        )
    
    def check_on_everyone(self):
        if self.everyone:
            raise ValidationError("Cet avantage est appliquer à tout le monde, vous ne pouvez pas ajouter des employés")

    def get_amount(self, total_payment: float) -> float:
        """
        Get amount, depending on percentage
        """
        if self.percentage:
            return total_payment * self.percentage / 100
        return self.amount

    
    def clean(self):
        if self.percentage and self.amount:
            raise ValidationError("Vous devez définir soit le montant soit le pourcentage.")
        if not self.percentage and not self.amount:
            raise ValidationError("Vous devez définir soit le montant soit le pourcentage.")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("La date de début doitêtre avant la date de fin.")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.amount} - {self.percentage}%)"

    class Meta:
        verbose_name = "Cotisation sociale"
        verbose_name_plural = "Cotisations sociales"
        ordering = ['start_date']


class ContributionEmployee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='social_contribution_employees',
        verbose_name="Employé"
    )
    contribution = models.ForeignKey(
        'SocialContribution',
        on_delete=models.CASCADE,
        related_name='contribution_employees',
        verbose_name="Cotisation sociale"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_contribution_employees',
        verbose_name="Creé par"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Cotisation sociale pour un employé"
        verbose_name_plural = "Cotisations sociales pour les employés"
        unique_together = ('employee', 'contribution')
        ordering = ["-created_at"]

