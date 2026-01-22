from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class PositionLevel(TextChoices):
    """
    The `level` represents the seniority or career stage.
    """
    TRAINEE = "TRAINEE", _("Trainee")                 # Entry-level training or internship
    APPRENTICE = "APPRENTICE", _("Apprentice")        # Practical learning with mentoring
    JUNIOR = "JUNIOR", _("Junior")                    # First independent work experience
    INTERMEDIATE = "INTERMEDIATE", _("Intermediate")  # Solid experience, some autonomy
    SENIOR = "SENIOR", _("Senior")                    # Advanced expertise, mentoring others
    LEAD = "LEAD", _("Lead")                          # Leads a small team or project
    MANAGER = "MANAGER", _("Manager")                 # Manages a team or functional area
    DIRECTOR = "DIRECTOR", _("Director")              # Manages multiple teams or departments
    EXECUTIVE = "EXECUTIVE", _("Executive")           # Strategic leadership role

