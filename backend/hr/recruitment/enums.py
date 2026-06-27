from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class ApplicationStatus(TextChoices):
    PENDING = 'PENDING', _('Pending')
    REVIEW = 'REVIEW', _('Under Review')
    INTERVIEW = 'INTERVIEW', _('Interviewing')
    OFFER = 'OFFER', _('Offer Made')
    ACCEPTED = 'ACCEPTED', _('Accepted')
    REJECTED = 'REJECTED', _('Rejected')
    WITHDRAWN = 'WITHDRAWN', _('Withdrawn')


class InterviewType(TextChoices):
    PHONE = 'PHONE', _('Phone Screen')
    VIDEO = 'VIDEO', _('Video Call')
    ONSITE = 'ONSITE', _('On-site Interview')
    TECHNICAL = 'TECHNICAL', _('Technical Assessment')


class InterviewStatus(TextChoices):
    SCHEDULED = 'SCHEDULED', _('Planifié')
    COMPLETED = 'COMPLETED', _('Terminé')
    CANCELLED = 'CANCELLED', _('Annulé')
    NO_SHOW = 'NO_SHOW', _('Absent')


class JobOfferStatus(TextChoices):
    DRAFT = 'DRAFT', _('Draft')
    OPEN = 'OPEN', _('Open')
    PAUSED = 'PAUSED', _('Paused')
    CLOSED = 'CLOSED', _('Closed')


class ContractType(TextChoices):
    CDI = 'CDI', _('CDI (Indéterminé)')
    CDD = 'CDD', _('CDD (Durée Déterminée)')
    INTERNSHIP = 'INTERNSHIP', _('Stage Professionnel')
    FREELANCE = 'FREELANCE', _('Consultance / Freelance')
    PROBATION = 'PROBATION', _('Période d\'Essai')
    TEMPORARY = 'TEMPORARY', _('Journalier / Temporaire')


class CandidateSource(TextChoices):
    LINKEDIN = 'LINKEDIN', _('LinkedIn')
    CAREER_SITE = 'CAREER_SITE', _('Career Site')
    REFERRAL = 'REFERRAL', _('Referral')
    DIRECT = 'DIRECT', _('Direct / Email')


class CandidatePriority(TextChoices):
    LOW = 'LOW', _('Low')
    MEDIUM = 'MEDIUM', _('Medium')
    HIGH = 'HIGH', _('High')

