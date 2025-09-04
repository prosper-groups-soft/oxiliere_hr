from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from utils_mixins.models import TimestampMixin



class Tenant(TenantMixin, TimestampMixin):
    name = models.CharField(max_length=100)
    industry = models.CharField(max_length=255)
    oxi_id = models.UUIDField(editable=False, index=True)
    on_trial = models.BooleanField(default=False)

    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True



class Domain(DomainMixin):
    pass

