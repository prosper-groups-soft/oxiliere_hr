from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db import transaction
from hr.models.enums import DegreeEnum, EmployeeStatus, GenderStatus, MaritalStatus, RelationshipType
from hr.utils import get_matricule_seq_key
from sequences import get_next_value
from utils_mixins.fn import create_unset_address
from utils_mixins.models import AddressMixin, BaseModelMixin
from core.models import ApplicationSettings





class EmployeeAddress(AddressMixin):
    pass


class Employee(BaseModelMixin):
    joined_date = models.DateTimeField(default=timezone.now)
    department = models.ForeignKey(
        "hr.Department",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="employee",
    )
    position = models.ForeignKey(
        "hr.Position",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="employee",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user",
        null=True,
    )

    first_name = models.CharField(
        max_length=75,
        verbose_name="Nom du Patient"
    )
    middle_name = models.CharField(
        max_length=75,
        verbose_name="Nom du Patient"
    )
    last_name = models.CharField(
        max_length=75, 
        verbose_name="Postnom du Patient"
    )
    matricule = models.CharField(
        max_length=16, unique=True,
        verbose_name="Matricule (automatique)",
    )
    
    email = models.EmailField(
        verbose_name="Adresse email", null=True, blank=True, unique=True
    )
    phone = models.CharField(
        max_length=13,  unique=True, null=True,
        verbose_name="Numero telephone",
    )

    gender = models.CharField(
        max_length=1,
        verbose_name='Sexe',
        choices=[
            (GenderStatus.MALE.value, 'Masculin'),
            (GenderStatus.FEMALE.value, 'Feminin'),
        ],
        default=GenderStatus.MALE
    )
    birthdate = models.DateField(verbose_name="Date de naissance")
    address = models.OneToOneField(
        EmployeeAddress, 
        on_delete=models.RESTRICT
    )
    is_active = models.BooleanField(default=True, verbose_name="Etat")
    marital_status = models.CharField(
        max_length=1, 
        choices=[
            (MaritalStatus.SINGLE.value, 'Single'),
            (MaritalStatus.MARRIED.value, 'Married'),
            (MaritalStatus.DIVORCED.value, 'Divorced'),
            (MaritalStatus.WIDOW.value, 'Widow'),
        ], 
        default=MaritalStatus.SINGLE, 
        verbose_name="Etat matrimonial"
    )
    status = models.CharField(
        max_length=2,
        choices=[
            (EmployeeStatus.PERMANENT_WORKER.value, 'Permanent Worker'),
            (EmployeeStatus.LABOR_TECHNICIAN.value, 'Labor Technician'),
            (EmployeeStatus.LABOR_WORKER.value, 'Labor Worker'),
        ],
        default=EmployeeStatus.PERMANENT_WORKER
    )
    photo = models.ImageField(
        upload_to="images/",
        default="images/user-dummy-img.jpg",
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    can_connect = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["last_name", "first_name"]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.matricule})"
    
    @staticmethod
    def create_employee(first_name, last_name, gender, status):
        addr = create_unset_address(created_by, model=EmployeeAddress)
        return Employee.objects.create(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            status=status,
            is_active=True,
            phone=None,
            marital_status=MaritalStatus.SINGLE,
            can_connect=False,
            birthdate=timezone.now(),
            address=addr,
        )
        

    def clean(self):
        # Formatage des noms pour standardiser la casse
        if self.first_name:
            self.first_name = self.first_name.strip().title()
        if self.middle_name:
            self.middle_name = self.middle_name.strip().title()
        if self.last_name:
            self.last_name = self.last_name.strip().title()
        if self.email:
            self.email = self.email.strip().lower()

        if not self.matricule:
            app_settings = ApplicationSettings.get_instance()

            year = timezone.now().year
            number = get_next_value(
                get_matricule_seq_key()
            )
            self.matricule = f"{app_settings.company_prefix}-{year}-{number:05d}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        return self
    

class EmergencyContact(AuditModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="emergency_contact",
    )
    first_name = models.CharField(
        max_length=75,
        verbose_name="Nom du contact"
    )
    last_name = models.CharField(
        max_length=75, 
        verbose_name="Postnom du contact"
    )
    phone = models.CharField(
        max_length=13,  unique=True, blank=True,
        verbose_name="Numero telephone",
    )
    relation = models.CharField(
        max_length=2,
        verbose_name='Relation',
        choices=[
            (RelationshipType.PARENT.value, 'Parent'),
            (RelationshipType.CHILD.value, 'Child'),
            (RelationshipType.SIBLING.value, 'Sibling'),
            (RelationshipType.FRIEND.value, 'Friend'),
            (RelationshipType.WIFE.value, 'Wife'),
            (RelationshipType.OTHER.value, 'Other'),
        ],
        default=RelationshipType.OTHER
    )
    priority = models.IntegerField(
        default=1,
        verbose_name="Priorité",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ]
    )
    
    class Meta:
        ordering = ["priority", "last_name"]


    def clean(self):
        # Formatage des noms pour standardiser la casse
        if self.first_name:
            self.first_name = self.first_name.strip().title()
        if self.last_name:
            self.last_name = self.last_name.strip().title()

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)



class Childreen(BaseModelMixin):
    parent = models.ForeignKey(
        "hr.Employee",
        on_delete=models.CASCADE,
        related_name="childreen",
    )

    first_name = models.CharField(
        max_length=75,
        verbose_name="Nom de l'enfant"
    )
    last_name = models.CharField(
        max_length=75, 
        verbose_name="Postnom de l'enfant"
    )

    gender = models.CharField(
        choices=GenderStatus.choices,
        max_length=1,
    )
    birthdate = models.DateField()
    
    class Meta:
        ordering = ["first_name", "-birthdate"]

    
    def clean(self):
        # Formatage des noms pour standardiser la casse
        if self.first_name:
            self.first_name = self.first_name.strip().title()
        if self.last_name:
            self.last_name = self.last_name.strip().title()


    @transaction.atomic
    def save(self, *args, **kwargs):
        self.clearn()
        return super().save(*args, **kwargs)


class Education(AuditModel):
    DEGREE_CHOICES = (
        (DegreeEnum.BREVET, 'Brevet'),
        (DegreeEnum.DIMPLOMA, 'Diplôme'),
        (DegreeEnum.LICENSE, 'Licence'),
        (DegreeEnum.MASTER, 'Master'),
        (DegreeEnum.PHD, 'Doctorat')
    )
    employee = models.ForeignKey(
        "hr.Employee",
        on_delete=models.CASCADE,
        related_name="education",
    )
    institute = models.CharField(max_length=255)
    degree = models.CharField(
        max_length=1,
        choices=DEGREE_CHOICES,
    )
    major = models.CharField(max_length=255)
    start_year = models.DateField()
    end_year = models.DateField()
    location = models.CharField(max_length=255)

    class Meta:
        ordering = ["-end_year", "degree"]

    @transaction.atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
