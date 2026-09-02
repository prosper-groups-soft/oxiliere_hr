"""
Payroll Orchestrator — Pipeline 8 étapes conforme à la documentation.

Conforme à :
- metamodel.md §Processus de paie (Pipeline)
- semantics.md §Événement : Lancement du processus de paie

Les 8 étapes s'exécutent dans l'ordre immuable 1→8 :
  1. Vérification et validation de l'intégrité des données
  2. Calcul individuel des gains et majorations d'heures
  3. Détermination et validation du Salaire Brut
  4. Construction des bases intermédiaires de calcul
  5. Calcul des retenues salariales
  6. Calcul des charges patronales
  7. Calcul du Salaire Net et du Net à Payer
  8. Génération du bulletin de paie et archivage d'audit
"""

from decimal             import Decimal
from datetime            import date
import hashlib
import json

from django.db           import transaction, models
from django.db.models    import Q
from django.utils        import timezone
from hr.employees.models import Employee
from hr.payroll.models   import (
    EmployeeContract, 
    PayrollRun, 
    EmployeePayslip, 
    PayslipLine, 
    PayrollConfiguration,
    OvertimeRule,
    WorkedDaysRecord
)
from hr.payroll.enums    import (
    PayrollStatus, 
    RemunerationType, 
    OvertimeRuleType,
    SalaryBaseType,
    SocialContributionType,
    LeaveDeductionMode,
)
from hr.enums import Currency

from .adjustments        import AdjustmentResolverService
from .advances.advances              import AdvanceService
from .calculations.calculators       import PayrollCalculatorService
from .calculations.taxes             import TaxCalculationService
from .calculations.contributions     import SocialContributionService
from .calculations.legal_allowances  import LegalAllowanceService
from .calculations.bases             import (
    CalculationBasisType,
    CalculationBasisBuilder,
    PayElementRef,
)
from hr.payroll.services.integration import PayrollIntegrationService
from hr.payroll.services.calculations.brutage import GrossUpService
from hr.payroll.services.calculations.prorata import calculate_prorata_ratio
from hr.payroll.services.integration.exchange import ExchangeRateService


