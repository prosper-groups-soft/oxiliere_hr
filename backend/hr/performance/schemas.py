from ninja import Schema, ModelSchema
from datetime import date, datetime
from uuid import UUID
from typing import Optional

from django.db.models import Q

from hr.schemas import BaseFilter
from hr.performance.enums import PerformanceGoalType
from hr.performance.models import (
    Campaign,
    PerformanceReview,
    Calibration,
    DevelopmentPlan,
)
from hr.jobs.models import EmployeePositionHistory


# -----------------------------------------------
#  NESTED SCHEMAS (contenus des champs JSON)
# -----------------------------------------------

class GoalSchema(Schema):
    """Objectif saisi par l'employe (auto-evaluation)."""
    description: str
    type: PerformanceGoalType
    weight: Optional[float] = None
    employee_rating: Optional[int] = None  # 1-5


class SkillSchema(Schema):
    """Competence evaluee par l'employe (auto-evaluation)."""
    name: str
    category: Optional[str] = "BEHAVIORAL"
    weight: Optional[float] = None
    employee_level: Optional[int] = None  # 1-5


class GoalManagerSchema(Schema):
    """Objectif evalue par le manager."""
    description: str
    type: PerformanceGoalType
    weight: Optional[float] = None
    manager_rating: Optional[int] = None  # 1-5
    manager_comment: Optional[str] = ""


class SkillManagerSchema(Schema):
    """Competence evaluee par le manager."""
    name: str
    category: Optional[str] = "BEHAVIORAL"
    weight: Optional[float] = None
    manager_level: Optional[int] = None  # 1-5


class DevelopmentPlanItemSchema(Schema):
    """Action d'un plan de developpement."""
    action: str
    deadline: Optional[str] = None
    status: str = "PENDING"


# -----------------------------------------------
#  CAMPAIGN SCHEMAS
# -----------------------------------------------

class CampaignCreateIn(Schema):
    name: str
    description: str = ""
    campaign_type: str
    start_date: date
    end_date: date
    submission_deadline: date
    goal_weight: float = 0.6
    skill_weight: float = 0.4
    default_goals: list[GoalSchema] = []
    default_skills: list[SkillSchema] = []
    participant_ids: list[UUID] = []
    evaluator_ids: list[UUID] = []


class CampaignUpdateIn(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    submission_deadline: Optional[date] = None
    goal_weight: Optional[float] = None
    skill_weight: Optional[float] = None
    default_goals: Optional[list[GoalSchema]] = None
    default_skills: Optional[list[SkillSchema]] = None
    participant_ids: Optional[list[UUID]] = None
    evaluator_ids: Optional[list[UUID]] = None


class ParticipantPreviewOut(Schema):
    """Apercu d'un participant dans la liste des campagnes."""
    id: UUID
    name: str = ""
    last_name: str = ""
    first_name: str = ""
    middle_name: Optional[str] = None
    job_title: Optional[str] = None
    org_unit: Optional[str] = None
    profile_photo: Optional[str] = None


class CampaignOut(ModelSchema):
    """Campagne d'evaluation -- sortie."""
    campaign_type: str
    status: str
    participant_count: int = 0
    participants_preview: list[ParticipantPreviewOut] = []
    evaluator_count: int = 0
    evaluators_preview: list[ParticipantPreviewOut] = []

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'description', 'campaign_type',
            'start_date', 'end_date', 'submission_deadline',
            'status', 'goal_weight', 'skill_weight',
            'default_goals', 'default_skills',
            'created_at', 'created_by',
        ]

    @staticmethod
    def resolve_participant_count(obj: Campaign) -> int:
        return obj.participation_records.count()

    @staticmethod
    def resolve_evaluator_count(obj: Campaign) -> int:
        return obj.evaluator_records.count()

    @staticmethod
    def resolve_status(obj: Campaign) -> str:
        return obj.status

    @staticmethod
    def resolve_campaign_type(obj: Campaign) -> str:
        return obj.campaign_type

    @staticmethod
    def resolve_participants_preview(obj: Campaign) -> list[dict]:
        result = []
        for p in obj.participation_records.select_related("employee")[:5]:
            emp = p.employee
            pos = EmployeePositionHistory.objects.filter(
                employee=emp, is_current=True
            ).select_related("position", "org_unit").first()

            result.append({
                "id": str(emp.id),
                "name": emp.full_name,
                "job_title": pos.position.name if pos and pos.position else None,
                "org_unit": pos.org_unit.name if pos and pos.org_unit else None,
                "profile_photo": emp.profile_photo.url if emp.profile_photo else None,
            })
        return result

    @staticmethod
    def resolve_evaluators_preview(obj: Campaign) -> list[dict]:
        result = []
        for p in obj.evaluator_records.select_related("employee")[:5]:
            emp = p.employee
            pos = EmployeePositionHistory.objects.filter(
                employee=emp, is_current=True
            ).select_related("position", "org_unit").first()

            result.append({
                "id": str(emp.id),
                "name": emp.full_name,
                "job_title": pos.position.name if pos and pos.position else None,
                "org_unit": pos.org_unit.name if pos and pos.org_unit else None,
                "profile_photo": emp.profile_photo.url if emp.profile_photo else None,
            })
        return result


