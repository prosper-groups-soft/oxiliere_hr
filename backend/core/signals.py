from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save


try:
    from cacheops import invalidate_model
    HAS_CACHEOPS = True
except ImportError:
    HAS_CACHEOPS = False


ADMIN_GROUP_SLUG = 'admins'
ADMIN_ROLE_SLUG = 'admin'


def _prevent_last_tenant_user_role(instance, field_name: str, display_name: str):
    """
    Empêche la désactivation du dernier utilisateur dans un tenant ayant le rôle donné.
    """
    # Ne rien faire si le champ est toujours à True
    if getattr(instance, field_name):
        return

    # Si on essaie de le passer à False, on vérifie s'il reste d'autres utilisateurs avec ce rôle
    klass = type(instance)
    query = {"tenant": instance.tenant, field_name: True, "is_active": True}
    count = klass.objects.filter(**query).exclude(id=instance.id).count()
    
    if count == 0:
        raise ValidationError(f"Action interdite : Il s'agit du dernier {display_name} actif pour ce tenant.")


# 1. Signaux sur TenantUser (core)
@receiver(pre_save, sender='core.TenantUser')
def guard_tenant_user_roles(sender, instance, **kwargs):
    # En création pure, pas de suppression de rôle
    if instance._state.adding:
        return

    try:
        old_instance = sender.objects.get(id=instance.id)
    except sender.DoesNotExist:
        return

    # S'il était owner et qu'il ne l'est plus
    if old_instance.is_owner and not instance.is_owner:
        _prevent_last_tenant_user_role(instance, 'is_owner', 'Propriétaire (Owner)')
        
    # S'il était admin et qu'il ne l'est plus
    if old_instance.is_admin and not instance.is_admin:
        _prevent_last_tenant_user_role(instance, 'is_admin', 'Administrateur')

    # S'il était actif et est désactivé manuellement, on vérifie ses rôles
    if old_instance.is_active and not instance.is_active:
        if old_instance.is_owner:
            instance.is_owner = False
            _prevent_last_tenant_user_role(instance, 'is_owner', 'Propriétaire (Owner)')
        if old_instance.is_admin:
            instance.is_admin = False
            _prevent_last_tenant_user_role(instance, 'is_admin', 'Administrateur')


@receiver(pre_delete, sender='core.TenantUser')
def guard_tenant_user_delete(sender, instance, **kwargs):
    # C'est la même contrainte, un delete équivaut à tout passer à False
    if instance.is_owner:
        instance.is_owner = False
        _prevent_last_tenant_user_role(instance, 'is_owner', 'Propriétaire (Owner)')
    if instance.is_admin:
        instance.is_admin = False
        _prevent_last_tenant_user_role(instance, 'is_admin', 'Administrateur')


# 2. Signaux sur oxutils.permissions (UserGroup et Grant)
@receiver(pre_delete, sender='permissions.UserGroup')
def guard_last_admin_group(sender, instance, **kwargs):
    """
    On empêche la suppression de la liaison entre un utilisateur et le groupe 'admins'
    si c'est le dernier admin.
    """
    if instance.group.slug == ADMIN_GROUP_SLUG:
        admin_count = sender.objects.filter(
            group__slug=ADMIN_GROUP_SLUG, 
            user__is_active=True
        ).exclude(id=instance.id).count()
        
        if admin_count == 0:
            raise ValidationError(f"Action interdite : Il s'agit du dernier administrateur dans le groupe '{ADMIN_GROUP_SLUG}'.")


@receiver(pre_delete, sender='permissions.Grant')
def guard_last_admin_role_grant(sender, instance, **kwargs):
    """
    Empêche qu'on supprime un Grant explicite du rôle 'admin' s'il n'y en a plus d'autres.
    """
    if instance.role.slug == ADMIN_ROLE_SLUG:
        grant_count = sender.objects.filter(
            role__slug=ADMIN_ROLE_SLUG, 
            user__is_active=True
        ).exclude(id=instance.id).count()
        
        if grant_count == 0:
            raise ValidationError(f"Action interdite : Il s'agit de la dernière attribution active du rôle '{ADMIN_ROLE_SLUG}'.")


@receiver(post_save, sender=get_user_model())
def invalidate_user_group_cache_on_user_save(sender, instance, **kwargs):
    """
    Lorsque le profil (User) est formellement mis à jour (nom, prénom...),
    son modèle enfant (UserGroup) conservé en cache par cacheops via des select_related
    peut se retrouver désynchronisé. On invalide donc le cache manuellement.
    """
    if HAS_CACHEOPS:
        from oxutils.permissions.models import UserGroup
        invalidate_model(UserGroup)
