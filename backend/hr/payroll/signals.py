from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from hr.payroll.models import (
    PayrollConfiguration,
    EmployeeContract,
    PayrollAdjustment,
    EmployeeAdjustment,
    PayrollRun,
    EmployeePayslip,
    SalaryAdvance,
    AdvanceDeductionConfiguration,
    RepaymentRecord,
    SMIGConfiguration,
    SocialContributionRate,
    OvertimeRule,
    LegalAllowance,
    WorkedDaysRecord,
    TaxBracket
)
from hr.payroll.services.cache import PayrollCacheService


@receiver([post_save, post_delete], sender=PayrollConfiguration)
@receiver([post_save, post_delete], sender=SMIGConfiguration)
@receiver([post_save, post_delete], sender=SocialContributionRate)
@receiver([post_save, post_delete], sender=TaxBracket)
@receiver([post_save, post_delete], sender=LegalAllowance)
@receiver([post_save, post_delete], sender=OvertimeRule)
def invalidate_payroll_config_cache(sender, instance, **kwargs):
    """Invalidate global payroll configuration and rules cache."""
    PayrollCacheService.clear_config_cache()


@receiver([post_save, post_delete], sender=EmployeeContract)
def invalidate_contract_cache(sender, instance, **kwargs):
    """Invalidate contract-related caches."""
    PayrollCacheService.clear_contract_cache(instance)


@receiver([post_save, post_delete], sender=PayrollAdjustment)
def invalidate_adjustment_cache(sender, instance, **kwargs):
    """Invalidate global adjustment cache."""
    PayrollCacheService.clear_adjustment_cache()


@receiver([post_save, post_delete], sender=EmployeeAdjustment)
def invalidate_employee_adjustment_cache(sender, instance, **kwargs):
    """Invalidate specific employee adjustment cache."""
    PayrollCacheService.clear_employee_cache(instance.employee_id)


@receiver([post_save, post_delete], sender=PayrollRun)
def invalidate_payroll_run_cache(sender, instance, **kwargs):
    """Invalidate payroll run cache."""
    PayrollCacheService.clear_payroll_run_cache(instance.id)


@receiver([post_save, post_delete], sender=EmployeePayslip)
def invalidate_payslip_cache(sender, instance, **kwargs):
    """Invalidate employee payslip cache via employee ID."""
    PayrollCacheService.clear_employee_cache(instance.contract.employee_id)


@receiver([post_save, post_delete], sender=SalaryAdvance)
@receiver([post_save, post_delete], sender=AdvanceDeductionConfiguration)
@receiver([post_save, post_delete], sender=RepaymentRecord)
def invalidate_advance_cache(sender, instance, **kwargs):
    """Invalidate salary advance related caches for the employee."""
    # All these models have an employee or can reach one
    employee_id = getattr(instance, 'employee_id', None)
    if not employee_id and hasattr(instance, 'salary_advance'):
        employee_id = instance.salary_advance.employee_id
    elif not employee_id and hasattr(instance, 'advance'):
        employee_id = instance.advance.employee_id
    
    if employee_id:
        PayrollCacheService.clear_employee_cache(employee_id)


@receiver([post_save, post_delete], sender=WorkedDaysRecord)
def invalidate_worked_days_cache(sender, instance, **kwargs):
    """Invalidate worked days record cache."""
    PayrollCacheService.clear_employee_cache(instance.employee_id)

