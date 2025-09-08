from django.utils import timezone


def get_matricule_seq_key():
    year = timezone.now().year
    return f"employee_matricule_{year}"


def get_contract_seq_key():
    year = timezone.now().year
    return f"employee_contract_{year}"
