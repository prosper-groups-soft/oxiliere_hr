"""
Middleware to add TokenTenant to request for Basic Auth compatibility.
This allows IsTenantAdmin permission to work with BasicNoPasswordAuth.
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from django.contrib.auth import get_user_model
import base64
import logging

logger = logging.getLogger(__name__)


def get_user_from_basic_auth(request):
    """Extract user from Basic Auth header if present"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Basic '):
        return None
    
    try:
        # Decode credentials
        encoded = auth_header[6:]  # Remove 'Basic '
        decoded = base64.b64decode(encoded).decode('utf-8')
        email, _ = decoded.split(':', 1)  # password is ignored for BasicNoPasswordAuth
        
        # Get user by email
        User = get_user_model()
        user = User.objects.get(email=email)
        return user
    except Exception as e:
        logger.debug(f"Could not extract user from Basic Auth: {e}")
        return None


class TokenTenantMiddleware(MiddlewareMixin):
    """
    Middleware that ensures request.tenant is a TokenTenant instance
    for authenticated requests. This is needed for BasicAuth to work
    with tenant-based permissions like IsTenantAdmin.
    """

    def process_request(self, request: HttpRequest):
        # Get user - either from Django auth or Basic Auth header
        user = None
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            user = request.user
        else:
            # Try to get user from Basic Auth header (for API requests)
            user = get_user_from_basic_auth(request)
            if user:
                # Set it on request so permissions can use it
                request.user = user
        
        # If request already has a tenant that's a TokenTenant, check if it's valid for current user
        if hasattr(request, 'tenant'):
            try:
                from oxutils.jwt.models import TokenTenant
                if isinstance(request.tenant, TokenTenant):
                    # Check if current TokenTenant matches the authenticated user
                    current_token_user = getattr(request.tenant, 'user', None)
                    if user and current_token_user and str(current_token_user.id) == str(user.id):
                        return
                    elif not user and not current_token_user:
                        return
                    # Otherwise recreate TokenTenant for the current user
            except ImportError:
                pass

        # Get the current tenant from the request (set by TenantMainMiddleware)
        # Note: request.tenant might already be a TokenTenant from previous request
        # We need to get the real Tenant model from DB
        tenant_obj = getattr(request, 'tenant', None)
        if not tenant_obj:
            logger.warning('TokenTenantMiddleware: No tenant found in request')
            return
        
        # If request.tenant is already a TokenTenant, get the real Tenant from DB
        try:
            from oxutils.jwt.models import TokenTenant
            if isinstance(tenant_obj, TokenTenant):
                # Get real tenant from DB using schema_name
                from core.models import Tenant
                tenant = Tenant.objects.get(schema_name=tenant_obj.schema_name)
            else:
                tenant = tenant_obj
        except Exception:
            tenant = tenant_obj

        # Create a TokenTenant from the current tenant
        try:
            from oxutils.jwt.models import TokenTenant, TenantUser as TokenTenantUser
            from core.models import TenantUser
            
            # Get the tenant user info
            try:
                tenant_user = TenantUser.objects.get(user=user, tenant=tenant)
                token_user = TokenTenantUser(
                    oxi_id=user.oxi_id if hasattr(user, 'oxi_id') else str(user.id),
                    id=str(user.id),
                    is_owner=tenant_user.is_owner,
                    is_admin=tenant_user.is_admin,
                    status='active' if tenant_user.is_active else 'inactive'
                )
            except TenantUser.DoesNotExist:
                token_user = None
            
            # Create TokenTenant with ALL required fields including schema_name
            token_tenant = TokenTenant(
                schema_name=tenant.schema_name,
                tenant_id=str(tenant.id),
                oxi_id=tenant.oxi_id,
                subscription_plan=getattr(tenant, 'subscription_plan', None) or '',
                subscription_status=getattr(tenant, 'subscription_status', None) or '',
                subscription_end_date=getattr(tenant, 'subscription_end_date', None),
                status=getattr(tenant, 'status', 'active'),
                user=token_user
            )
            
            request.tenant = token_tenant
            if user:
                logger.debug(f'TokenTenantMiddleware: Set TokenTenant for user {user.email} (admin={token_tenant.is_admin_user})')
        except ImportError:
            logger.error('TokenTenantMiddleware: Could not import TokenTenant')
        except Exception as e:
            logger.error(f'TokenTenantMiddleware: Error setting TokenTenant: {e}')

