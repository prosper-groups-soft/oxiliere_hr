from ninja    import Schema, ModelSchema
from datetime import date
from uuid   import UUID
from typing import Optional

from django.db.models import Q

from hr.schemas import BaseFilter
from hr.performance.enums  import PerformanceGoalType
from hr.performance.models import PerformanceReview


#  NESTED SCHEMAS

class GoalSchema(Schema):
    description: str
    type: PerformanceGoalType
    rating: Optional[int] = None


class SkillSchema(Schema):
    name: str
    level: int  # 1-5


#  INPUT SCHEMAS 

class PerformanceReviewCreateIn(Schema):
    employee_id: UUID
    reviewer_id: Optional[UUID] = None
    review_period_start: date
    review_period_end: date
    goals: list[GoalSchema] = []
    skills: list[SkillSchema] = []
    employee_comment: str = ""
    reviewer_comment: str = ""


class PerformanceReviewUpdateIn(Schema):
    reviewer_id: Optional[UUID] = None
    status: Optional[str] = None
    goals: Optional[list[GoalSchema]] = None
    skills: Optional[list[SkillSchema]] = None
    employee_comment: Optional[str] = None
    reviewer_comment: Optional[str] = None
    overall_rating: Optional[int] = None


#   OUTPUT SCHEMAS 

class PerformanceReviewOut(ModelSchema):
    """ Output schema aligned with real HR evaluation reports. """

    employee_name: str = ""
    reviewer_name: str = ""
    review_period_label: str = ""

    class Meta:
        model = PerformanceReview
        fields = [
            'id', 'employee', 'reviewer',
            'review_period_start', 'review_period_end',
            'status', 'goals', 'skills',
            'employee_comment', 'reviewer_comment',
            'overall_rating',
            'created_at', 'updated_at',
        ]

    @staticmethod
    def resolve_employee_name(obj: PerformanceReview) -> str:
        return str(obj.employee)

    @staticmethod
    def resolve_reviewer_name(obj: PerformanceReview) -> str:
        return str(obj.reviewer) if obj.reviewer else ""

    @staticmethod
    def resolve_review_period_label(obj: PerformanceReview) -> str:
        return f"{obj.review_period_start} / {obj.review_period_end}"


#   FILTERS

class PerformanceReviewListFilterIn(BaseFilter):
    """Filter parameters for listing performance reviews."""
    status: Optional[str] = None
    employee_id: Optional[UUID] = None

    def filter_status(self, value):
        if value:
            return Q(status=value)
        return Q()

    def filter_employee_id(self, value):
        if value:
            return Q(employee_id=value)
        return Q()
