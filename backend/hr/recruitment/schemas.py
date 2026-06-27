import json
from datetime import datetime, date
from typing   import Optional, List, Annotated
from uuid     import UUID
from ninja    import Schema, ModelSchema, Field
from pydantic import BeforeValidator

from hr.recruitment.models import (
    JobOffer, 
    Candidate, 
    Application, 
    Interview
)
from hr.jobs.models import Vacancy
from django.db.models import Q
from hr.schemas import BaseFilter


def parse_json_str_to_dict(v):
    """Accept both a dict or a JSON-encoded string (from FormData)."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except (json.JSONDecodeError, TypeError):
            return v
    return v


# Type alias : accepte un dict directement ou une chaîne JSON à parser
JsonDict = Annotated[dict, BeforeValidator(parse_json_str_to_dict)]


# --- CANDIDATE SCHEMAS ---

class CandidateOut(ModelSchema):
    """Standard output for candidate information."""
    avatar_url: Optional[str] = None

    class Meta:
        model = Candidate
        fields = [
            'id', 
            'first_name', 
            'middle_name', 
            'last_name',
            'email', 
            'phone', 
            'linkedin_profile',
            'profile_photo',
            'gender',
            'source',
            'priority',
            'location',
            'position',
            'experience',
            'summary',
            'notes',
            'skills',
            'technical_score',
            'experience_score',
            'communication_score',
            'culture_score',
        ]

    @staticmethod
    def resolve_avatar_url(obj):
        return obj.profile_photo.url if obj.profile_photo else None

    @staticmethod
    def resolve_resume(obj):
        return obj.resume.url if obj.resume else None


class CandidateUpdateIn(Schema):
    """Candidate profile update (CandidateService.update_profile)."""
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_profile: Optional[str] = None
    gender: Optional[str] = None
    source: Optional[str] = None
    priority: Optional[str] = None
    location: Optional[str] = None
    position: Optional[str] = None
    experience: Optional[str] = None
    summary: Optional[str] = None
    notes: Optional[str] = None
    skills: Optional[list[str]] = None
    technical_score: Optional[int] = None
    experience_score: Optional[int] = None
    communication_score: Optional[int] = None
    culture_score: Optional[int] = None
    offer_id: Optional[str] = None
    position_ids: Optional[list[str]] = None
    position_priorities: Optional[JsonDict] = None


class CandidateApplicationsSyncIn(Schema):
    """Sync a candidate's applications: positions and priorities."""
    offer_id: str
    position_ids: Optional[list[str]] = []
    position_priorities: Optional[JsonDict] = {}
    cover_letter: Optional[str] = None


# --- JOB OFFER SCHEMAS ---

class JobOfferVacancyOut(ModelSchema):
    """Vacancy info displayed within a job offer context."""
    position_id: Optional[str] = Field(None)
    position_name: Optional[str] = Field(None)
    slots: int = Field(1)

    class Meta:
        model = Vacancy
        fields = [
            'id', 
            'priority', 
            'status', 
            'opened_date', 
            'target_date', 
            'filled_date', 
            'reason'
        ]

    @staticmethod
    def resolve_position_id(obj):
        return str(obj.position.id) if obj.position else None

    @staticmethod
    def resolve_position_name(obj):
        return obj.position.name if obj.position else None

    @staticmethod
    def resolve_slots(obj):
        return getattr(obj, '_slots', 1)


class JobOfferOut(ModelSchema):
    """Detailed job offer output (JobOfferService.get_public_listings)."""
    position_names: Optional[list[str]] = Field(None)
    target_position_ids: Optional[list[str]] = Field(None, alias="target_position_ids")
    vacancy_ids: Optional[list[str]] = Field(None, alias="vacancy_ids")
    position_slots: Optional[dict[str, int]] = Field(None, alias="position_slots")
    total_candidates: Optional[int] = Field(None, alias="total_candidates")
    in_pipeline: Optional[int] = Field(None, alias="in_pipeline")
    interviews_count: Optional[int] = Field(None, alias="interviews_count")
    offers_sent: Optional[int] = Field(None, alias="offers_sent")
    offers_made: Optional[int] = Field(None, alias="offers_made")
    recruiter_id: Optional[str] = Field(None)
    recruiter_name: Optional[str] = Field(None)
    vacancies: Optional[list[JobOfferVacancyOut]] = Field(None, alias="vacancies")
    evaluation_template: Optional[dict] = Field(None)

    class Meta:
        model = JobOffer
        fields = [
            'id',
            'title',
            'slug',
            'location',
            'description',
            'requirements',
            'published_at',
            'end_date',
            "slots",
            "position_slots",
            "max_applications",
            'status',
        ]

    @staticmethod
    def resolve_position_names(obj):
        return [p.name for p in obj.target_positions.all()]

    @staticmethod
    def resolve_target_position_ids(obj):
        return [str(p.id) for p in obj.target_positions.all()]

    @staticmethod
    def resolve_vacancy_ids(obj):
        return [str(v.id) for v in obj.vacancies.all()]

    @staticmethod
    def resolve_recruiter_id(obj):
        return str(obj.recruiter.id) if obj.recruiter else None

    @staticmethod
    def resolve_recruiter_name(obj):
        if obj.recruiter:
            if obj.recruiter.middle_name:
                return f"{obj.recruiter.last_name} {obj.recruiter.middle_name} {obj.recruiter.first_name}"
            return f"{obj.recruiter.last_name} {obj.recruiter.first_name}"
        return "Non assigné"

    @staticmethod
    def resolve_vacancies(obj):
        """Return Vacancy model instances with slots from position_slots."""
        vacancies = list(obj.vacancies.select_related('position').all())
        for vacancy in vacancies:
            # Attach _slots so resolve_slots can pick it up
            if vacancy.position and obj.position_slots:
                position_id_str = str(vacancy.position.id)
                vacancy._slots = obj.position_slots.get(position_id_str, 1)
            else:
                vacancy._slots = 1
        return vacancies


