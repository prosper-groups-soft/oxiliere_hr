from datetime import timedelta, datetime
from typing import override
import uuid
import random
import string
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError
from hr.models.enums import AttendanceStatus, CalendarEventType, LeaveType
from hr.managers import AttendanceManager
from hr.models.employees import Employee

from utils_mixins.models import SingletonMxin, BaseModelMixin
from django.utils.translation import gettext_lazy as _
from hr.constants import WEEKDAYS




class Schedule(BaseModelMixin):
    opened_at = models.TimeField()
    closed_at = models.TimeField()
    is_open = models.BooleanField(
        default=True
    )
    weekday = models.CharField(
        max_length=15, 
        verbose_name="Jour de la semaine",
        unique=True
    )

    hours = models.DurationField(
        default=timedelta(0),
        editable=False
    )
    
    class Meta:
        ordering = ["weekday"]


    def update_hours(self):
        self.hours = timedelta(hours=self.get_total_hours())

    def get_total_hours(self):
        return (timezone.datetime.combine(timezone.now(), self.closed_at) - 
                    timezone.datetime.combine(timezone.now(), self.opened_at)).total_seconds() / 3600

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.hours = timedelta(hours=self.get_total_hours())
        return super().save(*args, **kwargs)


class Attendance(BaseModelMixin):
    name = models.CharField(max_length=255)
    date = models.DateField(
        verbose_name="Date",
        unique=True
    )
    code = models.CharField(max_length=100, unique=True)
    closed = models.BooleanField(default=False)
    computed = models.BooleanField(default=False)

    objects = AttendanceManager()
    
    class Meta:
        ordering = ["-date"]

    @override
    def clean(self):
        # Check if the date is not in a closed period
        closed_period = ClosingAttendance.objects.filter(date__gte=self.date).exists()
        if closed_period:
            raise ValidationError(
                _("Impossible de créer ou de modifier une fiche de présence pour une période fermée.")
            )
        return super().clean()

    def generate_code(self):
        date_part = datetime.now().strftime("%d%m%y")  # Format DDMMYY
        random_part = ''.join(random.choices(string.ascii_letters, k=6))  # 6 lettres aléatoires
        return f"{date_part}-{random_part}"


    def save(self, *args, **kwargs) -> None:
        self.clean()
        if self._state.adding:
            self.name = f"{self.date} - {self.get_weekday(self.date.strftime('%A'))}"
            self.code = self.generate_code()
        return super().save(*args, **kwargs)
    

    def get_weekday(self, d):
        if d in WEEKDAYS:
            return WEEKDAYS[d]
        return d
    

    @transaction.atomic
    def close(self):
        """
        Ferme la fiche de présence en générant des entrées d'absence pour les employés 
        sans enregistrement.
        """
        self.clean()

        employees = Employee.objects.all()

        existing_entries = self.entries.values_list('employee_id', flat=True)

        missing_employees = employees.exclude(id__in=existing_entries)

        entries_to_create = []

        for employee in missing_employees:
            
            on_leave = Leave.objects.filter(
                applicable_to=employee,
                approved=True,
                start_date__lte=self.date,
                end_date__gte=self.date
            ).exists()

            if not on_leave:
                entry = AttendanceEntry(
                    employee=employee,
                    attendance=self,
                    status=AttendanceStatus.ABSENT,
                    check_in_time="00:00:00",
                    check_out_time=None,
                    total_hours=timedelta(0),
                    overtime=timedelta(0),
                    undertime=timedelta(0),
                    created_by=self.created_by,
                    updated_by=self.updated_by
                )
                entries_to_create.append(entry)

        AttendanceEntry.objects.bulk_create(entries_to_create)

        self.closed = True
        self.save(update_fields=['closed'])


    class Meta:
        verbose_name = "Fiche de presence"
        verbose_name_plural = "Fiches de presences"
        ordering = ['-date']



