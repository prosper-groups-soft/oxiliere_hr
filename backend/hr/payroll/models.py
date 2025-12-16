

class Salary(BaseModelMixin):
    code = models.CharField(
        max_length=16, unique=True,
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
        default=PaymentPeriod.MONTHLY,
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
        verbose_name="Type de contrat",
        default=ContractType.CDD,
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
    is_active = models.BooleanField(default=True, verbose_name="Contrat actif")
    comments = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Commentaires"
    )

    def close_contract(self):
        pass


    def notify_contract_closing(self):
        pass

    
    def notify_new_contract(self):
        pass

    def clean(self):
        # si contrat est un CDI, il n'a pas de date de fin

        if not self.contract_type == ContractType.CDI and self.end_date is None:
            raise ValidationError("La date de fin est obligatoire pour un contrat non CDI.")

        if not self.contract_type == ContractType.CDI:
            if self.start_date >= self.end_date:
                raise ValidationError("La date de début doit être inférieure à la date de fin.")
            
            days = (self.end_date - self.start_date).days
            min_durations = {
                PaymentPeriod.MONTHLY: 30,  # Au moins 30 jours
                PaymentPeriod.DAILY: 1,      # Au moins 1 jour
                PaymentPeriod.PER_TASK: 1    # Au moins 1 jour
            }

            if days < min_durations[self.payment_period]:
                raise ValidationError(f"Le contrat doit avoir une durée d'au moins {min_durations[self.payment_period]} jours.")
        
        overlapping_salaries = Salary.objects.filter(
            employee=self.employee,
            start_date__lt=self.end_date if self.end_date else self.start_date,
            end_date__gt=self.start_date if self.start_date else self.end_date
        ).exclude(id=self.id)

        if overlapping_salaries.exists():
            raise ValidationError("Cet employé a déjà un contrat actif sur cette période.")


    def clean(self):
        # Vérifications existantes
        # si contrat est un CDI, il n'a pas de date de fin

        if not self.contract_type == ContractType.CDI and self.end_date is None:
            raise ValidationError("La date de fin est obligatoire pour un contrat non CDI.")

        if not self.contract_type == ContractType.CDI:
            if self.start_date >= self.end_date:
                raise ValidationError("La date de début doit être inférieure à la date de fin.")
            
            days = (self.end_date - self.start_date).days
            min_durations = {
                PaymentPeriod.MONTHLY: 30,  # Au moins 30 jours
                PaymentPeriod.DAILY: 1,     # Au moins 1 jour
                PaymentPeriod.PER_TASK: 1    # Au moins 1 jour
            }

            if days < min_durations[self.payment_period]:
                raise ValidationError(f"Le contrat doit avoir une durée d'au moins {min_durations[self.payment_period]} jours.")
        
        overlapping_salaries = Salary.objects.filter(
            employee=self.employee,
            is_active=True,
        ).exclude(id=self.id)

        if overlapping_salaries.exists():
            raise ValidationError("Cet employé a déjà un contrat actif sur cette période.")

        # Formatage des commentaires
        if self.comments:
            self.comments = self.comments.strip()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.clean()
            self.code = f"C-{get_rotate_value()}{get_next_value(get_contract_seq_key()):05d}"
        if self.payment_type == 'FIXED':
            self.total_payment = self.base_salary

        elif self.payment_type == 'HOURLY':
            self.total_payment = self.hourly_rate * self.hours_worked

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment of {self.total_payment} to {self.employee.first_name} {self.employee.last_name} on {self.payment_date}"

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salary = models.ForeignKey(
        Salary,
        on_delete=models.DO_NOTHING,
        related_name='salary_logs',
        verbose_name="Salaire"
    )
    payslip = models.ForeignKey(
        "hr.Payslip",
        on_delete=models.DO_NOTHING,
        related_name='salary_logs',
        verbose_name="Salaire"
    )
    start_date = models.DateField(
        verbose_name="Date de début"
    )
    end_date = models.DateField(
        verbose_name="Date de fin",
        null=True, blank=True
    )

    total_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Paiement total"
    )
    total_contributions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Total Cotisation Sociale"
    )
    total_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Total Avantage"
    )
    social_contributions = models.ManyToManyField(
        'SocialContribution',
        related_name='salary_logs',
        blank=True,
        verbose_name="Cotisations sociales"
    )
    overtime_payment = models.FloatField(
        null=True, blank=True,
        verbose_name="Paiement des heures supplémentaires"
    )
    overtime_hours = models.DurationField(
        null=True, blank=True,
        verbose_name="Nombre d'heures supplémentaires"
    )
    undertime_hours = models.DurationField(
        null=True, blank=True,
        verbose_name="Nombre d'heures perdues"
    )
    bonus = models.ManyToManyField(
        'Bonus',
        related_name='salary_logs',
        blank=True,
        verbose_name="Bonus"
    )
    salary_advance = models.ForeignKey(
        RepaymentLog,
        on_delete=models.SET_NULL,
        related_name='salary_logs',
        null=True, blank=True,
        verbose_name="Avance sur salaire"
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('BANK', 'Virement bancaire'),
            ('CASH', 'Espèces'),
            ('CHECK', 'Chèque'),
        ],
        default="CASH",
        verbose_name="Méthode de paiement"
    )
    payment_reference = models.CharField(
        max_length=100, 
        verbose_name="Référence de paiement",
        null=True, 
        blank=True
    )
    hours_worked = models.DurationField(
        null=True,
        blank=True,
        verbose_name="Heures travaillées"
    )
    is_paid = models.BooleanField(default=False, verbose_name="Paiement effectifié")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed = models.BooleanField(default=False, verbose_name="Paiement confirmé")
    comments = models.TextField(null=True, blank=True, verbose_name="Commentaires")


    @property
    def attendance_settings(self):
        from hr.caches import get_attendance_settings
        return get_attendance_settings()

    @transaction.atomic
    def compute_salary(self, override = False, commit=True):

        if self.is_paid and not override:
            return

        working_time = self.attendance_settings.total_working_time

        if self.salary.pay_overtime:
            self.overtime_hours, self.undertime_hours = Attendance.objects.compute_overtime_and_undertime(
                self.salary.employee,
                self.start_date,
                self.end_date
            )
            self.hours_worked = working_time + self.overtime_hours - self.undertime_hours
        else:
            self.hours_worked = working_time


        if self.salary.payment_type == 'FIXED':
            self.total_payment = self.salary.base_salary

        elif self.salary.payment_type == 'HOURLY':
            if self.hours_worked is None:
                self.total_payment = 0
            elif self.hours_worked.total_seconds() == 0:
                self.total_payment = 0
            else:
                hours_worked = self.hours_worked.total_seconds() / 3600
            self.total_payment = self.salary.hourly_rate * hours_worked
        

        salary_advance = SalaryAdvance.objects.filter(employee=self.salary.employee).first()
        if salary_advance:
            self.salary_advance = salary_advance.get_payment(self.total_payment)

        if self.salary_advance:
            self.total_payment -= self.salary_advance.amount

        # TODO: Add this to SaaS and his settings
        # self.total_contributions = self.compute_contributions()
        # self.total_payment -= self.total_contributions

        # self.total_bonus = self.compute_bonus()
        # self.total_payment += self.total_bonus

        if self.salary.payment_type == 'FIXED' and self.salary.pay_overtime:
            overtime = self.overtime_hours - self.undertime_hours
            self.total_payment += Decimal(overtime.total_seconds() / 3600) * self.salary.hourly_rate
        
        if commit:
            self.save()


    def compute_contributions(self):
        contributions = SocialContribution.objects.filter(
            applicable_to=self.salary.employee
        ).filter(
            Q(end_date__gte=self.end_date) | Q(end_date__isnull=True),
            Q(always_apply=True) | Q(start_date__lte=self.end_date)
        )

        self.social_contributions.set(contributions)

        total_contributions = 0
        for _c in contributions:
            total_contributions += _c.get_amount(self.total_payment)

        return total_contributions

    
    def compute_bonus(self):
        bonus = Bonus.objects.filter(
            applicable_to=self.salary.employee
        )

        self.bonus.set(bonus)

        total_bonus = 0
        for _b in bonus:
            total_bonus += _b.amount

        return total_bonus


    def confirm_payment(self):
        self.confirmed = True
        self.confirmed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Log de paiement de {self.employee} pour la période {self.payment_period}"

    class Meta:
        verbose_name = "Historique des paiements"
        verbose_name_plural = "Historiques des paiements"
        unique_together = (
            ('salary', 'payslip',)
        )


