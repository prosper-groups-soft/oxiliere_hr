import logging
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from celery import shared_task, group
from django_tenants.utils import tenant_context

from core.models import Tenant
from hr.employees.models import Employee
from hr.leaves.models import (
    LeavePolicy, 
    LeaveCarryOver, 
    LeaveRequest,
    LeaveTransaction
)
from hr.leaves.services.balance import BalanceService
from hr.leaves.enums import LeaveStatus, LeaveTransactionTypes


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
        active_employees = Employee.objects.filter(is_active=True)
        policies = {p.country_code: p for p in LeavePolicy.objects.all()}

        for employee in active_employees:
            try:
                with transaction.atomic():
                    policy = policies.get(employee.nationality)
                    if not policy:
                        continue
                    
                    # 1. Carry-over logic (Should create a LeaveTransaction internally)
                    if policy.allows_carry_over:
                        BalanceService.create_carry_over(employee, year, policy)
                    
                    # 2. Init Balance (Should create an EARN type LeaveTransaction internally)
                    BalanceService.init_employee_balance(employee, year)
                    
                    success_count += 1
            except Exception as e:
                error_count += 1
                logger.error(f"[{schema_name}] Error for employee {employee.id}: {str(e)}")

    return f"{schema_name}: Success {success_count}, Errors {error_count}"




@shared_task(name="hr.leaves.tasks.expire_carry_overs_daily")
def expire_carry_overs_task():
    """
    Optimized daily cleanup using bulk operations.
    Scalable for tenants with thousands of employees.
    """
    today = timezone.now().date()
    tenants = Tenant.objects.exclude(schema_name='public').values_list('schema_name', flat=True)
    total_expired_count = 0

    for schema_name in tenants:
        tenant = Tenant.objects.get(schema_name=schema_name)
        with tenant_context(tenant):
            # 1. Fetch all records to expire in one query
            # We use select_related if employee info is needed for the reason
            expired_records = list(LeaveCarryOver.objects.filter(
                expires_at__lt=today,
                used_days__lt=F("days")
            ).select_related('employee'))

            if not expired_records:
                continue

            transactions_to_create = []
            records_to_update = []

            for record in expired_records:
                lost_days = record.days - record.used_days
                
                # Prepare Transaction Audit
                transactions_to_create.append(
                    LeaveTransaction(
                        employee=record.employee,
                        year=today.year,
                        amount=-lost_days,
                        transaction_type=LeaveTransactionTypes.EXPIRE,
                        reason=f"Expiration of carry-over from {record.source_year}"
                    )
                )

                # Prepare record update
                record.used_days = record.days
                records_to_update.append(record)

            # 2. Database atomic block for bulk operations
            with transaction.atomic():
                # Create all transactions in one SQL INSERT
                LeaveTransaction.objects.bulk_create(transactions_to_create)
                
                # Update all CarryOver records in one SQL UPDATE
                LeaveCarryOver.objects.bulk_update(records_to_update, ['used_days'])
                
            count = len(records_to_update)
            total_expired_count += count
            logger.info(f"[{schema_name}] Bulk expired {count} carry-over records.")

    return total_expired_count


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
                leave.comment = f"{existing_comment}\n[ARCHIVÉ] Marqué automatiquement comme PRIS le {today}."
                leave.status = LeaveStatus.TAKEN

            # Bulk update the status and comment fields only
            LeaveRequest.objects.bulk_update(leaves_to_mark, ["status", "comment"])

            count_marked = leaves_to_mark.count()
            total_marked += count_marked
            logger.info(f"[{schema_name}] Marked {count_marked} leaves as TAKEN.")

    return total_marked

