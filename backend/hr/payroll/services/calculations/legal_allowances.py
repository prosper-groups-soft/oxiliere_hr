from decimal          import Decimal
from hr.payroll.enums import LegalAllowanceType, CalculationMode
from hr.payroll.services.cache import PayrollCacheService


class LegalAllowanceService:
    """ Handles calculation of statutory allowances (Housing, Transport). """

    @classmethod
    def calculate_allowances(
        cls,
        worked_days: int,
        child_count: int,
        base_salary: Decimal,
        gross_salary: Decimal | None = None,
    ):
        """
        Calcule les allocations légales (Logement, Transport).

        NOTE — Allocation familiale :
        Prestation CNSS versée directement au travailleur (8 100 FC / enfant / mois,
        payée trimestriellement par la Caisse). Ce n'est PAS une charge de l'employeur
        et elle n'apparaît donc pas dans le bulletin de paie.

        Args:
            worked_days: Jours travaillés dans la période.
            child_count: Conservé pour compatibilité d'appel (abattement fiscal IPR
                         dans l'orchestrateur — non utilisé ici).
            base_salary: Salaire de base (pour calcul taux journalier transport
                         et plafond exonération logement × 30%).
            gross_salary: Conservé pour compatibilité d'appel (non utilisé).

        Plafond logement : 30% du salaire de base (quotité légale exonérée).
        Réf. explications IRPP : "la quotité légale ne devant pas dépasser
        30% du salaire de base".
        """
        if gross_salary is None:
            gross_salary = base_salary

        config = PayrollCacheService.get_configuration()
        all_allowances = PayrollCacheService.get_legal_allowances()

        results = {
            'housing_allowance': Decimal('0.00'),
            'transport_allowance': Decimal('0.00'),
            'taxable_housing_excess': Decimal('0.00'),
            'total_allowances': Decimal('0.00'),
            'details': []
        }

        # ─────────────────────────────────────────────────────────
        # Allocation familiale : NON calculée ici.
        # Prestation CNSS versée directement au travailleur
        # (8 100 FC / enfant / mois, payée trimestriellement par la Caisse).
        # Ce n'est PAS une charge de l'employeur — voir docs s8-configuration.md.
        # ─────────────────────────────────────────────────────────

        # 1. Housing Allowance
        # ─────────────────────────────────────────────────────────
        housing_config = next((a for a in all_allowances if a.allowance_type == LegalAllowanceType.HOUSING), None)

        threshold = config.housing_allowance_min_percentage if (config and config.housing_allowance_min_percentage) else Decimal('30.00')
        if housing_config and housing_config.taxable_threshold_percentage is not None:
            threshold = housing_config.taxable_threshold_percentage

        # Plafond légal : 30% du salaire de base (quotité légale exonérée)
        # Réf. explications IRPP : "la quotité légale ne devant pas dépasser 30% du salaire de base"
        housing_exemption_limit = (base_salary * (threshold / Decimal('100'))).quantize(Decimal('0.01'))

        # Amount paid
        total_housing_paid = Decimal('0.00')
        if housing_config:
            if housing_config.calculation_mode == CalculationMode.FIXED:
                total_housing_paid = housing_config.base_amount or Decimal('0.00')
            elif housing_config.calculation_mode == CalculationMode.PERCENTAGE:
                total_housing_paid = (base_salary * (housing_config.base_amount / Decimal('100')))
            else:
                total_housing_paid = housing_config.base_amount if (housing_config.base_amount and housing_config.base_amount > 0) else housing_exemption_limit
        else:
            total_housing_paid = housing_exemption_limit

        # Taxable excess
        if housing_config and not housing_config.is_taxable:
            if total_housing_paid > housing_exemption_limit:
                results['taxable_housing_excess'] = total_housing_paid - housing_exemption_limit
        elif housing_config and housing_config.is_taxable:
            results['taxable_housing_excess'] = total_housing_paid

        results['housing_allowance'] = total_housing_paid.quantize(Decimal('0.01'))
        results['details'].append({
            'type': LegalAllowanceType.HOUSING,
            'label': 'Indemnité de Logement',
            'amount': results['housing_allowance']
        })

        # 2. Transport Allowance
        transport_config = next((a for a in all_allowances if a.allowance_type == LegalAllowanceType.TRANSPORT), None)
        if transport_config:
            amount = transport_config.base_amount or Decimal('2000.00')
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

        # Total
        results['total_allowances'] = (
            results['housing_allowance']
            + results['transport_allowance']
        )

        return results