class AddParticipantIn(Schema):
    employee_id: UUID


class AddEvaluatorIn(Schema):
    employee_id: UUID


class CampaignParticipationOut(Schema):
    id: UUID
    employee_id: UUID
    employee_name: str = ""
    campaign_id: UUID

    @staticmethod
    def resolve_employee_name(obj) -> str:
        return str(obj.employee)


# -----------------------------------------------
#  PERFORMANCE REVIEW SCHEMAS
# -----------------------------------------------

class PerformanceReviewCreateIn(Schema):
    """Creation d'une evaluation (liee a une campagne)."""
    campaign_id: UUID
    employee_id: UUID
    manager_id: Optional[UUID] = None
    goals: list[GoalSchema] = []
    skills: list[SkillSchema] = []
    employee_comment: str = ""


class PerformanceReviewUpdateEmployeeIn(Schema):
    """Mise a jour par l'employe (EMPLOYEE_DRAFT)."""
    goals: Optional[list[GoalSchema]] = None
    skills: Optional[list[SkillSchema]] = None
    employee_comment: Optional[str] = None


class PerformanceReviewUpdateManagerIn(Schema):
    """Mise a jour par le manager (MANAGER_DRAFT)."""
    goals_manager: Optional[list[GoalManagerSchema]] = None
    skills_manager: Optional[list[SkillManagerSchema]] = None
    manager_comment: Optional[str] = None
    manager_overall_score: Optional[int] = None  # Note indicative 1-5


class PerformanceReviewCalibrateIn(Schema):
    """Calibrage RH d'une evaluation."""
    calibrated_score: float
    reason: str


class DisputeReviewIn(Schema):
    """Contestation employé — motif optionnel."""
    reason: str = ""


class PerformanceReviewOut(ModelSchema):
    """Evaluation -- sortie complete."""
    campaign_id: Optional[UUID] = None
    campaign_name: str = ""
    campaign_goal_weight: float = 0.6
    campaign_skill_weight: float = 0.4
    employee_id: Optional[UUID] = None
    employee_name: str = ""
    employee_avatar: str = ""
    employee_job_title: str = ""
    employee_last_name: str = ""
    employee_middle_name: str = ""
    employee_first_name: str = ""
    manager_id: Optional[UUID] = None
    manager_name: str = ""
    manager_avatar: str = ""
    manager_last_name: str = ""
    manager_middle_name: str = ""
    manager_first_name: str = ""
    status: str

    class Meta:
        model = PerformanceReview
        fields = [
            'id', 'campaign', 'employee', 'manager',
            'status', 'disputed', 'dispute_reason',
            'goals', 'skills', 'employee_comment',
            'goals_manager', 'skills_manager',
            'manager_comment', 'manager_overall_score',
            'overall_score', 'calibrated_score',
            'employee_submitted_at', 'manager_submitted_at',
            'acknowledged_at',
            'created_at', 'updated_at',
        ]

    @staticmethod
    def resolve_campaign_id(obj: PerformanceReview) -> Optional[UUID]:
        return obj.campaign_id

    @staticmethod
    def resolve_campaign_name(obj: PerformanceReview) -> str:
        return obj.campaign.name

    @staticmethod
    def resolve_employee_id(obj: PerformanceReview) -> Optional[UUID]:
        return obj.employee_id

    @staticmethod
    def resolve_employee_name(obj: PerformanceReview) -> str:
        return obj.employee.full_name if obj.employee else ""

    @staticmethod
    def resolve_employee_avatar(obj: PerformanceReview) -> str:
        return obj.employee.profile_photo or ""

    @staticmethod
    def resolve_employee_last_name(obj: PerformanceReview) -> str:
        return obj.employee.last_name if obj.employee else ""

    @staticmethod
    def resolve_employee_middle_name(obj: PerformanceReview) -> str:
        return obj.employee.middle_name or "" if obj.employee else ""

    @staticmethod
    def resolve_employee_first_name(obj: PerformanceReview) -> str:
        return obj.employee.first_name if obj.employee else ""

    @staticmethod
    def resolve_employee_job_title(obj: PerformanceReview) -> str:
        pos = EmployeePositionHistory.objects.filter(
            employee=obj.employee, is_current=True
        ).select_related("position").first()
        return pos.position.name if pos and pos.position else ""

    @staticmethod
    def resolve_manager_id(obj: PerformanceReview) -> Optional[UUID]:
        return obj.manager_id

    @staticmethod
    def resolve_manager_name(obj: PerformanceReview) -> str:
        return str(obj.manager) if obj.manager else ""

    @staticmethod
    def resolve_manager_avatar(obj: PerformanceReview) -> str:
        return obj.manager.profile_photo or "" if obj.manager else ""

    @staticmethod
    def resolve_manager_last_name(obj: PerformanceReview) -> str:
        return obj.manager.last_name if obj.manager else ""

    @staticmethod
    def resolve_manager_middle_name(obj: PerformanceReview) -> str:
        return obj.manager.middle_name or "" if obj.manager else ""

    @staticmethod
    def resolve_manager_first_name(obj: PerformanceReview) -> str:
        return obj.manager.first_name if obj.manager else ""

    @staticmethod
    def resolve_status(obj: PerformanceReview) -> str:
        return obj.status

    @staticmethod
    def resolve_campaign_goal_weight(obj: PerformanceReview) -> float:
        return obj.campaign.goal_weight if obj.campaign else 0.6

    @staticmethod
    def resolve_campaign_skill_weight(obj: PerformanceReview) -> float:
        return obj.campaign.skill_weight if obj.campaign else 0.4


