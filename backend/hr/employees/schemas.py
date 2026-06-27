from __future__ import annotations
from typing   import Optional, List
from datetime import date
from uuid     import UUID
from decimal  import Decimal
from pydantic import Field as PydanticField

from ninja import Field, Schema
from ninja.orm import ModelSchema
from django.db.models import Q, Exists, OuterRef

from oxutils.permissions.models import UserGroup, Grant

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
from hr.payroll.models import EmployeeContract
from hr.jobs.models    import EmployeePositionHistory
from hr.attendance.models import EmploymentScheme


def _get_current_pos(obj):
    """Extract the current position from prefetch, or fall back to the latest position."""
    positions = getattr(obj, 'prefetched_current_position', [])
    if positions:
        return positions[0]
    # Offboarded employees: no is_current=True, use last known position
    latest = obj.position_history.order_by('-start_date').first()
    return latest


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
        fields_optional = [
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
class EmployeeAddressCreate(ModelSchema):
    """ Create a new address during onboarding (optional). """
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
        ]
        # All fields are optionals for onboarding
        fields_optional = "__all__"


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
            "is_primary"
        ]
        fields_optional = [
            "middle_name",
            "last_name",
            "is_primary"
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
            "is_primary"
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
            "is_primary",
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
            "reason",
            "created_at"
        ]


class PositionHistoryOut(ModelSchema):
    position_name: str = PydanticField(..., alias="position.name")
    seniority_label: Optional[str] = PydanticField(None, alias="seniority_level.label")
    org_unit_name: Optional[str] = PydanticField(None, alias="org_unit.name")

    class Meta:
        model = EmployeePositionHistory
        fields = ["id", "start_date", "end_date", "is_current", "description", "created_at"]


class EmployeeCreate(ModelSchema):
    """ Creation of a new employee profile. """
    create_account: bool = False
    group_slug: Optional[str] = None
    description: Optional[str] = None
    work_site_id: Optional[UUID] = PydanticField(default=None, alias="work_site")
    initial_status: Optional[str] = PydanticField(default="PROBATION", description="Initial status: PROBATION or ACTIVE")

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
        ]
        fields_optional = [
            "middle_name",
            "phone",
            "gender",
            "birthdate",
            "nationality",
            "marital_status",
        ]


class EmployeeUpdate(ModelSchema):
    """ Update core identification and civil status. """
    work_site_id: Optional[UUID] = PydanticField(default=None, alias="work_site")
    address: Optional[EmployeeAddressCreate] = None

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
    departure_type: str = 'TERMINATED'  # TERMINATED, RESIGNED, RETIRED
    reason: str


class EmployeeOnboardingContractIn(Schema):
    """Input schema for creating employee contract during onboarding."""
    position_id: UUID
    seniority_level_id: UUID
    base_salary: Decimal
    contract_type: str  # CDI, CDD, FREELANCE, INTERN
    remuneration_type: str = "FIXED"  # FIXED, HOURLY, GROSS_UP
    payment_period: str = "MONTHLY"  # MONTHLY, BIWEEKLY, WEEKLY
    salary_base_type: str = "NET"  # GROSS, NET
    start_date: date
    end_date: Optional[date] = None
    currency: str = "CDF"
    is_active: bool = True
    

