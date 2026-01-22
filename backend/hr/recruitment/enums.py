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

