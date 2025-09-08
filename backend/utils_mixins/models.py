import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError




class UUIDPrimaryKeyMixin(models.Model):
    """Mixin that provides a UUID primary key field."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record"
    )

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """Mixin that provides created_at and updated_at timestamp fields."""
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when this record was last updated"
    )

    class Meta:
        abstract = True


class UserTrackingMixin(models.Model):
    """Mixin that tracks which user created and last modified a record."""
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        help_text="User who last updated this record"
    )

    class Meta:
        abstract = True


class SlugMixin(models.Model):
    """Mixin that provides a slug field."""
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-friendly version of the name"
    )

    class Meta:
        abstract = True


class NameMixin(models.Model):
    """Mixin that provides name and description fields."""
    name = models.CharField(
        max_length=255,
        help_text="Name of this record"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class ActiveMixin(models.Model):
    """Mixin that provides an active/inactive status field."""
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this record is active"
    )

    class Meta:
        abstract = True


class OrderingMixin(models.Model):
    """Mixin that provides an ordering field."""
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order for sorting records"
    )

    class Meta:
        abstract = True
        ordering = ['order']


class BaseModelMixin(UUIDPrimaryKeyMixin, TimestampMixin, ActiveMixin):
    """
    Base mixin that combines the most commonly used mixins.
    Provides UUID primary key, timestamps, and active status.
    """
    class Meta:
        abstract = True


class SingletonMxin(BaseModelMixin):
    """
    Classe de base pour un modèle singleton.
    """
    
    class Meta:
        abstract = True

    @classmethod
    def get_instance(cls):
        """
        Retourne l'unique instance du modèle singleton. Si aucune instance
        n'existe, une nouvelle est créée.
        """

        instance = None
        try:
            instance = cls.objects.get()
        except cls.DoesNotExist:
            instance = cls.objects.create()
        except cls.MultipleObjectsReturned:
            instances = cls.objects.all()
            instance = instances.first()
            instances.exclude(pk=instance.pk).delete()
        
        return instance

    def save(self, *args, **kwargs):
        """
        Vérifie si une instance existe déjà avant de sauvegarder.
        """
        if self.pk is not None and self.__class__.objects.exclude(pk=self.pk).exists():
            raise ValidationError("There can only be one instance of this model.")
        super().save(*args, **kwargs)



class AddressMixin(BaseModelMixin):
    number = models.CharField(max_length=5)
    street = models.CharField(max_length=75)
    municipality = models.CharField(max_length=75)
    city = models.CharField(max_length=75)
    province = models.CharField(max_length=75)
    country = models.CharField(max_length=75)
    country_code = models.CharField(max_length=3, verbose_name="Code Pays", default="cd")

    class Meta:
        abstract = True
