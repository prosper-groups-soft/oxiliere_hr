
from django.core.cache import cache
from django_redis      import get_redis_connection

from hr.services.cache_helpers import (
    generate_cache_key,
    invalidate_cache_prefix,
    CacheKeys
)
from hr.leaves.models import (
    LeavePolicy,
    SeniorityRule,
    CircumstanceLeaveRule,
    LeaveBalance,
    LeaveCarryOver,
    LeaveRequest,
)


class LeaveCacheService:
    """ Optimized data access for leave policies, entitlements, and employee requests. """
    
    @staticmethod
    def get_leave_policy(country_code):
        """ Retrieves the leave policy for a specific country from cache or database. """
        cache_key = generate_cache_key("hr:leaves:policy", country_code)
        policy = cache.get(cache_key)
        
        if policy is None:
            policy = LeavePolicy.objects.filter(country_code=country_code).first()
            if policy:
                cache.set(cache_key, policy, timeout=60*60*24)
        
        return policy
    
    @staticmethod
    def get_seniority_rules(policy):
        """ Retrieves additional leave rules based on years of service for a given policy. """
        if isinstance(policy, LeavePolicy):
            policy_id = policy.id
        else:
            policy_id = policy
        
        cache_key = CacheKeys.seniority_rules(policy_id)
        rules = cache.get(cache_key)
        
        if rules is None:
            rules = list(SeniorityRule.objects.filter(
                policy_id=policy_id
            ).order_by('years_of_service'))
            cache.set(cache_key, rules, timeout=60*60*24)
        
        return rules
    
    @staticmethod
    def get_circumstance_rules(policy, leave_type=None):
        """ Retrieves rules for special leave categories (e.g., family events). """
        if isinstance(policy, LeavePolicy):
            policy_id = policy.id
        else:
            policy_id = policy
        
        cache_key = generate_cache_key(
            "hr:leaves:circumstance_rules", policy_id, leave_type
        )
        rules = cache.get(cache_key)
        
        if rules is None:
            query = CircumstanceLeaveRule.objects.filter(policy_id=policy_id)
            if leave_type:
                query = query.filter(type=leave_type)
            
            rules = list(query)
            cache.set(cache_key, rules, timeout=60*60*24)
        
        return rules
    
    @staticmethod
    def get_leave_balance_object(employee, year):
        """ Retrieves the core balance record for an employee for a specific year. """
        cache_key = generate_cache_key("hr:leaves:balance_obj", employee.id, year)
        balance_obj = cache.get(cache_key)
        
        if balance_obj is None:
            balance_obj = LeaveBalance.objects.filter(
                employee=employee,
                year=year
            ).first()
            if balance_obj:
                cache.set(cache_key, balance_obj, timeout=60*60)
        
        return balance_obj
    
    @staticmethod
    def get_leave_balance_dict(employee, year):
        """ Calculates a comprehensive summary of an employee's leave entitlement and usage. """
        cache_key = CacheKeys.leave_balance(employee.id, year)
        balance_data = cache.get(cache_key)
        
        if balance_data is None:
            balance_obj = LeaveCacheService.get_leave_balance_object(employee, year)
            
            if balance_obj:
                balance_data = {
                    'allocated': balance_obj.total_granted,
                    'deducted': balance_obj.used_days,
                    'available': balance_obj.remaining_days,
                    'carry_over': None,
                    'total_available': balance_obj.remaining_days
                }

                carry_over_obj = LeaveCarryOver.objects.filter(
                    employee=employee,
                    source_year=year - 1
                ).first()

                if carry_over_obj:
                    carry_data = {
                        'total': carry_over_obj.days,
                        'used': carry_over_obj.used_days,
                        'available': carry_over_obj.days - carry_over_obj.used_days,
                        'expires_at': carry_over_obj.expires_at
                    }
                    balance_data['carry_over'] = carry_data
                    balance_data['total_available'] += carry_data['available']
                
                cache.set(cache_key, balance_data, timeout=60*60)
            else:
                balance_data = None
        
        return balance_data
    
    @staticmethod
    def get_leave_requests(employee, year=None, status=None):
        """ Retrieves a list of leave requests for an employee, optionally filtered by year or status. """
        cache_key = generate_cache_key("hr:leaves:requests", employee.id, year, status)
        requests = cache.get(cache_key)
        
        if requests is None:
            query = LeaveRequest.objects.filter(employee=employee)
            if year:
                query = query.filter(start_date__year=year)
            if status:
                query = query.filter(status=status)
            
            requests = list(query.order_by('-start_date'))
            cache.set(cache_key, requests, timeout=60*30)
        
        return requests
    
    @staticmethod
    def clear_api_cache_prefix(prefix: str):
        """ Invalidates all cached API responses for a specific feature area. """
        invalidate_cache_prefix(prefix)

    @staticmethod
    def clear_employee_requests_cache(employee_id):
        """ Clears all personal leave request data from cache. """
        cache.delete(generate_cache_key("hr:leaves:requests", employee_id, None, None))
        LeaveCacheService.clear_api_cache_prefix("leave_requests_list")

    @staticmethod
    def clear_employee_balances_cache(employee_id):
        """ Clears all personal leave balance and transaction data from cache. """
        LeaveCacheService.clear_api_cache_prefix("leave_balances_list")
        LeaveCacheService.clear_api_cache_prefix("leave_transactions_list")

    @staticmethod
    def clear_employee_cache(employee):
        """ Performs a full cache wipe for all leave-related data of an employee. """        
        redis_conn = get_redis_connection("default")
        pattern = f"*hr:leaves*{employee.id}*"
        keys = list(redis_conn.scan_iter(match=pattern, count=100))
        if keys:
            redis_conn.delete(*keys)
            
        LeaveCacheService.clear_api_cache_prefix("leave_requests_list")
        LeaveCacheService.clear_api_cache_prefix("leave_balances_list")
        LeaveCacheService.clear_api_cache_prefix("leave_transactions_list")

    @staticmethod
    def clear_all_policies_cache():
        """ Clears global leave policy and rule data from cache. """
        redis_conn = get_redis_connection("default")
        
        for pattern in ["*hr:leaves:policy*", "*hr:leaves:seniority_rules*", "*hr:leaves:circumstance_rules*"]:
            keys = list(redis_conn.scan_iter(match=pattern, count=100))
            if keys:
                redis_conn.delete(*keys)
            
        LeaveCacheService.clear_api_cache_prefix("leave_balances_list")
