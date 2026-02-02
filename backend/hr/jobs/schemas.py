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


# ----------------  JOB CATALOG SCHEMAS  -------------------
class JobFamilyOut(ModelSchema):
    """ High-level career categories (e.g., Engineering, HR). """
    class Meta:
        model = JobFamily
        fields = ['id', 'name', 'description']


class PositionOut(ModelSchema):
    """ Specific roles and seniority levels within a Job Family. """
    job_family: JobFamilyOut
    level_display: str = None

    class Meta:
        model = Position
        fields = ['id', 'name', 'level', 'description']
    
    @staticmethod
    def resolve_level_display(obj):
        return obj.get_level_display()


class PositionCreateIn(Schema):
    """ Data required to define a new company position. """
    name: str
    family_name: str
    level: str
    description: Optional[str] = None
    
    
# --------------  ORGANIZATIONAL STRUCTURE SCHEMAS  ------------------
class DepartmentOut(ModelSchema):
    """ Information about a functional department. """
    manager: Optional[EmployeeOut] = None
    parent_id: Optional[UUID] = None

    class Meta:
        model = Department
        fields = ['id', 'name', 'description']


class DepartmentTreeOut(Schema):
    """ Hierarchical representation of the company organization chart. """
    id: UUID
    name: str
    manager: Optional[str] = None
    sub_departments: List['DepartmentTreeOut'] = []


class DepartmentCreateIn(Schema):
    """ Data required to establish a new organizational unit. """
    name: str
    parent_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None


# -----------  CAREER PROGRESSION  --------------
class CareerHistoryOut(ModelSchema):
    """ Details of an employee's specific role assignment and duration. """
    position: PositionOut
    department: Optional[DepartmentOut]
    days_spent: Optional[int] = None

    class Meta:
        model = EmployeePositionHistory
        fields = ['id', 'start_date', 'end_date', 'is_current', 'description']


class EmployeeMoveIn(Schema):
    """ Data for processing promotions, transfers, or lateral moves. """
    new_position_id: UUID
    new_department_id: Optional[UUID] = None
    effective_date: Optional[date] = None
    description: Optional[str] = None


class InitialAssignmentIn(Schema):
    """ Initial role assignment during the onboarding process. """
    position_id: UUID
    department_id: UUID
    start_date: Optional[date] = None


# -----------  DEVELOPMENT & TRAINING  -------------
class TrainingOut(ModelSchema):
    """ Records of professional certifications and corporate training. """
    employee: EmployeeOut
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

