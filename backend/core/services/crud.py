from typing import Type, Iterable
from django.db import models
from django.shortcuts import get_object_or_404


class BaseCRUDService:
    """
    A generic base service class providing standard CRUD operations.
    
    This class abstracts common database interactions (list, get, create, update, delete)
    to promote code reuse and maintain a clean separation between the API layer 
    and the data persistence layer.
    """
    model: Type[models.Model]
    allowed_update_fields: Iterable[str] | None = None

    def list(self, **filters):
        return self.model.objects.filter(**filters)

    def get(self, *, id):
        return get_object_or_404(self.model, id=id)

    def create(self, *, data: dict, **extra):
        instance = self.model.objects.create(**data, **extra)
        return instance

    def update(self, *, instance: models.Model, data: dict) -> models.Model:
        """
        Updates a model instance safely and optimizes performance 
        by only persisting changed fields to the database.
        """
        allowed = self.allowed_update_fields or data.keys()
        updated_fields: list[str] = []

        for field, value in data.items():
            if field not in allowed:
                continue

            # Performance optimization: only update if the value has actually changed
            if getattr(instance, field) != value:
                setattr(instance, field, value)
                updated_fields.append(field)

        if updated_fields:
            # Enforce model-level validation (clean methods, validators, etc.)
            instance.full_clean()
            # Database optimization: only touch modified columns in the UPDATE query
            instance.save(update_fields=updated_fields)

        return instance

    def delete(self, *, instance):
        instance.delete()

    def exists(self, **filters) -> bool:
        """
        Check whether at least one object exists
        matching the given filters.
        """
        return self.model.objects.filter(**filters).exists()

