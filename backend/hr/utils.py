from typing import Optional, Dict, Callable, Iterable
from django.utils import timezone
from django.db import models
import pycountry


def get_contract_seq_key():
    year = timezone.now().year
    return f"employee_contract_{year}"


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


def update_instance(
    *, 
    instance: models.Model, 
    allowed_fields: Iterable[str], 
    data: dict
) -> models.Model:
    """
    Generic helper to update model instances safely.
    Optimizes performance by only updating changed fields.
    """
    updated_fields: list[str] = []

    for field, value in data.items():
        if field not in allowed_fields:
            continue

        if getattr(instance, field) != value:
            setattr(instance, field, value)
            updated_fields.append(field)

    if updated_fields:
        # Crucial for enforcing model-level validation
        instance.full_clean()
        # Optimization: only touch the modified columns
        instance.save(update_fields=updated_fields)

    return instance


def get_country_codes():
    """
    Returns a list of tuples (ISO alpha-2 code, country name)
    """
    countries = []
    for country in pycountry.countries:
        countries.append((country.alpha_2, country.name))

    return countries


def normalize_names(
    last_name: Optional[str] = None, 
    middle_name: Optional[str] = None, 
    first_name: Optional[str] = None
) -> Dict[str, Optional[str]]:
    """
    Normalize name components using a transformation mapping.
    
    Args:
        last_name: The family name to be uppercased.
        middle_name: The middle name(s) to be uppercased.
        first_name: The given name to be title-cased.
        
    Returns:
        A dictionary containing the normalized name components.
    """
    
    # Mapping configuration: key -> (raw_value, transformation_function)
    config: Dict[str, tuple[Optional[str], Callable[[str], str]]] = {
        'last_name': (last_name, str.upper),
        'middle_name': (middle_name, str.upper),
        'first_name': (first_name, str.title)
    }
    
    return {
        key: func(val.strip()) if val and val.strip() else None 
        for key, (val, func) in config.items()
    }

