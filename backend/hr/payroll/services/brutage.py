from decimal import Decimal
from .contributions    import SocialContributionService
from .taxes            import TaxCalculationService
from .legal_allowances import LegalAllowanceService


class GrossUpService:
    """
    Handles 'Net-to-Gross' (Brutage) calculations for DRC.
    Calculates the Base Salary required to reach a target Net Salary.
    """

    @classmethod
    def calculate_base_from_net(
        cls, 
        target_net: Decimal, 
        company_size: int = 1, 
        worked_days: int = 26,
        child_count: int = 0,
        is_hourly: bool = False,
        std_monthly_hours: Decimal = Decimal('195'),
        tolerance: Decimal = Decimal('1.00')
    ) -> Decimal:
        if target_net <= 0:
            return Decimal('0.00')

        # Bounds: Lower 0, Upper is high enough to cover 40% tax + social
        low = Decimal('0.00')
        high = target_net * Decimal('3.0') 
        
        candidate = (low + high) / 2
        
        # Max 50 iterations to find the base salary
        for _ in range(50):
            current_net = cls._derive_total_net(
                candidate=candidate, 
                company_size=company_size,
                worked_days=worked_days,
                child_count=child_count,
                is_hourly=is_hourly,
                std_monthly_hours=std_monthly_hours
            )
            
            if abs(current_net - target_net) < tolerance:
                break
                
            if current_net < target_net:
                low = candidate
            else:
                high = candidate
            
            candidate = (low + high) / 2

        return candidate.quantize(Decimal('0.01'))

    @classmethod
    def _derive_total_net(
        cls, 
        candidate: Decimal, 
        company_size: int,
        worked_days: int,
        child_count: int,
        is_hourly: bool,
        std_monthly_hours: Decimal
    ) -> Decimal:
        # Determine the monthly base salary for simulation
        if is_hourly:
            base_salary = (candidate * std_monthly_hours).quantize(Decimal('0.01'))
        else:
            base_salary = candidate

        # We assume Gross = Base during simulation (excluding allowances)
        # Note: OT and other bonuses are ignored during Net-to-Base search
        gross_before_allowances = base_salary 

        # 1. Social Contributions (CNSS 5% with ceiling)
        social = SocialContributionService.calculate_contributions(
            gross_amount=gross_before_allowances, 
            company_size=company_size
        )
        cnss_employee = social['employee_total']
        
        # 2. Legal Allowances
        allowances = LegalAllowanceService.calculate_allowances(
            worked_days=worked_days,
            child_count=child_count,
            base_salary=base_salary
        )
        
        # 3. Taxable Base for IPR
        # In DRC: (Gross - CNSS) + Taxable Housing Excess
        taxable_base = (gross_before_allowances - cnss_employee) + allowances['taxable_housing_excess']
        
        # 4. IPR Tax calculation
        ipr = TaxCalculationService.calculate_progressive_tax(taxable_base)
        
        # 5. Final Net to Pay
        # Net = (Gross + Total Allowances) - (CNSS + IPR)
        total_monthly_net = (gross_before_allowances + allowances['total_allowances']) - (cnss_employee + ipr)
        
        if is_hourly:
            # Return net hourly rate to compare with target
            return (total_monthly_net / std_monthly_hours).quantize(Decimal('0.01'))
        
        return total_monthly_net

