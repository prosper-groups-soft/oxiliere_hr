from decimal import Decimal, ROUND_HALF_UP
from hr.payroll.enums import SocialContributionType
from hr.payroll.services.cache import PayrollCacheService


class SocialContributionService:
    """ Handles calculation of statutory social contributions (CNSS, ONEM, INPP). """

    @classmethod
    def calculate_contributions(cls, gross_amount: Decimal, company_size: int = 1):
        """ Calculates employee and employer social contributions based on active rates and ceilings. """
        results = {
            'employee_total': Decimal('0.00'),
            'employer_total': Decimal('0.00'),
            'details': []
        }

        # Fetch active rates
        rates = PayrollCacheService.get_social_contribution_rates()

        for rate in rates:
            # 1. Base selection
            # In DRC, CNSS, INPP, and ONEM are calculated on the Gross Income 
            # (Rémunération soumise à cotisation)
            calc_base = gross_amount

            # 2. INPP Company Size Validation
            if rate.contribution_type == SocialContributionType.INPP:
                if rate.company_size_min and company_size < rate.company_size_min:
                    continue
                if rate.company_size_max and company_size > rate.company_size_max:
                    continue

            # 3. Ceiling Application (Mainly for CNSS)
            applied_base = calc_base
            if rate.ceiling_amount and calc_base > rate.ceiling_amount:
                applied_base = rate.ceiling_amount

            # 4. Calculate portions using high precision rounding
            employee_amt = (applied_base * (rate.employee_portion / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            employer_amt = (applied_base * (rate.employer_portion / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            # 5. Accumulate totals
            results['employee_total'] += employee_amt
            results['employer_total'] += employer_amt
            
            results['details'].append({
                'type': rate.contribution_type,
                'label': rate.get_contribution_type_display(),
                'employee_amount': employee_amt,
                'employer_amount': employer_amt,
                'applied_base': applied_base,
                'rate': rate.rate_percentage
            })

        return results

