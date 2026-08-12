from uuid import UUID
from typing   import List, Optional, Annotated
from datetime import date, datetime
from pydantic import Field
from ninja    import Schema, ModelSchema
from hr.jobs.models import (
    JobFamily, 
    Position, 
    OrgUnit, 
    EmployeePositionHistory, 
    Training,
    Vacancy
)
from hr.employees.schemas import EmployeeOut
from hr.schemas import BaseFilter
from django.db.models import Q


# ---  JOB CATALOG SCHEMAS  ---
class JobFamilyOut(ModelSchema):
    """ High-level career categories (e.g., Engineering, HR). """
    class Meta:
        model = JobFamily
        fields = ['id', 'name', 'description']


class JobFamilyCreateIn(Schema):
    """ Data required to create a new job family. """
    name: str
    description: Optional[str] = None


class JobFamilyUpdateIn(Schema):
    """ Data for updating a job family. """
    name: Optional[str] = None
    description: Optional[str] = None


class OrgUnitBriefOut(Schema):
    """ Brief org unit info for Position output. """
    id: UUID
    name: str
    type: Optional[str] = None


class SeniorityLevelOut(Schema):
    """ Seniority level definition with rank and requirements. """
    id: UUID
    level: str
    rank: int
    label: str
    requirements: List[str]
    classe: Optional[int] = Field(default=None, ge=1, le=7)
    professional_category_id: Optional[UUID] = None
    is_active: bool = True


class ProfessionalCategoryOut(Schema):
    """Output schema for a professional category (grille légale 7x4)."""
    id: UUID
    classe: int
    echelon: int
    label: str
    application: str = ''
    is_active: bool = True


class ProfessionalCategoryUpdateIn(Schema):
    """Partial update schema for a professional category."""
    label: Optional[str] = None
    application: Optional[str] = None
    is_active: Optional[bool] = None


class ProfessionalCategoryCreateIn(Schema):
    """Create schema for a professional category."""
    classe: Annotated[int, Field(ge=1, le=7)]
    echelon: Annotated[int, Field(ge=1, le=4)]
    label: str
    application: str = ''
    is_active: bool = True


class SeniorityLevelUpdateIn(Schema):
    """ Data for updating a seniority level definition. """
    label: Optional[str] = None
    rank: Optional[int] = None
    requirements: Optional[List[str]] = None
    professional_category_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class SeniorityLevelCreateIn(Schema):
    """ Data for creating a seniority level definition. """
    level: str  # Required: 'TRAINEE', 'JUNIOR', etc.
    label: str  # Required: display name
    rank: int   # Required: hierarchy order
    requirements: List[str] = []
    professional_category_id: Optional[UUID] = None
    is_active: bool = True
    

class PositionSeniorityOut(Schema):
    """ Position with seniority level and salary range. """
    id: UUID
    position_id: UUID
    seniority_level: SeniorityLevelOut
    salary_min: int
    salary_max: int
    echelon: Optional[Annotated[int, Field(ge=1, le=4)]] = None
    professional_category_id: Optional[UUID] = None
    rank: int
    next_level_id: Optional[UUID] = None
    is_active: bool = True


class PositionSeniorityCreateIn(Schema):
    """ Data for creating a position seniority level. """
    seniority_level: str  # Seniority level code
    salary_min: int
    salary_max: int
    echelon: Optional[Annotated[int, Field(ge=1, le=4)]] = None
    rank: int = 1
    next_level_id: Optional[UUID] = None
    is_active: bool = True


class PositionSeniorityUpdateIn(Schema):
    """ Data for updating a position seniority level. """
    seniority_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    echelon: Optional[Annotated[int, Field(ge=1, le=4)]] = None
    rank: Optional[int] = None
    next_level_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class PositionOut(ModelSchema):
    """ Specific roles within a Job Family with multiple seniority levels. """
    job_family: JobFamilyOut
    org_unit: Optional[OrgUnitBriefOut] = None
    seniority_levels: List[PositionSeniorityOut] = []

    class Meta:
        model = Position
        fields = ['id', 'name', 'description', 'requirements', 'skills']


class PositionCreateIn(Schema):
    """ Data required to define a new company position. """
    name: str
    family_name: str
    org_unit_id: Optional[UUID] = None
    description: Optional[str] = None
    seniority_levels: List[PositionSeniorityCreateIn] = []
    requirements: Optional[List[str]] = []
    skills: Optional[List[dict]] = []


class PositionUpdateIn(Schema):
    """ Data for updating an existing position. """
    name: Optional[str] = None
    family_name: Optional[str] = None
    org_unit_id: Optional[UUID] = None
    description: Optional[str] = None
    seniority_levels: Optional[List[PositionSeniorityCreateIn]] = None
    requirements: Optional[List[str]] = None
    skills: Optional[List[dict]] = None


