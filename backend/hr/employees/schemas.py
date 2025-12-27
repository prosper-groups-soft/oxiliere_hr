from typing import Optional
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
        fields = ['id'] + EMPL_ADDR_FIELDS

        
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
    'description',
    'can_connect',
    'user',
    'address',
]
class EmployeeCreateIn(ModelSchema):


    class Meta:
        model = Employee
        fields = EMPL_FIELDS
        fields_optional = ['user', 'address', 'matricule']


class EmployeeUpdateIn(ModelSchema):
    
    class Meta:
        model = Employee
        fields = EMPL_FIELDS
        fields_optional = '__all__'


class EmployeeDetailOut(ModelSchema):

    user: Optional[LightUserDetailOut] = None
    address: Optional[EmployeeAddressDetailOut] = None

    class Meta:
        model = Employee
        fields = ['id'] + EMPL_FIELDS
        
        

class EmployeeListOut(ModelSchema):
    user: Optional[LightUserDetailOut] = None
    
    class Meta:
        model = Employee
        fields = ['id'] + [f for f in EMPL_FIELDS if f != 'address']


class EmployeeFullProfileOut(EmployeeDetailOut):
    children: list['EmployeeChildrenDetailOut']
    educations: list['EmployeeEducationDetailOut']
    emergency_contacts: list['EmployeeEmergencyContactDetailOut']


# ----------------  Emergency Contact Schemas  ---------------
EMPL_EMERG_CONTACT_FIEDS = [
    'first_name',
    'middle_name',
    'last_name',
    'phone',
    'relation',
    'priority'
]
class EmployeeEmergencyContactCreateIn(ModelSchema):
    
    class Meta:
        model = EmployeeEmergencyContact
        fields = EMPL_EMERG_CONTACT_FIEDS
        fields_optional = [
            'phone',
            'relation',
            'middle_name',
            'priority',
        ]


class EmployeeEmergencyContactUpdateIn(ModelSchema):

    class Meta:
        model = EmployeeEmergencyContact
        fields = EMPL_EMERG_CONTACT_FIEDS
        
        fields_optional = '__all__'


class EmployeeEmergencyContactDetailOut(ModelSchema):

    class Meta:
        model = EmployeeEmergencyContact
        fields = ['id'] + EMPL_EMERG_CONTACT_FIEDS


# ----------------  Children Schemas  ------------------------
EMPL_CHILDREN_FIELDS = [
    'first_name',
    'middle_name',
    'last_name',
    'gender',
    'birthdate',
    'parent',
]
class EmployeeChildrenCreateIn(ModelSchema):
    
    class Meta:
        model = EmployeeChildren
        fields = [ f for f in EMPL_CHILDREN_FIELDS if f != "parent"]
        fields_optional = [
            'middle_name',
            'birthdate',
            'gender',
        ]


class EmployeeChildrenUpdateIn(ModelSchema):
    
    class Meta:
        model = EmployeeChildren
        fields = EMPL_CHILDREN_FIELDS
        
        fields_optional = '__all__'


class EmployeeChildrenDetailOut(ModelSchema):

    class Meta:
        model = EmployeeChildren
        fields = ['id'] + EMPL_CHILDREN_FIELDS


# ----------------  Education Schemas   ---------------------
EMPL_EDUCATION_FIELDS = [
    'institute',
    'degree',
    'major',
    'start_year',
    'end_year',
    'location',
]
class EmployeeEducationCreateIn(ModelSchema):
    
    class Meta:
        model = EmployeeEducation
        fields = EMPL_EDUCATION_FIELDS
        fields_optional = ['degree', 'major']


class EmployeeEducationUpdateIn(ModelSchema):
    
    class Meta:
        model = EmployeeEducation
        fields = EMPL_EDUCATION_FIELDS
        fields_optional = '__all__'


class EmployeeEducationDetailOut(ModelSchema):

    class Meta:
        model = EmployeeEducation
        fields = ['id'] + EMPL_EDUCATION_FIELDS

      