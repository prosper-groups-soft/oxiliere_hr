from datetime import datetime, date
from typing import Optional
from ninja import Schema, ModelSchema, Field
from hr.recruitment.models import (
    JobOffer, 
    Candidate, 
    Application, 
    Interview
)
from hr.schemas import BaseFilter


# --- CANDIDATE SCHEMAS ---

class CandidateOut(ModelSchema):
    """Standard output for candidate information."""
    class Meta:
        model = Candidate
        fields = [
            'id', 
            'first_name', 
            'middle_name', 
            'last_name',
            'email', 
            'phone', 
            'linkedin_profile'
        ]


class CandidateUpdateIn(Schema):
    """Candidate profile update (CandidateService.update_profile)."""
    phone: Optional[str] = None
    linkedin_profile: Optional[str] = None
    # Name and email are rarely allowed to be updated through a simple profile update


# --- JOB OFFER SCHEMAS ---

class JobOfferOut(ModelSchema):
    """Detailed job offer output (JobOfferService.get_public_listings)."""
    department_name: str = Field(None, alias="department.name")
    position_name: str = Field(None, alias="target_position.name")

    class Meta:
        model = JobOffer
        fields = [
            'id', 
            'title', 
            'slug', 
            'location', 
            'salary_range',
            'description', 
            'requirements', 
            'published_at', 
            'end_date',
            "slots",
            "max_applications",
        ]


class JobOfferCreateIn(Schema):
    """Job offer creation payload (JobOfferService.create_offer)."""
    title: str
    target_position_id: int
    department_id: int
    recruiter_id: int
    description: str
    requirements: str
    location: str = "Remote"
    salary_range: Optional[str] = None
    end_date: Optional[date] = None

    slots: int = 1
    max_applications: Optional[int] = None


class JobOfferFilter(BaseFilter):
    """Search parameters for job offers."""
    department_id: Optional[int] = None
    is_active: Optional[bool] = True


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
    cover_letter: Optional[str] = None


class ApplicationOut(ModelSchema):
    """Detailed application output."""
    candidate: CandidateOut
    job_offer_title: str = Field(None, alias="job_offer.title")

    class Meta:
        model = Application
        fields = ['id', 'status', 'applied_at', 'resume', 'cover_letter']


# --- INTERVIEW SCHEMAS ---

class InterviewScheduleIn(Schema):
    """Interview scheduling payload (InterviewService.schedule_interview)."""
    application_id: int
    interviewer_id: int
    scheduled_at: datetime
    interview_type: str
    duration_minutes: int = 60


class InterviewFeedbackIn(Schema):
    """Interview feedback payload (InterviewService.submit_feedback)."""
    score: int
    notes: str


class InterviewOut(ModelSchema):
    interviewer_name: str = Field(None, alias="interviewer.full_name")

    class Meta:
        model = Interview
        fields = ['id', 'interview_type', 'scheduled_at', 'score', 'notes']


# --- HIRING SCHEMAS ---

class HireCandidateIn(Schema):
    """Final hiring action payload (HiringService.hire_candidate)."""
    start_date: date
