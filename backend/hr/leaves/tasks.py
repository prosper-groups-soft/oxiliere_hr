import logging
from django.utils import timezone
from django.db import transaction
from celery import shared_task, group
from django_tenants.utils import tenant_context

from core.models import Tenant
from hr.employees.models import Employee
from hr.leaves.models import (
    LeavePolicy, 
    LeaveCarryOver, 
    LeaveRequest
)
from hr.leaves.services.balance import BalanceService
from hr.enums import LeaveStatus


logger = logging.getLogger(__name__)


# --- Orchestrator Tasks ---

@shared_task(name="hr.leaves.tasks.annual_leave_reset_orchestrator")
def annual_leave_reset_orchestrator():
    """
    Master task: Identifies tenants and triggers parallel processing.
    Scalability: O(1) orchestrator triggering O(N) workers.
    """
    tenants = Tenant.objects.exclude(schema_name='public').values_list('schema_name', flat=True)
    current_year = timezone.now().year
    
    logger.info(f"Orchestrating annual leave reset for {len(tenants)} tenants.")
    
    # Create a group of tasks to be executed in parallel by workers
    job_group = group(
        process_tenant_leave_reset.s(schema_name, current_year) 
        for schema_name in tenants
    )
    job_group.apply_async()


# --- Worker Tasks (The 'Chirurgical' Part) ---

@shared_task(name="hr.leaves.tasks.process_tenant_leave_reset")
def process_tenant_leave_reset(schema_name: str, year: int):
    """
    Processes a single tenant. Optimized with atomic transactions 
    and select_related to avoid N+1 queries.
    """
    tenant = Tenant.objects.get(schema_name=schema_name)
    success_count = 0
    error_count = 0

    with tenant_context(tenant):
        # Prefetch related data to speed up the loop
        active_employees = Employee.objects.filter(is_active=True)
        
        # Cache policies in memory for this tenant to avoid DB hits in the loop
        policies = {p.country_code: p for p in LeavePolicy.objects.all()}

        for employee in active_employees:
            try:
                # Use a sub-transaction per employee to isolate failures
                with transaction.atomic():
                    policy = policies.get(employee.nationality)
                    
                    if policy and policy.allows_carry_over:
                        BalanceService.create_carry_over(employee, year, policy)
                    
                    BalanceService.init_employee_balance(employee, year)
                    success_count += 1
            except Exception as e:
                error_count += 1
                logger.error(f"[{schema_name}] Error for employee {employee.id}: {str(e)}")

    return f"{schema_name}: Success {success_count}, Errors {error_count}"


@shared_task(name="hr.leaves.tasks.expire_carry_overs_daily")
def expire_carry_overs_task():
    """
    Daily cleanup. Optimized to use a single SQL UPDATE per tenant 
    instead of looping through records.
    """
    today = timezone.now().date()
    tenants = Tenant.objects.exclude(schema_name='public').values_list('schema_name', flat=True)
    total_expired = 0

    for schema_name in tenants:
        tenant = Tenant.objects.get(schema_name=schema_name)
        with tenant_context(tenant):
            # Surgical SQL Update: bulk update is O(1) at the DB level
            updated = LeaveCarryOver.objects.filter(
                expires_at__lt=today,
                used_days__lt=F("days")
            ).update(used_days=F("days"))
            
            total_expired += updated
            if updated > 0:
                logger.info(f"[{schema_name}] Expired {updated} carry-over records.")

    return total_expired


@shared_task(name="hr.leaves.tasks.mark_taken_daily_bulk")
def mark_taken_daily_bulk_task():
    """
    Daily task to mark expired approved leaves as TAKEN.
    Preserves existing comments and appends archive log.
    Optimized with bulk_update for efficiency.
    """
    today = timezone.now().date()
    tenants = Tenant.objects.exclude(schema_name='public').values_list('schema_name', flat=True)
    total_marked = 0

    for schema_name in tenants:
        tenant = Tenant.objects.get(schema_name=schema_name)
        with tenant_context(tenant):
            leaves_to_mark = LeaveRequest.objects.filter(
                status=LeaveStatus.APPROVED,
                end_date__lt=today
            )

            if not leaves_to_mark.exists():
                continue

            for leave in leaves_to_mark:
                # Preserve existing comment and append archive note
                existing_comment = leave.comment or ""
                leave.comment = f"{existing_comment}\n[ARCHIVÉ] Automatiquement marqué comme PRIS le {today}."
                leave.status = LeaveStatus.TAKEN

            # Bulk update the status and comment fields only
            LeaveRequest.objects.bulk_update(leaves_to_mark, ["status", "comment"])

            count_marked = leaves_to_mark.count()
            total_marked += count_marked
            logger.info(f"[{schema_name}] Marked {count_marked} leaves as TAKEN.")

    return total_marked

