from ninja import ModelSchema
from typing import Type, Dict, List
from django.db import models as dj_models


def _make_meta(model_cls: Type[dj_models.Model], fields: List[str], optional=None):
    """Helper to generate the Meta class for a ModelSchema."""
    return type("Meta", (), {
        "model": model_cls,
        "fields": fields,
        "fields_optional": optional or []
    })


def _get_foreignkey_nested_fields(model_cls: Type[dj_models.Model], cache: Dict):
    """Detect ForeignKey fields and replace them with nested DetailSchema."""
    nested_fields = {}
    for field in model_cls._meta.get_fields():
        if isinstance(field, dj_models.ForeignKey):
            related_model = field.related_model
            nested_schemas = generate_schemas(related_model, cache)
            nested_fields[field.name] = nested_schemas["detail"]
    return nested_fields


def _get_create_fields(model_cls: Type[dj_models.Model]):
    """
    Get all model fields for CreateSchema and mark optional fields 
    based on default, blank, or null.
    """
    create_fields = []
    optional_fields = []
    for field in model_cls._meta.get_fields():
        if isinstance(field, dj_models.Field):
            create_fields.append(field.name)
            if getattr(field, "default", None) not in (dj_models.NOT_PROVIDED, None) \
               or getattr(field, "blank", False) \
               or getattr(field, "null", False):
                optional_fields.append(field.name)
    return create_fields, optional_fields


def generate_schemas(
    model_cls: Type[dj_models.Model],
    cache: Dict = None,
    external_nested: Dict[str, Type[ModelSchema]] = None
):
    """
    Automatically generates DetailSchema, CreateSchema, and UpdateSchema
    for a Django model. ForeignKey fields are replaced with nested DetailSchema.
    You can also pass external_nested to inject already existing schemas for certain fields.

    Args:
        model_cls: Django model class.
        cache: Internal dictionary to avoid infinite recursion.
        external_nested: Optional mapping {field_name: ModelSchema} for fields that are not standard ForeignKeys.

    Returns:
        Dict containing 'detail', 'create', 'update' schemas.
    """
    if cache is None:
        cache = {}
    if external_nested is None:
        external_nested = {}

    if model_cls in cache:
        return cache[model_cls]

    # ---------------- Generate nested fields ----------------
    nested_fields = _get_foreignkey_nested_fields(model_cls, cache)
    # Add external nested schemas
    nested_fields.update(external_nested)

    # ---------------- DetailSchema ----------------
    DetailSchema = type(
        f"{model_cls.__name__}DetailSchema",
        (ModelSchema,),
        {**nested_fields, "Meta": _make_meta(model_cls, "__all__")}
    )

    # ---------------- CreateSchema ----------------
    create_fields, optional_fields = _get_create_fields(model_cls)
    CreateSchema = type(
        f"{model_cls.__name__}CreateSchema",
        (ModelSchema,),
        {"Meta": _make_meta(model_cls, create_fields, optional_fields)}
    )

    # ---------------- UpdateSchema ----------------
    UpdateSchema = type(
        f"{model_cls.__name__}UpdateSchema",
        (ModelSchema,),
        {"Meta": _make_meta(model_cls, create_fields, "__all__")}
    )

    # ---------------- Cache and return ----------------
    schemas = {"detail": DetailSchema, "create": CreateSchema, "update": UpdateSchema}
    cache[model_cls] = schemas
    return schemas
