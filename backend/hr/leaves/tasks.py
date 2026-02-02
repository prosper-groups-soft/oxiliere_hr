import logging
from django.utils import timezone
from django.db    import transaction
from django.db.models import F
from celery           import shared_task, group
from django_tenants.utils import tenant_context

from core.models         import Tenant
from hr.employees.models import Employee
from hr.leaves.models    import (
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
    """ Identifies all organizations and triggers the annual leave entitlement reset in parallel. """
    tenants = Tenant.objects.exclude(schema_name='public').values_list('schema_name', flat=True)
    current_year = timezone.now().year
    
    logger.info(f"Orchestrating annual leave reset for {len(tenants)} tenants.")
    
    job_group = group(
        process_tenant_leave_reset.s(schema_name, current_year) 
        for schema_name in tenants
    )
    job_group.apply_async()


# --- Individual Processing Tasks ---

@shared_task(name="hr.leaves.tasks.process_tenant_leave_reset")
def process_tenant_leave_reset(schema_name: str, year: int):
    """ Processes the annual leave reset and carry-overs for all active employees within a single organization. """
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
                    
                    if policy.allows_carry_over:
                        BalanceService.create_carry_over(employee, year, policy)
                    
                    BalanceService.init_employee_balance(employee, year)
                    
                    success_count += 1
            except Exception as e:
                error_count += 1
                logger.error(f"[{schema_name}] Error for employee {employee.id}: {str(e)}")

    return f"{schema_name}: Success {success_count}, Errors {error_count}"


@shared_task(name="hr.leaves.tasks.expire_carry_overs_daily")
def expire_carry_overs_task():
    """ Runs daily to identify and expire leave days that were carried over but not used within the allowed period. """
    today = timezone.now().date()
    tenants = Tenant.objects.exclude(schema_name='public').values_list('schema_name', flat=True)
    total_expired_count = 0

    for schema_name in tenants:
        tenant = Tenant.objects.get(schema_name=schema_name)
        with tenant_context(tenant):
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
                
                transactions_to_create.append(
                    LeaveTransaction(
                        employee=record.employee,
                        year=today.year,
                        amount=-lost_days,
                        transaction_type=LeaveTransactionTypes.EXPIRE,
                        reason=f"Expiration of carry-over from {record.source_year}"
                    )
                )

                record.used_days = record.days
                records_to_update.append(record)

            with transaction.atomic():
                LeaveTransaction.objects.bulk_create(transactions_to_create)
                LeaveCarryOver.objects.bulk_update(records_to_update, ['used_days'])
                
            count = len(records_to_update)
            total_expired_count += count
            logger.info(f"[{schema_name}] Bulk expired {count} carry-over records.")

    return total_expired_count


@shared_task(name="hr.leaves.tasks.mark_taken_daily_bulk")
def mark_taken_daily_bulk_task():
    """ Runs daily to formally mark approved leaves that have ended as 'Taken'. """
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
                existing_comment = leave.comment or ""
                leave.comment = f"{existing_comment}\n[ARCHIVÉ] Marqué automatiquement comme PRIS le {today}."
                leave.status = LeaveStatus.TAKEN

            LeaveRequest.objects.bulk_update(leaves_to_mark, ["status", "comment"])

            count_marked = leaves_to_mark.count()
            total_marked += count_marked
            logger.info(f"[{schema_name}] Marked {count_marked} leaves as TAKEN.")

    return total_marked

