from django.db import models
from utils_mixins.models import SingletonMxin
from math import radians, sin, cos, sqrt, atan2




class ApplicationSettings(SingletonMxin):
    company_prefix = models.CharField(max_length=4)


class WorkSite(SingletonModel):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    accepted_distance = models.FloatField(default=60)
    is_configured = models.BooleanField(default=False)

    number = models.CharField(max_length=5)
    street = models.CharField(max_length=75)
    municipality = models.CharField(max_length=75)
    city = models.CharField(max_length=75)
    province = models.CharField(max_length=75)
    country = models.CharField(max_length=75)
    country_code = models.CharField(max_length=3, verbose_name="Code Pays", default="cd")
    
    class Meta(SingletonModel.Meta):
        ordering = ["name"]


    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"

    def distance_to(self, lat2, lon2):
        """Calcule la distance en mètres entre ce point et un autre point (lat2, lon2)"""
        R = 6371000  # Rayon de la Terre en mètres
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(lat2), radians(lon2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c  # Distance en mètres

    def is_within_acceptable_distance(self, lat2, lon2):
        """Vérifie si un point est dans la distance acceptable"""
        return self.distance_to(lat2, lon2) <= self.accepted_distance
    

    def configure(self, commit=True):
        if self.latitude is None or self.longitude is None:
            raise ValidationError("Veillez définir les coordonnées géographiques.")
        
        self.is_configured = True

        if commit:
            self.save(
                update_fields=['is_configured',]
            )

    def save(self, *args, **kwargs):
        self.configure(commit=False)
        return super().save(*args, **kwargs)
