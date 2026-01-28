"""
Leaves caching services.

Handles caching of leave-related queries and calculations.
"""

from django.core.cache import cache
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.leaves.models import (
    LeavePolicy,
    SeniorityRule,
    CircumstanceLeaveRule,
    EmployeeLeaveAllocation,
    LeaveRequest,
)


class LeaveCacheService:
    """Cache operations for leaves module."""
    
    @staticmethod
    def get_leave_policy(country_code):
        """
        Get leave policy for country (cached - stable).
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code
        
        Returns:
            LeavePolicy instance
        """
        cache_key = generate_cache_key("hr:leaves:policy", country_code)
        policy = cache.get(cache_key)
        
        if policy is None:
            policy = LeavePolicy.objects.filter(
                country_code=country_code
            ).first()
            
            if policy:
                cache.set(cache_key, policy, timeout=60*60*24)  # 24h
        
        return policy
    
    @staticmethod
    def get_seniority_rules(policy):
        """
        Get seniority rules for a policy (cached - stable).
        
        Args:
            policy: LeavePolicy instance
        
        Returns:
            Queryset or list of SeniorityRule instances
        """
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
            
            cache.set(cache_key, rules, timeout=60*60*24)  # 24h
        
        return rules
    
    @staticmethod
    def get_circumstance_rules(policy, leave_type=None):
        """
        Get circumstance leave rules for a policy.
        
        Args:
            policy: LeavePolicy instance
            leave_type: Specific leave type (optional)
        
        Returns:
            List of CircumstanceLeaveRule instances
        """
        if isinstance(policy, LeavePolicy):
            policy_id = policy.id
        else:
            policy_id = policy
        
        cache_key = generate_cache_key(
            "hr:leaves:circumstance_rules", policy_id, leave_type
        )
        rules = cache.get(cache_key)
        
        if rules is None:
            query = CircumstanceLeaveRule.objects.filter(
                policy_id=policy_id
            )
            
            if leave_type:
                query = query.filter(type=leave_type)
            
            rules = list(query)
            cache.set(cache_key, rules, timeout=60*60*24)  # 24h
        
        return rules
    
    @staticmethod
    def get_leave_allocation(employee, year):
        """
        Get leave allocation for employee in year.
        
        Args:
            employee: Employee instance
            year: Year (int)
        
        Returns:
            EmployeeLeaveAllocation instance or None
        """
        cache_key = generate_cache_key(
            "hr:leaves:allocation", employee.id, year
        )
        allocation = cache.get(cache_key)
        
        if allocation is None:
            allocation = EmployeeLeaveAllocation.objects.filter(
                employee=employee,
                year=year
            ).first()
            
            if allocation:
                cache.set(cache_key, allocation, timeout=60*60)  # 1h
        
        return allocation
    
    @staticmethod
    def get_leave_balance(employee, year):
        """
        Get leave balance for employee in year (cached calculation).
        
        Args:
            employee: Employee instance
            year: Year (int)
        
        Returns:
            Dict with balance information
        """
        cache_key = CacheKeys.leave_balance(employee.id, year)
        balance = cache.get(cache_key)
        
        if balance is None:
            allocation = LeaveCacheService.get_leave_allocation(
                employee, year
            )
            
            if allocation:
                # Calculate balance
                from hr.leaves.models import LeaveTransaction
                
                deducted = LeaveTransaction.objects.filter(
                    allocation=allocation
                ).aggregate(
                    total=models.Sum('days')
                )['total'] or 0
                
                balance = {
                    'allocated': allocation.allocated_days,
                    'deducted': deducted,
                    'available': allocation.allocated_days - deducted,
                    'carried_over': allocation.carried_over_days or 0,
                }
                
                cache.set(cache_key, balance, timeout=60*60)  # 1h
            else:
                balance = None
        
        return balance
    
    @staticmethod
    def get_leave_requests(employee, year=None, status=None):
        """
        Get leave requests for employee (short cache).
        
        Args:
            employee: Employee instance
            year: Optional year filter
            status: Optional status filter
        
        Returns:
            List of LeaveRequest instances
        """
        cache_key = generate_cache_key(
            "hr:leaves:requests", employee.id, year, status
        )
        requests = cache.get(cache_key)
        
        if requests is None:
            query = LeaveRequest.objects.filter(employee=employee)
            
            if year:
                query = query.filter(start_date__year=year)
            
            if status:
                query = query.filter(status=status)
            
            requests = list(query.order_by('-start_date'))
            cache.set(cache_key, requests, timeout=60*30)  # 30m
        
        return requests
    
    @staticmethod
    def get_pending_requests(employee):
        """Get pending leave requests for employee."""
        return LeaveCacheService.get_leave_requests(
            employee, status='pending'
        )
    
    @staticmethod
    def clear_allocation_cache(employee, year):
        """Clear leave allocation cache for employee-year."""
        cache.delete(generate_cache_key(
            "hr:leaves:allocation", employee.id, year
        ))
    
    @staticmethod
    def clear_balance_cache(employee, year):
        """Clear leave balance cache for employee-year."""
        cache.delete(CacheKeys.leave_balance(employee.id, year))
    
    @staticmethod
    def clear_employee_cache(employee):
        """Clear all leave cache for an employee."""
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        pattern = f"*hr:leaves*{employee.id}*"
        keys = redis_conn.keys(pattern)
        if keys:
            redis_conn.delete(*keys)