class JobOfferCreateIn(Schema):
    """Job offer creation payload (JobOfferService.create_offer)."""
    title: str
    target_position_ids: list[str]
    position_slots: Optional[dict[str, int]] = None  # position_id -> number of slots
    vacancy_ids: Optional[list[str]] = None
    recruiter_id: Optional[str] = None
    description: str
    requirements: str
    location: str = "Remote"
    end_date: Optional[date] = None
    status: Optional[str] = "DRAFT"
    is_published: Optional[bool] = False
    is_active: Optional[bool] = True
    published_at: Optional[datetime] = None

    slots: int = 1  # Deprecated: use position_slots instead, kept for backward compatibility
    max_applications: Optional[int] = None
    evaluation_template: Optional[dict] = None


class JobOfferUpdateIn(Schema):
    """Job offer update payload."""
    title: Optional[str] = None
    target_position_ids: Optional[list[str]] = None
    position_slots: Optional[dict[str, int]] = None
    vacancy_ids: Optional[list[str]] = None
    recruiter_id: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    is_published: Optional[bool] = None
    published_at: Optional[datetime] = None

    is_active: Optional[bool] = None
    slots: Optional[int] = None
    max_applications: Optional[int] = None
    evaluation_template: Optional[dict] = None


class JobOfferFilterSearch(BaseFilter):
    """Search parameters for job offers."""
    is_active: Optional[bool] = True
    status: Optional[str] = None
    job_names: Optional[List[str]] = None

    def filter_search(self, value):
        """Filter by search term in title or description."""
        if value:
            return Q(title__icontains=value) | Q(description__icontains=value)
        return Q()

    def filter_job_names(self, value):
        """Filter by job names (position names)."""
        if value:
            return Q(target_positions__name__in=value)
        return Q()


class JobOfferFilter(JobOfferFilterSearch):
    """Search + ordering parameters for job offers."""
    sort_by: Optional[str] = None
    sort_order: Optional[str] = 'asc'

    def filter_sort_by(self, value):
        """Sort by field (handled in filter method override)."""
        return Q()

    def filter_sort_order(self, value):
        """Sort order (handled in filter method override)."""
        return Q()

    def filter(self, queryset):
        """Override filter to apply sorting."""
        queryset = super().filter(queryset)
        if self.sort_by:
            prefix = '' if self.sort_order == 'asc' else '-'
            sort_field = self._get_sort_field(self.sort_by)
            if sort_field:
                queryset = queryset.order_by(f'{prefix}{sort_field}')
        return queryset

    @staticmethod
    def _get_sort_field(sort_by: str) -> str:
        mapping = {
            'title': 'title',
            'status': 'status',
            'openDate': 'published_at',
            'closeDate': 'end_date',
            'slots': 'slots',
            'jobName': 'title',
            'type': 'status',
        }
        return mapping.get(sort_by, 'title')

    def filter_is_active(self, value):
        if value is not None:
            return Q(is_active=value)
        return Q()

    def filter_status(self, value):
        if value:
            return Q(status=value)
        return Q()


# --- APPLICATION SCHEMAS ---

class ApplicationCreateIn(Schema):
    """
    Application submission payload (ApplicationService.submit_application).
    Note: The 'resume' file will be handled via File(...) in the controller.
    """
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: str
    phone: Optional[str] = None
    linkedin_profile: Optional[str] = None
    gender: Optional[str] = None
    source: Optional[str] = None
    priority: Optional[str] = None
    location: Optional[str] = None
    position: Optional[str] = None
    experience: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[list[str]] = None
    technical_score: Optional[int] = None
    experience_score: Optional[int] = None
    communication_score: Optional[int] = None
    culture_score: Optional[int] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    target_position_ids: Optional[list[str]] = None
    position_priorities: Optional[JsonDict] = None  # position_id -> priority


