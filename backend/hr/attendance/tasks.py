import logging
from django_tenants.utils import tenant_context
from core.models          import Tenant
from celery               import shared_task, group
from hr.attendance.services.scheduling import SchedulingService


logger = logging.getLogger(__name__)


@shared_task(name="hr.attendance.tasks.orchestrate_rotation_backfill")
def orchestrate_rotation_backfill():
    """ Triggers a system-wide update of future shift assignments across all tenants. """
    tenants = Tenant.objects.exclude(schema_name='public').values_list('schema_name', flat=True)
    
    job_group = group(
        process_tenant_rotation_backfill.s(schema_name) 
        for schema_name in tenants
    )
    job_group.apply_async()


@shared_task(name="hr.attendance.tasks.process_tenant_rotation_backfill")
def process_tenant_rotation_backfill(schema_name: str):
    """ Generates future shift assignments for a specific tenant for the next 30 days. """
    tenant = Tenant.objects.get(schema_name=schema_name)
    
    with tenant_context(tenant):
        try:
            SchedulingService.backfill_rotations(look_ahead_days=30)
            logger.info(f"[{schema_name}] Rotation backfill completed successfully.")
        except Exception as e:
            logger.error(f"[{schema_name}] Failed to backfill rotations: {str(e)}")
            return False
            
    return True

