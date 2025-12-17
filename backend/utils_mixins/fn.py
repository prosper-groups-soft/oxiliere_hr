from django.utils import timezone
from ninja import ModelSchema
from typing import Type
from django.db import models as dj_models


def get_rotate_value():
    return timezone.now().strftime("%y%m%d")


def create_unset_address(user, model):
    return model.objects.create(
        number = "N/A",
        street = "N/A",
        municipality = "N/A",
        city = "N/A",
        province = "N/A",
        country = "Republique démocratique du Congo",
        country_code = "CD",
        created_by = user,
        updated_by = user
    )


def enum_to_choices(enum_class):
    """
    Convert a Python Enum into Django `choices`:
    - Uses enum.value as stored DB value
    - If enum.value already looks like a human label (contains spaces), use it
    - Otherwise generate a spaced, title-cased label from the enum name
    """
    choices = []
    
    for item in enum_class:
        value = item.value

        # If value already looks like a label
        if isinstance(value, str) and " " in value:
            label = value
        else:
            # Convert ENUM_NAME → "Enum Name"
            label = item.name.replace("_", " ").title()
        
        choices.append((value, label))
    
    return choices