class PayrollOrchestrator:
    """
    Moteur principal — orchestre le pipeline de paie en 8 étapes.
    
    Principe : Pipeline immuable, déterministe, stratégies interchangeables
    (metamodel.md §Règles du pipeline).
    """

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def process_run(cls, payroll_run: PayrollRun):
        """
        Traite tous les contrats actifs pour un run de paie donné.
        
        Conforme à l'invariant I7 — Unité de période :
        Tous les employés actifs sont payés dans le même run.
        """
        if payroll_run.status != PayrollStatus.DRAFT:
            raise ValueError("Seuls les runs en statut DRAFT peuvent être traités.")

        today = timezone.localdate()
        active_contracts = EmployeeContract.objects.filter(
            start_date__lte=today,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        )

        # --- Filtrage selon la sélection persistée à la création (params_snapshot) ---
        # Rétro-compat : run sans snapshot (créé avant cette fonctionnalité)
        # → tous les contrats actifs sont traités.
        selection = (payroll_run.params_snapshot or {}).get('selection', {})
        scope = selection.get('scope', 'all')

        if scope == 'org_units':
            org_unit_ids = selection.get('org_unit_ids') or []
            if org_unit_ids:
                active_contracts = active_contracts.filter(
                    employee__position_history__org_unit_id__in=org_unit_ids,
                    employee__position_history__is_current=True,
                ).distinct()
        elif scope == 'employees':
            employee_ids = selection.get('employee_ids') or []
            if employee_ids:
                active_contracts = active_contracts.filter(
                    employee_id__in=employee_ids
                )

        config = PayrollConfiguration.objects.first()

        for contract in active_contracts:
            cls._generate_single_payslip(payroll_run, contract, config)

        payroll_run.status = PayrollStatus.VALIDATED
        payroll_run.save()

    # ------------------------------------------------------------------
    # Pipeline principal — 8 étapes
    # ------------------------------------------------------------------

    @classmethod
    def _generate_single_payslip(cls, run, contract, config):
        """
        Génère un bulletin complet en exécutant les 8 étapes du pipeline.
        
        Ordre immuable conforme à metamodel.md L581-L607.
        """
        # Prévention doublons
        existing = EmployeePayslip.objects.filter(
            payroll_run=run, contract=contract
        ).first()
        if existing:
            return existing

        # === ÉTAPE 1 : Vérification et validation de l'intégrité des données ===
        validated_data = cls._step1_validate_data(contract, run, config)

        # === ÉTAPE 2 : Calcul individuel des gains et majorations d'heures ===
        earnings = cls._step2_calculate_earnings(contract, validated_data, config, run)

        # === ÉTAPE 3 : Détermination et validation du Salaire Brut ===
        gross_salary = cls._step3_validate_gross(earnings, contract)

        # === ÉTAPE 4 : Construction des bases intermédiaires de calcul ===
        bases, pay_elements = cls._step4_build_calculation_bases(
            earnings, validated_data, config, gross_salary
        )

        # === ÉTAPE 5 : Calcul des retenues salariales ===
        deductions = cls._step5_calculate_deductions(
            bases, validated_data, config
        )

        # === ÉTAPE 6 : Calcul des charges patronales ===
        employer_charges = cls._step6_calculate_employer_charges(
            bases, validated_data
        )

        # === ÉTAPE 7 : Calcul du Salaire Net et du Net à Payer ===
        net_data = cls._step7_calculate_net(
            gross_salary, earnings, deductions, employer_charges,
            pay_elements, contract, run
        )

        # === ÉTAPE 8 : Génération du bulletin de paie et archivage d'audit ===
        payslip = cls._step8_generate_payslip_with_snapshot(
            run, contract, config,
            gross_salary, earnings, bases, pay_elements,
            deductions, employer_charges, net_data, validated_data
        )

        return payslip

    # ------------------------------------------------------------------
    # ÉTAPE 1 : Vérification et validation de l'intégrité des données
    # ------------------------------------------------------------------

    @classmethod
    def _step1_validate_data(cls, contract, run, config):
        """
        Vérifie l'intégrité des données avant tout calcul.
        
        Conforme à metamodel.md :
        - Vérifier que l'employé est actif et éligible
        - Vérifier que le contrat est actif sur la période
        - Données obligatoires présentes
        
        Récupère également les données d'entrée (attendance, family, leaves).
        """
        # --- Validation contrat actif ---
        if contract.start_date and contract.start_date > run.end_date:
            raise ValueError(
                f"Contrat {contract.id} non encore actif "
                f"(début={contract.start_date}, fin période={run.end_date})"
            )
        if contract.end_date and contract.end_date < run.start_date:
            raise ValueError(
                f"Contrat {contract.id} expiré "
                f"(fin={contract.end_date}, début période={run.start_date})"
            )

        # --- Validation salaire ---
        if contract.remuneration_type == RemunerationType.FIXED:
            if not contract.base_salary or contract.base_salary <= 0:
                raise ValueError(
                    f"Contrat {contract.id} : salaire de base absent ou nul"
                )
        elif contract.remuneration_type == RemunerationType.HOURLY:
            if not contract.hourly_rate or contract.hourly_rate <= 0:
                raise ValueError(
                    f"Contrat {contract.id} : taux horaire absent ou nul"
                )

        # --- Récupération données d'entrée ---
        attendance = PayrollIntegrationService.get_worked_days_data(
            contract.employee_id,
            run.start_date,
            run.end_date,
        )
        family = PayrollIntegrationService.get_employee_family_data(
            contract.employee_id
        )

        leave = {
            'paid_leave_days': Decimal('0.00'),
            'unpaid_leave_days': Decimal('0.00'),
        }
        if config.include_leaves_in_payroll:
            leave = PayrollIntegrationService.get_employee_leave_data(
                contract.employee_id,
                run.start_date,
                run.end_date,
            )

        company_size = Employee.objects.filter(is_active=True).count()

        conversion_rate = run.exchange_rate_applied or Decimal('1.0')
        if not run.exchange_rate_applied and contract.currency != Currency.CDF:
            conversion_rate = ExchangeRateService.get_exchange_rate(
                contract.currency, Currency.CDF
            )

        # Persister les jours travaillés
        standard_ot = Decimal(str(attendance['overtime_hours_standard']))
        tier_limit = Decimal('6.0')
        WorkedDaysRecord.objects.update_or_create(
            employee=contract.employee,
            payroll_run=run,
            defaults={
                'regular_days': attendance['regular_days'],
                'overtime_hours_first_tier': min(standard_ot, tier_limit),
                'overtime_hours_second_tier': max(Decimal('0'), standard_ot - tier_limit),
                'overtime_hours_weekend': attendance.get('overtime_hours_weekend', 0),
                'overtime_hours_holiday': attendance['overtime_hours_holiday'],
                'absence_days': attendance['absence_days'],
            }
        )

        return {
            'attendance': attendance,
            'family': family,
            'leave': leave,
            'company_size': company_size,
            'contract_currency': contract.currency,
            'conversion_rate': conversion_rate,
        }

    # ------------------------------------------------------------------
    # ÉTAPE 2 : Calcul individuel des gains et majorations d'heures
    # ------------------------------------------------------------------

    @classmethod
    def _step2_calculate_earnings(cls, contract, validated_data, config, run):
        """
        Calcule le salaire de base, les heures supplémentaires,
        les primes et bonus pour un employé.
        
        Conforme à metamodel.md Étape 2.
        Gère : multi-devise, brutage net→brut, HS, ajustements.
        """
        d = validated_data
        attendance = d['attendance']
        family = d['family']
        leave = d['leave']
        
        payroll_cfg = PayrollConfiguration.objects.first()
        std_monthly_hours = Decimal(str(
            payroll_cfg.work_hours_per_month if payroll_cfg else 195
        ))

        # --- Salaire de base ---
        if contract.remuneration_type == RemunerationType.FIXED:
            target_amount = contract.base_salary or Decimal('0')

            if d['contract_currency'] != Currency.CDF:
                target_amount = (
                    target_amount * d['conversion_rate']
                ).quantize(Decimal('0.01'))

            if contract.salary_base_type == SalaryBaseType.NET:
                base_amount = GrossUpService.calculate_base_from_net(
                    target_net=target_amount,
                    company_size=d['company_size'],
                    worked_days=attendance['regular_days'],
                    is_hourly=False,
                )
            else:
                base_amount = target_amount

            hourly_rate = base_amount / std_monthly_hours

            # --- Prorata calendaire (entrees/sorties en cours de periode) ---
            # Conforme a semantics.md §Proratisation
            # Seul le salaire de base est proratise, pas les indemnites ni HS
            prorata_ratio = calculate_prorata_ratio(
                contract_start=contract.start_date,
                contract_end=contract.end_date,
                period_start=run.start_date,
                period_end=run.end_date,
            )
            if prorata_ratio < Decimal('1.0'):
                base_amount = (base_amount * prorata_ratio).quantize(
                    Decimal('0.01')
                )
                hourly_rate = base_amount / std_monthly_hours

        else:  # HOURLY
            target_rate = contract.hourly_rate or Decimal('0')

            if d['contract_currency'] != Currency.CDF:
                target_rate = (
                    target_rate * d['conversion_rate']
                ).quantize(Decimal('0.01'))

            if contract.salary_base_type == SalaryBaseType.NET:
                hourly_rate = GrossUpService.calculate_base_from_net(
                    target_net=target_rate,
                    company_size=d['company_size'],
                    worked_days=attendance['regular_days'] + int(leave['paid_leave_days']),
                    is_hourly=True,
                    std_monthly_hours=std_monthly_hours,
                )
            else:
                hourly_rate = target_rate

            paid_leave_hours = Decimal(str(leave['paid_leave_days'])) * Decimal('8.0')
            total_hours = Decimal(str(attendance['total_worked_hours'])) + paid_leave_hours
            base_amount = (hourly_rate * total_hours).quantize(Decimal('0.01'))

        # --- Déduction des absences non payées (mode exclusif) ---
        # Conforme à semantics.md L472 : l'absence est traduite en réduction
        # du salaire de base avant la construction des bases de calcul.
        # Le mode est exclusif : un seul des 4 états (DISABLED, DAILY_RATE,
        # CALENDAR_DAYS, FIXED_AMOUNT) est actif à la fois.
        unpaid_leave_days = Decimal(str(leave['unpaid_leave_days']))
        absence_deduction = Decimal('0.00')
        leave_mode = config.leave_deduction_mode

        # Mode ATTENDANCE_DAYS : le diviseur est le nombre réel de jours de
        # travail planifiés de l'employé (planning d'attendance : jours ouvrés
        # du shift policy, moins fériés/clôtures, moins overrides manuels).
        # Le planning hebdomadaire est étendu à toute la période du bulletin.
        theoretical_days = None
        if (
            unpaid_leave_days > 0
            and leave_mode == LeaveDeductionMode.ATTENDANCE_DAYS
        ):
            theoretical_days = PayrollIntegrationService.get_theoretical_working_days(
                contract.employee_id,
                run.start_date,
                run.end_date,
            )

        if unpaid_leave_days > 0:
            if leave_mode == LeaveDeductionMode.DAILY_RATE:
                divisor = Decimal(str(config.leave_deduction_divisor)) or Decimal('26')
                per_day = base_amount / divisor
                absence_deduction = (per_day * unpaid_leave_days).quantize(Decimal('0.01'))
            elif leave_mode == LeaveDeductionMode.CALENDAR_DAYS:
                divisor = Decimal((run.end_date - run.start_date).days + 1)
                per_day = base_amount / divisor
                absence_deduction = (per_day * unpaid_leave_days).quantize(Decimal('0.01'))
            elif leave_mode == LeaveDeductionMode.ATTENDANCE_DAYS:
                # Si l'employé n'a aucun planning (0 jour théorique), on retombe
                # sur le diviseur calendaire par sécurité.
                divisor = theoretical_days if (theoretical_days and theoretical_days > 0) else Decimal((run.end_date - run.start_date).days + 1)
                per_day = base_amount / divisor
                absence_deduction = (per_day * unpaid_leave_days).quantize(Decimal('0.01'))
            elif leave_mode == LeaveDeductionMode.FIXED_AMOUNT:
                per_day = Decimal(str(config.fixed_deduction_per_absent_day or 0))
                absence_deduction = (per_day * unpaid_leave_days).quantize(Decimal('0.01'))

        # Garde-fou : la déduction ne peut pas dépasser le salaire de base
        absence_deduction = min(absence_deduction, base_amount)

        # --- Heures supplémentaires (4 paliers DRC) ---
        rules_qs = OvertimeRule.objects.filter(is_active=True)
        multipliers = {
            'first_period': (
                rules_qs.filter(rule_type=OvertimeRuleType.FIRST_TIER)
                .values_list('multiplier', flat=True).first()
                or Decimal('1.30')
            ),
            'subsequent': (
                rules_qs.filter(rule_type=OvertimeRuleType.SUBSEQUENT_HOURS)
                .values_list('multiplier', flat=True).first()
                or Decimal('1.60')
            ),
            'weekend': (
                rules_qs.filter(rule_type=OvertimeRuleType.WEEKEND)
                .values_list('multiplier', flat=True).first()
                or Decimal('2.00')
            ),
            'holiday': (
                rules_qs.filter(rule_type=OvertimeRuleType.HOLIDAY)
                .values_list('multiplier', flat=True).first()
                or Decimal('2.00')
            ),
            'night': (
                rules_qs.filter(rule_type=OvertimeRuleType.NIGHT)
                .values_list('multiplier', flat=True).first()
                or Decimal('1.50')
            ),
        }

        overtime_pay = PayrollCalculatorService.calculate_overtime_pay(
            hourly_rate=hourly_rate,
            std_hours=attendance['overtime_hours_standard'],
            hol_hours=attendance['overtime_hours_holiday'],
            weekend_hours=attendance.get('overtime_hours_weekend', 0),
            night_hours=attendance.get('overtime_hours_night', 0),
            multipliers=multipliers,
        )

        # --- Ajustements (primes, bonus, déductions) ---
        ref_date = attendance.get('end_date') or timezone.now().date()
        applicable_adjs = AdjustmentResolverService.get_applicable_adjustments(
            contract.employee_id, ref_date
        )

        total_bonuses = Decimal('0.00')
        total_other_deductions = Decimal('0.00')
        adjustment_lines = []

        for adj in applicable_adjs:
            val = PayrollCalculatorService.calculate_adjustment_value(
                adj['mode'], base_amount, adj['amount'], adj['percentage']
            )
            if adj['type'] == 'BONUS':
                total_bonuses += val
                adjustment_lines.append({
                    'label': adj['label'], 'amount': val, 'type': 'BONUS',
                    'is_taxable': adj.get('is_taxable', True),
                    'is_cnss_subject': adj.get('is_cnss_subject', True),
                })
            else:
                total_other_deductions += val
                adjustment_lines.append({
                    'label': adj['label'], 'amount': val, 'type': 'CONTRIBUTION',
                    'is_taxable': adj.get('is_taxable', True),
                    'is_cnss_subject': adj.get('is_cnss_subject', True),
                })

        return {
            'base_amount': base_amount,
            'absence_deduction': absence_deduction,
            'leave_deduction_mode': leave_mode,
            'hourly_rate': hourly_rate,
            'overtime_pay': overtime_pay,
            'total_bonuses': total_bonuses,
            'total_other_deductions': total_other_deductions,
            'adjustment_lines': adjustment_lines,
        }

    # ------------------------------------------------------------------
    # ÉTAPE 3 : Détermination et validation du Salaire Brut
    # ------------------------------------------------------------------

    @classmethod
    def _step3_validate_gross(cls, earnings, contract):
        """
        Calcule le salaire brut et applique les déductions d'absences.
        
        Conforme à metamodel.md Étape 3.
        Le brut est la somme : base + primes + heures sup.
        Les absences non payées sont déduites à cette étape
        (semantics.md §Absence non rémunérée).
        """
        gross_salary = (
            (earnings['base_amount'] - earnings['absence_deduction'])
            + earnings['total_bonuses']
            + earnings['overtime_pay']
        )

        # Validation : le brut ne peut pas être négatif
        if gross_salary < Decimal('0.00'):
            raise ValueError(
                f"Contrat {contract.id} : salaire brut négatif ({gross_salary})"
            )

        return gross_salary

    # ------------------------------------------------------------------
    # ÉTAPE 4 : Construction des bases intermédiaires de calcul
    # ------------------------------------------------------------------

    @classmethod
    def _step4_build_calculation_bases(cls, earnings, validated_data, config, gross_salary):
        """
        Construit les 5 bases de calcul conformément au catalogue.md §4.
        
        Ordre de construction (obligatoire) :
          BASE_BRUT → BASE_CNSS → BASE_INPP → BASE_ONEM → BASE_IMPOSABLE
        
        Retourne le dict des bases + la liste des PayElementRef.
        """
        d = validated_data
        attendance = d['attendance']
        family = d['family']
        leave = d['leave']
        base_salary = earnings['base_amount']
        absence_deduction = earnings['absence_deduction']

        # Salaire de base effectif après déduction des absences non payées
        # (semantics.md L472 : l'absence est traduite en réduction du salaire de base)
        effective_base_salary = max(base_salary - absence_deduction, Decimal('0.00'))

        # --- Allocation logement ---
        # Plafond exonération logement : 30 % du salaire de base effectif
        # (quotité légale exonérée — explications IRPP). Le gross_salary est
        # conservé pour compatibilité d'appel (non utilisé dans le plafond).
        allowances = LegalAllowanceService.calculate_allowances(
            worked_days=attendance['regular_days'] + int(leave['paid_leave_days']),
            child_count=family['child_count'],
            base_salary=effective_base_salary,
            gross_salary=gross_salary,
        )

        # --- Construction des PayElementRef ---
        # Chaque ligne correspond à un élément de paie avec ses flags d'assujettissement
        elements = []

        # Salaire de base : toujours imposable, soumis CNSS/INPP/ONEM
        elements.append(PayElementRef(
            code="SAL_BASE",
            libelle="Salaire de base",
            montant=effective_base_salary,
            est_imposable=True,
            soumis_cnss=True,
            soumis_inpp=True,
            soumis_onem=True,
            est_exonere_logement=False,
            est_exonere_transport=False,
        ))

        # Heures supplémentaires
        if earnings['overtime_pay'] > 0:
            elements.append(PayElementRef(
                code="HS",
                libelle="Heures Supplémentaires",
                montant=earnings['overtime_pay'],
                est_imposable=True,
                soumis_cnss=True,
                soumis_inpp=True,
                soumis_onem=True,
            ))

        # Primes (BONUS adjustments)
        for adj in earnings['adjustment_lines']:
            if adj['type'] == 'BONUS':
                elements.append(PayElementRef(
                    code="PRIME",
                    libelle=adj['label'],
                    montant=adj['amount'],
                    # Conforme grille IRPP : primes conventionnelles imposables par défaut
                    est_imposable=adj.get('is_taxable', True),
                    soumis_cnss=adj.get('is_cnss_subject', True),
                    soumis_inpp=adj.get('is_cnss_subject', True),
                    soumis_onem=adj.get('is_cnss_subject', True),
                ))

        # Indemnité logement
        if allowances['housing_allowance'] > 0:
            elements.append(PayElementRef(
                code="IND_LOG",
                libelle="Indemnité de Logement",
                montant=allowances['housing_allowance'],
                est_imposable=True,
                soumis_cnss=True,   # pratique sociale RDC
                soumis_inpp=True,
                soumis_onem=True,
                est_exonere_logement=True,
            ))

        # Indemnité transport
        if allowances['transport_allowance'] > 0:
            elements.append(PayElementRef(
                code="IND_TRANSP",
                libelle="Indemnité de Transport",
                montant=allowances['transport_allowance'],
                est_imposable=True,
                soumis_cnss=True,   # forfaitaire non justifié → soumis
                soumis_inpp=True,
                soumis_onem=True,
                est_exonere_transport=True,
            ))

        # (Allocation familiale : prestation CNSS versée directement au travailleur,
        #  pas une charge de l'employeur — non incluse dans le bulletin.)

        # --- CNSS salariale (nécessaire pour BASE_IMPOSABLE) ---
        # La CNSS est calculée ici car elle est déduite de la base imposable
        # (cf. semantics.md §Ordre de calcul des retenues)

        # Seuil exonération logement = 30% du salaire de base effectif
        # (quotité légale exonérée — explications IRPP)
        housing_exemption_limit = (
            effective_base_salary * Decimal('0.30')
        ).quantize(Decimal('0.01'))
        exoneration_logement = min(
            allowances['housing_allowance'],
            housing_exemption_limit,
        )

        # Exonération transport (totale si non exagérée)
        exoneration_transport = allowances['transport_allowance']

        # CNSS salariale = BASE_CNSS × 5%
        cnss_base = sum(e.montant for e in elements if e.soumis_cnss)
        cnss_salariale = (cnss_base * Decimal('0.05')).quantize(Decimal('0.01'))

        # --- Construction des 5 bases ---
        bases = CalculationBasisBuilder.build_all(
            elements=elements,
            cnss_salariale=cnss_salariale,
            exoneration_logement=exoneration_logement,
            exoneration_transport=exoneration_transport,
        )

        # Enrichir avec les données d'allocations
        allowances_meta = {
            'housing_allowance': allowances['housing_allowance'],
            'transport_allowance': allowances['transport_allowance'],
            'total_allowances': allowances['total_allowances'],
            'allowance_details': allowances.get('details', []),
            'housing_exemption_limit': housing_exemption_limit,
            'exoneration_logement': exoneration_logement,
            'exoneration_transport': exoneration_transport,
            'taxable_housing_excess': allowances['taxable_housing_excess'],
            'cnss_salariale_for_basis': cnss_salariale,
        }

        return bases, {
            'elements': elements,
            'allowances': allowances_meta,
        }

    # ------------------------------------------------------------------
    # ÉTAPE 5 : Calcul des retenues salariales
    # ------------------------------------------------------------------

    @classmethod
    def _step5_calculate_deductions(cls, bases, validated_data, config):
        """
        Calcule les retenues salariales : CNSS + IPR/IRPP.
        
        Conforme à metamodel.md Étape 5.
        Ordre imposé par semantics.md §Ordre de calcul :
          1. CNSS salariale (BASE_CNSS x 5%)
          2. Base imposable nette
          3. Impôt (IPR/IRPP via barème progressif)
        """
        base_cnss = bases[CalculationBasisType.CNSS].montant
        base_imposable = bases[CalculationBasisType.IMPOSABLE].montant

        # 1. CNSS salariale
        cnss_employee = (base_cnss * Decimal('0.05')).quantize(Decimal('0.01'))

        # 2. Impôt progressif (IPR ou IRPP selon la date) + abattement familial
        nb_charges = validated_data.get('family', {}).get('child_count', 0)
        ipr_tax = TaxCalculationService.calculate_progressive_tax(
            base_imposable,
            nb_charges=nb_charges,
        )

        return {
            'cnss_employee': cnss_employee,
            'ipr_tax': ipr_tax,
            'taxable_base': base_imposable,
            'base_cnss': base_cnss,
        }

    # ------------------------------------------------------------------
    # ÉTAPE 6 : Calcul des charges patronales
    # ------------------------------------------------------------------

    @classmethod
    def _step6_calculate_employer_charges(cls, bases, validated_data):
        """
        Calcule les charges patronales : CNSS (13%), INPP, ONEM.
        
        Conforme à metamodel.md Étape 6.
        Les charges patronales n'affectent PAS le net à payer.
        """
        d = validated_data

        # Calcul via le service existant (réutilise la logique CNSS+INPP+ONEM)
        social_data = SocialContributionService.calculate_contributions(
            gross_amount=bases[CalculationBasisType.CNSS].montant,
            company_size=d['company_size'],
        )

        employer_charges = Decimal('0.00')
        cnss_patronale = Decimal('0.00')
        inpp_amount = Decimal('0.00')
        onem_amount = Decimal('0.00')
        charge_details = []

        for detail in social_data['details']:
            employer_charges += detail['employer_amount']
            if detail['type'] == SocialContributionType.CNSS:
                cnss_patronale = detail['employer_amount']
            elif detail['type'] == SocialContributionType.ONEM:
                onem_amount = detail['employer_amount']
            elif detail['type'] == SocialContributionType.INPP:
                inpp_amount = detail['employer_amount']
            charge_details.append(detail)

        return {
            'cnss_patronale': cnss_patronale,
            'inpp_amount': inpp_amount,
            'onem_amount': onem_amount,
            'total_employer_charges': employer_charges,
            'charge_details': charge_details,
        }

    # ------------------------------------------------------------------
    # ÉTAPE 7 : Calcul du Salaire Net et du Net à Payer
    # ------------------------------------------------------------------

    @classmethod
    def _step7_calculate_net(
        cls, gross_salary, earnings, deductions, employer_charges,
        pay_elements, contract, run
    ):
        """
        Calcul le net à payer et le coût total employeur.
        
        Conforme à metamodel.md Étape 7.
        
        net_à_payer = brut + allocations - retenues - avances - autres déductions
        coût_employeur = brut + charges patronales
        """
        allowances = pay_elements.get('allowances', {})
        total_allowances = allowances.get('total_allowances', Decimal('0.00'))

        # Net avant avances
        net_before_advances = (
            (gross_salary + total_allowances)
            - (deductions['cnss_employee'] + deductions['ipr_tax']
               + earnings['total_other_deductions'])
        )

        # Traitement des avances
        advance_deductions, total_advance_deduction = (
            AdvanceService.process_advances_for_payslip(
                employee_id=contract.employee.id,
                gross_salary=gross_salary,
                net_salary_before_advances=net_before_advances,
                payroll_date=run.end_date,
            )
        )

        # Net à payer final
        net_amount = net_before_advances - total_advance_deduction

        # Coût total employeur
        cout_total_employeur = (
            gross_salary + employer_charges['total_employer_charges']
        )

        return {
            'net_before_advances': net_before_advances,
            'net_amount': net_amount,
            'cout_total_employeur': cout_total_employeur,
            'advance_deductions': advance_deductions,
            'total_advance_deduction': total_advance_deduction,
        }

    # ------------------------------------------------------------------
    # ÉTAPE 8 : Génération du bulletin de paie et archivage d'audit
    # ------------------------------------------------------------------

    @classmethod
    def _step8_generate_payslip_with_snapshot(
        cls, run, contract, config,
        gross_salary, earnings, bases, pay_elements,
        deductions, employer_charges, net_data, validated_data
    ):
        """
        Génère le bulletin et le snapshot d'audit.
        
        Conforme à metamodel.md Étape 8 et semantics.md §Snapshot d'audit.
        
        Le bulletin fige :
        - Tous les éléments de gain
        - Les 5 bases de calcul
        - Les retenues
        - Les charges patronales
        - Le snapshot des paramètres légaux
        """
        d = validated_data
        allowances = pay_elements['allowances']

        # --- Persistance du bulletin ---
        payslip = EmployeePayslip.objects.create(
            payroll_run=run,
            contract=contract,
            base_salary_snapshot=earnings['base_amount'],
            gross_amount=gross_salary,
            taxable_base=deductions['taxable_base'],
            cnss_amount=deductions['cnss_employee'],
            onem_amount=employer_charges['onem_amount'],
            inpp_amount=employer_charges['inpp_amount'],
            ipr_amount=deductions['ipr_tax'],
            housing_allowance=allowances['housing_allowance'],
            transport_allowance=allowances['transport_allowance'],
            total_adjustments=(
                allowances['total_allowances']
                + earnings['total_bonuses']
                - deductions['cnss_employee']
                - deductions['ipr_tax']
                - net_data['total_advance_deduction']
                - earnings['total_other_deductions']
                - earnings['absence_deduction']
            ),
            net_amount=net_data['net_amount'],
            worked_days=d['attendance']['regular_days'],
            worked_hours=d['attendance']['total_worked_hours'],
            paid_leave_days=Decimal(d['leave']['paid_leave_days']),
            unpaid_leave_days=Decimal(d['leave']['unpaid_leave_days']),
            contract_currency=d['contract_currency'],
            exchange_rate_used=d['conversion_rate'],
            currency=config.currency,
            payment_method=(
                contract.employee.preferred_payment_method
                or config.default_payment_method
            ),
        )

        # --- Correction 0.4 : Snapshot + Signature SHA-256 ---
        cls._build_snapshot(run, config, bases, allowances, d)
        payslip.signature_hash = cls._sign_payslip(payslip, bases, allowances)
        payslip.save(update_fields=['signature_hash'])

        # --- Correction 0.7 #9 : Persistance charges patronales ---
        cls._persist_employer_charges(payslip, employer_charges)

        # --- Enregistrement des lignes détaillées ---
        cls._record_payslip_lines_v2(
            payslip, earnings, deductions, employer_charges,
            net_data, allowances, d
        )

        # --- Enregistrement des remboursements d'avances ---
        if net_data['advance_deductions']:
            AdvanceService.record_batch_repayments(
                payslip, net_data['advance_deductions']
            )

        return payslip

    # ------------------------------------------------------------------
    # Snapshot d'audit + Signature SHA-256 (Etape 8 helpers)
    # ------------------------------------------------------------------

    @classmethod
    def _build_snapshot(cls, run, config, bases, allowances, validated_data):
        """
        Construit le snapshot JSON des parametres legaux du Run.
        Conforme a semantics.md L481-507.
        Capture UNE FOIS par run.
        """
        from hr.payroll.services.cache import PayrollCacheService

        # Ne pas ecraser un snapshot existant
        if run.params_snapshot and run.params_snapshot.get('date_generation'):
            return

        brackets = PayrollCacheService.get_tax_brackets()
        smig = PayrollCacheService.get_smig()

        snapshot = {
            "date_generation": timezone.now().isoformat(),
            "run_code": run.code,
            "periode": {
                "debut": str(run.start_date),
                "fin": str(run.end_date),
            },
            "parametres_legaux": {
                "SMIG": {
                    "valeur": str(smig.daily_rate) if smig else "N/A",
                    "devise": "CDF/jour",
                },
                "bareme_IRPP": [
                    {
                        "label": b.label,
                        "lower_limit": str(b.lower_limit),
                        "upper_limit": str(b.upper_limit) if b.upper_limit else None,
                        "rate": str(b.rate_percentage) + "%",
                    }
                    for b in brackets
                ] if brackets else [],
                "taux_CNSS_salarial": "5%",
                "taux_change": {
                    "devise": validated_data.get('contract_currency', 'CDF'),
                    "taux": str(validated_data.get('conversion_rate', 1)),
                },
                "deduction_absences": {
                    "mode": config.leave_deduction_mode,
                    "diviseur": str(config.leave_deduction_divisor),
                    "forfait_jour": (
                        str(config.fixed_deduction_per_absent_day)
                        if config.fixed_deduction_per_absent_day
                        else None
                    ),
                },
            },
            "formules_appliquees": {
                "cnss_salariale": "base_cnss x 0.05",
                "irpp": "bareme progressif -> plafonnement 30% -> abattement familial",
                "logement_exoneration": "min(indemnite, brut_imposable x 30%)",
            },
        }

        run.params_snapshot = snapshot
        run.save(update_fields=['params_snapshot'])

    @classmethod
    def _sign_payslip(cls, payslip, bases, allowances) -> str:
        """Calcule le hash SHA-256 du bulletin pour integrite."""
        canonical = json.dumps({
            "payslip_id": payslip.id,
            "run_code": payslip.payroll_run.code,
            "contract_id": payslip.contract_id,
            "gross": str(payslip.gross_amount),
            "taxable": str(payslip.taxable_base),
            "net": str(payslip.net_amount),
            "cnss": str(payslip.cnss_amount),
            "ipr": str(payslip.ipr_amount),
            "housing": str(payslip.housing_allowance),
            "transport": str(payslip.transport_allowance),
            "unpaid_leave_days": str(payslip.unpaid_leave_days),
            "bases": {
                bt.value: str(basis.montant)
                for bt, basis in bases.items()
            },
        }, sort_keys=True, ensure_ascii=False)

        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    # ------------------------------------------------------------------
    # Persistance charges patronales (Correction 0.7 #9 + #13)
    # ------------------------------------------------------------------

    @classmethod
    def _persist_employer_charges(cls, payslip, employer_charges):
        """Persiste les charges patronales dans EmployerCharge."""
        from hr.payroll.models import EmployerCharge

        for detail in employer_charges.get('charge_details', []):
            EmployerCharge.objects.create(
                payslip=payslip,
                contribution_type=detail['type'],
                label=detail['label'],
                amount=detail['employer_amount'],
                base_amount=detail.get('applied_base', Decimal('0.00')),
            )

    # ------------------------------------------------------------------
    # Enregistrement des lignes détaillées
    # ------------------------------------------------------------------

    @classmethod
    def _record_payslip_lines_v2(
        cls, payslip, earnings, deductions, employer_charges,
        net_data, allowances, validated_data
    ):
        """Enregistre les lignes détaillées du bulletin."""
        d = validated_data

        # Salaire de base
        PayslipLine.objects.create(
            payslip=payslip,
            label="Salaire de Base",
            amount=earnings['base_amount'],
            adjustment_type='BONUS',
        )

        # Heures supplémentaires
        if earnings['overtime_pay'] > 0:
            PayslipLine.objects.create(
                payslip=payslip,
                label="Heures Supplémentaires",
                amount=earnings['overtime_pay'],
                adjustment_type='BONUS',
            )

        # Ajustements (primes, déductions)
        for adj in earnings['adjustment_lines']:
            PayslipLine.objects.create(
                payslip=payslip,
                label=adj['label'],
                amount=adj['amount'],
                adjustment_type=adj['type'],
            )

        # Allocations légales
        for detail in allowances['allowance_details']:
            PayslipLine.objects.create(
                payslip=payslip,
                label=detail['label'],
                amount=detail['amount'],
                adjustment_type='BONUS',
            )

        # Congés payés
        if d['leave']['paid_leave_days'] > 0:
            PayslipLine.objects.create(
                payslip=payslip,
                label=(
                    f"Maintien de salaire - Congés Payés "
                    f"({d['leave']['paid_leave_days']} jrs)"
                ),
                amount=Decimal('0.00'),
                adjustment_type='BONUS',
            )

        # Taux de change
        if d['contract_currency'] != Currency.CDF:
            PayslipLine.objects.create(
                payslip=payslip,
                label=(
                    f"Taux de change appliqué "
                    f"(1 {d['contract_currency']} = {d['conversion_rate']} CDF)"
                ),
                amount=Decimal('0.00'),
                adjustment_type='BONUS',
            )

        # Déduction des absences non payées (si applicable)
        if earnings['absence_deduction'] > 0:
            PayslipLine.objects.create(
                payslip=payslip,
                label=(
                    f"Déduction Absences "
                    f"({d['leave']['unpaid_leave_days']} jrs)"
                ),
                amount=earnings['absence_deduction'],
                adjustment_type='CONTRIBUTION',
            )

        # Retenues salariales
        PayslipLine.objects.create(
            payslip=payslip,
            label="CNSS (5%)",
            amount=deductions['cnss_employee'],
            adjustment_type='CONTRIBUTION',
        )
        PayslipLine.objects.create(
            payslip=payslip,
            label="IPR",
            amount=deductions['ipr_tax'],
            adjustment_type='CONTRIBUTION',
        )

        # Excédent logement imposable (si applicable)
        if allowances.get('taxable_housing_excess', Decimal('0')) > 0:
            PayslipLine.objects.create(
                payslip=payslip,
                label=(
                    f"Dont excédent logement imposable: "
                    f"{allowances['taxable_housing_excess']} CDF"
                ),
                amount=Decimal('0.00'),
                adjustment_type='BONUS',
            )

        # Remboursements d'avances
        for advance, amount in net_data['advance_deductions']:
            PayslipLine.objects.create(
                payslip=payslip,
                label=f"Retenue Avance sur Salaire #{advance.id}",
                amount=amount,
                adjustment_type='CONTRIBUTION',
            )

