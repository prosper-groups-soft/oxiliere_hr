from ninja import Schema
from hr.employees.schemas import EmployeeDetailOut
from ninja.orm import ModelSchema
from .models import (
    JobFamily, 
    Position, 
    Department,
    Training,
    EmployeePositionHistory,
)


# -------------  JobFamily Schemas   ---------------------
JOB_FAMILY_FIELDS = [
    'name',
    'description'
]
class JobFamilyCreateIn(ModelSchema):

    class Meta:
        model = JobFamily
        fields = JOB_FAMILY_FIELDS
        fields_optional = ['description']


class JobFamilyUpdateIn(Schema):

    class Meta:
        model = JobFamily
        fields = JOB_FAMILY_FIELDS
        fields_optional = '__all__'


class JobFamilyDetailOut(ModelSchema):

    class Meta:
        model = JobFamily
        fields = [
            'id',
            JOB_FAMILY_FIELDS
        ]


#--------------------  Position Schemas   ------------------
POSITION_FIELDS = [
    'name',
    'level'
    'description',
]
class PositionCreateIn(Schema):
    
    class Meta:
        model = Position
        fields = [
            'job_family_id',
            *POSITION_FIELDS
        ]
        fields_optional = ['level', 'description']


class PositionUpdateIn(ModelSchema):

    class Meta:
        model = Position
        fields = [
            'job_family_id',
            *POSITION_FIELDS
        ]
        fields_optional = '__all__'


class PositionDetailOut(ModelSchema):
    job_family: JobFamilyDetailOut

    class Meta:
        model = Position
        fields = [
            'id',
            'job_family',
            *POSITION_FIELDS
        ]

# ----------------------------------------------------------
# Department Schemas
# ----------------------------------------------------------
DEPARTMENT_FIELDS = [
    'name',
    'description',
]
class DepartmentCreateIn(ModelSchema):

    class Meta:
        model = Department
        fields = [
            'manager_id',
            *DEPARTMENT_FIELDS
        ]
        fields_optional = [
            'manager_id',
            'description'
        ]


class DepartmentUpdateIn(ModelSchema):
    
    class Meta:
        model = Department
        fields = [
            'manager_id',
            *DEPARTMENT_FIELDS
        ]
        fields_optional = '__all__'


class DepartementDetailOut(ModelSchema):
    manager: EmployeeDetailOut

    class Meta:
        model = Department
        fields = [
            'id',
            'manager',
            *DEPARTMENT_FIELDS
        ]


# ---------------   EmployeePositionHistory Schemas   --------------
EMPL_POS_HIST_FIELDS = [
    'start_date',
    'end_date',
    'description'
]
class EmployeePositionHistoryCreateIn(ModelSchema):

    class Meta:
        model = EmployeePositionHistory
        fields = [
            'employee_id',
            'position_id',
            *EMPL_POS_HIST_FIELDS
        ]
        fields_optional = [
            'description',
            'start_date',
            'end_date'
        ]


class EmployeePositionHistoryUpdateIn(ModelSchema):

    class Meta:
        model = EmployeePositionHistory
        fields = [
            'employee_id',
            'position_id',
            *EMPL_POS_HIST_FIELDS
        ]
        fields_optional = '__all__'


class EmployeePositionHistoryDetailOut(ModelSchema):
    employee: EmployeeDetailOut
    position: PositionDetailOut

    class Meta:
        model = EmployeePositionHistory
        fields = [
            'id',
            'employee',
            'position',
            *EMPL_POS_HIST_FIELDS
        ]


# -----------------   Training Schemas   -------------------
TRAINING_FIELDS = [
    'name',
    'institute',
    'start_date',
    'end_date',
    'location',
    'description'
]
class TrainingCreateIn(ModelSchema):

    class Meta:
        model = Training
        fields = [
            'employee_id',
            *TRAINING_FIELDS
        ]
        fields_optional = [
            'institute',
            'start_date',
            'end_date',
            'location',
            'description'
        ]


class TrainingUpdateIn(ModelSchema):
    
    class Meta:
        model = Training
        fields = [
            'employee_id',
            *TRAINING_FIELDS
        ]
        fields_optional = '__all__'


class TrainingDetailOut(ModelSchema):
    employee: EmployeeDetailOut

    class Meta:
        model = Training
        fields = [
            'id',
            'employee',
            *TRAINING_FIELDS
        ]