class AttendanceEntry(BaseModelMixin):
    _settings = None # Local cache for attendance Settings

    manual = models.BooleanField(default=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances")
    check_in_time = models.TimeField(verbose_name="Heure d'arrivée")
    check_out_time = models.TimeField(null=True, blank=True, verbose_name="Heure de départ")
    total_hours = models.DurationField(
        default=timedelta(minutes=0),
        blank=True,
        verbose_name="Total d'heures"
    )
    leave = models.ForeignKey(
        'hr.Leave',
        on_delete=models.DO_NOTHING, null=True,
        blank=True, verbose_name="Congé",
        related_name="attendances"
    )
    attendance = models.ForeignKey(
        'hr.Attendance',
        on_delete=models.CASCADE, verbose_name="Fiche de presence",
        related_name="entries"
    )
    overtime = models.DurationField(
        default=timedelta(minutes=0), 
        blank=True, 
        verbose_name="Heures suplementaires"
    )
    undertime = models.DurationField(
        default=timedelta(minutes=0), 
        blank=True, 
        verbose_name="Heures manquantes"
    )
    status = models.CharField(
        max_length=1, 
        choices=AttendanceStatus.choices, 
        default=AttendanceStatus.PRESENT, 
        verbose_name="Statut"
    )

    
    class Meta:
        unique_together = ['employee', 'attendance']
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        ordering = ['-attendance__date']
        indexes = [
            models.Index(fields=['employee', 'attendance']),
            models.Index(fields=['employee', 'attendance', 'status']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.date} : {self.get_status_display()}"


    @property
    def is_late(self):
        if self.is_employee_on_leave():
            return False
        
        schedule = self.get_scheduled_time()

        if not schedule:
            return False
        
        if not schedule.is_open:
            return False
        
        today = datetime.today().date()
        opened_at_datetime = datetime.combine(today, schedule.opened_at)
        late_allowed_time = opened_at_datetime + self.attendance_settings.late_acceptable
        check_in_datetime = datetime.combine(today, self.check_in_time)
        return check_in_datetime > late_allowed_time


    def get_scheduled_time(self) -> Schedule | None:
        from hr.caches import get_schedules
        schedules = get_schedules()
        for schedule in schedules:
            weekday = WEEKDAYS[self.attendance.date.strftime("%A")]
            if schedule.weekday == weekday:
                return schedule
        return None
    

    @property
    def attendance_settings(self):
        if not self._settings:
            from hr.caches import get_attendance_settings
            self._settings = get_attendance_settings()
        return self._settings


    def get_overtime(self):
        total = self.get_total_hours()
        schedule = self.get_scheduled_time()
        return timedelta(hours=total) - schedule.hours
    

    @property
    def is_present(self):
        "Return True if the employee is present"
        return self.status == "P"

    @property
    def is_excused(self):
        "Return True if the employee is excused"
        return self.status == "E"
    
    @property
    def is_absent(self):
        "Return True if the employee is absent"
        return self.status == "A"
    

    @property
    def is_payable(self):
        "Return True if the employee is payable"
        return not self.is_absent
    

    def is_employee_on_leave(self):
        
        return Leave.objects.filter(
            applicable_to=self.employee,
            approved=True,
            start_date__lte=self.attendance.date,
            end_date__gte=self.attendance.date
        ).exists()
    

    def get_total_hours(self):
        if self.check_in_time and self.check_out_time:
            return (timezone.datetime.combine(timezone.now(), self.check_out_time) - 
                    timezone.datetime.combine(timezone.now(), self.check_in_time)).total_seconds() / 3600
        return 0
    

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.clean()
        self.total_hours = timedelta(hours=self.get_total_hours())
        self.overtime = self.get_overtime()
        ts = self.overtime.total_seconds()
        self.undertime = timedelta(seconds=ts * -1) if ts < 1 else timedelta(seconds=0)

        if self.is_employee_on_leave():
            self.status = "H"

        elif self.is_late and not (self.is_absent or self.is_excused):
            self.status = "L"

        return super().save(*args, **kwargs)


    @override
    def clean(self):
        # Check if the attendance date is not in a closed period
        if self.attendance and self.attendance.date:
            closed_period = ClosingAttendance.objects.filter(date__gte=self.attendance.date).exists()
            if closed_period:
                raise ValidationError(
                    _("Impossible de créer ou de modifier une entrée de présence pour une période fermée.")
                )
        return super().clean()


class ClosingAttendance(BaseModelMixin):
    last_closing = models.ForeignKey(
        'self', on_delete=models.SET_NULL, 
        null=True, blank=True, editable=False,
        related_name="last_closings"
    )
    next_closing = models.ForeignKey(
        'self', on_delete=models.SET_NULL, 
        null=True, blank=True, editable=False,
        related_name="next_closings"
    )
    date = models.DateField()
    locked = models.BooleanField(
        default=False, editable=False,
        verbose_name="Verrouillé",
    )

    @override
    def clean(self):
        # Validate that date is not more than 3 hours in the future
        current_time = timezone.now()
        max_future_time = current_time + timedelta(hours=3)
        
        if self.date > max_future_time.date():
            raise ValidationError(
                _("La date de fermeture ne peut pas être plus de 3 heures dans le futur.")
            )
            
        # Validate locked field
        if self.locked:
            raise ValidationError(
                _("La fermeture est verrouillée.")
            )
        
        # Validate that the new closing date is after the last closing date
        if self.last_closing and self.date <= self.last_closing.date:
            raise ValidationError(
                _("La date de fermeture doit être postérieure à la dernière date de fermeture.")
            )
            
        return super().clean()
        
    @transaction.atomic
    def save(self, *args, **kwargs):
        # If adding a new record, set last_closing to the most recent closing
        if self._state.adding and not self.last_closing:
            latest_closing = ClosingAttendance.objects.first()
            if latest_closing:
                self.last_closing = latest_closing
        
        self.full_clean()
        if self._state.adding:
            from hr.caches import get_attendance_settings
            settings = get_attendance_settings()
            settings.last_closing = self
            settings.save(update_fields=['last_closing'])
        
        result = super().save(*args, **kwargs)

        if self.last_closing:
            self.last_closing.next_closing = self
            self.last_closing.save(update_fields=['next_closing'])
        
        return result


    @override
    def delete(self, using=None, keep_parents=False):
        from hr.caches import get_attendance_settings
        settings = get_attendance_settings()

        if settings.last_closing and settings.last_closing.date > self.date:
            raise ValidationError(
                _("La date de cette période de fermeture doit être postérieure à la dernière date de fermeture.")
            )
        settings.last_closing = self.last_closing
        settings.save(update_fields=['last_closing'])

        if self.next_closing:
            self.next_closing.last_closing = self.last_closing
            self.next_closing.save(update_fields=['last_closing'])
        
        return super().delete(using, keep_parents)

    class Meta:
        verbose_name = "Fermeture de la periode pour les presences"
        verbose_name_plural = "Fermetures de la periode pour les presences"
        constraints = [
            models.UniqueConstraint(
                fields=["date"],
                name="closing_attendance_unique_date"
            )
        ]
        indexes = [
            models.Index(fields=["date"])
        ]
        ordering = ['-date']



class AttendanceSettings(SingletonMxin):
    late_acceptable = models.DurationField(default=timedelta(minutes=15), verbose_name="Duree de retard acceptable")
    accept_late_count = models.IntegerField(default=3, verbose_name="Nombre de retard")
    acept_excuse_count  = models.IntegerField(default=3, verbose_name="Nombre d'excuse")
    work_sunday = models.BooleanField(default=False)
    work_saturday = models.BooleanField(default=False)
    last_closing = models.ForeignKey(ClosingAttendance, on_delete=models.SET_NULL, null=True, blank=True)
    total_working_time = models.DurationField(default=timedelta(hours=0), verbose_name="Duree de travail")
    
    class Meta(SingletonMxin.Meta):
        ordering = ["-id"]


class Leave(BaseModelMixin):
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    leave_type = models.CharField(
        max_length=2, 
        choices=LeaveType.choices, 
        verbose_name="Type de congé"
    )
    reason = models.TextField(null=True, blank=True, verbose_name="Raison")
    applicable_to = models.ManyToManyField(
        Employee,
        related_name="leaves",
        verbose_name="Applicable à",
        through="LeaveEmployee"
    )
    everyone = models.BooleanField(default=False, verbose_name="Tout le monde")
    approved = models.BooleanField(default=False, verbose_name="Approuvé")
    canceled = models.BooleanField(default=False, verbose_name="Annulé", editable=False)
    paid = models.BooleanField(default=False, verbose_name="Payé")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.DO_NOTHING,
        null=True, 
        related_name="approved_leaves",
        verbose_name="Approuve par"
    )

    def total_days(self):
        return (self.end_date - self.start_date).days
    

    def add_employees(self, employee_ids, created_by_user, check_on_everyone=True):
        if check_on_everyone:
            self.check_on_everyone()

        if employee_ids is None or len(employee_ids) == 0:
            return []
        
        existing_employee_ids = self.leaves_employee.values_list('employee__id', flat=True)
        new_employee_ids = [emp_id for emp_id in employee_ids if emp_id not in existing_employee_ids]
        new_employees = Employee.objects.filter(id__in=new_employee_ids)
        bonus_employee_instances = [
            LeaveEmployee(
                employee=employee,
                leave=self,
                created_by=created_by_user
            )
            for employee in new_employees
        ]
        
        LeaveEmployee.objects.bulk_create(bonus_employee_instances)
        return new_employee_ids
    

    def remove_employees(self, employee_ids, created_by_user, check_on_everyone=True):
        if check_on_everyone:
            self.check_on_everyone()

        if employee_ids is None or len(employee_ids) == 0:
            return []
        
        existing_employee_ids = self.leaves_employee.values_list('employee__id', flat=True)
        existed_ids = [emp_id for emp_id in employee_ids if emp_id in existing_employee_ids]
        self.leaves_employee.filter(employee__id__in=existed_ids).delete()
        return existed_ids
    
    def reset(self, created_by_user):
        self.everyone = False
        self.leaves_employee.all().delete()
        self.updated_by = created_by_user
        self.save(
            update_fields=['everyone', 'updated_by']
        )

    def approve(self, created_by_user):
        self.approved = True
        self.approved_by = created_by_user
        self.save(
            update_fields=['approved', 'approved_by']
        )

    def cancel(self, created_by_user):
        self.canceled = True
        self.updated_by = created_by_user
        self.save(
            update_fields=['canceled', 'updated_by']
        )
    
    def check_on_everyone(self):
        if self.everyone:
            raise ValidationError("Cet avantage est appliquer à tout le monde, vous ne pouvez pas ajouter des employés")
    

    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"
    
    def __str__(self):
        return f"{self.employee} - {self.get_leave_type_display()} ({self.start_date} à {self.end_date})"
    

    @transaction.atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class LeaveEmployee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="employee_leaves",
        verbose_name="Employé"
    )
    leave = models.ForeignKey(
        Leave,
        on_delete=models.CASCADE,
        related_name="leaves_employee",
        verbose_name="Congé"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name="Créé par"
    )
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.leave}"

    class Meta:
        unique_together = ['employee', 'leave']
        verbose_name = "Congé employé"
        verbose_name_plural = "Congés employés"


