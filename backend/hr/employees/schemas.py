from __future__ import annotations
from typing import Optional, List
from datetime import date
from pydantic import Field as PydanticField

from ninja import Field, Schema
from ninja.orm import ModelSchema
from django.db.models import Q

from hr.schemas import BaseFilter, LightUserOut
from hr.employees.models import (
    Employee,
    EmployeeAddress,
    EmployeeChild,
    EmployeeEducation,
    EmergencyContact,
    EmployeeDocument,
    StatusHistory,
    WorkSite
)


#  -------- Employee Document Schemas -------- 

class EmployeeDocumentCreate(ModelSchema):
    """ Upload legal or academic documents. """
    class Meta:
        model = EmployeeDocument
        fields = [
            "document_type", 
            "document_number", 
            "issue_date", 
            "expiry_date"
        ]


class EmployeeDocumentOut(ModelSchema):
    class Meta:
        model = EmployeeDocument
        fields = [
            "id",
            "document_type", 
            "document_number", 
            "issue_date",
            "expiry_date", 
            "file", 
            "is_verified"
        ]


#  -------- Employee Address Schemas -------- 

class EmployeeAddressCorrectIn(ModelSchema):
    """ Correct an existing address record. """
    class Meta:
        model = EmployeeAddress
        fields = [
            "number",
            "street",
            "municipality",
            "city",
            "province",
            "country",
            "country_code",
            "move_in_date",
            "move_out_date",
        ]
        # All fields are optionals
        fields_optional = "__all__"


class EmployeeAddressOut(ModelSchema):
    class Meta:
        model = EmployeeAddress
        fields = [
            "id", 
            "number", 
            "street", 
            "municipality", 
            "city", 
            "province", 
            "country", 
            "country_code", 
            "is_current", 
            "move_in_date", 
            "move_out_date",
        ]


class EmployeeAddressMoveIn(ModelSchema):
    """ Record a change of residence. """
    class Meta:
        model = EmployeeAddress
        fields = [
            "number", 
            "street", 
            "municipality", 
            "city", 
            "province", 
            "country", 
            "country_code", 
            "move_in_date"
        ]


#  -------- Employee Children Schemas -------- 

class EmployeeChildCreate(ModelSchema):
    class Meta:
        model = EmployeeChild
        fields = [
            "first_name", 
            "middle_name", 
            "last_name", 
            "is_dependent", 
            "gender", 
            "birthdate"
        ]


class EmployeeChildOut(ModelSchema):
    class Meta:
        model = EmployeeChild
        fields = [
            "id", 
            "first_name", 
            "middle_name", 
            "last_name", 
            "gender", 
            "birthdate", 
            "is_dependent"
        ]


#  -------- Employee Education Schemas -------- 

class EmployeeEducationCreate(ModelSchema):
    class Meta:
        model = EmployeeEducation
        fields = [
            "institute", 
            "degree", 
            "major", 
            "start_year", 
            "end_year", 
            "location"
        ]


class EmployeeEducationUpdate(EmployeeEducationCreate):
    class Meta(EmployeeEducationCreate.Meta):
        fields_optional = '__all__'


class EmployeeEducationOut(ModelSchema):
    class Meta:
        model = EmployeeEducation
        fields = [
            "id", 
            "institute", 
            "degree", 
            "major", 
            "start_year", 
            "end_year", 
            "location"
        ]


#  -------- Employee Emergency Contact Schemas -------- 

class EmergencyContactCreate(ModelSchema):
    class Meta:
        model = EmergencyContact
        fields = [
            "first_name", 
            "middle_name", 
            "last_name", 
            "phone", 
            "relation", 
            "priority"
        ]


class EmergencyContactUpdate(ModelSchema):
    class Meta:
        model = EmergencyContact
        fields = [
            "first_name", 
            "middle_name", 
            "last_name", 
            "phone", 
            "relation", 
            "priority"
        ]
        fields_optional = '__all__'


class EmergencyContactOut(ModelSchema):
    class Meta:
        model = EmergencyContact
        fields = [
            "id", 
            "first_name", 
            "middle_name", 
            "last_name", 
            "phone", 
            "relation", 
            "priority"
        ]


#  -------- Employee Schemas -------- 

class StatusHistoryOut(ModelSchema):
    """ Intention: Historical timeline of status changes. """
    class Meta:
        model = StatusHistory
        fields = [
            "id", 
            "status", 
            "start_date", 
            "end_date", 
            "reason"
        ]


class EmployeeCreate(ModelSchema):
    """ Onboarding a new employee. """
    class Meta:
        model = Employee
        fields = [
            "first_name", 
            "middle_name", 
            "last_name",
            "email", 
            "phone", 
            "gender", 
            "birthdate",
            "nationality", 
            "marital_status", 
            "hire_date", 
            "description",
        ]


