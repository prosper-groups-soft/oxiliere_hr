from uuid import UUID
from ninja import Query
from ninja_extra import (
    api_controller,
    ControllerBase,
    http_get,
    http_post,
    http_patch,
    http_delete,
    paginate,
)
from ninja_extra.permissions import IsAuthenticated
from ninja_extra.pagination import (
    PageNumberPaginationExtra, 
    PaginatedResponseSchema
)
from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from hr.employees.schemas import (
    UserOut, 
    UserCreateIn, 
    UserUpdateIn,
    BaseFilter,
    UserFilter,
    SystemUserOut
)
from oxutils.permissions.models import UserGroup, Grant
from oxutils.permissions.perms import ScopePermission
from oxutils.permissions.utils import assign_group
from oxutils.oxiliere.utils import get_tenant_user_model
from django.shortcuts import get_object_or_404
            

User = get_user_model()
TenantUser = get_tenant_user_model()

@api_controller(
    '/account',
    tags=['User Management'],
    permissions=[IsAuthenticated & ScopePermission('access:r')]
)
class UserController(ControllerBase):
    """
    Controller for managing system users and their accounts.
    """

    @http_get('', response=PaginatedResponseSchema[SystemUserOut])
    @paginate(PageNumberPaginationExtra, page_size=20)
    def list_users(self, filters: UserFilter = Query(...)):
        """
        List all system users with their assigned group slugs.
        Returns data in SystemUser format for frontend compatibility.
        """
        queryset = User.objects.all().order_by('-date_joined')
        queryset = filters.filter(queryset)
        
        # Get TenantUser data for is_admin/is_owner lookup
        tenant_users = {tu.user_id: tu for tu in TenantUser.objects.all()}
                
        users_data = []
        for user in queryset:
            # Use UserGroup directly to avoid duplicates from multiple Grants per group
            groups = list(UserGroup.objects.filter(user_id=user.id)
                          .values_list('group__slug', flat=True).distinct())
            
            # Get tenant user data if exists
            tu = tenant_users.get(user.id)
            is_admin = tu.is_admin if tu else False
            is_owner = tu.is_owner if tu else False
            tenant_id = tu.id if tu else user.id
            
            # Build nested user object
            user_data = {
                "id": user.id,
                "oxi_id": user.id,  # Same as id for now
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "photo": None,
                "groups": groups
            }
                  
            users_data.append({
                "id": tenant_id,
                "user": user_data,
                "is_admin": is_admin,
                "is_owner": is_owner,
                "status": "active" if user.is_active else "inactive",
                "is_active": user.is_active,
                "first_name": user.first_name,  # For convenience
                "last_name": user.last_name
            })
            
        return users_data

    @http_post('', response={201: UserOut}, permissions=[IsAuthenticated & ScopePermission('access:w')])
    @transaction.atomic
    def create_user(self, data: UserCreateIn):
        """
        Create a new system user and assign initial groups.
        """
        # Default password logic: first_name (lowercase) + @oxiliere
        password = data.password or f"{data.first_name.lower()}@oxiliere"
        
        user = User.objects.create_user(
            email=data.email,
            username=data.email,
            password=password,
            first_name=data.first_name,
            last_name=data.last_name,
            is_active=data.is_active
        )

        if data.groups:
            for group_slug in data.groups:
                try:
                    assign_group(user, group_slug)
                except Exception:
                    pass

        # Return with groups
        return 201, self.get_user(user.id)

    @http_get('/{user_id}', response=UserOut)
    def get_user(self, user_id: UUID):
        """
        Get details for a specific user including groups.
        """
        user = get_object_or_404(User, id=user_id)
        # Use UserGroup directly to avoid duplicates from multiple Grants per group
        groups = list(UserGroup.objects.filter(user_id=user.id)
                      .values_list('group__slug', flat=True).distinct())
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "groups": groups
        }

    @http_patch('/{user_id}', response=UserOut, permissions=[IsAuthenticated & ScopePermission('access:w')])
    @transaction.atomic
    def update_user(self, user_id: UUID, data: UserUpdateIn):
        """
        Update user profile and synchronize permission groups.
        """
        user = get_object_or_404(User, id=user_id)
        
        # Update basic info
        if data.first_name is not None: user.first_name = data.first_name
        if data.last_name is not None: user.last_name = data.last_name
        if data.email is not None:
            user.email = data.email
            user.username = data.email
        if data.is_active is not None: user.is_active = data.is_active
        
        user.save()

        # Sync groups if provided
        if data.groups is not None:
            # Clear existing groups
            Grant.objects.filter(user_id=user.id, user_group__isnull=False).delete()
            
            # Assign new ones
            for group_slug in data.groups:
                try:
                    assign_group(user, group_slug)
                except Exception:
                    pass 
        
        return self.get_user(user.id)

    @http_delete('/{user_id}', response={204: None}, permissions=[IsAuthenticated & ScopePermission('access:d')])
    def delete_user(self, user_id: UUID):
        """
        Delete a user account.
        """
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return 204, None
