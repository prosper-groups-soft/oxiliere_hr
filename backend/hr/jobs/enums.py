from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class OrgUnitType(TextChoices):
    """
    Types d'unités organisationnelles dans la structure de l'entreprise.
    """
    DEPARTMENT = "DEPARTMENT", _("Département")       # Grande division fonctionnelle
    DIVISION = "DIVISION", _("Division")              # Sous-division d'un département
    TEAM = "TEAM", _("Équipe")                        # Équipe opérationnelle
    FUNCTION = "FUNCTION", _("Fonction")              # Unité fonctionnelle spécialisée
    BRANCH = "BRANCH", _("Succursale")                # Site géographique
    PROJECT = "PROJECT", _("Projet")                  # Unité temporaire projet


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
    DIRECTOR = "DIRECTOR", _("Director")              # Manages multiple teams or organization unity
    EXECUTIVE = "EXECUTIVE", _("Executive")           # Strategic leadership role


class TransitionType(TextChoices):
    """
    Types of employee career movements/transitions.
    """
    PROMOTION = "PROMOTION", _("Promotion")           # Advancement to higher level/role
    TRANSFER = "TRANSFER", _("Transfer")              # Lateral move to different unit/position
    HIRE = "HIRE", _("Hire")                          # New employee onboarding
    OFFBOARD = "OFFBOARD", _("Offboard")              # Employee departure/exit


class VacancyPriority(TextChoices):
    """
    Priority levels for job vacancies.
    """
    HIGH = "HIGH", _("High")                          # Critical, urgent fill needed
    MEDIUM = "MEDIUM", _("Medium")                    # Standard priority
    LOW = "LOW", _("Low")                             # Can wait, backfill position


class VacancyStatus(TextChoices):
    """
    Status stages for job vacancies lifecycle.
    """
    OPEN = "OPEN", _("Open")                          # Vacancy posted, accepting candidates
    IN_PROGRESS = "IN_PROGRESS", _("In Progress")     # Internal process underway
    RECRUITMENT = "RECRUITMENT", _("Recruitment")     # External recruitment active
    CANCELLED = "CANCELLED", _("Cancelled")           # Position no longer needed
    FILLED = "FILLED", _("Filled")                    # Position successfully filled

