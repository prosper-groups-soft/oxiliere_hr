from decimal           import Decimal
from hr.payroll.models import TaxBracket


class TaxCalculationService:
    """
    Handles progressive tax calculations based on defined brackets.
    """

    @classmethod
    def calculate_progressive_tax(cls, taxable_income: Decimal) -> Decimal:
        """
        Calculates IPR (Income Tax) using progressive annual brackets.
        Logic: Annualizes monthly income, calculates tax, then returns monthly portion.
        DRC Rules:
        - Progressive rates (3%, 15%, 30%, 40%)
        - Minimum tax: 2,000 FC (per month)
        - Maximum tax: 30% of taxable income
        """
        if taxable_income <= 0:
            return Decimal('0.00')

        # 1. Annualize taxable income
        annual_income = taxable_income * Decimal('12')
        total_annual_tax = Decimal('0.00')

        # We order by lower_limit to apply brackets sequentially
        brackets = TaxBracket.objects.filter(is_active=True).order_by('lower_limit')
        
        if not brackets.exists():
            return Decimal('0.00')

        # 2. Calculate annual tax based on progressive brackets
        for bracket in brackets:
            if annual_income > bracket.lower_limit:
                upper = bracket.upper_limit if bracket.upper_limit else annual_income
                applicable_amount = min(annual_income, upper) - bracket.lower_limit
                
                tax_for_bracket = applicable_amount * (bracket.rate_percentage / Decimal('100'))
                total_annual_tax += tax_for_bracket
            else:
                break

        # 3. Monthly portion
        monthly_tax = total_annual_tax / Decimal('12')

        # 4. Apply DRC constraints (monthly)
        first_bracket = brackets.first()
        
        # Minimum Tax Rule (e.g., 2000 FC per month)
        if first_bracket.min_tax_amount and monthly_tax < first_bracket.min_tax_amount:
            monthly_tax = first_bracket.min_tax_amount

        # Maximum Tax Rule (e.g., 30% of taxable base)
        if first_bracket.max_tax_percentage:
            max_allowed = taxable_income * (first_bracket.max_tax_percentage / Decimal('100'))
            if monthly_tax > max_allowed:
                monthly_tax = max_allowed

        return monthly_tax.quantize(Decimal('0.01'))
    
    