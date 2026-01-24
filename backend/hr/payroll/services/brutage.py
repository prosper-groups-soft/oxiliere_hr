from decimal           import Decimal
from .contributions    import SocialContributionService
from .taxes            import TaxCalculationService
from .legal_allowances import LegalAllowanceService


class GrossUpService:
    """
    Handles 'Net-to-Gross' (Brutage) calculations for DRC.
    This service finds the Gross amount (Base Salary or Hourly Rate) required 
    to reach a target Net (Base or Total Net à Payer) after all deductions 
    and legal allowances.
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
        """
        Uses a bisection (goal-seeking) algorithm to find the Base Salary or Hourly Rate.
        
        This enhanced version targets the 'Net à Payer' (Total Net).
        Net = (Gross + Allowances) - (SocialDeductions + IPR)
        """
        if target_net <= 0:
            return Decimal('0.00')

        # Initial bounds for bisection
        # Lower bound: 0 (since allowances can make base salary < net)
        low = Decimal('0.00')
        # Upper bound: Roughly net * 2 (to cover taxes + social + potential high base)
        high = target_net * Decimal('2.5') 
        
        candidate = (low + high) / 2
        
        # Max 50 iterations for precision and safety
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
        """
        Helper to calculate the Net (Monthly or Hourly) for a candidate.
        Includes social contributions, legal allowances, and progressive tax.
        """
        if is_hourly:
            hourly_rate = candidate
            base_salary = (hourly_rate * std_monthly_hours).quantize(Decimal('0.01'))
            gross_salary = base_salary # Simplification for goal seeking: assume 0 OT
        else:
            base_salary = candidate
            gross_salary = base_salary # Simplification for goal seeking: assume 0 OT

        # 1. Social Contributions (Worker 5% on Gross)
        social = SocialContributionService.calculate_contributions(gross_salary, base_salary, company_size)
        cnss_employee = Decimal('0.00')
        for d in social['details']:
            if d['type'] == 'CNSS':
                cnss_employee = d['employee_amount']
        
        # 2. Legal Allowances
        allowances = LegalAllowanceService.calculate_allowances(
            worked_days=worked_days,
            child_count=child_count,
            gross_salary=gross_salary,
            base_salary=base_salary
        )
        
        # 3. Taxable Base
        # Base IPR = (Gross - CNSS) + Taxable Housing Excess
        taxable_base = (gross_salary - cnss_employee) + allowances['taxable_housing_excess']
        
        # 4. IPR Tax
        ipr = TaxCalculationService.calculate_progressive_tax(taxable_base)
        
        # 5. Resulting Net à Payer
        # Net = (Gross + Total Allowances) - (CNSS + IPR)
        total_monthly_net = (gross_salary + allowances['total_allowances']) - (cnss_employee + ipr)
        
        if is_hourly:
            return (total_monthly_net / std_monthly_hours).quantize(Decimal('0.01'))
        
        return total_monthly_net