class ContractOut(ModelSchema):
    """Output schema for retrieving employee contract details."""
    class Meta:
        model = EmployeeContract
        fields = [
            "id",
            "remuneration_type",
            "payment_period",
            "contract_type",
            "base_salary",
            "salary_base_type",
            "hourly_rate",
            "currency",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]


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
    position_history: List[PositionHistoryOut] = PydanticField(default_factory=list)
    work_site: Optional[str] = None
    work_site_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    current_contract: Optional[ContractOut] = None
    job_title: Optional[str] = None
    seniority_level: Optional[str] = None
    seniority_level_id: Optional[UUID] = None
    org_unit: Optional[str] = None
    org_unit_id: Optional[UUID] = None
    org_unit_type: Optional[str] = None

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
            "profile_photo",
        ]

    @staticmethod
    def resolve_work_site(obj):
        return obj.work_site.name if obj.work_site else None

    @staticmethod
    def resolve_work_site_id(obj):
        return obj.work_site.id if obj.work_site else None

    @staticmethod
    def resolve_current_contract(obj):
        contracts = getattr(obj, 'prefetched_latest_contract', [])
        if contracts and len(contracts) > 0:
            return contracts[0]
        return None

    @staticmethod
    def resolve_current_status(obj):
        # We look for the prefetched_current_status which is ordered by -created_at
        status_list = getattr(obj, 'prefetched_current_status', [])
        if status_list and len(status_list) > 0:
            return status_list[0]
        return None

    @staticmethod
    def resolve_status_history(obj):
        return obj.status_history.order_by('-created_at')

    @staticmethod
    def resolve_job_title(obj):
        pos = _get_current_pos(obj)
        return pos.position.name if pos and pos.position else None

    @staticmethod
    def resolve_position_id(obj):
        pos = _get_current_pos(obj)
        return pos.position.id if pos and pos.position else None

    @staticmethod
    def resolve_seniority_level(obj):
        pos = _get_current_pos(obj)
        return pos.seniority_level.label if pos and pos.seniority_level else None

    @staticmethod
    def resolve_seniority_level_id(obj):
        pos = _get_current_pos(obj)
        return pos.seniority_level.id if pos and pos.seniority_level else None

    @staticmethod
    def resolve_org_unit(obj):
        pos = _get_current_pos(obj)
        return pos.org_unit.name if pos and pos.org_unit else None

    @staticmethod
    def resolve_org_unit_id(obj):
        pos = _get_current_pos(obj)
        return pos.org_unit.id if pos and pos.org_unit else None

    @staticmethod
    def resolve_org_unit_type(obj):
        pos = _get_current_pos(obj)
        return getattr(pos.org_unit, 'type', None) if pos and pos.org_unit else None

    @staticmethod
    def resolve_position_history(obj):
        return obj.position_history.all().order_by('-start_date')


class EmployeeOut(ModelSchema):
    """ Enriched employee profile using Ninja resolvers. """

    # On définit les champs additionnels
    job_title: Optional[str] = None
    org_unit: Optional[str] = None
    org_unit_id: Optional[str] = None
    org_unit_type: Optional[str] = None
    position_id: Optional[str] = None
    contract_type: Optional[str] = None
    work_site: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    avatar_url: Optional[str] = None
    current_status: Optional[StatusHistoryOut] = None

    class Meta:
        model = Employee
        fields = [
            "id", "matricule", "first_name", "middle_name",
            "last_name", "email", "gender", "phone",
            "is_active", "hire_date", "termination_date",
            "profile_photo",
        ]

    # --- RESOLVERS ---
    # Django Ninja appelle automatiquement resolve_<field_name> 
    # en passant l'instance du modèle (obj)

    @staticmethod
    def resolve_current_status(obj):
        # We look for the prefetched_current_status which is ordered by -created_at
        status_list = getattr(obj, 'prefetched_current_status', [])
        if status_list and len(status_list) > 0:
            return status_list[0]
        return None

    @staticmethod
    def resolve_job_title(obj):
        pos = _get_current_pos(obj)
        return pos.position.name if pos and pos.position else None

    @staticmethod
    def resolve_position_id(obj):
        pos = _get_current_pos(obj)
        return str(pos.position.id) if pos and pos.position else None

    @staticmethod
    def resolve_org_unit(obj):
        pos = _get_current_pos(obj)
        return pos.org_unit.name if pos and pos.org_unit else None

    @staticmethod
    def resolve_org_unit_id(obj):
        pos = _get_current_pos(obj)
        return str(pos.org_unit.id) if pos and pos.org_unit else None

    @staticmethod
    def resolve_org_unit_type(obj):
        pos = _get_current_pos(obj)
        return getattr(pos.org_unit, 'type', None) if pos and pos.org_unit else None

    @staticmethod
    def resolve_contract_type(obj):
        contracts = getattr(obj, 'prefetched_latest_contract', [])
        return contracts[0].contract_type if contracts else None

    @staticmethod
    def resolve_work_site(obj):
        return obj.work_site.name if obj.work_site else None

    @staticmethod
    def resolve_location(obj):
        addrs = getattr(obj, 'prefetched_current_address', [])
        if addrs:
            addr = addrs[0]
            parts = [p for p in [addr.city, addr.province] if p]
            return ", ".join(parts)
        return None

    @staticmethod
    def resolve_status(obj):
        if obj.termination_date:
            return 'inactive'
        return 'active' if obj.is_active else 'inactive'

    @staticmethod
    def resolve_avatar_url(obj):
        return obj.profile_photo.url if obj.profile_photo else None
    