class Bonus(BaseModelMixin):
    BONUS_TYPES = (
        ('transport_allowance', 'Indemnité de transport'),
        ('housing_allowance', 'Indemnité de logement'),
        ('remote_work_allowance', 'Indemnité de télétravail'),
        ('meal_allowance', 'Indemnité repas'),
        ('company_health_insurance', 'Mutuelle d\'entreprise'),
        ('disability_insurance', 'Assurance prévoyance'),
        ('travel_expenses', 'Frais de mission'),
        ('back_to_school_allowance', 'Allocation de rentrée scolaire'),
        ('childcare_allowance', 'Allocation de garde d\'enfants'),
        ('housing_aid', 'Aide au logement'),
        ('thirteenth_month', '13e mois'),
        ('health_insurance', 'Assurance santé'),
        ('transport_bonus', 'Primes de transport'),
        ('seniority_bonus', 'Prime d\'ancienneté'),
        ('other', 'Autre'),
    )
    name = models.CharField(max_length=100, verbose_name="Nom du bonus", blank=True, null=True)
    bonus_type = models.CharField(
        max_length=50, 
        choices=BONUS_TYPES, 
        verbose_name="Type de bonus"
    )
    
    def clean(self):
        # Formatage du nom pour standardiser la casse
        if self.name:
            self.name = self.name.strip().title()
        if self.description:
            self.description = self.description.strip()
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Montant"
    )
    applicable_to = models.ManyToManyField(
        Employee, 
        related_name='bonuses', 
        verbose_name="Applicable à",
        through='BonusEmployee',
    )
    always_apply = models.BooleanField(
        default=False,
        verbose_name="Toujours applicable"
    )
    everyone = models.BooleanField(
        default=False,
        verbose_name="Appliquer à tout le monde"
    )
    start_date = models.DateField(
        verbose_name="Date de début",
        null=True, blank=True
    )
    end_date = models.DateField(
        verbose_name="Date de fin",
        null=True, blank=True
    )
    description = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Description"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")


    def add_employees(self, employee_ids, created_by_user, check_on_everyone=True):
        if check_on_everyone:
            self.check_on_everyone()

        if employee_ids is None or len(employee_ids) == 0:
            return []
        
        existing_employee_ids = self.bonus_employees.values_list('employee__id', flat=True)
        new_employee_ids = [emp_id for emp_id in employee_ids if emp_id not in existing_employee_ids]
        new_employees = Employee.objects.filter(id__in=new_employee_ids)
        bonus_employee_instances = [
            BonusEmployee(
                employee=employee,
                bonus=self,
                created_by=created_by_user
            )
            for employee in new_employees
        ]
        
        BonusEmployee.objects.bulk_create(bonus_employee_instances)
        return new_employee_ids
    

    def remove_employees(self, employee_ids, created_by_user, check_on_everyone=True):
        if check_on_everyone:
            self.check_on_everyone()

        if employee_ids is None or len(employee_ids) == 0:
            return []
        
        existing_employee_ids = self.bonus_employees.values_list('employee__id', flat=True)
        existed_ids = [emp_id for emp_id in employee_ids if emp_id in existing_employee_ids]
        self.bonus_employees.filter(employee__id__in=existed_ids).delete()
        return existed_ids
    
    def reset(self, created_by_user):
        self.everyone = False
        self.bonus_employees.all().delete()
        self.updated_by = created_by_user
        self.save(
            update_fields=['everyone', 'updated_by']
        )
    
    def check_on_everyone(self):
        if self.everyone:
            raise ValidationError("Cet avantage est appliquer à tout le monde, vous ne pouvez pas ajouter des employés")
    
    
    def __str__(self):
        return f"{self.bonus_type()} : {self.amount}"
    

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = timezone.now().strftime("%d/%m/%Y") + " - " + self.bonus_type
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Bonus"
        verbose_name_plural = "Bonus"


