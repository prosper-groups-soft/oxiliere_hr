import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PerformanceReview

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PerformanceReview)
def log_review_saved(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    logger.info(
        "Performance review %s: review_id=%s employee=%s status=%s actor=%s",
        action,
        instance.id,
        instance.employee_id,
        instance.status,
        getattr(instance, "updated_by_id", None) or getattr(instance, "created_by_id", None),
    )


@receiver(post_delete, sender=PerformanceReview)
def log_review_deleted(sender, instance, **kwargs):
    logger.info(
        "Performance review deleted: review_id=%s employee=%s",
        instance.id,
        instance.employee_id,
    )
