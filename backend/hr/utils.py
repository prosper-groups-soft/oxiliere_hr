from django.utils import timezone


def get_matricule_seq_key():
    year = timezone.now().year
    return f"employee_matricule_{year}"


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
