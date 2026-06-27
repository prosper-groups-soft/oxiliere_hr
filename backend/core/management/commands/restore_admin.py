"""
Restore dev@oxiliere.com to admins group.
Run: python manage.py restore_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import TenantUser


User = get_user_model()


class Command(BaseCommand):
    help = "Restore dev@oxiliere.com to admins group"

    def handle(self, *args, **options):
        try:
            # Get the user
            user = User.objects.get(email='dev@oxiliere.com')
            self.stdout.write(f"Found user: {user.email} (ID: {user.id})")
            
            # Get the tenant user
            tenant_user = TenantUser.objects.get(user=user)
            self.stdout.write(f"Found tenant user: {tenant_user}")
            
            # Check current state
            self.stdout.write(f"is_admin: {tenant_user.is_admin}")
            self.stdout.write(f"is_owner: {tenant_user.is_owner}")
            
            # Restore admin access
            if not tenant_user.is_admin:
                tenant_user.is_admin = True
                tenant_user.save()
                self.stdout.write(self.style.SUCCESS("✓ Restored is_admin = True"))
            else:
                self.stdout.write("User already has is_admin = True")
            
            if not tenant_user.is_owner:
                tenant_user.is_owner = True
                tenant_user.save()
                self.stdout.write(self.style.SUCCESS("✓ Restored is_owner = True"))
            else:
                self.stdout.write("User already has is_owner = True")
            
            # Ensure user is in admins group using PermissionService directly
            from oxutils.permissions.services import PermissionService
            from oxutils.permissions.utils import group_sync
            service = PermissionService()
            
            # Assign user to admins group (ignore if already assigned)
            try:
                service.assign_group_to_user(
                    user_id=user.id,
                    group_slug='admins',
                    by_user=user
                )
                self.stdout.write(self.style.SUCCESS("✓ User assigned to 'admins' group"))
            except Exception as e:
                self.stdout.write(f"Note: {e}")
            
            # Synchronize grants for all users in this group (always run)
            self.stdout.write("Synchronizing grants...")
            result = group_sync('admins')
            self.stdout.write(self.style.SUCCESS(
                f"✓ Grants synchronized: {result['grants_updated']} grants updated for {result['users_synced']} users"
            ))
            
            self.stdout.write(self.style.SUCCESS("\n✅ Admin access restored successfully!"))
            self.stdout.write("You can now log in again with dev@oxiliere.com")
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User dev@oxiliere.com not found!"))
        except TenantUser.DoesNotExist:
            self.stdout.write(self.style.ERROR("TenantUser for dev@oxiliere.com not found!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

