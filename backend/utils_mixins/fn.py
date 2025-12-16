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


def generate_schemas(model_cls: Type[dj_models.Model], nested_map: dict = None):
    """
    Génère CreateSchema, UpdateSchema et DetailSchema pour un modèle Django.

    Args:
        model_cls: La classe Django modèle.
        nested_map: Dictionnaire {ForeignKey_field_name: DetailSchema} pour nested.
    
    Returns:
        Dict avec les 3 schémas sous clés: 'detail', 'create', 'update'
    """
    nested_map = nested_map or {}

    # ---------------- DetailSchema ----------------
    attrs_detail = {}
    for field in model_cls._meta.get_fields():
        if field.name in nested_map:
            # remplacer FK par nested schema
            attrs_detail[field.name] = nested_map[field.name]
    
    DetailSchema = type(
        f"{model_cls.__name__}DetailSchema",
        (ModelSchema,),
        {
            **attrs_detail,
            "Meta": type(
                "Meta",
                (),
                {"model": model_cls, "fields": "__all__"}
            )
        }
    )

    # ---------------- CreateSchema ----------------
    create_fields = []
    optional_fields = []

    for field in model_cls._meta.get_fields():
        if isinstance(field, dj_models.Field):
            create_fields.append(field.name)
            # rendre optionnel si default, null ou blank
            if getattr(field, "default", None) not in (dj_models.NOT_PROVIDED, None) or getattr(field, "blank", False) or getattr(field, "null", False):
                optional_fields.append(field.name)

    CreateSchema = type(
        f"{model_cls.__name__}CreateSchema",
        (ModelSchema,),
        {
            "Meta": type(
                "Meta",
                (),
                {
                    "model": model_cls,
                    "fields": create_fields,
                    "fields_optional": optional_fields,
                }
            )
        }
    )

    # ---------------- UpdateSchema ----------------
    UpdateSchema = type(
        f"{model_cls.__name__}UpdateSchema",
        (ModelSchema,),
        {
            "Meta": type(
                "Meta",
                (),
                {
                    "model": model_cls,
                    "fields": create_fields,
                    "fields_optional": "__all__",
                }
            )
        }
    )

    return {
        "detail": DetailSchema,
        "create": CreateSchema,
        "update": UpdateSchema,
    }
