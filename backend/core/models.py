from django_tenants.models import DomainMixin
from oxutils.oxiliere.models import BaseTenant, BaseTenantUser




class Tenant(BaseTenant):
    pass


class TenantUser(BaseTenantUser):
    pass


class Domain(DomainMixin):
    pass

