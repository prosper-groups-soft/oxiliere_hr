from decimal           import Decimal
from hr.payroll.models import SocialContributionRate
from hr.payroll.enums  import SocialContributionType


class SocialContributionService:
    """
    Handles calculation of social contributions in DRC (CNSS, ONEM, INPP).
    """

    @classmethod
    def calculate_contributions(cls, gross_amount: Decimal, base_salary: Decimal, company_size: int = 1):
        """
        Calculates all active social contributions based on the DRC rules.
        
        - CNSS: On Gross Salary.
        - INPP: On Gross Salary (size dependent).
        - ONEM: On Base Salary specifically.
        
        Returns:
            dict: Containing employee and employer portions for each contribution type.
        """
        results = {
            'employee_total': Decimal('0.00'),
            'employer_total': Decimal('0.00'),
            'details': []
        }

        rates = SocialContributionRate.objects.filter(is_active=True).order_by('contribution_type')

        for rate in rates:
            # Determine correct base for this specific contribution
            if rate.contribution_type == SocialContributionType.ONEM:
                calc_base = base_salary
            else:
                # CNSS and INPP are typically on Gross
                calc_base = gross_amount

            # Check company size constraint for INPP
            if rate.contribution_type == SocialContributionType.INPP:
                if rate.company_size_min and company_size < rate.company_size_min:
                    continue
                if rate.company_size_max and company_size > rate.company_size_max:
                    continue

            # Calculate portions
            applied_base = calc_base
            if rate.ceiling_amount and calc_base > rate.ceiling_amount:
                applied_base = rate.ceiling_amount

            employee_amt = (applied_base * (rate.employee_portion / Decimal('100'))).quantize(Decimal('0.01'))
            employer_amt = (applied_base * (rate.employer_portion / Decimal('100'))).quantize(Decimal('0.01'))

            results['employee_total'] += employee_amt
            results['employer_total'] += employer_amt
            results['details'].append({
                'type': rate.contribution_type,
                'label': rate.get_contribution_type_display(),
                'employee_amount': employee_amt,
                'employer_amount': employer_amt,
                'rate': rate.rate_percentage
            })

        return results
