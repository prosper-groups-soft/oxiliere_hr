import uuid6


def generate_event_code():
    "Generate a unique code for an event (e.g., EVT-A1B2C3D4)."
    return f"EVT-{uuid6.uuid7().hex[:8].upper()}"

