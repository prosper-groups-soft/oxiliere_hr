from decimal import Decimal, ROUND_HALF_UP
from hr.payroll.services.cache import PayrollCacheService


class TaxCalculationService:
    """ Handles calculation of progressive income tax (IPR). """

    @classmethod
    def calculate_progressive_tax(cls, taxable_income: Decimal) -> Decimal:
        """ Calculates monthly income tax using progressive brackets and statutory limits. """
        if taxable_income <= 0:
            return Decimal('0.00')

        # 1. Annualize the monthly taxable income
        annual_income = taxable_income * Decimal('12')
        total_annual_tax = Decimal('0.00')

        # Retrieve active tax brackets
        brackets = PayrollCacheService.get_tax_brackets()
        
        if not brackets:
            return Decimal('0.00')

        # 2. Calculate annual tax using progressive brackets
        for bracket in brackets:
            # If income exceeds the bracket's lower limit
            if annual_income > bracket.lower_limit.amount:
                # Determine the upper boundary for calculation
                upper_limit = bracket.upper_limit.amount if bracket.upper_limit else annual_income
                
                # Calculate the portion of income within this specific bracket
                taxable_in_bracket = min(annual_income, upper_limit) - bracket.lower_limit.amount
                
                if taxable_in_bracket > 0:
                    tax_for_bracket = taxable_in_bracket * (bracket.rate_percentage / Decimal('100'))
                    total_annual_tax += tax_for_bracket
            else:
                # Income does not reach higher brackets
                break

        # 3. Convert back to monthly tax amount
        monthly_tax = total_annual_tax / Decimal('12')

        # 4. Apply DRC legal constraints (retrieved from brackets if available)
        # Defaults for DRC: 2000 FC min, 30% max cap
        min_tax = Decimal('2000.00')
        max_tax_cap_rate = Decimal('0.30')
        
        # We take the constraints from the first active bracket record
        # In DRC, these are unique system-wide constants usually stored with the brackets
        first_bracket = brackets[0] if brackets else None
        if first_bracket:
            if first_bracket.min_tax_amount is not None:
                min_tax = first_bracket.min_tax_amount.amount
            if first_bracket.max_tax_percentage is not None:
                max_tax_cap_rate = first_bracket.max_tax_percentage / Decimal('100')

        # Minimum Tax Rule
        if monthly_tax < min_tax:
            monthly_tax = min_tax

        # Maximum Tax Cap Rule (Total tax cannot exceed X% of the taxable base)
        # Ref: Article 84 of the DRC Tax Code
        max_allowed_tax = taxable_income * max_tax_cap_rate
        
        if monthly_tax > max_allowed_tax:
            monthly_tax = max_allowed_tax

        return monthly_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

