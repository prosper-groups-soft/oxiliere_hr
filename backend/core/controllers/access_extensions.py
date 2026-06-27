from ninja_extra import api_controller, ControllerBase, http_post
from django.conf import settings
from django.db import transaction
from oxutils.permissions.models import Role, RoleGrant
from oxutils.permissions.perms import access_manager
from ninja_extra.permissions import IsAuthenticated


@api_controller(
    "/access",
    permissions=[
        IsAuthenticated & access_manager('w')
    ],
    tags=["Access Extension"]
)
class AccessExtensionController(ControllerBase):
    """
    Contrôleur étendu pour les actions spécifiques d'administration des accès.
    """

    @http_post("/roles/{role_slug}/restore-defaults", response={204: None})
    @transaction.atomic
    def restore_role_defaults(self, role_slug: str):
        """
        Rétablit les permissions par défaut d'un rôle selon les presets du système.
        """
        # 1. Vérifier si le rôle existe
        try:
            role = Role.objects.get(slug=role_slug)
        except Role.DoesNotExist:
            return 404, {"message": f"Rôle '{role_slug}' introuvable."}

        # 2. Récupérer les presets
        presets = getattr(settings, 'PERMISSION_PRESET', {}).get('role_grants', [])
        role_presets = [p for p in presets if p.get('role') == role_slug]

        if not role_presets:
            # Si aucun preset n'est défini pour ce rôle, on peut décider de juste tout vider 
            # ou de renvoyer une erreur. Ici, on vide tout pour ce rôle.
            pass

        # 3. Supprimer les grants actuels
        RoleGrant.objects.filter(role=role).delete()

        # 4. Recréer les grants à partir des presets
        for p in role_presets:
            RoleGrant.objects.create(
                role=role,
                scope=p.get('scope'),
                actions=p.get('actions', []),
                context=p.get('context', {})
            )

        # 5. Synchronisation
        # Le service PermissionService de oxutils fait normalement des role_sync/group_sync.
        # Pour faire simple ici, on délègue à l'utilisateur le soin de rafraîchir son store.
        # Mais techniquement, on pourrait importer role_sync de oxutils.permissions.utils
        from oxutils.permissions.utils import role_sync
        role_sync(role.slug)

        return 204, None
