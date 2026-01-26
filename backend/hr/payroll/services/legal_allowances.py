from decimal           import Decimal
from hr.payroll.enums  import LegalAllowanceType
from hr.payroll.models import (
    LegalAllowance, 
    SMIGConfiguration, 
    PayrollConfiguration
)


class LegalAllowanceService:
    """
    Handles calculation of legal allowances in DRC (Family, Housing, Transport).
    """

    @classmethod
    def calculate_allowances(cls, worked_days: int, child_count: int, base_salary: Decimal):
        """
        Calculates legal allowances for DRC (Family, Housing, Transport).
        Ref: DRC Labor Code & Tax Code 2026.
        """
        config = PayrollConfiguration.objects.first()

        results = {
            'family_allowance': Decimal('0.00'),
            'housing_allowance': Decimal('0.00'),
            'transport_allowance': Decimal('0.00'),
            'taxable_housing_excess': Decimal('0.00'),
            'total_allowances': Decimal('0.00'),
            'details': []
        }

        # 1. Family Allowance (Exempt from tax)
        family_config = LegalAllowance.objects.filter(allowance_type=LegalAllowanceType.FAMILY, is_active=True).first()
        smig = SMIGConfiguration.objects.filter(is_active=True).first()
        
        daily_min_family = config.family_allowance_min_amount if config else Decimal('262.00')
        if smig:
            # Min: 1/27 of SMIG per day per child
            daily_min_family = max(daily_min_family, (smig.daily_rate / Decimal('27.0')))
            
        daily_per_child = (family_config.base_amount if family_config and family_config.base_amount else daily_min_family)
        results['family_allowance'] = (daily_per_child * Decimal(child_count) * Decimal(worked_days)).quantize(Decimal('0.01'))
        
        # 2. Housing Allowance
        housing_config = LegalAllowance.objects.filter(allowance_type=LegalAllowanceType.HOUSING, is_active=True).first()
        
        # Legal Exemption Limit: 30% of BASE SALARY
        housing_exemption_limit = (base_salary * Decimal('0.30')).quantize(Decimal('0.01'))
        
        # Amount paid: Use config base_amount if set, otherwise default to 30% of base salary
        total_housing_paid = housing_config.base_amount if (housing_config and housing_config.base_amount > 0) else housing_exemption_limit
        
        # Taxable calculation: only the excess above 30% of base_salary is taxable
        if total_housing_paid > housing_exemption_limit:
            results['taxable_housing_excess'] = total_housing_paid - housing_exemption_limit
        
        results['housing_allowance'] = total_housing_paid.quantize(Decimal('0.01'))

        # 3. Transport Allowance (Exempt from tax if reasonable)
        transport_config = LegalAllowance.objects.filter(allowance_type=LegalAllowanceType.TRANSPORT, is_active=True).first()
        if transport_config:
            daily_transport = transport_config.base_amount or Decimal('2000.00')
            results['transport_allowance'] = (daily_transport * Decimal(worked_days)).quantize(Decimal('0.01'))

        # Total
        results['total_allowances'] = results['family_allowance'] + results['housing_allowance'] + results['transport_allowance']
        
        return results

