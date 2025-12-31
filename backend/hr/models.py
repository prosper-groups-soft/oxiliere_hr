from django.db import models
from oxutils.models import UserTrackingMixin, BaseModelMixin


class AddressMixin(UserTrackingMixin, BaseModelMixin):
    number = models.CharField(max_length=5, null=True, blank=True)
    street = models.CharField(max_length=75, null=True, blank=True)
    municipality = models.CharField(max_length=75, null=True, blank=True)
    city = models.CharField(max_length=75, null=True, blank=True)
    province = models.CharField(max_length=75, null=True, blank=True)
    country = models.CharField(max_length=75, null=True, blank=True)
    country_code = models.CharField(max_length=3, verbose_name="Code Pays", default="cd")

    class Meta:
        abstract = True
