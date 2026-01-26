import secrets
import string


def generate_daily_register_code(register_date):
    """Generates a unique code (DR-YYYYMMDD-XXXX) upon creation."""
    date_str = register_date.strftime("%Y%m%d")
    rand = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    code = f"DR-{date_str}-{rand}"
    
    return code

