from uuid import UUID
from oxutils.oxiliere.schemas import (
    TenantUserListSchema as BaseTenantUserListSchema,
    TenantUserDetailSchema as BaseTenantUserDetailSchema
)


class TenantUserListSchema(BaseTenantUserListSchema):
    id: UUID


class TenantUserDetailSchema(BaseTenantUserDetailSchema):
    id: UUID

