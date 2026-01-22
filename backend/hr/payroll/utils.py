import uuid6


def generate_payroll_run_code():
    """
    Generates a unique code for a payroll run.
    Example: PR-A1B2C3D4
    """
    unique_id = uuid6.uuid7().hex[:8].upper()
    return f"PR-{unique_id}"

