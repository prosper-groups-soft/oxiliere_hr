from typing import Iterable
from django.db import models


def update_instance(*, instance: models.Model, allowed_fields: Iterable[str], data: dict) -> models.Model:
    """
    Generic helper to update model instances safely.
    """
    updated_fields: list[str] = []

    for field, value in data.items():
        if field not in allowed_fields:
            continue

        if getattr(instance, field) != value:
            setattr(instance, field, value)
            updated_fields.append(field)

    if updated_fields:
        instance.full_clean()
        instance.save(update_fields=updated_fields)

    return instance