class BonusEmployee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
        on_delete=models.CASCADE,
        related_name='bonus_employees_created_by',
        verbose_name="Creé par"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.bonus}"
    
    class Meta:
        verbose_name = "Employé - Bonus"
        verbose_name_plural = "Employé - Bonus"
        unique_together = ['employee', 'bonus']
        ordering = ['-created_at']


class SalaryAdvance(BaseModelMixin):
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='salary_advances',
        verbose_name="Employé"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant de l'avance")
    repayment_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Pourcentage de remboursement (%)", null=True, blank=True
    )
    is_repaid = models.BooleanField(default=False, verbose_name="Entièrement remboursée")
    comments = models.TextField(null=True, blank=True, verbose_name="Commentaires")

    def __str__(self):
        return f"Avance de {self.amount} pour {self.employee}"

    def clean(self):
        unpaid_advances = SalaryAdvance.objects.filter(employee=self.employee, is_repaid=False).exclude(pk=self.pk)
        if unpaid_advances.exists():
            raise ValidationError(f"L'employé {self.employee} a déjà une avance non remboursée.")


    def get_last_repayment(self):
        if not hasattr(self, '_last_repayment'):
            if self.repayment_logs.exists():
                self._last_repayment = self.repayment_logs.last()
            return None
        return self._last_repayment
    

    def get_payment(self, amount):
        if self.is_repaid:
            return None
        
        last_repayment = self.get_last_repayment()
        if last_repayment:
            sold = last_repayment.sold
            repay_amount = min(sold, self.computed_percentage)
            new_sold = sold - repay_amount
        else:
            repay_amount = self.computed_percentage
            new_sold = self.amount - repay_amount

        if amount < repay_amount:
            return None

        self._last_repayment = RepaymentLog.objects.create(
            sold = new_sold,
            salary_advance = self,
            amount = repay_amount,
        )

        if new_sold <= 0:
            self.is_repaid = True
            self.save()

        return self._last_repayment

        
    @property
    def computed_percentage(self):
        return self.amount / 100 * self.repayment_percentage
    
    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Avance sur salaire"
        verbose_name_plural = "Avances sur salaire"
        ordering = ['-created_at']


