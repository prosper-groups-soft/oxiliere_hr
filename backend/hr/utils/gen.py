import uuid6
import secrets
import string
from django.utils import timezone


def generate_daily_register_code(register_date):
    """Generates a unique code (DR-YYYYMMDD-XXXX) upon creation."""
    date_str = register_date.strftime("%Y%m%d")
    rand = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    code = f"DR-{date_str}-{rand}"
    
    return code


def generate_payroll_run_code():
    """
    Generates a unique code for a payroll run.
    Example: PR-A1B2C3D4
    """
    unique_id = uuid6.uuid7().hex[:8].upper()
    return f"PR-{unique_id}"


def get_contract_seq_key():
    year = timezone.now().year
    return f"employee_contract_{year}"


def get_rotate_value():
    return timezone.now().strftime("%y%m%d")

