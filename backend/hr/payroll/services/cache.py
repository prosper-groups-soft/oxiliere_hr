"""
Payroll caching services.

Handles caching of payroll-related queries and calculations.
"""

from django.core.cache import cache
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.payroll.models import (
    PayrollConfiguration,
    EmployeeContract,
    PayrollRun,
    SalaryAdvance,
    WorkedDaysRecord,
)


class PayrollCacheService:
    """Cache operations for payroll module."""
    
    @staticmethod
    def get_configuration():
        """
        Get payroll configuration (cached - stable data).
        
        Returns:
            PayrollConfiguration instance
        """
        cache_key = CacheKeys.payroll_config()
        config = cache.get(cache_key)
        
        if config is None:
            config = PayrollConfiguration.objects.first()
            if config:
                cache.set(cache_key, config, timeout=60*60*24)  # 24h
        
        return config
    
    @staticmethod
    def get_employee_contract_for_date(employee, date):
        """
        Get active employee contract for a specific date.
        
        Args:
            employee: Employee instance
            date: Date to check contract validity
        
        Returns:
            EmployeeContract instance or None
        """
        cache_key = CacheKeys.payroll_contract(employee.id, date)
        contract = cache.get(cache_key)
        
        if contract is None:
            contract = EmployeeContract.objects.filter(
                employee=employee,
                effective_date__lte=date,
                end_date__gte=date
            ).first()
            
            if contract:
                cache.set(cache_key, contract, timeout=60*60)  # 1h
        
        return contract
    
    @staticmethod
    def get_employee_contracts(employee):
        """
        Get all contracts for an employee (cached).
        
        Args:
            employee: Employee instance
        
        Returns:
            List of EmployeeContract instances
        """
        cache_key = generate_cache_key("hr:payroll:contracts", employee.id)
        contracts = cache.get(cache_key)
        
        if contracts is None:
            contracts = list(EmployeeContract.objects.filter(
                employee=employee
            ).order_by('-effective_date'))
            
            cache.set(cache_key, contracts, timeout=60*60*24)  # 24h
        
        return contracts
    
    @staticmethod
    def get_active_contracts(date=None):
        """
        Get all active contracts for a date.
        
        Args:
            date: Date to check (default: today)
        
        Returns:
            List of active EmployeeContract instances
        """
        from django.utils import timezone
        
        if date is None:
            date = timezone.now().date()
        
        cache_key = generate_cache_key("hr:payroll:active_contracts", date)
        contracts = cache.get(cache_key)
        
        if contracts is None:
            contracts = list(EmployeeContract.objects.filter(
                effective_date__lte=date,
                end_date__gte=date
            ))
            
            cache.set(cache_key, contracts, timeout=60*60)  # 1h
        
        return contracts
    
    @staticmethod
    def get_payroll_run(payroll_run_id):
        """
        Get payroll run by ID (cached).
        
        Args:
            payroll_run_id: PayrollRun ID or instance
        
        Returns:
            PayrollRun instance
        """
        if isinstance(payroll_run_id, PayrollRun):
            payroll_run_id = payroll_run_id.id
        
        cache_key = CacheKeys.payroll_run(payroll_run_id)
        payroll_run = cache.get(cache_key)
        
        if payroll_run is None:
            payroll_run = PayrollRun.objects.get(id=payroll_run_id)
            cache.set(cache_key, payroll_run, timeout=60*15)  # 15m
        
        return payroll_run
    
    @staticmethod
    def get_pending_salary_advances(employee):
        """
        Get pending salary advances for employee (short cache).
        
        Args:
            employee: Employee instance
        
        Returns:
            List of SalaryAdvance instances
        """
        cache_key = CacheKeys.salary_advance(employee.id)
        advances = cache.get(cache_key)
        
        if advances is None:
            advances = list(SalaryAdvance.objects.filter(
                employee=employee,
                status__in=['approved', 'pending']
            ))
            
            cache.set(cache_key, advances, timeout=60*30)  # 30m
        
        return advances
    
    @staticmethod
    def get_worked_days_record(employee, start_date, end_date):
        """
        Get worked days record for employee period.
        
        Args:
            employee: Employee instance
            start_date: Period start
            end_date: Period end
        
        Returns:
            WorkedDaysRecord instance or None
        """
        cache_key = generate_cache_key(
            "hr:payroll:worked_days", employee.id, start_date, end_date
        )
        record = cache.get(cache_key)
        
        if record is None:
            record = WorkedDaysRecord.objects.filter(
                employee=employee,
                start_date=start_date,
                end_date=end_date
            ).first()
            
            if record:
                cache.set(cache_key, record, timeout=60*30)  # 30m
        
        return record
    
    @staticmethod
    def clear_config_cache():
        """Clear payroll configuration cache."""
        cache.delete(CacheKeys.payroll_config())
    
    @staticmethod
    def clear_employee_cache(employee):
        """Clear all cache for an employee."""
        from django.core.cache import cache
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        pattern = f"*hr:payroll*{employee.id}*"
        keys = redis_conn.keys(pattern)
        if keys:
            redis_conn.delete(*keys)
    
    @staticmethod
    def clear_payroll_run_cache(payroll_run_id):
        """Clear cache for a specific payroll run."""
        cache.delete(CacheKeys.payroll_run(payroll_run_id))