class EmployeeUpdate(ModelSchema):
    """ Update core identification and civil status. """
    class Meta:
        model = Employee
        fields = [
            "first_name", 
            "middle_name", 
            "last_name",
            "email", 
            "phone", 
            "gender", 
            "birthdate",
            "nationality", 
            "marital_status", 
            "description",
        ]
        fields_optional = "__all__"


class EmployeeStatusUpdate(Schema):
    """ Manual status change with effective date. """
    new_status: str
    effective_date: date
    reason: Optional[str] = None
    is_active: Optional[bool] = None
    can_connect: Optional[bool] = None
    

#  -------- Employee Lifecycle Schemas -------- 

class EmployeeStatusIn(Schema):
    """ Employment status evolution. """
    new_status: str
    effective_date: date
    reason: Optional[str] = None


class EmployeeSuspensionIn(Schema):
    """ Administrative or disciplinary suspension. """
    reason: str
    effective_date: Optional[date] = Field(default_factory=date.today)


class EmployeeReactiveIn(Schema):
    """ Reactivate a previously inactive employee. """
    effective_date: Optional[date] = Field(default_factory=date.today)
    reason: Optional[str] = None
    is_active: Optional[bool] = Field(default=True)
    can_connect: Optional[bool] = None


class EmployeeOffboardingIn(Schema):
    """ Permanent company exit. """
    end_date: date
    reason: str


#  -------- Employee List & Detail -------- 

class EmployeeFullProfileOut(ModelSchema):
    """ Complete HR dossier for detailed view. """
    addresses: List[EmployeeAddressOut]
    children: List[EmployeeChildOut]
    educations: List[EmployeeEducationOut]
    emergency_contacts: List[EmergencyContactOut]
    documents: List[EmployeeDocumentOut]
    user: Optional[LightUserOut] = None
    current_address: Optional["EmployeeAddressOut"] = None
    current_status: Optional["StatusHistoryOut"] = None
    status_history: List[StatusHistoryOut] = PydanticField(default_factory=list)

    class Meta:
        model = Employee
        fields = [
            "id", 
            "matricule", 
            "first_name", 
            "middle_name", 
            "last_name",
            "email", 
            "phone", 
            "gender", 
            "birthdate", 
            "nationality",
            "marital_status", 
            "description", 
            "hire_date", 
            "termination_date",
            "is_active", 
            "can_connect",
        ]


class EmployeeOut(ModelSchema):
    """ Concise profile for directory listings. """
        
    class Meta:
        model = Employee
        fields = [
            "id", 
            "matricule", 
            "first_name", 
            "middle_name",
            "last_name", 
            "email", 
            "gender",
            "phone", 
            "is_active"
        ]


class EmployeeFilterIn(BaseFilter):
    """ Filtering criteria for workforce directory. """
    
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    is_active: Optional[bool] = Field(None, alias="active_only")
    
    # Specific specialized filters
    # We use 'addresses__is_current=True' to ensure we filter by their current location
    city: Optional[str] = Field(None, q="addresses__city__icontains")
    province: Optional[str] = Field(None, q="addresses__province__icontains")
    
    # Filter by Academic Level (using our new AcademicLevel Enum)
    degree: Optional[str] = Field(None, q="educations__degree")

    def filter_search(self, value: str) -> Q:
        """
        Broad global search across primary fields and related models.
        """
        search_query = (
            # Search In Core Identity
            Q(first_name__icontains=value) | 
            Q(last_name__icontains=value) |
            Q(middle_name__icontains=value) |
            Q(matricule__icontains=value) |
            Q(email__icontains=value) |
            Q(phone__icontains=value)
        )
        
        return search_query


#  -------- Work site --------

class WorkSiteOut(ModelSchema):
    employees: list[EmployeeOut]
    
    class Meta:
        model = WorkSite
        fields = [
            'id',
            'name',
            'latitude',
            'longitude',
            'allowed_radius'
        ]
 
class WorkSiteCreateIn(ModelSchema):
     class Meta:
         model = WorkSite
         fields = [
            'name',
            'latitude',
            'longitude',
            'allowed_radius'         
         ]

class WorkSiteUpdateIn(ModelSchema):
    class Meta:
        model = WorkSite
        fields = [
            'name',
            'latitude',
            'longitude',
            'allowed_radius'
        ]
        fields_optional = '__all__'

class WorkSiteFilterIn(BaseFilter):
    
    def filter_search(self, value: str) -> Q:
        return Q(name__icontains=value)

