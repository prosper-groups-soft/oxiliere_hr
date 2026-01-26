from decimal import Decimal, ROUND_HALF_UP
from hr.payroll.models import SocialContributionRate
from hr.payroll.enums import SocialContributionType


class SocialContributionService:
    """
    Handles calculation of social contributions in DRC (CNSS, ONEM, INPP).
    Ref: Social Security Law and Professional Training Laws 2026.
    """

    @classmethod
    def calculate_contributions(cls, gross_amount: Decimal, company_size: int = 1):
        """
        Calculates all active social contributions based on DRC rules.
        
        Assumptions for DRC:
        - All contributions (CNSS, INPP, ONEM) share the same gross base (excluding legal allowances).
        - CNSS applies a ceiling for the Family branch (252,750 FC).
        - INPP and ONEM are 100% employer-funded.
        """
        results = {
            'employee_total': Decimal('0.00'),
            'employer_total': Decimal('0.00'),
            'details': []
        }

        # Fetch active rates
        rates = SocialContributionRate.objects.filter(is_active=True)

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

