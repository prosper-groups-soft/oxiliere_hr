from datetime import date
from uuid import UUID
from typing import Optional
from ninja import Schema, Field
from ninja.orm import ModelSchema
from django.db.models import QuerySet, Q

from hr.employees.schemas import EmployeeDetailOut
from utils_mixins.schemas import LightUserDetailOut, BaseFilter
from .models import Leave, LeaveEmployee


# ------------------ FIELD DICTIONARY --------------------
MODEL_FIELDS = {
    "leave": [
        "start_date",
        "end_date",
        "reason",
        "everyone",
        "paid",
        "leave_type",
        "status",
        "approved_at",
        "applicable_to_id",
        "approved_by",
    ],
    "leave_employee": [
        "employee_id",
        "leave_id",
        "created_by",
    ],
}


# --------------------- Leave Schemas -------------------------
class LeaveCreateIn(ModelSchema):
    """Input schema for creating a Leave record."""
    class Meta:
        model = Leave
        fields = MODEL_FIELDS["leave"]
        fields_optional = [
            "reason",
            "everyone",
            "paid",
            "leave_type",
            "status",
            "approved_at",
            "applicable_to_id",
            "approved_by",
        ]


class LeaveUpdateIn(ModelSchema):
    """Input schema for updating a Leave record."""
    class Meta:
        model = Leave
        fields = MODEL_FIELDS["leave"]
        fields_optional = "__all__"


class LeaveDetailOut(ModelSchema):
    """Output schema representing detailed leave info."""
    applicable_to: Optional[EmployeeDetailOut] = None
    approved_by: Optional[LightUserDetailOut] = None

    class Meta:
        model = Leave
        fields = ["applicable_to", "approved_by"] + MODEL_FIELDS["leave"][:-2]  # exclude IDs


class LeaveFilterIn(BaseFilter):
    """Filter schema for Leave queries."""
    status: Optional[str] = None
    leave_type: Optional[str] = None
    paid: Optional[bool] = None
    everyone: Optional[bool] = None

    approver_id: Optional[UUID] = Field(None, q="approved_by_id")
    employee_id: Optional[UUID] = Field(None, q="leaves_employees__employee_id")

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    def filter_search(self, value: str) -> Q:
        """Custom search on reason field."""
        return Q(reason__icontains=value)

    def filter_dates(self) -> Q:
        """Filter leaves that overlap with the specified date range."""
        if self.start_date and self.end_date:
            return Q(start_date__lte=self.end_date, end_date__gte=self.start_date)
        return Q()

    def filter(self, queryset: QuerySet) -> QuerySet:
        """Apply all filters including date overlap."""
        queryset = super().filter(queryset)
        if self.start_date and self.end_date:
            queryset = queryset.filter(self.filter_dates())
        return queryset.distinct()


# -------------------- LeaveEmployee Schemas --------------------
class LeaveEmployeeCreateIn(ModelSchema):
    """Input schema for creating a LeaveEmployee record."""
    class Meta:
        model = LeaveEmployee
        fields = MODEL_FIELDS["leave_employee"]
        fields_optional = ["created_by"]


class LeaveEmployeeUpdateIn(ModelSchema):
    """Input schema for updating a LeaveEmployee record."""
    class Meta:
        model = LeaveEmployee
        fields = MODEL_FIELDS["leave_employee"]
        fields_optional = "__all__"


class LeaveEmployeeDetailOut(ModelSchema):
    """Output schema representing a LeaveEmployee record with nested relations."""
    employee: EmployeeDetailOut
    leave: LeaveDetailOut
    created_by: LightUserDetailOut

    class Meta:
        model = LeaveEmployee
        fields = MODEL_FIELDS["leave_employee"]

