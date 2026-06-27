from django.db.models.signals import post_save, post_delete
from django.dispatch          import receiver

from hr.recruitment.models import (
    JobOffer,
    Candidate,
    Application,
    Interview
)
from hr.jobs.models import Position
from hr.recruitment.services.cache import RecruitmentCacheService


@receiver([post_save, post_delete], sender=JobOffer)
def invalidate_offer_cache(sender, instance, **kwargs):
    """Invalidate job offer cache."""
    RecruitmentCacheService.clear_offer_cache(instance)


@receiver([post_save, post_delete], sender=Position)
def invalidate_position_related_offers(sender, instance, **kwargs):
    """Invalidate job offer cache when a position is modified."""
    # Get all job offers that reference this position
    related_offers = instance.job_offers.all()
    for offer in related_offers:
        RecruitmentCacheService.clear_offer_cache(offer)


@receiver([post_save, post_delete], sender=Candidate)
def invalidate_candidate_cache(sender, instance, **kwargs):
    """Invalidate candidate cache."""
    RecruitmentCacheService.clear_candidate_cache(instance)


@receiver([post_save, post_delete], sender=Application)
def invalidate_application_cache(sender, instance, **kwargs):
    """Invalidate application cache and related lists."""
    RecruitmentCacheService.clear_application_cache(instance)


@receiver([post_save, post_delete], sender=Interview)
def invalidate_interview_cache(sender, instance, **kwargs):
    """Invalidate interview cache and schedule."""
    RecruitmentCacheService.clear_interview_cache(instance)

