from django.core.cache         import cache
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.payroll.models import (
    PayrollConfiguration,
    EmployeeContract,
    PayrollRun,
    SalaryAdvance,
    WorkedDaysRecord,
    TaxBracket,
    SocialContributionRate,
    SMIGConfiguration,
    LegalAllowance,
    OvertimeRule,
)


class PayrollCacheService:
    """ Cache management for payroll models and calculations. """
    
    @staticmethod
    def get_configuration():
        """ Gets cached payroll configuration. """
        cache_key = CacheKeys.payroll_config()
        config = cache.get(cache_key)
        
        if config is None:
            config = PayrollConfiguration.objects.first()
            if config:
                cache.set(cache_key, config, timeout=60*60*24)  # 24h
        
        return config
    
    @staticmethod
    def get_tax_brackets():
        """ Gets active tax brackets from cache. """
        cache_key = generate_cache_key("hr:payroll:tax_brackets")
        brackets = cache.get(cache_key)
        
        if brackets is None:
            brackets = list(TaxBracket.objects.filter(is_active=True).order_by('lower_limit'))
            cache.set(cache_key, brackets, timeout=60*60*24)  # 24h
        
        return brackets

    @staticmethod
    def get_social_contribution_rates():
        """ Gets active social contribution rates from cache. """
        cache_key = generate_cache_key("hr:payroll:social_rates")
        rates = cache.get(cache_key)
        
        if rates is None:
            rates = list(SocialContributionRate.objects.filter(is_active=True))
            cache.set(cache_key, rates, timeout=60*60*24)  # 24h
        
        return rates

    @staticmethod
    def get_smig():
        """ Gets active SMIG configuration from cache. """
        cache_key = generate_cache_key("hr:payroll:smig")
        smig = cache.get(cache_key)
        
        if smig is None:
            smig = SMIGConfiguration.objects.filter(is_active=True).first()
            if smig:
                cache.set(cache_key, smig, timeout=60*60*24)  # 24h
        
        return smig

    @staticmethod
    def get_legal_allowances():
        """ Gets active legal allowances from cache. """
        cache_key = generate_cache_key("hr:payroll:legal_allowances")
        allowances = cache.get(cache_key)
        
        if allowances is None:
            allowances = list(LegalAllowance.objects.filter(is_active=True))
            cache.set(cache_key, allowances, timeout=60*60*24)  # 24h
        
        return allowances

    @staticmethod
    def get_overtime_rules():
        """ Gets active overtime rules from cache. """
        cache_key = generate_cache_key("hr:payroll:overtime_rules")
        rules = cache.get(cache_key)
        
        if rules is None:
            rules = list(OvertimeRule.objects.filter(is_active=True))
            cache.set(cache_key, rules, timeout=60*60*24)  # 24h
        
        return rules

    @staticmethod
    def get_employee_contract_for_date(employee, date):
        """ Retrieves the active employee contract for a specific date. """
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
        """ Retrieves all contracts for an employee. """
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
        """ Retrieves all active contracts for a specific date (default: today). """
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
        """ Retrieves a payroll run by ID from cache. """
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
        """ Retrieves pending salary advances for an employee. """
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
        """ Retrieves the worked days record for an employee in a given period. """
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
        cache.delete(generate_cache_key("hr:payroll:tax_brackets"))
        cache.delete(generate_cache_key("hr:payroll:social_rates"))
        cache.delete(generate_cache_key("hr:payroll:smig"))
        cache.delete(generate_cache_key("hr:payroll:legal_allowances"))
        cache.delete(generate_cache_key("hr:payroll:overtime_rules"))
    
    @staticmethod
    def clear_employee_cache(employee):
        """Clear all cache for an employee."""
        from django_redis import get_redis_connection
        
        employee_id = employee.id if hasattr(employee, 'id') else employee
        
        redis_conn = get_redis_connection("default")
        pattern = f"*hr:payroll*{employee_id}*"
        keys = redis_conn.keys(pattern)
        if keys:
            redis_conn.delete(*keys)
    
    @staticmethod
    def clear_payroll_run_cache(payroll_run_id):
        """Clear cache for a specific payroll run."""
        cache.delete(CacheKeys.payroll_run(payroll_run_id))

    @staticmethod
    def clear_contract_cache(contract):
        """Clear contract-related caches."""
        PayrollCacheService.clear_employee_cache(contract.employee_id)
        cache.delete(generate_cache_key("hr:payroll:active_contracts", contract.start_date))

