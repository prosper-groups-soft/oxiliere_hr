from ninja.orm import ModelSchema
from .models import (
    EmployeeAddress,
    Employee,
    EmployeeEducation,
    EmployeeChildren,
    EmployeeEmergencyContact,
)
from utils_mixins.schemas import LightUserDetailOut


# ---------------------  Address Schemas  -----------------------
EMPL_ADDR_FIELDS = [
    'number',
    'street',
    'municipality',
    'city',
    'province',
    'country',
    'country_code',
]
class EmployeeAddressCreateIn(ModelSchema):
    
    class Meta:
        model = EmployeeAddress
        fields = EMPL_ADDR_FIELDS
        fields_optional = '__all__'


class EmployeeAddressUpdateIn(ModelSchema):
    
    class Meta:
        model = EmployeeAddress
        fields = EMPL_ADDR_FIELDS
        fields_optional = '__all__'


class EmployeeAddressDetailOut(ModelSchema):
    
    class Meta:
        model = EmployeeAddress
        fields = [
            'id',
            *EMPL_ADDR_FIELDS
        ]

        
# -----------------  Employee Schemas  ----------------------
EMPL_FIELDS = [
    'first_name',
    'middle_name',
    'last_name',
    'matricule',
    'email',
    'phone',
    'gender',
    'birthdate',
    'is_active',
    'marital_status',
    'status',
    'photo',
    'description',
    'can_connect',
]
class EmployeeCreateIn(ModelSchema):


    class Meta:
        model = Employee
        fields = [
            'user_id',
            'address_id',
            *EMPL_FIELDS
        ]
        fields_optional = [
            'user_id',
            'address_id'
        ]


class EmployeeUpdateIn(ModelSchema):
    
    class Meta:
        model = Employee
        fields = [
            'user_id',
            'address_id',
            *EMPL_FIELDS
        ]
        fields_optional = '__all__'


class EmployeeDetailOut(ModelSchema):

    user: LightUserDetailOut
    address: EmployeeAddressDetailOut

    class Meta:
        model = Employee
        fields = [
            'id',
            'user',
            'address'
            *EMPL_FIELDS
        ]


# ----------------  Emergency Contact Schemas  ---------------
EMPL_EMERG_CONTACT_FIEDS = [
    'first_name',
    'middle_name',
    'last_name',
    'phone',
    'relation',
    'priority',
]
class EmployeeEmergencyContactCreateIn(ModelSchema):
    
    class Meta:
        model = EmployeeEmergencyContact
        fields = [
            'employee_id',
            *EMPL_EMERG_CONTACT_FIEDS
        ]
        fields_optional = [
            'phone',
            'relation',
            'middle_name',
            'priority',
        ]


class EmployeeEmergencyContactUpdateIn(ModelSchema):

    class Meta:
        model = EmployeeEmergencyContact
        fields = [
            'employee_id',
            *EMPL_EMERG_CONTACT_FIEDS
        ]
        fields_optional = '__all__'


class EmployeeEmergencyContactDetailOut(ModelSchema):
    employee: EmployeeDetailOut

    class Meta:
        model = EmployeeEmergencyContact
        fields = [
            'id',
            'employee',
            *EMPL_EMERG_CONTACT_FIEDS,
        ]


# ----------------  Children Schemas  ------------------------
EMPL_CHILDREN_FIELDS = [
    'first_name',
    'middle_name',
    'last_name',
    'gender',
    'birthdate',
]
class EmployeeChildrenCreateIn(ModelSchema):
    
    class Meta:
        model = EmployeeChildren
        fields = [
            'parent_id'
            *EMPL_CHILDREN_FIELDS
        ]
        fields_optional = [
            'middle_name',
            'birthdate',
            'gender',
        ]


class EmployeeChildrenUpdateIn(ModelSchema):
    
    class Meta:
        model = EmployeeChildren
        fields = [
            'parent_id',
            *EMPL_CHILDREN_FIELDS
        ]
        fields_optional = '__all__'


class EmployeeChildrenDetailOut(ModelSchema):
    parent: EmployeeDetailOut

    class Meta:
        model = EmployeeChildren
        fields = [
            'id',
            'parent',
            *EMPL_CHILDREN_FIELDS
        ]


# ----------------  Education Schemas   ---------------------
EMPL_EDUCATION_FIELDS = [
    'institute',
    'degree',
    'major',
    'start_year',
    'end_year',
    'location'
]
class EmployeeEducationCreateIn(ModelSchema):
    
    class Meta:
        model = EmployeeEducation
        fields = [
            'employee_id',
            *EMPL_EDUCATION_FIELDS
        ]
        fields_optional = ['degree']


class EmployeeEducationUpdateIn(ModelSchema):
    
    class Meta:
        model = EmployeeEducation
        fields = [
            'employee_id',
            *EMPL_EDUCATION_FIELDS
        ]
        fields_optional = '__all__'


class EmployeeEducationDetailOut(ModelSchema):
    employee: EmployeeDetailOut

    class Meta:
        model = EmployeeEducation
        fields = [
            'id',
            'employee',
            *EMPL_EDUCATION_FIELDS
        ]

      