# ---  ORGANIZATIONAL STRUCTURE SCHEMAS  ---
class OrgChartEmployeeOut(Schema):
    """ Simplified employee representation for org chart display. """
    id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    photo: Optional[str] = None
    
    @staticmethod
    def resolve_first_name(obj):
        return getattr(obj, 'first_name', None)
    
    @staticmethod
    def resolve_last_name(obj):
        return getattr(obj, 'last_name', None)
    
    @staticmethod
    def resolve_middle_name(obj):
        return getattr(obj, 'middle_name', None)
    
    @staticmethod
    def resolve_photo(obj):
        # Try to get photo from user relation or directly
        user = getattr(obj, 'user', None)
        if user:
            return getattr(user, 'photo', None)
        return getattr(obj, 'photo', None)


class OrgUnitOut(ModelSchema):
    """ Information about an organizational unit (department, team, etc.). """
    manager: Optional[OrgChartEmployeeOut] = None
    affoint: Optional[OrgChartEmployeeOut] = None
    parent_id: Optional[UUID] = None
    type: Optional[str] = None
    employee_count: int = 0
    authorized_headcount: int = 0

    class Meta:
        model = OrgUnit
        fields = ['id', 'name', 'description']
    
    @staticmethod
    def resolve_type(obj):
        return obj.type  # Retourne le code technique (DEPARTMENT, BRANCH, etc.)
    
    @staticmethod
    def resolve_employee_count(obj):
        return obj.employee_count


class OrgUnitTreeOut(Schema):
    """ Hierarchical representation of the company organization chart. """
    id: UUID
    name: str
    type: str = "DEPARTMENT"
    employee_count: int = 0
    authorized_headcount: int = 0
    manager: Optional[OrgChartEmployeeOut] = None
    affoint: Optional[OrgChartEmployeeOut] = None
    sub_units: List['OrgUnitTreeOut'] = []


class OrgUnitCreateIn(Schema):
    """ Data required to establish a new organizational unit. """
    name: str
    type: Optional[str] = "DEPARTMENT"  # DEPARTMENT, DIVISION, TEAM, FUNCTION, BRANCH, PROJECT
    parent_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    affoint_id: Optional[UUID] = None
    authorized_headcount: Optional[int] = 0


class OrgUnitUpdateIn(Schema):
    """ Data for updating an organizational unit. """
    name: Optional[str] = None
    type: Optional[str] = None
    parent_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    affoint_id: Optional[UUID | str] = None  # str pour permettre "" (supprimer adjoint)
    authorized_headcount: Optional[int] = None


class EmployeeAssignIn(Schema):
    """ Data for assigning an employee to an organizational unit. """
    position_id: Optional[UUID] = None


# ---  CAREER PROGRESSION  ---
class CareerHistoryOut(ModelSchema):
    """ Details of an employee's specific role assignment and duration. """
    position: PositionOut
    seniority_level: Optional[SeniorityLevelOut] = None
    salary_at_assignment: Optional[int] = None
    org_unit: Optional[OrgUnitOut]
    days_spent: Optional[int] = None

    class Meta:
        model = EmployeePositionHistory
        fields = ['id', 'start_date', 'end_date', 'is_current', 'description']


class EmployeeMoveIn(Schema):
    """ Data for processing promotions, transfers, or lateral moves. """
    new_position_id: UUID
    new_seniority_level_id: Optional[UUID] = None
    new_org_unit_id: Optional[UUID] = None
    effective_date: Optional[date] = None
    description: Optional[str] = None


class InitialAssignmentIn(Schema):
    """ Initial role assignment during the onboarding process. """
    position_id: UUID
    seniority_level_id: Optional[UUID] = None
    org_unit_id: UUID
    start_date: Optional[date] = None


# ---  DEVELOPMENT & TRAINING  ---
class TrainingOut(ModelSchema):
    """ Records of professional certifications and corporate training. """
    employee: OrgChartEmployeeOut
    status: str = "Active"

    class Meta:
        model = Training
        fields = [
            'id', 'name', 'institute', 'start_date', 
            'end_date', 'expiry_date', 'location', 'description'
        ]

    @staticmethod
    def resolve_status(obj):
        if obj.expiry_date and obj.expiry_date < date.today():
            return "Expired"
        return "Active"


class TrainingRecordIn(Schema):
    """ Data for recording a new training session or certification. """
    name: str
    institute: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    expiry_date: Optional[date] = None
    location: Optional[str] = None
    description: Optional[str] = None


# ---  EMPLOYEE TRANSITIONS  ---
class TransitionOut(Schema):
    """ Employee career movement event (promotion, transfer, hire, offboard). """
    id: UUID
    employee_id: UUID
    employee: Optional[EmployeeOut] = None  # Nested employee info
    transition_type: str
    transition_type_display: Optional[str] = None
    from_position: Optional[PositionOut] = None
    from_seniority_level: Optional[SeniorityLevelOut] = None
    to_position: Optional[PositionOut] = None
    to_seniority_level: Optional[SeniorityLevelOut] = None
    date: date
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by_id: Optional[UUID] = None

    @staticmethod
    def resolve_transition_type_display(obj):
        return obj.get_transition_type_display()

    @staticmethod
    def resolve_employee(obj):
        return obj.employee


