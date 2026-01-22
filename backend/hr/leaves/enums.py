from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class LeaveCategory(TextChoices):
    """
    High-level legal category of leave.
    Determines if it's deductible from annual balance or managed separately.
    """
    ANNUAL = "ANNUAL", _("Annual Leave")              # Deducted from balance
    SICK = "SICK", _("Sick Leave")                    # Outside balance, justified
    CIRCUMSTANCE = "CIRCUMSTANCE", _("Special Leave") # Outside balance, fixed duration
    UNPAID = "UNPAID", _("Unpaid Leave")              # Outside balance
    OTHER = "OTHER", _("Other")


class LeaveStatus(TextChoices):
    """
    Lifecycle of a leave request.
    PENDING -> APPROVED or REJECTED
    APPROVED -> TAKEN (once start_date is passed) or CANCELLED
    """
    PENDING = "PENDING", _("Pending Approval")
    APPROVED = "APPROVED", _("Approved")
    REJECTED = "REJECTED", _("Rejected")
    CANCELLED = "CANCELLED", _("Cancelled")
    # TAKEN is useful for historical reporting once the leave period is over
    TAKEN = "TAKEN", _("Taken / Archived")


class LeaveTransactionTypes(TextChoices):
    EARN = "EARN", _("Accrual (Monthly/Yearly)")
    CONSUME = "CONSUME", _("Consumption (Leave)")
    REFUND = "REFUND", _("Refund (Cancellation/Recall)")
    ADJUST = "ADJUST", _("Manual Adjustment")
    CARRY_OVER = "CARRY_OVER", _("Yearly Carry-over")
    EXPIRE = "EXPIRE", _("Expiration")


class CircumstanceType(TextChoices):
    """
    Specific events based on Labor Law.
    Common durations (for reference in policy config):
    - MARRIAGE_EMPLOYEE: 2-3 days
    - BIRTH_SPOUSE: 2-3 days
    - DEATH_1ST_DEGREE: 4 days (Spouse, Child, Parent)
    - DEATH_2ND_DEGREE: 2 days (Sibling, Grandparent)
    - CHILD_MARRIAGE: 1 day
    """
    MARRIAGE_EMPLOYEE = "MARRIAGE_EMPLOYEE", _("Employee's own marriage")
    BIRTH_SPOUSE = "BIRTH_SPOUSE", _("Birth of spouse's child")
    DEATH_FIRST_DEGREE = "DEATH_FIRST_DEGREE", _("Death of a 1st degree relative")
    DEATH_SECOND_DEGREE = "DEATH_SECOND_DEGREE", _("Death of a 2nd degree relative")
    CHILD_MARRIAGE = "CHILD_MARRIAGE", _("Marriage of employee's child")
    MOVING = "MOVING", _("Relocation / Moving")
    CHILD_HOSPITALIZATION = "CHILD_HOSPITALIZATION", _("Hospitalization of a child")
    OTHER = "OTHER", _("Other legal circumstance")

