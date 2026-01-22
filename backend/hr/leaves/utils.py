from datetime import date
import calendar


def get_carry_over_expiration_date(year: int, month: int) -> date:
    """
    Returns the last day of the specified month and year to determine 
    the expiration date of carried-over leave days.
    """
    last_day = calendar.monthrange(year, month)[1]  # last day of the month
    return date(year, month, last_day)