class ApplicationOut(ModelSchema):
    """Detailed application output."""
    candidate: CandidateOut
    job_offer_id: Optional[str] = None
    job_offer_title: Optional[str] = Field(None, alias="job_offer.title")
    target_position_id: Optional[str] = None
    target_position_name: Optional[str] = None
    priority: Optional[str] = None

    class Meta:
        model = Application
        fields = ['id', 'status', 'applied_at', 'cover_letter', 'scores', 'evaluation_notes', 'salary_min', 'salary_max', 'salary_currency', 'offer_start_date']

    @staticmethod
    def resolve_job_offer_id(obj):
        return str(obj.job_offer.id) if obj.job_offer else None

    @staticmethod
    def resolve_target_position_id(obj):
        return str(obj.target_position_id) if obj.target_position_id else None

    @staticmethod
    def resolve_target_position_name(obj):
        return obj.target_position.name if obj.target_position else None


class ApplicationUpdateIn(Schema):
    """Payload for updating application metadata."""
    priority: Optional[str] = None


class ApplicationEvaluationIn(Schema):
    """Payload for updating application evaluation scores."""
    scores: Optional[dict] = None
    evaluation_notes: Optional[str] = None


class ApplicationOfferIn(Schema):
    """Payload for updating application offer details."""
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    offer_start_date: Optional[date] = None


# --- INTERVIEW SCHEMAS ---

class InterviewScheduleIn(Schema):
    """Interview scheduling payload (InterviewService.schedule_interview)."""
    application_id: str
    interviewer_id: str
    scheduled_at: datetime
    interview_type: str
    duration_minutes: int = 60
    location: Optional[str] = None
    notes: Optional[str] = None


class InterviewFeedbackIn(Schema):
    """Interview feedback payload (InterviewService.submit_feedback)."""
    score: int
    feedback: Optional[str] = None
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    would_hire: Optional[bool] = None
    next_steps: Optional[str] = None
    status: Optional[str] = None


class InterviewUpdateIn(Schema):
    """Interview update payload — modifiable fields for an existing interview."""
    interviewer_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    interview_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    video_link: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class InterviewOut(ModelSchema):
    interviewer_name: Optional[str] = Field(None, alias="interviewer.full_name")
    application_id: Optional[str] = None
    candidate_id: Optional[str] = None
    candidate_name: Optional[str] = None
    position_name: Optional[str] = None
    interviewer_id: Optional[str] = None
    status: str = "SCHEDULED"

    class Meta:
        model = Interview
        fields = ['id', 'interview_type', 'scheduled_at', 'score', 'feedback', 'strengths', 'weaknesses', 'would_hire', 'next_steps', 'location', 'video_link', 'duration_minutes', 'notes']

    @staticmethod
    def resolve_application_id(obj):
        return str(obj.application_id) if obj.application_id else None

    @staticmethod
    def resolve_candidate_id(obj):
        return str(obj.application.candidate_id) if obj.application and obj.application.candidate_id else None

    @staticmethod
    def resolve_candidate_name(obj):
        if obj.application and obj.application.candidate:
            c = obj.application.candidate
            parts = [c.last_name]
            if c.middle_name:
                parts.append(c.middle_name)
            parts.append(c.first_name)
            return " ".join(parts)
        return None

    @staticmethod
    def resolve_position_name(obj):
        if obj.application and obj.application.target_position:
            return obj.application.target_position.name
        return None

    @staticmethod
    def resolve_interviewer_id(obj):
        return str(obj.interviewer_id) if obj.interviewer_id else None


class ApplicationBriefOut(Schema):
    """Lightweight application info without nested candidate (used in grouped view)."""
    id: UUID
    status: str
    priority: str
    target_position_id: Optional[str] = None
    target_position_name: Optional[str] = None
    job_offer_id: Optional[str] = None
    scores: Optional[dict] = None
    evaluation_notes: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    offer_start_date: Optional[date] = None
    applied_at: datetime
    cover_letter: Optional[str] = None

    @staticmethod
    def resolve_target_position_id(obj):
        return str(obj.target_position_id) if obj.target_position_id else None

    @staticmethod
    def resolve_target_position_name(obj):
        return obj.target_position.name if obj.target_position else None

    @staticmethod
    def resolve_job_offer_id(obj):
        return str(obj.job_offer_id) if obj.job_offer_id else None


class CandidateWithApplicationsOut(Schema):
    """Candidate with all their applications grouped together."""
    id: UUID
    first_name: str
    middle_name: str = ""
    last_name: str
    email: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    linkedin_profile: Optional[str] = None
    gender: str = "NOT_SPECIFIED"
    source: str
    priority: str
    location: Optional[str] = None
    position: Optional[str] = None
    experience: Optional[str] = None
    summary: Optional[str] = None
    notes: Optional[str] = None
    skills: list = []
    applications: list[ApplicationBriefOut] = []
    resume: Optional[str] = None

    @staticmethod
    def resolve_avatar_url(obj):
        return obj.profile_photo.url if obj.profile_photo else None

    @staticmethod
    def resolve_applications(obj):
        return getattr(obj, '_applications', [])

    @staticmethod
    def resolve_resume(obj):
        return obj.resume.url if obj.resume else None


# --- HIRING SCHEMAS ---

class HireCandidateIn(Schema):
    """Final hiring action payload (HiringService.hire_candidate)."""
    start_date: date
