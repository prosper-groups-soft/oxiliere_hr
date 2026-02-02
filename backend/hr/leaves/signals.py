import logging
from django.dispatch import receiver
from django.db       import transaction
from django.db.models.signals import post_save, post_delete

from hr.leaves.models import (
    LeavePolicy,
    SeniorityRule,
    CircumstanceLeaveRule,
    LeaveRequest,
    LeaveBalance,
    LeaveTransaction,
    LeaveRecall
)
from hr.leaves.services.cache import LeaveCacheService


logger = logging.getLogger(__name__)


# --- POLICY INVALIDATION ---

POLICY_MODELS = [
    LeavePolicy,
    SeniorityRule,
    CircumstanceLeaveRule
]

@receiver([post_save, post_delete])
def invalidate_policy_cache(sender, instance, **kwargs):
    """ Ensures organizational leave policies and rules are refreshed when modified. """
    if sender not in POLICY_MODELS:
        return

    def clear_cache():
        try:
            LeaveCacheService.clear_all_policies_cache()
        except Exception as e:
            logger.error(f"Error refreshing leave policy: {e}")

    transaction.on_commit(clear_cache)


# --- EMPLOYEE DATA INVALIDATION ---

@receiver([post_save, post_delete], sender=LeaveRequest)
def invalidate_leave_request_cache(sender, instance, **kwargs):
    """ Refreshes an employee's leave request list and balance summary after a change. """
    def clear_cache():
        try:
            if instance.employee:
                LeaveCacheService.clear_employee_requests_cache(instance.employee.id)
                LeaveCacheService.clear_employee_balances_cache(instance.employee.id)
        except Exception as e:
            logger.error(f"Error refreshing employee request data: {e}")

    transaction.on_commit(clear_cache)


@receiver([post_save, post_delete], sender=LeaveBalance)
def invalidate_leave_balance_cache(sender, instance, **kwargs):
    """ Refreshes an employee's balance summary when their entitlement record changes. """
    def clear_cache():
        try:
            if instance.employee:
                LeaveCacheService.clear_employee_balances_cache(instance.employee.id)
        except Exception as e:
            logger.error(f"Error refreshing employee balance data: {e}")

    transaction.on_commit(clear_cache)


@receiver([post_save, post_delete], sender=LeaveTransaction)
def invalidate_leave_transaction_cache(sender, instance, **kwargs):
    """ Updates an employee's balance and history after a new transaction is recorded. """
    def clear_cache():
        try:
            if instance.employee:
                LeaveCacheService.clear_employee_balances_cache(instance.employee.id)
        except Exception as e:
            logger.error(f"Error refreshing employee transaction history: {e}")

    transaction.on_commit(clear_cache)


@receiver([post_save, post_delete], sender=LeaveRecall)
def invalidate_leave_recall_cache(sender, instance, **kwargs):
    """ Updates leave requests and balances following an employee recall. """
    def clear_cache():
        try:
            if instance.leave_request and instance.leave_request.employee:
                employee = instance.leave_request.employee
                LeaveCacheService.clear_employee_requests_cache(employee.id)
                LeaveCacheService.clear_employee_balances_cache(employee.id)
        except Exception as e:
            logger.error(f"Error refreshing recall data: {e}")

    transaction.on_commit(clear_cache)
