

class RuleContext:
    """
    Container for all data needed to evaluate rules.

    Example attributes:
        attendance_entry
        schedule_day
        employee
        settings (AttendanceSettings)
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

