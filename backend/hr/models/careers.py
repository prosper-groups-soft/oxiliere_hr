from django.db import models
from django.db import transaction


from utils_mixins.models import BaseModelMixin



class Position(BaseModelMixin):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        ordering = ["name"]


    def clean(self):
        self.name = self.name.strip().title()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)



class Department(BaseModelMixin):
    name = models.CharField(max_length=100)
    description = models.TextField()
    manager = models.ForeignKey(
        "hr.Employee",
        on_delete=models.SET_NULL,
        null=True,
        related_name="department_manager",
    )
    
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        self.name = self.name.strip().title()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)



class Training(BaseModelMixin):
    employee = models.ForeignKey(
        "hr.Employee",
        on_delete=models.CASCADE,
        related_name="training",
    )
    name = models.CharField(max_length=255)
    institute = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()
    location = models.CharField(max_length=255)
    
    class Meta:
        ordering = ["-start_date"]


    @transaction.atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class CarreerHistory(BaseModelMixin):
    employee = models.ForeignKey(
        "hr.Employee",
        on_delete=models.CASCADE,
        related_name="carreer_history",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        null=True,
        related_name="carreer_history",
    )
    position = models.ForeignKey(
        "hr.Position",
        on_delete=models.CASCADE,
        null=True,
        related_name="carreer_history",
    )
    department = models.ForeignKey(
        "hr.Department",
        on_delete=models.CASCADE,
        null=True,
        related_name="carreer_history",
    )
    start_date = models.DateField()
    end_date = models.DateField(
        null=True
    )
    description = models.TextField()
    
    class Meta:
        ordering = ["-start_date"]
