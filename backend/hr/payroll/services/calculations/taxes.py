from decimal import Decimal, ROUND_HALF_UP
from hr.payroll.models import TaxBracket


class TaxCalculationService:
    """
    Handles the calculation of IPR (Income Tax on Remunerations) for DRC.
    """

    @classmethod
    def calculate_progressive_tax(cls, taxable_income: Decimal) -> Decimal:
        """
        Calculates the monthly IPR tax based on progressive tax brackets in DRC.
        """
        if taxable_income <= 0:
            return Decimal('0.00')

        # 1. Annualize the monthly taxable income
        annual_income = taxable_income * Decimal('12')
        total_annual_tax = Decimal('0.00')

        # Retrieve active tax brackets
        brackets = TaxBracket.objects.filter(is_active=True).order_by('lower_limit')
        
        if not brackets.exists():
            return Decimal('0.00')

        # 2. Calculate annual tax using progressive brackets
        for bracket in brackets:
            # If income exceeds the bracket's lower limit
            if annual_income > bracket.lower_limit:
                # Determine the upper boundary for calculation
                upper_limit = bracket.upper_limit if bracket.upper_limit else annual_income
                
                # Calculate the portion of income within this specific bracket
                taxable_in_bracket = min(annual_income, upper_limit) - bracket.lower_limit
                
                if taxable_in_bracket > 0:
                    tax_for_bracket = taxable_in_bracket * (bracket.rate_percentage / Decimal('100'))
                    total_annual_tax += tax_for_bracket
            else:
                # Income does not reach higher brackets
                break

        # 3. Convert back to monthly tax amount
        monthly_tax = total_annual_tax / Decimal('12')

        # 4. Apply DRC legal constraints
        
        # Minimum Tax Rule (2 000 FC per month as per DRC tax law)
        min_tax = Decimal('2000.00')
        if monthly_tax < min_tax:
            monthly_tax = min_tax

        # Maximum Tax Cap Rule (Total tax cannot exceed 30% of the taxable base)
        # Ref: Article 84 of the DRC Tax Code
        max_tax_cap_rate = Decimal('0.30')
        max_allowed_tax = taxable_income * max_tax_cap_rate
        
        if monthly_tax > max_allowed_tax:
            monthly_tax = max_allowed_tax

        return monthly_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

