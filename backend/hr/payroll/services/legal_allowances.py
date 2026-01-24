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
    def calculate_allowances(cls, worked_days: int, child_count: int, gross_salary: Decimal, base_salary: Decimal):
        """
        Calculates legal allowances (Family, Housing, Transport) following DRC standards.
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

        # 1. Family Allowance (Allocation Familiale)
        # Rule: Minimum per child per day (or 1/27 of SMIG if higher)
        family_config = LegalAllowance.objects.filter(allowance_type=LegalAllowanceType.FAMILY, is_active=True).first()
        smig = SMIGConfiguration.objects.filter(is_active=True).first()
        
        # Flexibility: Use DB constants
        daily_min_family = config.family_allowance_min_amount if config else Decimal('262.00')
        smig_divider = config.family_allowance_smig_divider if config else Decimal('27.0')
        
        if smig and smig_divider > 0:
            daily_min_family = max(daily_min_family, (smig.daily_rate / smig_divider))
            
        daily_per_child = (family_config.base_amount if family_config and family_config.base_amount else daily_min_family)
        results['family_allowance'] = (daily_per_child * Decimal(child_count) * Decimal(worked_days)).quantize(Decimal('0.01'))
        
        if results['family_allowance'] > 0:
            results['details'].append({
                'type': LegalAllowanceType.FAMILY,
                'label': 'Allocations Familiales',
                'amount': results['family_allowance']
            })

        # 2. Housing Allowance (Contre-valeur Logement)
        housing_config = LegalAllowance.objects.filter(allowance_type=LegalAllowanceType.HOUSING, is_active=True).first()
        
        # Flexibility: Use DB constant for minimum percentage
        min_housing_perc = (config.housing_allowance_min_percentage / Decimal('100')) if config else Decimal('0.30')
        min_housing_monthly = base_salary * min_housing_perc
        
        if housing_config and housing_config.base_amount:
            total_housing = housing_config.base_amount
        else:
            total_housing = min_housing_monthly
            
        total_housing = total_housing.quantize(Decimal('0.01'))

        # Taxable rule
        if housing_config and housing_config.taxable_threshold_percentage:
            threshold = gross_salary * (housing_config.taxable_threshold_percentage / Decimal('100'))
            if total_housing > threshold:
                results['taxable_housing_excess'] = total_housing - threshold
        
        results['housing_allowance'] = total_housing
        results['details'].append({
            'type': LegalAllowanceType.HOUSING,
            'label': 'Contre-valeur Logement',
            'amount': total_housing,
            'taxable_excess': results['taxable_housing_excess']
        })

        # 3. Transport Allowance
        transport_config = LegalAllowance.objects.filter(allowance_type=LegalAllowanceType.TRANSPORT, is_active=True).first()
        if transport_config:
            daily_transport = transport_config.base_amount or Decimal('2000.00')
            results['transport_allowance'] = (daily_transport * Decimal(worked_days)).quantize(Decimal('0.01'))
            results['details'].append({
                'type': LegalAllowanceType.TRANSPORT,
                'label': 'Indemnité de Transport',
                'amount': results['transport_allowance']
            })

        results['total_allowances'] = results['family_allowance'] + results['housing_allowance'] + results['transport_allowance']
        return results

