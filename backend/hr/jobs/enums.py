
from enum import Enum


class PositionLevel(str, Enum):
    """
    The `level` represents the seniority or career stage:
        - TRAINEE: Entry-level training or internship
        - APPRENTICE: Practical learning with mentoring
        - JUNIOR: First independent work experience
        - INTERMEDIATE: Solid experience, some autonomy
        - SENIOR: Advanced expertise, mentoring others
        - LEAD: Leads a small team or project
        - MANAGER: Manages a team or functional area
        - DIRECTOR: Manages multiple teams or departments
        - EXECUTIVE: Strategic leadership role
    """

    TRAINEE = "TRAINEE"               # Entry-level training or internship
    APPRENTICE = "APPRENTICE"         # Practical learning with mentoring
    JUNIOR = "JUNIOR"                 # First independent work experience
    INTERMEDIATE = "INTERMEDIATE"     # Solid experience, some autonomy
    SENIOR = "SENIOR"                 # Advanced expertise, mentoring others
    LEAD = "LEAD"                     # Leads a small team or project
    MANAGER = "MANAGER"               # Manages a team or functional area
    DIRECTOR = "DIRECTOR"             # Manages multiple teams or departments
    EXECUTIVE = "EXECUTIVE"           # Strategic leadership role
