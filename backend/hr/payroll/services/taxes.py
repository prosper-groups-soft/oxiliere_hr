from decimal import Decimal
from hr.payroll.models import TaxBracket


class TaxCalculationService:
    """
    Handles progressive tax calculations based on defined brackets.
    """

    @classmethod
    def calculate_progressive_tax(cls, taxable_income: Decimal) -> Decimal:
        """
        Calculates tax by splitting the income into brackets.
        Example for 5000 income:
        - 0 to 1000 @ 0% = 0
        - 1000 to 4000 @ 15% = 450
        - 4000 to 5000 @ 30% = 300
        Total Tax = 750
        """
        if taxable_income <= 0:
            return Decimal('0.00')

        total_tax = Decimal('0.00')
        brackets = TaxBracket.objects.filter(is_active=True).order_by('lower_limit')

        for bracket in brackets:
            if taxable_income > bracket.lower_limit:
                # Determine the amount within this bracket
                upper = bracket.upper_limit if bracket.upper_limit else taxable_income
                applicable_amount = min(taxable_income, upper) - bracket.lower_limit
                
                tax_for_bracket = applicable_amount * (bracket.rate_percentage / Decimal('100'))
                total_tax += tax_for_bracket
            else:
                break # Income doesn't reach higher brackets

        return total_tax.quantize(Decimal('0.01'))
    
    