class EmployeeFilterIn(BaseFilter):
    """ Filtering criteria for workforce directory. """
    
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    is_active: Optional[bool] = Field(None, alias="active_only")
    
    # Org unit filter (based on current contract/position) - supports comma-separated values
    org_unit: Optional[str] = None
    
    # Status filter (employment status) - supports comma-separated values
    status: Optional[str] = None
    
    # Location filter (city from current address) - supports comma-separated values
    location: Optional[str] = None
    
    # Specific specialized filters
    # We use 'addresses__is_current=True' to ensure we filter by their current location
    city: Optional[str] = Field(None, q="addresses__city__icontains")  # type: ignore
    province: Optional[str] = Field(None, q="addresses__province__icontains")  # type: ignore
    
    # Filter by Academic Level (using our new AcademicLevel Enum)
    degree: Optional[str] = Field(None, q="educations__degree")  # type: ignore
    
    # Filter by contract type (CDI, CDD, FREELANCE, INTERN) - supports comma-separated values
    contract_type: Optional[str] = None

    # Filter by presence of active employment scheme (attendance schedule)
    has_scheme: Optional[bool] = None

    def filter_org_unit(self, value: Optional[str]) -> Q:
        """Filter by org unit ID (supports comma-separated UUIDs)."""
        if not value:
            return Q()  # No filter if value is None or empty
        if ',' in value:
            org_unit_ids = [u.strip() for u in value.split(',')]
            return Q(position_history__org_unit__id__in=org_unit_ids, position_history__is_current=True)
        return Q(position_history__org_unit__id=value, position_history__is_current=True)
    
    def filter_status(self, value: Optional[str]) -> Q:
        """Filter by current employment status (supports comma-separated values)."""
        if not value:
            return Q()  # No filter if value is None or empty
        if ',' in value:
            statuses = [s.strip() for s in value.split(',')]
            # Filter on current status (no end_date)
            return Q(status_history__status__in=statuses, status_history__end_date__isnull=True)
        return Q(status_history__status__iexact=value, status_history__end_date__isnull=True)
    
    def filter_location(self, value: Optional[str]) -> Q:
        """Filter by location/city (supports comma-separated values)."""
        if not value:
            return Q()  # No filter if value is None or empty
        if ',' in value:
            locations = [l.strip() for l in value.split(',')]
            return Q(addresses__city__in=locations)
        return Q(addresses__city__icontains=value)
    
    def filter_contract_type(self, value: Optional[str]) -> Q:
        """Filter by contract type (supports comma-separated values)."""
        if not value:
            return Q()  # No filter if value is None or empty
        if ',' in value:
            contract_types = [ct.strip() for ct in value.split(',')]
            return Q(contracts__contract_type__in=contract_types)
        return Q(contracts__contract_type__iexact=value)

    def filter_has_scheme(self, value: Optional[bool]) -> Q:
        """Filter by presence of an active EmploymentScheme (attendance schedule).
        Uses EXISTS subquery to avoid duplicate rows from JOIN.
        """
        if value is None:
            return Q()
        subquery = EmploymentScheme.objects.filter(
            employee_id=OuterRef('id'),
            is_active=True
        )
        if value:
            return Q(Exists(subquery))
        else:
            return ~Q(Exists(subquery))

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

    def apply_ordering(self, qs, ordering: Optional[str] = None):
        """
        Apply ordering to the queryset based on the ordering parameter.
        Supports: name, -name, hire_date, -hire_date, status, -status
        """
        if not ordering:
            # Default ordering by last_name, first_name
            return qs.order_by('last_name', 'middle_name', 'first_name')
        
        ordering_map = {
            'name': ['last_name', 'first_name'],
            '-name': ['-last_name', '-first_name'],
            'hire_date': ['hire_date', 'last_name'],
            '-hire_date': ['-hire_date', 'last_name'],
            'status': ['status_history__status', 'last_name'],
            '-status': ['-status_history__status', 'last_name'],
        }
        
        order_fields = ordering_map.get(ordering, ['last_name', 'middle_name', 'first_name'])
        return qs.order_by(*order_fields)


