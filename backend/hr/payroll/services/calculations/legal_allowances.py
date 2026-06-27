from decimal          import Decimal
from hr.payroll.enums import LegalAllowanceType, CalculationMode
from hr.payroll.services.cache import PayrollCacheService


class LegalAllowanceService:
    """ Handles calculation of statutory allowances (Family, Housing, Transport). """

    @classmethod
    def calculate_allowances(cls, worked_days: int, child_count: int, base_salary: Decimal):
        """ Calculates statutory allowances based on local regulations and company configuration. """
        config = PayrollCacheService.get_configuration()

        results = {
            'family_allowance': Decimal('0.00'),
            'housing_allowance': Decimal('0.00'),
            'transport_allowance': Decimal('0.00'),
            'taxable_housing_excess': Decimal('0.00'),
            'total_allowances': Decimal('0.00'),
            'details': []
        }

        # 1. Family Allowance (Exempt from tax)
        all_allowances = PayrollCacheService.get_legal_allowances()
        family_config = next((a for a in all_allowances if a.allowance_type == LegalAllowanceType.FAMILY), None)
        smig = PayrollCacheService.get_smig()

        daily_min_family = config.family_allowance_min_amount.amount if config and config.family_allowance_min_amount else Decimal('262.00')
        if smig:
            # Min: usually 1/27 of SMIG per day per child, but depends on config
            divider = config.family_allowance_smig_divider if config else Decimal('27.0')
            daily_min_family = max(daily_min_family, (smig.daily_rate.amount / divider))

        daily_per_child = (family_config.base_amount.amount if family_config and family_config.base_amount else daily_min_family)
        results['family_allowance'] = (daily_per_child * Decimal(child_count) * Decimal(worked_days)).quantize(Decimal('0.01'))
        results['details'].append({
            'type': LegalAllowanceType.FAMILY,
            'label': 'Allocations Familiales',
            'amount': results['family_allowance']
        })

        # 2. Housing Allowance
        housing_config = next((a for a in all_allowances if a.allowance_type == LegalAllowanceType.HOUSING), None)

        # Legal Exemption Limit: Defaults to 30% of BASE SALARY if not specified in model or config
        threshold = config.housing_allowance_min_percentage if (config and config.housing_allowance_min_percentage) else Decimal('30.00')
        if housing_config and housing_config.taxable_threshold_percentage is not None:
            threshold = housing_config.taxable_threshold_percentage

        housing_exemption_limit = (base_salary * (threshold / Decimal('100'))).quantize(Decimal('0.01'))

        # Amount paid: Use calculation mode
        total_housing_paid = Decimal('0.00')
        if housing_config:
            if housing_config.calculation_mode == CalculationMode.FIXED:
                total_housing_paid = housing_config.base_amount.amount or Decimal('0.00')
            elif housing_config.calculation_mode == CalculationMode.PERCENTAGE:
                total_housing_paid = (base_salary * (housing_config.base_amount.amount / Decimal('100')))
            else:
                # Default to exemption limit if nothing set
                total_housing_paid = housing_config.base_amount.amount if (housing_config.base_amount and housing_config.base_amount.amount > 0) else housing_exemption_limit
        else:
            total_housing_paid = housing_exemption_limit

        # Taxable calculation: if is_taxable is false, we check the excess above threshold
        # In DRC, even if "non-taxable", the excess above 30% is taxable.
        if housing_config and not housing_config.is_taxable:
            if total_housing_paid > housing_exemption_limit:
                results['taxable_housing_excess'] = total_housing_paid - housing_exemption_limit
        elif housing_config and housing_config.is_taxable:
            # If explicitly marked as taxable, the whole amount is taxable
            results['taxable_housing_excess'] = total_housing_paid

        results['housing_allowance'] = total_housing_paid.quantize(Decimal('0.01'))
        results['details'].append({
            'type': LegalAllowanceType.HOUSING,
            'label': 'Indemnité de Logement',
            'amount': results['housing_allowance']
        })

        # 3. Transport Allowance (Exempt from tax if reasonable)
        transport_config = next((a for a in all_allowances if a.allowance_type == LegalAllowanceType.TRANSPORT), None)
        if transport_config:
            amount = transport_config.base_amount.amount or Decimal('2000.00')
            if transport_config.calculation_mode == CalculationMode.PERCENTAGE:
                daily_transport = (base_salary / Decimal('26')) * (amount / Decimal('100'))
            else:
                daily_transport = amount

            results['transport_allowance'] = (daily_transport * Decimal(worked_days)).quantize(Decimal('0.01'))
            results['details'].append({
                'type': LegalAllowanceType.TRANSPORT,
                'label': 'Indemnité de Transport',
                'amount': results['transport_allowance']
            })

            # If taxable or exceeds limit (if we had a limit for transport, usually 4 trips/day in DRC)
            if transport_config.is_taxable:
                # We should add a field for transport taxable excess if needed,
                # but currently we assume it's either exempt or fully taxable if marked.
                pass

        # Total
        results['total_allowances'] = results['family_allowance'] + results['housing_allowance'] + results['transport_allowance']

        return results