class RepaymentLog(models.Model):
    salary_advance = models.ForeignKey(
        'SalaryAdvance',
        on_delete=models.CASCADE,
        related_name='repayment_logs',
        verbose_name="Avance sur salaire"
    )
    date = models.DateField(auto_now_add=True, verbose_name="Date de remboursement")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant remboursé")
    sold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant restant")


    def __str__(self):
        return f"Remboursement de {self.repayment_amount} pour l'avance {self.salary_advance}"

    class Meta:
        verbose_name = "Historique de remboursement"
        verbose_name_plural = "Historiques de remboursement"
        ordering = ['-date']


class Payslip(BaseModelMixin):
    code = models.CharField(max_length=16)
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
    employees = models.ManyToManyField(
        Employee, 
        related_name="payslips", 
        verbose_name="Employés inclus"
    )
    # txs = models.ForeignKey(
    #     "accounting.TransactionFlow",
    #     on_delete=models.SET_NULL,
    #     null=True,
    # )
    # ledger = models.ForeignKey(
    #     "accounting.LedgerModel",
    #     on_delete=models.SET_NULL,
    #     null=True,
    # )

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

    def get_eligible_employees(self):
        """Sélectionne les employés dont la prochaine date de paiement est dans la période
        et exclut ceux qui sont déjà inclus dans une fiche de paie pour la même période."""
        
        eligible_employees = Employee.objects.filter(
            salaries__payment_period=self.payment_period,
            salaries__is_active=True,
        ).filter(
            Q(salaries__contract_type=ContractType.CDI) | Q(salaries__end_date__gte=self.start_date)
        ).exclude(
            payslips=self
        )
        return eligible_employees
    

    def mark_as_canceled(self, commit=True, **kwargs):
        """Annule la fiche de paie et libère potentiellement les employés pour une autre fiche."""
        if self.status == PayslipStatus.PAID:
            raise ValidationError("Impossible d'annuler une fiche de paie déjà payée.")
        
        self.status = PayslipStatus.CANCELED
        if self.txs:
            self.txs.mark_as_cancelled(commit=True)
        self.canceled_date = timezone.now()
        
        if commit:
            self.save(
                update_fields=['status' , 'canceled_date']
            )

    def mark_as_confirmed(self, commit=True, user=None):
        """Confirme la fiche de paie et verrouille les employés dedans."""
        if self.status != PayslipStatus.REVIEW:
            raise ValidationError("Seules les fiches en révision peuvent être confirmées.")
        
        self.status = PayslipStatus.CONFIRMED
        self.confirmed_date = timezone.now()

        s_logs, tx = self.create_salary_logs(user=user)

        if commit:
            self.save(
                update_fields=['status', 'confirmed_date']
            )
        return s_logs, tx

    def mark_as_review(self, commit=True, **kwargs):
        """Remet la fiche de paie en révision si elle n'est pas encore payée."""
        if self.status == PayslipStatus.PAID:
            raise ValidationError("Impossible de repasser en révision une fiche déjà payée.")
        
        self.status = PayslipStatus.REVIEW
        
        if commit:
            self.save(
                update_fields=['status']
            )

    def mark_as_paid(self, commit=True, **kwargs):
        """Marque la fiche de paie comme payée et notifie les employés concernés."""
        if self.status != PayslipStatus.CONFIRMED:
            raise ValidationError("Seules les fiches confirmées peuvent être payées.")
        
        self.status = PayslipStatus.PAID
        self.paid_date = timezone.now()

        # update salarylogs
        qs = SalaryLog.objects.filter(
            payslip=self
        ).update(
            is_paid=True,
            paid_at=self.paid_date
        )
        self.notify_payment()

        if commit:
            self.save(
                update_fields=['status', 'paid_date']
            )

    # def create_transaction(self, amount=0, user=None):
    #     """Crée une transaction comptable liée à cette fiche de paie."""
    #     if self.status != PayslipStatus.CONFIRMED:
    #         raise ValidationError("Une transaction ne peut être créée que pour une fiche confirmée.")

    #     if self.txs:
    #         raise ValidationError("Une transaction a déjà été créée pour cette fiche de paie.")
        
    #     from accounting.models import TransactionFlow

    #     user = user or self.created_by

    #     tx = TransactionFlow.objects.create(
    #         x_number=self.code,
    #         date=timezone.now(),
    #         type=TransactionFlow.OUTFLOW,
    #         amount=amount,
    #         status='new',
    #         description=f"Paiement des salaires pour la période {self.start_date} - {self.end_date}",
    #         created_by=user,
    #         updated_by=user,
    #         meta={
    #             "initiator": "payslip",
    #             "target": str(self.id)
    #         }
    #     )
    #     self.txs = tx
    #     self.save()
        
    #     return tx

    @transaction.atomic
    def create_salary_logs(self, user=None):
        """Crée les bulletins de paie pour chaque employé inclus dans cette fiche de paie."""

        if not self.status == PayslipStatus.CONFIRMED:
            raise ValueError("Les bulletins de paie ne peuvent être générés que pour une fiche en révision ou confirmée.")

        salary_logs: list[SalaryLog] = []

        employees = self.employees.prefetch_related(
            Prefetch(
                "salaries",
                queryset=Salary.objects.filter(is_active=True),
                to_attr="active_salaries"
            )
        )

        for employee in employees:
            salary = employee.active_salaries[0] if employee.active_salaries else None
            
            if not salary:
                continue  # L'employé n'a pas de contrat actif


            # check active salary 
            if not salary.contract_type == ContractType.CDI and salary.end_date < self.start_date:
                continue

            # if not (self.start_date <= payment_state.next_payment_date <= self.end_date):
            #     continue

            salary_log = SalaryLog(
                salary=salary,
                payslip=self,
                start_date=self.start_date,
                end_date=self.end_date,
                total_payment=0,
                is_paid=False
            )
            salary_logs.append(salary_log)

        SalaryLog.objects.bulk_create(salary_logs)

        total_amount = 0
        for salary_log in salary_logs:
            salary_log.compute_salary()
            total_amount += salary_log.total_payment

        if total_amount == 0:
            raise ValidationError("Le montant total des bulletins de paie est de 0.")
        
        tx = self.create_transaction(total_amount, user)

        return salary_logs, tx


    def get_period_days(self):
        """Retourne le nombre de jours correspondant à la période de paiement."""
        periods = {
            PaymentPeriod.MONTHLY: 30,
            PaymentPeriod.DAILY: 1,
            PaymentPeriod.PER_TASK: 1
        }
        return periods.get(self.payment_period, 30)  # Par défaut, 30 jours

    def notify_payment(self):
        """Envoie une notification aux employés une fois la fiche de paie payée."""
        # Ici, tu peux utiliser un système de notification (email, webhook, etc.)
        for employee in self.employees.all():
            print(f"Notification envoyée à {employee.email} pour la paie du {self.start_date} - {self.end_date}")


    # def create_entry(self, description: str):
    #     je_model = lazy_loader.get_journal_entry_model()
    #     jentry = je_model(
    #         ledger = self.ledger,
    #         posted = False,
    #         description = description,
    #         timestamp = timezone.now(),
    #         locked=False
    #     )
    #     jentry.save(verify=False)
    #     return jentry
    
    # @transaction.atomic
    # def transaction_recorded(self):
    #     if self.ledger:
    #         return
        
    #     if not self.txs or not self.txs.account:
    #         raise ValidationError("La fiche de paie doit être liée un bordereau configuré.")
        
    #     # create ledger
    #     ledger_model = lazy_loader.get_ledger_model()
    #     ledger = ledger_model(
    #         name = f"Paie ({self.code}) ({self.start_date} - {self.end_date})",
    #     )
    #     ledger.configure_for_wrapper_model(model_instance=self.txs)
    #     ledger.clean()
    #     ledger.clean_fields()
    #     self.ledger = ledger
        
    #     self.ledger.save()

    #     self.save(
    #         update_fields=['ledger', 'updated_at']
    #     )

    #     account_model = lazy_loader.get_account_model()
    #     txs_model = lazy_loader.get_txs_model()

    #     salary_charges_accounts = account_model.objects.get(code="661")
    #     # bonus_charges_accounts = account_model.objects.get(code="6617")

    #     # cash account bank or cash account
    #     cash_account = self.txs.account.cash_account
    #     personnal_dues_account = account_model.objects.get(code="422")

    #     # amounts
    #     total_contributions_amount = self.employees.aggregate(
    #         total=models.Sum("salaries__salary_logs__total_contributions")
    #     )["total"] or 0
    #     # total_bonus_amount = self.employees.aggregate(
    #     #     total=models.Sum("salaries__salary_logs__total_bonus")
    #     # )["total"] or 0
    #     brut_charges_amount = self.txs.amount + total_contributions_amount

    #     social_charges_accounts = None
    #     if total_contributions_amount > 0:
    #         social_charges_accounts = account_model.objects.get(code="6641")


    #     bulk_txs = []

    #     # create journal entry for payslip record
    #     je_init = self.create_entry(
    #         "La paie de la fiche {} ({})".format(self.code, self.start_date)
    #     )

    #     bulk_txs += [
    #         txs_model(
    #             journal_entry = je_init,
    #             tx_type = txs_model.CREDIT,
    #             account = personnal_dues_account,
    #             amount = self.txs.amount,
    #             description = "Net à payer"
    #         ),
    #         txs_model(
    #             journal_entry = je_init,
    #             tx_type = txs_model.DEBIT,
    #             account = salary_charges_accounts,
    #             amount = brut_charges_amount,
    #             description = "Salaire brut du personnel"
    #         )
    #     ]

    #     if social_charges_accounts:
    #         bulk_txs += [
    #             txs_model(
    #                 journal_entry = je_init,
    #                 tx_type = txs_model.CREDIT,
    #                 account = social_charges_accounts,
    #                 amount = total_contributions_amount,
    #                 description = "Dettes sociales - Cotisations salariales"
    #             ),
    #         ]

    #     # create journal entry for net salary
    #     je_net = self.create_entry(
    #         "Salaires nets des employés. Fiche {} ({})".format(self.code, self.start_date)
    #     )

    #     bulk_txs += [
    #         txs_model(
    #             journal_entry = je_net,
    #             tx_type = txs_model.DEBIT,
    #             account = personnal_dues_account,
    #             amount = self.txs.amount,
    #             description = "Paiement des salaires nets"
    #         ),
    #         txs_model(
    #             journal_entry = je_net,
    #             tx_type = txs_model.CREDIT,
    #             account = cash_account,
    #             amount = self.txs.amount,
    #             description = "Paiement des salaires nets"
    #         ),
    #     ]

    #     if social_charges_accounts:
    #         # create journal entry for tax and social contributions
    #         je_tax = self.create_entry(
    #             "Cotisations et impôts. Fiche {} ({})".format(self.code, self.start_date)
    #         )

    #         bulk_txs += [
    #             txs_model(
    #                 journal_entry = je_tax,
    #                 tx_type = txs_model.DEBIT,
    #                 account = social_charges_accounts,
    #                 amount = total_contributions_amount,
    #                 description = "Dettes sociales - Cotisations salariales"
    #             ),
    #             txs_model(
    #                 journal_entry = je_tax,
    #                 tx_type = txs_model.CREDIT,
    #                 account = cash_account,
    #                 amount = self.txs.amount,
    #                 description = "Paiement des salaires nets"
    #             ),
    #         ]

    #     txs_model.objects.bulk_create(bulk_txs)
    #     self.mark_as_paid(commit=True)


    def save(self, *args, **kwargs):
        """Ajoute automatiquement les employés éligibles"""

        if not self.code:
            self.code = f"FICHE-{uuid.uuid4().hex[:8].upper()}"
        
        super().save(*args, **kwargs)


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