class TransitionCreateIn(Schema):
    """ Data for creating a new employee transition/movement. """
    employee_id: UUID
    transition_type: str  # PROMOTION, TRANSFER, HIRE, OFFBOARD
    from_position_id: Optional[UUID] = None
    from_seniority_level_id: Optional[UUID] = None
    to_position_id: Optional[UUID] = None
    to_seniority_level_id: Optional[UUID] = None
    date: Optional[str] = None  # ISO date string format YYYY-MM-DD
    reason: Optional[str] = None


class TransitionUpdateIn(Schema):
    """ Data for updating an existing transition. """
    transition_type: Optional[str] = None
    from_position_id: Optional[UUID] = None
    from_seniority_level_id: Optional[UUID] = None
    to_position_id: Optional[UUID] = None
    to_seniority_level_id: Optional[UUID] = None
    date: Optional[str] = None  # ISO date string format YYYY-MM-DD
    reason: Optional[str] = None


class TransitionFilter(BaseFilter):
    """ Filter schema for transitions list endpoint. """
    transition_type: Optional[str] = None
    employee_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

    def filter_search(self, value: str):
        """Search across employee names, matricule, reason, and position names."""
        return (
            Q(employee__first_name__icontains=value) |
            Q(employee__last_name__icontains=value) |
            Q(employee__matricule__icontains=value) |
            Q(reason__icontains=value) |
            Q(from_position__name__icontains=value) |
            Q(to_position__name__icontains=value)
        )

    def filter_transition_type(self, value: str):
        """Filter by transition type."""
        return Q(transition_type=value)

    def filter_employee_id(self, value: UUID):
        """Filter by employee ID."""
        return Q(employee_id=value)

    def filter_date_from(self, value: date):
        """Filter transitions from date."""
        return Q(date__gte=value)

    def filter_date_to(self, value: date):
        """Filter transitions to date."""
        return Q(date__lte=value)


# ---  VACANCY SCHEMAS  ---
class VacancyOut(ModelSchema):
    """ Full vacancy output with nested position info. """
    position: PositionOut
    priority_display: Optional[str] = None
    status_display: Optional[str] = None

    class Meta:
        model = Vacancy
        fields = ['id', 'priority', 'status', 'opened_date', 'target_date', 
                  'reason', 'filled_date', 'created_at', 'updated_at']

    @staticmethod
    def resolve_priority_display(obj):
        return obj.get_priority_display()

    @staticmethod
    def resolve_status_display(obj):
        return obj.get_status_display()


class VacancyBriefOut(ModelSchema):
    """ Brief vacancy info for lists. """
    position_name: Optional[str] = None

    class Meta:
        model = Vacancy
        fields = ['id', 'priority', 'status', 'opened_date']

    @staticmethod
    def resolve_position_name(obj):
        return obj.position.name if obj.position else None


class VacancyCreateIn(Schema):
    """ Data required to create a vacancy. """
    position_id: UUID
    priority: str = 'MEDIUM'
    status: str = 'OPEN'
    opened_date: Optional[date] = None
    target_date: Optional[date] = None
    reason: Optional[str] = None


class VacancyUpdateIn(Schema):
    """ Data for updating a vacancy (all fields optional). """
    position_id: Optional[UUID] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    opened_date: Optional[date] = None
    target_date: Optional[date] = None
    reason: Optional[str] = None
    filled_date: Optional[date] = None


class VacancyFilter(BaseFilter):
    """ Filter schema for vacancy list endpoint. """
    priority: Optional[str] = Field(None, description="Filter by priority (HIGH, MEDIUM, LOW)")
    status: Optional[str] = Field(None, description="Filter by status")
    opened_date_from: Optional[date] = Field(None, description="Filter from opened date")
    opened_date_to: Optional[date] = Field(None, description="Filter to opened date")
    position_id: Optional[UUID] = Field(None, description="Filter by position ID")

    def filter_search(self, value: str):
        """Search across position name, reason, priority, and status."""
        if not value:
            return Q()
        return (
            Q(position__name__icontains=value) |
            Q(reason__icontains=value) |
            Q(priority__icontains=value) |
            Q(status__icontains=value)
        )

    def filter_priority(self, value: str):
        """Filter by priority."""
        if not value:
            return Q()
        return Q(priority=value)

    def filter_status(self, value: str):
        """Filter by status."""
        if not value:
            return Q()
        return Q(status=value)

    def filter_opened_date_from(self, value: date):
        """Filter vacancies opened from date."""
        return Q(opened_date__gte=value)

    def filter_opened_date_to(self, value: date):
        """Filter vacancies opened to date."""
        return Q(opened_date__lte=value)

    def filter_position_id(self, value: UUID):
        """Filter by position ID."""
        if not value:
            return Q()
        return Q(position_id=value)