# -----------------------------------------------
#  CALIBRATION SCHEMAS
# -----------------------------------------------

class CalibrationOut(ModelSchema):
    """Calibrage RH -- sortie."""
    calibrated_by_name: str = ""

    class Meta:
        model = Calibration
        fields = [
            'id', 'evaluation', 'original_score',
            'calibrated_score', 'reason', 'calibrated_by',
            'calibrated_at',
        ]

    @staticmethod
    def resolve_calibrated_by_name(obj: Calibration) -> str:
        return str(obj.calibrated_by) if obj.calibrated_by else ""


# -----------------------------------------------
#  DEVELOPMENT PLAN SCHEMAS
# -----------------------------------------------

class DevelopmentPlanCreateIn(Schema):
    """Creation d'un plan de developpement."""
    items: list[DevelopmentPlanItemSchema] = []


class DevelopmentPlanUpdateIn(Schema):
    """Mise a jour d'un plan de developpement."""
    items: Optional[list[DevelopmentPlanItemSchema]] = None
    completed_at: Optional[datetime] = None


class DevelopmentPlanOut(ModelSchema):
    """Plan de developpement -- sortie."""

    class Meta:
        model = DevelopmentPlan
        fields = [
            'id', 'evaluation', 'items',
            'completed_at', 'created_at', 'updated_at',
        ]


# -----------------------------------------------
#  FILTERS
# -----------------------------------------------

class CampaignListFilterIn(BaseFilter):
    """Filtres pour lister les campagnes."""
    status: Optional[str] = None
    campaign_type: Optional[str] = None

    def filter_status(self, value):
        if value:
            return Q(status=value)
        return Q()

    def filter_campaign_type(self, value):
        if value:
            return Q(campaign_type=value)
        return Q()

    def filter_search(self, value):
        if value:
            return Q(name__icontains=value) | Q(description__icontains=value)
        return Q()


class PerformanceReviewListFilterIn(BaseFilter):
    """Filtres pour lister les evaluations."""
    status: Optional[str] = None
    campaign_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None

    def filter_status(self, value):
        if value:
            return Q(status=value)
        return Q()

    def filter_campaign_id(self, value):
        if value:
            return Q(campaign_id=value)
        return Q()

    def filter_employee_id(self, value):
        if value:
            return Q(employee_id=value)
        return Q()

    def filter_manager_id(self, value):
        if value:
            return Q(manager_id=value)
        return Q()

    def filter_search(self, value):
        if value:
            return (
                Q(employee__first_name__icontains=value)
                | Q(employee__last_name__icontains=value)
                | Q(campaign__name__icontains=value)
                | Q(campaign__description__icontains=value)
                | Q(manager__first_name__icontains=value) | Q(manager__last_name__icontains=value)
            )
        return Q()
