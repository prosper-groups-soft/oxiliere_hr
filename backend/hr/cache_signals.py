"""
Cache invalidation signals.

Automatically invalidates cache when models are saved or deleted.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

# Payroll signals
from hr.payroll.models import (
    PayrollConfiguration,
    EmployeeContract,
    PayrollRun,
    SalaryAdvance,
)
from hr.payroll.services.cache import PayrollCacheService

# Leaves signals
from hr.leaves.models import (
    LeavePolicy,
    SeniorityRule,
    CircumstanceLeaveRule,
    EmployeeLeaveAllocation,
    LeaveRequest,
    LeaveTransaction,
)
from hr.leaves.services.cache import LeaveCacheService

# Attendance signals
from hr.attendance.models import (
    ShiftPolicy,
    EmploymentScheme,
    Punch,
    DailyRegister,
)
from hr.attendance.services.cache import AttendanceCacheService

# Employees signals
from hr.employees.models import Employee
from hr.employees.services.cache import EmployeeCacheService

# Jobs signals
from hr.jobs.models import (
    Department,
    Position,
    JobFamily,
    EmploymentPosition,
)
from hr.jobs.services.cache import JobsCacheService

# Calendar signals
from hr.calendar.models import CalendarEvent
from hr.calendar.services.cache import CalendarCacheService

# Banking signals
from hr.banking.models import BankAccount
from hr.banking.services.cache import BankingCacheService

# Recruitment signals
from hr.recruitment.models import (
    JobOffer,
    Candidate,
    Application,
    Interview,
)
from hr.recruitment.services.cache import RecruitmentCacheService


# =============================================
# PAYROLL CACHE INVALIDATION
# =============================================

@receiver(post_save, sender=PayrollConfiguration)
@receiver(post_delete, sender=PayrollConfiguration)
def invalidate_payroll_config(sender, instance, **kwargs):
    """Invalidate payroll configuration cache."""
    PayrollCacheService.clear_config_cache()


@receiver(post_save, sender=EmployeeContract)
@receiver(post_delete, sender=EmployeeContract)
def invalidate_employee_contract(sender, instance, **kwargs):
    """Invalidate contract cache when changed."""
    PayrollCacheService.clear_employee_cache(instance.employee)
    # Also invalidate payroll runs that depend on this contract
    cache.delete_pattern("hr:payroll:contract:*")


@receiver(post_save, sender=PayrollRun)
@receiver(post_delete, sender=PayrollRun)
def invalidate_payroll_run(sender, instance, **kwargs):
    """Invalidate payroll run cache."""
    PayrollCacheService.clear_payroll_run_cache(instance.id)


@receiver(post_save, sender=SalaryAdvance)
@receiver(post_delete, sender=SalaryAdvance)
def invalidate_salary_advance(sender, instance, **kwargs):
    """Invalidate salary advance cache."""
    from hr.services.cache_helpers import CacheKeys
    cache.delete(CacheKeys.salary_advance(instance.employee.id))


# =============================================
# LEAVES CACHE INVALIDATION
# =============================================

@receiver(post_save, sender=LeavePolicy)
@receiver(post_delete, sender=LeavePolicy)
def invalidate_leave_policy(sender, instance, **kwargs):
    """Invalidate leave policy cache."""
    from hr.services.cache_helpers import generate_cache_key
    cache.delete(generate_cache_key("hr:leaves:policy", instance.country_code))


@receiver(post_save, sender=SeniorityRule)
@receiver(post_delete, sender=SeniorityRule)
def invalidate_seniority_rules(sender, instance, **kwargs):
    """Invalidate seniority rules cache."""
    from hr.services.cache_helpers import CacheKeys
    cache.delete(CacheKeys.seniority_rules(instance.policy.id))


@receiver(post_save, sender=CircumstanceLeaveRule)
@receiver(post_delete, sender=CircumstanceLeaveRule)
def invalidate_circumstance_rules(sender, instance, **kwargs):
    """Invalidate circumstance leave rules cache."""
    cache.delete_pattern(f"hr:leaves:circumstance_rules:{instance.policy.id}:*")


@receiver(post_save, sender=EmployeeLeaveAllocation)
@receiver(post_delete, sender=EmployeeLeaveAllocation)
def invalidate_leave_allocation(sender, instance, **kwargs):
    """Invalidate leave allocation cache."""
    LeaveCacheService.clear_allocation_cache(instance.employee, instance.year)
    LeaveCacheService.clear_balance_cache(instance.employee, instance.year)


@receiver(post_save, sender=LeaveRequest)
@receiver(post_delete, sender=LeaveRequest)
def invalidate_leave_request(sender, instance, **kwargs):
    """Invalidate leave request cache."""
    LeaveCacheService.clear_employee_cache(instance.employee)


@receiver(post_save, sender=LeaveTransaction)
@receiver(post_delete, sender=LeaveTransaction)
def invalidate_leave_transaction(sender, instance, **kwargs):
    """Invalidate leave balance when transaction changes."""
    LeaveCacheService.clear_balance_cache(
        instance.allocation.employee,
        instance.allocation.year
    )


# =============================================
# ATTENDANCE CACHE INVALIDATION
# =============================================

@receiver(post_save, sender=ShiftPolicy)
@receiver(post_delete, sender=ShiftPolicy)
def invalidate_shift_policy(sender, instance, **kwargs):
    """Invalidate shift policy cache."""
    from hr.services.cache_helpers import generate_cache_key
    cache.delete(generate_cache_key("hr:attendance:shift_policy", instance.id))
    cache.delete(generate_cache_key("hr:attendance:shift_details", instance.id))


@receiver(post_save, sender=EmploymentScheme)
@receiver(post_delete, sender=EmploymentScheme)
def invalidate_employment_scheme(sender, instance, **kwargs):
    """Invalidate employment scheme cache."""
    AttendanceCacheService.clear_employee_cache(instance.employee)


@receiver(post_save, sender=Punch)
@receiver(post_delete, sender=Punch)
def invalidate_punch(sender, instance, **kwargs):
    """Invalidate punch cache (real-time)."""
    from hr.services.cache_helpers import CacheKeys, generate_cache_key
    from django_redis import get_redis_connection
    
    employee = instance.daily_register.employee
    date = instance.daily_register.date
    
    # Clear worked hours
    cache.delete(CacheKeys.worked_hours(employee.id, date))
    
    # Clear punches list
    cache.delete(generate_cache_key("hr:attendance:punches", employee.id, date))
    
    # Clear daily register
    cache.delete(CacheKeys.daily_register(employee.id, date))


@receiver(post_save, sender=DailyRegister)
@receiver(post_delete, sender=DailyRegister)
def invalidate_daily_register(sender, instance, **kwargs):
    """Invalidate daily register cache."""
    AttendanceCacheService.clear_employee_cache(instance.employee)


# =============================================
# EMPLOYEES CACHE INVALIDATION
# =============================================

@receiver(post_save, sender=Employee)
@receiver(post_delete, sender=Employee)
def invalidate_employee(sender, instance, **kwargs):
    """Invalidate employee cache when changed."""
    EmployeeCacheService.clear_employee_cache(instance)


# =============================================
# JOBS CACHE INVALIDATION
# =============================================

@receiver(post_save, sender=Department)
@receiver(post_delete, sender=Department)
def invalidate_department(sender, instance, **kwargs):
    """Invalidate department cache."""
    JobsCacheService.clear_department_cache()


@receiver(post_save, sender=Position)
@receiver(post_delete, sender=Position)
def invalidate_position(sender, instance, **kwargs):
    """Invalidate position cache."""
    from hr.services.cache_helpers import generate_cache_key
    
    JobsCacheService.clear_department_cache()
    cache.delete(generate_cache_key("hr:jobs:position", instance.id))
    cache.delete(generate_cache_key(
        "hr:jobs:positions_dept", instance.department.id
    ))


@receiver(post_save, sender=JobFamily)
@receiver(post_delete, sender=JobFamily)
def invalidate_job_family(sender, instance, **kwargs):
    """Invalidate job family cache."""
    from hr.services.cache_helpers import CacheKeys
    cache.delete(CacheKeys.positions_by_family(instance.id))


@receiver(post_save, sender=EmploymentPosition)
@receiver(post_delete, sender=EmploymentPosition)
def invalidate_employment_position(sender, instance, **kwargs):
    """Invalidate employment position cache."""
    JobsCacheService.clear_employee_position_cache(instance.employee)


# =============================================
# CALENDAR CACHE INVALIDATION
# =============================================

@receiver(post_save, sender=CalendarEvent)
@receiver(post_delete, sender=CalendarEvent)
def invalidate_calendar_event(sender, instance, **kwargs):
    """Invalidate calendar cache when event changes."""
    CalendarCacheService.clear_all_calendar_cache()


# =============================================
# BANKING CACHE INVALIDATION
# =============================================

@receiver(post_save, sender=BankAccount)
@receiver(post_delete, sender=BankAccount)
def invalidate_bank_account(sender, instance, **kwargs):
    """Invalidate bank account cache."""
    BankingCacheService.clear_account_cache(instance)


# =============================================
# RECRUITMENT CACHE INVALIDATION
# =============================================

@receiver(post_save, sender=JobOffer)
@receiver(post_delete, sender=JobOffer)
def invalidate_job_offer(sender, instance, **kwargs):
    """Invalidate job offer cache."""
    RecruitmentCacheService.clear_offer_cache(instance)
    from hr.services.cache_helpers import CacheKeys
    cache.delete(CacheKeys.active_job_offers())


@receiver(post_save, sender=Candidate)
@receiver(post_delete, sender=Candidate)
def invalidate_candidate(sender, instance, **kwargs):
    """Invalidate candidate cache."""
    RecruitmentCacheService.clear_candidate_cache(instance)


@receiver(post_save, sender=Application)
@receiver(post_delete, sender=Application)
def invalidate_application(sender, instance, **kwargs):
    """Invalidate application cache."""
    RecruitmentCacheService.clear_offer_cache(instance.job_offer)
    RecruitmentCacheService.clear_candidate_cache(instance.candidate)


@receiver(post_save, sender=Interview)
@receiver(post_delete, sender=Interview)
def invalidate_interview(sender, instance, **kwargs):
    """Invalidate interview cache."""
    from hr.services.cache_helpers import generate_cache_key
    
    cache.delete(generate_cache_key("hr:recruitment:interview", instance.id))
    cache.delete(generate_cache_key(
        "hr:recruitment:candidate_interviews",
        instance.application.candidate.id,
        None
    ))
    cache.delete("hr:recruitment:pending_interviews")


def connect_cache_signals():
    """
    Explicitly connect all cache invalidation signals.
    
    Call this in apps.py ready() method if signals don't auto-connect.
    """
    pass  # Signals are auto-connected via decorators