class EmployeeContractInfoUpdateIn(Schema):
    """ Unified schema for updating both position/seniority and contract terms. """
    # Career Positioning
    position_id: Optional[UUID] = None
    seniority_level_id: Optional[UUID] = None
    org_unit_id: Optional[UUID] = None
    effective_date: Optional[date] = None
    
    # Contract Terms
    contract_type: Optional[str] = None
    remuneration_type: Optional[str] = None
    base_salary: Optional[float] = None
    hourly_rate: Optional[float] = None
    payment_period: Optional[str] = None
    salary_base_type: Optional[str] = None
    currency: Optional[str] = None
    hire_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


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


#  -------- User Management Schemas --------

class UserOut(Schema):
    id: UUID
    oxi_id: Optional[UUID] = None  # Added for frontend compatibility
    email: str
    username: Optional[str] = None
    first_name: str
    last_name: str
    is_active: bool
    photo: Optional[str] = None  # Added for frontend compatibility
    groups: List[str]


class UserCreateIn(Schema):
    email: str
    first_name: str
    last_name: str
    password: Optional[str] = None
    is_active: bool = True
    groups: List[str] = []


class UserUpdateIn(Schema):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    groups: Optional[List[str]] = None


class UserFilter(BaseFilter):
    """Filter for user listing with search, is_active, and groups filters"""
    search: Optional[str] = None
    is_active: Optional[bool] = None
    groups: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    
    def filter_search(self, value: str) -> Q:
        """Search in first_name, last_name, email"""
        print(f"[FILTER] search value: {value!r}")
        return (
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value)
        )
    
    def filter_is_active(self, value: bool) -> Q:
        """Filter by is_active status"""
        return Q(is_active=value)
    
    def filter_groups(self, value: Optional[List[str]]) -> Q:
        """Filter users who have any of the specified group slugs"""
        if not value:
            return Q()  # Return empty Q object if no groups specified
        user_ids = UserGroup.objects.filter(
            group__slug__in=value
        ).values_list('user_id', flat=True).distinct()
        return Q(id__in=user_ids)

    def filter_roles(self, value: Optional[List[str]]) -> Q:
        """Filter users who have any of the specified roles (directly or via groups)"""
        if not value:
            return Q()
        user_ids = Grant.objects.filter(
            role__slug__in=value
        ).values_list('user_id', flat=True).distinct()
        return Q(id__in=user_ids)


class SystemUserOut(Schema):
    """Output schema matching frontend SystemUser type with nested user object"""
    id: UUID  # TenantUser ID (we'll use user.id for now)
    user: UserOut  # Nested user object
    is_owner: bool = False
    is_admin: bool = False
    status: str = "active"
    is_active: bool  # Convenience access to user.is_active
    first_name: Optional[str] = None
    last_name: Optional[str] = None

