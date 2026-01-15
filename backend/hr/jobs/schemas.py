from uuid import UUID
from typing import List, Optional
from datetime import date
from ninja import Schema, ModelSchema
from hr.jobs.models import (
    JobFamily, 
    Position, 
    Department, 
    EmployeePositionHistory, 
    Training
)
from hr.employees.schemas import EmployeeOut


# ----------------  JOB REPOSITORY SCHEMAS  -------------------
class JobFamilyOut(ModelSchema):
    """Output schema for Job Families (e.g., Engineering, Sales)."""
    class Meta:
        model = JobFamily
        fields = ['id', 'name', 'description']


class PositionOut(ModelSchema):
    """Output schema for specific job positions with seniority level details."""
    job_family: JobFamilyOut   # Nested to provide full family context in lists
    level_display: str = None  # Returns "Junior" instead of the raw value "JUNIOR"

    class Meta:
        model = Position
        fields = [
            'id', 
            'name', 
            'level', 
            'description'
        ]
    
    @staticmethod
    def resolve_level_display(obj):
        return obj.get_level_display()


class PositionCreateIn(Schema):
    """Input schema for creating a new position within a family."""
    name: str
    family_name: str
    level: str
    description: Optional[str] = None
    
    
# --------------  ORGANIZATION & HIERARCHY SCHEMAS  ------------------
class DepartmentOut(ModelSchema):
    """Basic department output schema."""
    manager: Optional[EmployeeOut] = None
    parent_id: Optional[UUID] = None

    class Meta:
        model = Department
        fields = [
            'id', 
            'name', 
            'description'
        ]


class DepartmentTreeOut(Schema):
    """Recursive schema for organizational chart visualization."""
    id: UUID
    name: str
    manager: Optional[str] = None
    sub_departments: List['DepartmentTreeOut'] = [] # Self-referencing recursion


class DepartmentCreateIn(Schema):
    """Input schema for creating a new functional unit."""
    name: str
    parent_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None


# -----------  CAREER TRACKING & MOVEMENTS  --------------
class CareerHistoryOut(ModelSchema):
    """Represents a specific chapter in an employee's career path."""
    position: PositionOut
    department: Optional[DepartmentOut]
    days_spent: Optional[int] = None # Calculated by the service layer

    class Meta:
        model = EmployeePositionHistory
        fields = [
            'id', 
            'start_date', 
            'end_date', 
            'is_current', 
            'description'
        ]


class EmployeeMoveIn(Schema):
    """Schema for handling promotions, demotions, or lateral transfers."""
    new_position_id: UUID
    new_department_id: Optional[UUID] = None
    effective_date: Optional[date] = None
    description: Optional[str] = None


class InitialAssignmentIn(Schema):
    """Schema used during the onboarding process for the first job assignment."""
    position_id: UUID
    department_id: UUID
    start_date: Optional[date] = None


# -----------  TRAINING & CERTIFICATIONS  -------------
class TrainingOut(ModelSchema):
    """Output schema for employee skills development and certifications."""
    employee: EmployeeOut
    status: str = "Active"

    class Meta:
        model = Training
        fields = [
            'id', 
            'name', 
            'institute', 
            'start_date', 
            'end_date', 
            'expiry_date', 
            'location', 
            'description'
        ]

    @staticmethod
    def resolve_status(obj):
        """Calculates if the certification is still valid as of today (2026)."""
        if obj.expiry_date and obj.expiry_date < date.today():
            return "Expired"
        return "Active"


class TrainingRecordIn(Schema):
    """Input schema for recording a new training session or certificate."""
    name: str
    institute: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    expiry_date: Optional[date] = None
    location: Optional[str] = None
    description: Optional[str] = None

