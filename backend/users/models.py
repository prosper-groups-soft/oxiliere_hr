import uuid
from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE
from auditlog.registry import auditlog
from utils_mixins.models import BaseModelMixin



class UserManager(BaseUserManager):
    """
    Gestionnaire personnalisé pour le modèle User
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Crée et sauvegarde un utilisateur avec l'email et le mot de passe donnés.
        """
        raise RuntimeError("This application can't create Users....")

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crée et sauvegarde un superutilisateur avec l'email et le mot de passe donnés.
        """
        raise RuntimeError("This application can't create Users....")


class User(AbstractUser, SafeDeleteModel, BaseModelMixin):
    """
    Modèle d'utilisateur personnalisé qui utilise l'email comme identifiant unique
    et intègre la suppression sécurisée (soft delete)
    """
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    # Suppression du champ username qui est obligatoire dans AbstractUser
    username = None
    password = None # Don't need password

    oxi_id = models.UUIDField(unique=True)  # id venant de auth.oxi.com
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email



# Enregistrement du modèle User pour l'audit logging
auditlog.register(User)