class CalendarEvent(BaseModelMixin):
    name = models.CharField(max_length=200, verbose_name="Nom de l'événement")
    date = models.DateField(verbose_name="Date de l'événement")
    event_type = models.CharField(
        max_length=50, 
        choices=CalendarEventType.choices, 
        default=CalendarEventType.OTHER, 
        verbose_name="Type d'événement"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Description de l'événement")
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Date et heure de début")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Date et heure de fin")
    comments = models.CharField(max_length=500, blank=True, null=True, verbose_name="Commentaires")
    code = models.CharField(max_length=100, unique=True, verbose_name="Code de l'événement")
    recurrent = models.BooleanField(default=False, verbose_name="Récurrent")
    status = models.CharField(max_length=100, verbose_name="Statut de l'événement")

    class Meta:
        verbose_name = "Événement du calendrier"
        verbose_name_plural = "Événements du calendrier"
        unique_together = ('name', 'date', 'event_type')

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()} - {self.date})"
    

    @transaction.atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class CalenderEventSettings(SingletonMxin):
    show_anniversary = models.BooleanField(default=False, verbose_name="Anniversaires")
    show_deadline = models.BooleanField(default=False, verbose_name="Démarrages")
    show_meeting = models.BooleanField(default=False, verbose_name="Meetings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.DO_NOTHING,
        null=True, 
        related_name="calender_event_settings",
        verbose_name="Mis à jour par"
    )


    @transaction.atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
