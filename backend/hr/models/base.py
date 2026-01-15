from django.db import models
from hr.enums import CountryCode
from django.utils.translation import gettext_lazy as _
from oxutils.models import (
    UserTrackingMixin, 
    BaseModelMixin, 
    SafeDeleteModelMixin
)
from uuid6 import uuid7
from hr.utils import get_country_codes


class BaseAuditableModel(BaseModelMixin, UserTrackingMixin, SafeDeleteModelMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid7,
        editable=False
    )
        
    class Meta:
        abstract = True
    

class AddressMixin(BaseAuditableModel):
    number = models.CharField(max_length=5, null=True, blank=True)
    street = models.CharField(max_length=75, null=True, blank=True)
    municipality = models.CharField(max_length=75, null=True, blank=True)
    city = models.CharField(max_length=75, null=True, blank=True)
    province = models.CharField(max_length=75, null=True, blank=True)
    country = models.CharField(max_length=75, null=True, blank=True)
    country_code = models.CharField(
        max_length=2,
        default=CountryCode.DRC,
        choices=get_country_codes(),
        help_text=_("ISO country code (e.g. CD, FR, BE)")
    )

    class Meta:
        abstract = True

