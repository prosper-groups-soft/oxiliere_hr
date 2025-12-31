from typing import Optional
from datetime import date
from ninja.orm import ModelSchema
from ninja import Field
from django.db.models import Q
from utils_mixins.schemas import LightUserDetailOut, BaseFilter
from .models import (
    EmployeeAddress,
    Employee,
    EmployeeEducation,
    EmployeeChildren,
    EmployeeEmergencyContact,
)
<<<<<<< HEAD

# ------------------ FIELD DICTIONARY --------------------
MODEL_FIELDS = {
    "address": [
        "number", 
        "street", 
        "municipality", 
        "city", 
        "province", 
        "country", 
        "country_code"
    ],
    "employee": [
        "first_name", 
        "middle_name", 
        "last_name", 
        "matricule", 
        "email", 
        "phone",
        "gender", 
        "birthdate", 
        "is_active", 
        "marital_status", 
        "description",
        "can_connect", 
        "user", 
        "address"
    ],
    "children": [
        "first_name", 
        "middle_name", 
        "last_name", 
        "gender", 
        "birthdate",
        "parent"
    ],
    "education": [
        "institute", 
        "degree", 
        "major", 
        "start_year", 
        "end_year", 
        "location"
    ],
    "emergency_contact": [
        "first_name", 
        "middle_name", 
        "last_name", 
        "phone", 
        "relation", 
        "priority"
    ],
}
=======
from hr.schemas import LightUserDetailOut
from datetime import date
from hr.schemas import BaseSearchFilter
>>>>>>> d9d914b (add: oxiliere tenant)


# ------------------ Address Schemas --------------------
class EmployeeAddressCreateIn(ModelSchema):

    class Meta:
        model = EmployeeAddress
        fields = MODEL_FIELDS["address"]
        fields_optional = "__all__"


class EmployeeAddressUpdateIn(EmployeeAddressCreateIn):
    pass


class EmployeeAddressDetailOut(ModelSchema):

    class Meta:
        model = EmployeeAddress
        fields = ["id"] + MODEL_FIELDS["address"]


# ------------------ Employee Schemas -------------------
class EmployeeCreateIn(ModelSchema):

    class Meta:
        model = Employee
        fields = MODEL_FIELDS["employee"]
        fields_optional = ["user", "address", "matricule"]


class EmployeeUpdateIn(ModelSchema):

    class Meta:
        model = Employee
        fields = MODEL_FIELDS["employee"]
        fields_optional = "__all__"


class EmployeeDetailOut(ModelSchema):
    user: Optional[LightUserDetailOut] = None
    address: Optional[EmployeeAddressDetailOut] = None

    class Meta:
        model = Employee
        fields = ["id"] + MODEL_FIELDS["employee"]


class EmployeeListOut(ModelSchema):
    user: Optional[LightUserDetailOut] = None

    class Meta:
        model = Employee
        fields = ["id"] + [f for f in MODEL_FIELDS["employee"] if f != "address"]


class EmployeeFullProfileOut(EmployeeDetailOut):
    children: list["EmployeeChildrenDetailOut"]
    educations: list["EmployeeEducationDetailOut"]
    emergency_contacts: list["EmployeeEmergencyContactDetailOut"]


class EmployeeFilterIn(BaseFilter):
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    is_active: Optional[bool] = Field(None, alias="active_only")
    born_before: Optional[date] = Field(None, q="birthdate__lte")
    born_after: Optional[date] = Field(None, q="birthdate__gte")

    def filter_search(self, value: str) -> Q:
        return Q(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(middle_name__icontains=value) |
            Q(email__icontains=value) |
            Q(phone__icontains=value)
        )


# ------------------ Emergency Contact Schemas -----------
class EmployeeEmergencyContactCreateIn(ModelSchema):

    class Meta:
        model = EmployeeEmergencyContact
        fields = MODEL_FIELDS["emergency_contact"]
        fields_optional = ["phone", "relation", "middle_name", "priority"]


class EmployeeEmergencyContactUpdateIn(ModelSchema):

    class Meta:
        model = EmployeeEmergencyContact
        fields = MODEL_FIELDS["emergency_contact"]
        fields_optional = "__all__"


class EmployeeEmergencyContactDetailOut(ModelSchema):

    class Meta:
        model = EmployeeEmergencyContact
        fields = ["id"] + MODEL_FIELDS["emergency_contact"]


class EmployeeEmergencyContactFilterIn(BaseFilter):

    def filter_search(self, value: str) -> Q:
        return Q(
            Q(first_name__icontains=value) |
            Q(middle_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(phone__icontains=value)
        )


# ------------------ Children Schemas -------------------
class EmployeeChildrenCreateIn(ModelSchema):

    class Meta:
        model = EmployeeChildren
        fields = [f for f in MODEL_FIELDS["children"] if f != "parent"]
        fields_optional = ["middle_name", "birthdate", "gender"]


class EmployeeChildrenUpdateIn(ModelSchema):

    class Meta:
        model = EmployeeChildren
        fields = MODEL_FIELDS["children"]
        fields_optional = "__all__"


class EmployeeChildrenDetailOut(ModelSchema):

    class Meta:
        model = EmployeeChildren
        fields = ["id"] + MODEL_FIELDS["children"]


class EmployeeChildrenFilterIn(BaseFilter):

    gender: Optional[str] = None

    def filter_search(self, value: str) -> Q:
        return Q(
            Q(first_name__icontains=value) |
            Q(middle_name__icontains=value) |
            Q(last_name__icontains=value)
        )


# ------------------ Education Schemas ------------------
class EmployeeEducationCreateIn(ModelSchema):

    class Meta:
        model = EmployeeEducation
        fields = MODEL_FIELDS["education"]
        fields_optional = ["degree", "major"]


class EmployeeEducationUpdateIn(ModelSchema):

    class Meta:
        model = EmployeeEducation
        fields = MODEL_FIELDS["education"]
        fields_optional = "__all__"


class EmployeeEducationDetailOut(ModelSchema):

    class Meta:
        model = EmployeeEducation
        fields = ["id"] + MODEL_FIELDS["education"]


class EmployeeEducationFilterIn(BaseFilter):

    degree: Optional[str] = None

    def filter_search(self, value: str) -> Q:
        return Q(
            Q(institute__icontains=value) |
            Q(major__icontains=value) |
            Q(location__icontains=value)
        )

