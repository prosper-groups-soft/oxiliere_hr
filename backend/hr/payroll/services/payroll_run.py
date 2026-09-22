import logging
from decimal import Decimal
from typing  import Dict, Any
from uuid    import UUID

from django.utils import timezone
from django.db    import transaction
from django.core.exceptions import ValidationError
from django.db.models import QuerySet, Sum, Count, Q, Value, OuterRef, Subquery, F
from django.db.models.functions import Coalesce

from hr.payroll.models import (
    PayrollRun, 
    EmployeePayslip, 
    PayslipLine, 
    EmployeeContract,
    EmployerCharge,
    PayrollConfiguration,
)
from django.core.cache         import cache
from hr.services.cache_helpers import CacheKeys
from .orchestrator             import PayrollOrchestrator
from hr.payroll.enums          import PayrollStatus, PayslipStatus
from hr.payroll.services.contract_eligibility import contract_active_on_period
from hr.jobs.models import EmployeePositionHistory
from django.db.models.functions import Concat
from hr.payroll.services.cache  import PayrollCacheService
from hr.payroll.services.integration.integration import PayrollIntegrationService


logger = logging.getLogger(__name__)


class PayrollRunService:
    """
    Manages payroll run lifecycle and operations.
    
    Responsibilities:
    - Create new payroll runs with date ranges
    - Manage run status transitions (DRAFT → PROCESSING → COMPLETED → CANCELLED)
    - Generate payslips for all active employees in a run
    - Query run details and financial summaries
    - Coordinate with PayrollOrchestrator for actual processing
    - Provide detailed run statistics (employee count, totals, etc.)
    """

    # ===== CRUD OPERATIONS =====

    @classmethod
    def get_run_by_id(cls, run_id: UUID) -> PayrollRun:
        """ Retrieves a payroll run with its associated payslips. """
        logger.debug("[PayrollRun] Getting run by ID", extra={"run_id": run_id})

        return PayrollRun.objects.prefetch_related('payslips').get(id=run_id)
    
    @classmethod
    def get_run_detail(cls, run_id: UUID) -> Dict[str, Any]:
        """ Gets a detailed financial and operational summary of a payroll run. """
        logger.debug("[PayrollRun] Getting run detail", extra={"run_id": run_id})

        # Use select_related/prefetch if needed for performance
        run = cls.get_run_by_id(run_id)
        payslips = run.payslips.all()
        
        total_payslips = payslips.count()
        # Better: use a status field on the payslip model if available
        processed_payslips = payslips.filter(status="COMPLETED").count() 
        pending_payslips = total_payslips - processed_payslips

        aggregates = payslips.aggregate(
            total_gross=Sum('gross_amount'),
            total_net=Sum('net_amount'),
            # Include tax and social contributions specifically for DRC reporting
            total_ipr=Sum('ipr_amount'), # Income tax
            total_employee_cnss=Sum('cnss_amount'),
            total_onem=Sum('onem_amount'),
            total_inpp=Sum('inpp_amount'),
        )

        total_gross = aggregates.get("total_gross") or Decimal("0.00")
        total_net = aggregates.get("total_net") or Decimal("0.00")
        total_employer_liability = (
            (aggregates.get("total_employee_cnss") or Decimal("0.00"))
            + (aggregates.get("total_onem") or Decimal("0.00"))
            + (aggregates.get("total_inpp") or Decimal("0.00"))
        )

        return {
            "id": run.id,
            "code": run.code,
            "status": run.status,
            "period": f"{run.start_date} - {run.end_date}",
            "start_date": run.start_date,
            "end_date": run.end_date,
            "exchange_rate": run.exchange_rate_applied,
            "params_snapshot": run.params_snapshot or {},
            "created_at": run.created_at,
            "updated_at": run.updated_at,
            "stats": {
                "total_count": total_payslips,
                "processed_count": processed_payslips,
                "pending_count": pending_payslips,
            },
            "financials": {
                "gross_total": total_gross,
                "net_total": total_net,
                "total_tax_deductions": total_gross - total_net,
                "employer_liability": total_employer_liability,
            }
        }

    @classmethod
    @transaction.atomic
    def create_payroll_run(cls, data: Dict[str, Any], actor=None) -> PayrollRun:
        """ Creates a new payroll run for a specific date range. """
        logger.debug("[PayrollRun] Creating payroll run", extra={"data": data, "actor": actor})

        # Validate dates
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not start_date or not end_date:
            raise ValidationError("start_date and end_date are required")

        if start_date >= end_date:
            logger.warning("[PayrollRun] Invalid date range", extra={"start": start_date, "end": end_date})
            raise ValidationError("start_date must be before end_date")

        # Contrainte : un seul run actif à la fois (quel que soit le chevauchement de période).
        # Un run est "actif" tant qu'il n'est ni payé ni annulé — la paie en cours
        # doit rester unique pendant tout son cycle (DRAFT → … → APPROVED).
        active_statuses = [
            PayrollStatus.DRAFT,
            PayrollStatus.PROCESSING,
            PayrollStatus.VALIDATED,
            PayrollStatus.REVIEWED,
            PayrollStatus.APPROVED,
        ]
        existing_active = PayrollRun.objects.filter(status__in=active_statuses)
        if existing_active.exists():
            logger.warning(
                "[PayrollRun] Another active run exists",
                extra={"existing_ids": list(existing_active.values_list('id', flat=True))},
            )
            raise ValidationError("Une paie est déjà en cours. Terminez ou annulez-la avant d'en démarrer une nouvelle.")

        # Check for existing runs with overlapping periods (dépasse rarement car un seul run actif max)
        existing = PayrollRun.objects.filter(
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date),
            status__in=[PayrollStatus.DRAFT, PayrollStatus.PROCESSING]
        )
        if existing.exists():
            logger.warning("[PayrollRun] Overlapping run exists", extra={"start": start_date, "end": end_date})
            raise ValidationError("A payroll run already exists for this period")

        # Taux de change figé pour le run (None si devise CDF — aucune conversion)
        exchange_rate = data.get('exchange_rate_applied')

        # Sélection des employés couverts par le run (persistée pour audit)
        scope = data.get('selection_scope', 'all')
        org_unit_ids = data.get('org_unit_ids') or []
        employee_ids = data.get('employee_ids') or []

        # Create run
        run = PayrollRun.objects.create(
            start_date=start_date,
            end_date=end_date,
            exchange_rate_applied=Decimal(str(exchange_rate)) if exchange_rate else None,
            status=PayrollStatus.DRAFT,
            created_by=actor,
            params_snapshot={
                "selection": {
                    "scope": scope,
                    "org_unit_ids": [str(uid) for uid in org_unit_ids],
                    "employee_ids": [str(uid) for uid in employee_ids],
                },
            },
        )

        logger.info(
            "[PayrollRun] Payroll run created",
            extra={"run_id": run.id, "period": f"{start_date} to {end_date}"}
        )
        return run

    @classmethod
    @transaction.atomic
    def update_payroll_run(cls, run_id: UUID, data: Dict[str, Any], actor=None) -> PayrollRun:
        """ Updates a draft payroll run's configuration.

        Seuls les champs présents dans `data` (exclude_unset côté controller)
        sont touchés. Pour `params_snapshot`, on merge la sous-clé `selection`
        avec l'existant : les autres clés (audit légal SMIG/IRPP/CNSS figées
        au moment du calcul) sont préservées.
        """
        logger.info(
            "[PayrollRun] PATCH incoming",
            extra={"run_id": run_id, "data_keys": list(data.keys()), "has_params_snapshot": 'params_snapshot' in data}
        )

        run = PayrollRun.objects.get(id=run_id)

        if run.status != PayrollStatus.DRAFT:
            logger.warning(
                "[PayrollRun] Cannot update non-draft run",
                extra={"run_id": run_id, "status": run.status}
            )
            raise ValidationError(f"Cannot update run with status {run.status}")

        # Update scalar fields
        new_start = data.get('start_date', run.start_date)
        new_end = data.get('end_date', run.end_date)
        if 'start_date' in data or 'end_date' in data:
            if new_start and new_end and str(new_start) >= str(new_end):
                raise ValidationError("start_date must be before end_date")
            if 'start_date' in data:
                run.start_date = data['start_date']
            if 'end_date' in data:
                run.end_date = data['end_date']

        if 'exchange_rate_applied' in data:
            run.exchange_rate_applied = data['exchange_rate_applied']

        # Merge params_snapshot.selection (PATCH partiel : seul le bloc
        # `selection` est éditable ; les snapshots légaux restent intacts).
        if 'params_snapshot' in data and data['params_snapshot'] is not None:
            incoming = data['params_snapshot']
            logger.info(
                "[PayrollRun] PATCH params_snapshot incoming",
                extra={"run_id": run_id, "incoming": incoming}
            )
            if isinstance(incoming, dict) and 'selection' in incoming:
                existing_snapshot = dict(run.params_snapshot or {})
                existing_snapshot['selection'] = incoming['selection']
                run.params_snapshot = existing_snapshot

        run.updated_by = actor
        run.save()

        # Invalider TOUT le cache lié à ce run, y compris les caches
        # `cache_api_response` de NinjaAPI (qui mettent en cache la réponse
        # HTTP complète de l'endpoint GET /summary/, GET /payslips/, etc.).
        # Le pattern des clés NinjaAPI ressemble à :
        #   :1:cache_api_response:GET:api.payroll.runs.<id>.summary:...
        #   :1:cache_api_response:GET:api.payroll.runs.<id>.:...
        #   :1:cache_api_response:GET:api.payroll.runs.<id>.:...
        # On ne peut pas prédire toutes les formes : on SCAN tout le namespace
        # cache_api_response et on filtre côté Python (cheap, le dataset est petit).
        try:
            # 1) Clé directe du run (cache de l'objet PayrollRun)
            cache.delete(CacheKeys.payroll_run(run_id))

            # 2) Caches contrats/employés des employés de la sélection
            selected_ids = []
            if run.params_snapshot and isinstance(run.params_snapshot, dict):
                sel = run.params_snapshot.get('selection') or {}
                selected_ids = sel.get('employee_ids') or []
            for emp_id in selected_ids:
                PayrollCacheService.clear_employee_cache(emp_id)

            # 3) Purge SCAN-based de TOUTES les clés cache_api_response qui
            #    mentionnent ce run_id (UUID sous forme str ou avec tirets).
            #    On scan :1:cache_api_response:* (préfixe Django par défaut)
            #    puis on filtre en mémoire.
            run_id_str = str(run_id)
            run_id_compact = run_id_str.replace('-', '')
            purged = 0

            # Scan les clés de cache API et purge toute clé contenant l'UUID
            cursor = 0
            while True:
                cursor, batch = PayrollCacheService.redis_conn.scan(
                    cursor=cursor, match="*:cache_api_response:*", count=500
                )
                keys_to_delete = [
                    k for k in batch
                    if (run_id_str in k or run_id_compact in k)
                ]
                if keys_to_delete:
                    PayrollCacheService.redis_conn.delete(*keys_to_delete)
                    purged += len(keys_to_delete)
                if cursor == 0:
                    break
            
            # 4) Purge par pattern "au cas où" dans le namespace payroll
            for pattern in (
                f"*payroll*run*{run_id_str}*",
                f"*{run_id_str}*",
                f"*{run_id_compact}*",
            ):
                cursor = 0
                while True:
                    cursor, batch = PayrollCacheService.redis_conn.scan(
                        cursor=cursor, match=pattern, count=500
                    )
                    # Ne pas supprimer les clés directes du run qu'on a déjà
                    # purgées (pas grave de re-tenter, c'est idempotent).
                    if batch:
                        PayrollCacheService.redis_conn.delete(*batch)
                        purged += len(batch)
                    if cursor == 0:
                        break

            logger.info(
                "[PayrollRun] Cache purged for run",
                extra={"run_id": run_id, "employees_purged": len(selected_ids),
                       "api_response_keys_purged": purged}
            )
        except Exception as e:
            # On ne fait PAS échouer le PATCH si la purge échoue :
            # au pire l'utilisateur verra l'ancienne valeur jusqu'à expiration TTL.
            logger.warning(
                "[PayrollRun] Cache purge failed (non-fatal)",
                extra={"run_id": run_id, "error": str(e)}
            )

        logger.info(
            "[PayrollRun] Run updated",
            extra={"run_id": run_id, "new_selection": run.params_snapshot.get('selection') if run.params_snapshot else None}
        )
        return run

    # Champs de tri serveur exposés par le frontend (liste des exécutions).
    ORDERING_FIELDS = {
        'period': 'start_date',
        'status': 'status',
        'employeeCount': '_employee_count',
        'grossTotal': '_gross_total',
        'createdAt': 'created_at',
    }

    @classmethod
    def _resolve_ordering(cls, ordering: str | None):
        """Traduit un token de tri ('period', '-grossTotal', …) en tri Django."""
        if not ordering:
            return ['-created_at']
        desc = ordering.startswith('-')
        key = ordering[1:] if desc else ordering
        field = cls.ORDERING_FIELDS.get(key)
        if not field:
            return ['-created_at']
        return [('-' if desc else '') + field]

    @classmethod
    def list_runs_annotated(cls, filters=None, ordering: str | None = None):
        """
        Returns payroll runs with list-oriented annotations (payslip count,
        gross total, employee count) so the list endpoint can serialize
        directly into PayrollRunOut without N+1 queries.

        Le brut total est calculé par sous-requête corrélée (et non par une
        jointure agrégée) pour rester exact quand un filtre ajoute des jointures
        (ex. org_unit via position_history) qui multiplieraient la somme.
        """
        logger.debug("[PayrollRun] Listing runs with annotations")

        gross_subquery = (
            EmployeePayslip.objects
            .filter(payroll_run=OuterRef('pk'))
            .order_by()
            .values('payroll_run')
            .annotate(total=Sum('gross_amount'))
            .values('total')[:1]
        )
        qs = PayrollRun.objects.annotate(
            _payslip_count=Count('payslips', distinct=True),
            _gross_total=Coalesce(Subquery(gross_subquery), Decimal('0.00')),
            _employee_count=Count('payslips__contract', distinct=True),
        )

        if filters is not None:
            qs = filters.filter(qs)

        # org_unit filtre via payslips → jointure qui duplique le run ; distinct obligatoire.
        qs = qs.distinct()
        return qs.order_by(*cls._resolve_ordering(ordering))

    @classmethod
    def list_run_periods(cls) -> list[dict]:
        """Périodes d'exécution distinctes (label + bornes), triées desc.

        Utilisé par le filtre « Période » du frontend, désormais alimenté par le
        serveur (la liste est paginée côté serveur : on ne peut plus la déduire
        d'une page locale).
        """
        rows = (
            PayrollRun.objects
            .order_by('-start_date')
            .values_list('start_date', 'end_date')
            .distinct()
        )
        return [
            {'label': f"{start} - {end}", 'start_date': start, 'end_date': end}
            for start, end in rows
        ]

    @classmethod
    def serialize_run(cls, run) -> Dict[str, Any]:
        """
        Converts a PayrollRun (optionally annotated) into the dict shape
        expected by PayrollRunOut, computing period_label and closed_at.
        """
        status = run.status
        closed_at = None
        if status in (PayrollStatus.PAID, PayrollStatus.CANCELED):
            closed_at = run.updated_at

        period_label = None
        if run.start_date and run.end_date:
            period_label = f"{run.start_date} - {run.end_date}"

        return {
            "id": run.id,
            "code": run.code,
            "start_date": run.start_date,
            "end_date": run.end_date,
            "status": status,
            "exchange_rate_applied": run.exchange_rate_applied,
            "created_at": run.created_at,
            "updated_at": run.updated_at,
            "total_payslips": getattr(run, '_payslip_count', 0) or 0,
            "gross_total": getattr(run, '_gross_total', Decimal('0.00')) or Decimal('0.00'),
            "employee_count": getattr(run, '_employee_count', 0) or 0,
            "closed_at": closed_at,
            "period_label": period_label,
            "params_snapshot": run.params_snapshot or {},
        }

    # ===== STATUS TRANSITIONS =====

    @classmethod
    def get_presence_preview(cls, run_id: UUID) -> Dict[str, Any]:
        """Présence agrégée des employés éligibles d'un run (vue préparation).

        Renvoie, pour chaque contrat retenu par la sélection du run et actif sur
        la période, exactement ce que l'orchestrateur utilisera au calcul :
        jours travaillés, heures, absences et congés — en ne comptant que les
        registres de présence FINALISÉS (voir AttendanceSummaryService).
        """
        logger.debug("[PayrollRun] Building presence preview", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)

        contracts = EmployeeContract.objects.filter(
            contract_active_on_period(run.start_date, run.end_date)
        )
        selection = (run.params_snapshot or {}).get('selection', {})
        scope = selection.get('scope', 'all')
        if scope == 'org_units':
            org_unit_ids = selection.get('org_unit_ids') or []
            if org_unit_ids:
                contracts = contracts.filter(
                    employee__position_history__org_unit_id__in=org_unit_ids,
                    employee__position_history__is_current=True,
                ).distinct()
        elif scope == 'employees':
            employee_ids = selection.get('employee_ids') or []
            if employee_ids:
                contracts = contracts.filter(employee_id__in=employee_ids)

        config = PayrollConfiguration.objects.first()
        include_leaves = bool(config and config.include_leaves_in_payroll)

        employees = []
        for contract in contracts.select_related('employee'):
            att = PayrollIntegrationService.get_worked_days_data(
                contract.employee_id, run.start_date, run.end_date
            )
            paid_leave = unpaid_leave = Decimal('0.00')
            if include_leaves:
                lv = PayrollIntegrationService.get_employee_leave_data(
                    contract.employee_id, run.start_date, run.end_date
                )
                paid_leave = lv.get('paid_leave_days') or Decimal('0.00')
                unpaid_leave = lv.get('unpaid_leave_days') or Decimal('0.00')

            unfinalized = int(att.get('unfinalized_days') or 0)
            worked = int(att['regular_days'] or 0)
            absence = int(att['absence_days'] or 0)
            employees.append({
                'employee_id': contract.employee_id,
                'worked_days': worked,
                'total_worked_hours': float(att['total_worked_hours'] or 0),
                'overtime_hours_standard': float(att['overtime_hours_standard'] or 0),
                'overtime_hours_holiday': float(att['overtime_hours_holiday'] or 0),
                'absence_days': absence,
                'paid_leave_days': float(paid_leave),
                'unpaid_leave_days': float(unpaid_leave),
                'unfinalized_days': unfinalized,
                'has_attendance': bool(worked or absence or unfinalized),
            })

        return {
            'run_id': run.id,
            'period_start': run.start_date,
            'period_end': run.end_date,
            'employees': employees,
        }

    @classmethod
    @transaction.atomic
    def start_payroll_processing(cls, run_id: UUID, actor=None, orchestrator: PayrollOrchestrator | None = None) -> Dict[str, Any]:
        """ Initiates the calculation process for all eligible employee contracts. """
        logger.debug("[PayrollRun] Starting payroll processing", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)

        if run.status != PayrollStatus.DRAFT:
            logger.warning(
                "[PayrollRun] Cannot process non-draft run",
                extra={"run_id": run_id, "status": run.status}
            )
            raise ValidationError(f"Cannot process run with status {run.status}")

        # Nombre de contrats dont la validité chevauche la période du run.
        active_contracts = EmployeeContract.objects.filter(
            contract_active_on_period(run.start_date, run.end_date)
        ).count()

        if active_contracts == 0:
            logger.warning("[PayrollRun] No active contracts found", extra={"run_id": run_id})
            raise ValidationError("No active contracts found for processing")

        # Update run status to PROCESSING
        run.status = PayrollStatus.PROCESSING
        run.updated_by = actor
        run.save()

        logger.info(
            "[PayrollRun] Processing started",
            extra={"run_id": run_id, "employees": active_contracts}
        )

        # Call PayrollOrchestrator to generate payslips
        # PayrollOrchestrator will update status to VALIDATED after completing
        if orchestrator:
            try:
                orchestrator.process_run(run)
                payslips_count = run.payslips.count()
                logger.info(
                    "[PayrollRun] Processing completed",
                    extra={"run_id": run_id, "payslips": payslips_count}
                )
                return {
                    "status": run.status,  # Should be VALIDATED by orchestrator
                    "total_employees": active_contracts,
                    "payslips_generated": payslips_count,
                    "message": f"Successfully processed {payslips_count} payslips",
                }
            except Exception as e:
                logger.exception(
                    "[PayrollRun] Processing failed",
                    extra={"run_id": run_id, "error": str(e)}
                )
                run.status = PayrollStatus.DRAFT
                run.save()
                raise
        else:
            # If orchestrator not provided, just return status
            return {
                "status": PayrollStatus.PROCESSING,
                "task_id": f"payroll_run_{run_id}",
                "total_employees": active_contracts,
                "message": f"Processing started for {active_contracts} employees",
            }

    @classmethod
    @transaction.atomic
    def complete_payroll_run(cls, run_id: UUID, actor=None) -> PayrollRun:
        """ Marks a payroll run as PAID, finalizing and locking all associated data. """
        logger.debug("[PayrollRun] Completing payroll run", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)

        if run.status not in (PayrollStatus.VALIDATED, PayrollStatus.REVIEWED, PayrollStatus.APPROVED):
            logger.warning(
                "[PayrollRun] Cannot complete run",
                extra={"run_id": run_id, "status": run.status}
            )
            raise ValidationError(
                f"Cannot complete run with status {run.status}. Must be VALIDATED, REVIEWED or APPROVED."
            )

        # Verify payslips exist
        payslip_count = run.payslips.count()
        if payslip_count == 0:
            logger.warning("[PayrollRun] No payslips generated", extra={"run_id": run_id})
            raise ValidationError("Cannot complete run without payslips")

        run.status = PayrollStatus.PAID
        run.updated_by = actor
        run.save()
        EmployeePayslip.objects.filter(payroll_run_id=run.id).update(status=PayslipStatus.PAID, paid_at=timezone.now())

        logger.info("[PayrollRun] Run completed and marked PAID", extra={"run_id": run_id, "payslips": payslip_count})
        return run

    @classmethod
    @transaction.atomic
    def review_payroll_run(cls, run_id: UUID, actor=None) -> PayrollRun:
        """
        Moves a processed run into the review stage.
        Status transition: VALIDATED → REVIEWED.
        """
        logger.debug("[PayrollRun] Reviewing payroll run", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)

        if run.status != PayrollStatus.VALIDATED:
            logger.warning(
                "[PayrollRun] Cannot review run",
                extra={"run_id": run_id, "status": run.status}
            )
            raise ValidationError(f"Cannot review run with status {run.status}. Must be VALIDATED.")

        run.status = PayrollStatus.REVIEWED
        run.updated_by = actor
        run.save()
        EmployeePayslip.objects.filter(payroll_run_id=run.id).update(status=PayslipStatus.CONFIRMED)

        logger.info("[PayrollRun] Run reviewed", extra={"run_id": run_id})
        return run

    @classmethod
    @transaction.atomic
    def approve_payroll_run(cls, run_id: UUID, actor=None) -> PayrollRun:
        """
        Approves a reviewed run, ready for payment.
        Status transition: REVIEWED → APPROVED.
        """
        logger.debug("[PayrollRun] Approving payroll run", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)

        if run.status != PayrollStatus.REVIEWED:
            logger.warning(
                "[PayrollRun] Cannot approve run",
                extra={"run_id": run_id, "status": run.status}
            )
            raise ValidationError(f"Cannot approve run with status {run.status}. Must be REVIEWED.")

        run.status = PayrollStatus.APPROVED
        run.updated_by = actor
        run.save()
        EmployeePayslip.objects.filter(payroll_run_id=run.id).update(status=PayslipStatus.CONFIRMED)

        logger.info("[PayrollRun] Run approved", extra={"run_id": run_id})
        return run

    @classmethod
    @transaction.atomic
    def cancel_payroll_run(cls, run_id: UUID, actor=None) -> PayrollRun:
        """ Cancels a payroll run that has not yet been finalized. """
        logger.debug("[PayrollRun] Cancelling payroll run", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)

        if run.status == PayrollStatus.PAID:
            logger.warning(
                "[PayrollRun] Cannot cancel paid run",
                extra={"run_id": run_id}
            )
            raise ValidationError("Cannot cancel a payroll run that has been paid")

        run.status = PayrollStatus.CANCELED
        run.updated_by = actor
        run.save()
        EmployeePayslip.objects.filter(payroll_run_id=run.id).update(status=PayslipStatus.CANCELED)

        logger.info("[PayrollRun] Run cancelled", extra={"run_id": run_id})
        return run

    # ===== PAYSLIP QUERIES =====

    @classmethod
    def get_payslips_for_run(cls, run_id: UUID) -> QuerySet:
        """ Retrieves all payslips generated for a specific run. """
        logger.debug("[PayrollRun] Getting payslips for run", extra={"run_id": run_id})

        # Verify run exists
        PayrollRun.objects.get(id=run_id)

        return EmployeePayslip.objects.filter(
            payroll_run_id=run_id
        ).select_related(
            'contract',
            'contract__employee',
            'contract__employee__user',
            'payroll_run',
        ).prefetch_related(
            'lines'
        ).annotate(
            # Employé + unité + POSTE courant (source liste).
            employee_name=Concat(
                'contract__employee__last_name',
                Value(' '),
                'contract__employee__middle_name',
                Value(' '),
                'contract__employee__first_name',
            ),
            job_title=Subquery(
                EmployeePositionHistory.objects.filter(
                    employee_id=OuterRef('contract__employee_id'),
                    is_current=True,
                ).values('position__name')[:1]
            ),
            org_unit=Subquery(
                EmployeePositionHistory.objects.filter(
                    employee_id=OuterRef('contract__employee_id'),
                    is_current=True,
                ).values('org_unit__name')[:1]
            ),
            # Chemin de la photo de profil (relation déjà préchargée) — le front
            # applique getMediaUrl() dessus pour afficher l'avatar de l'employé.
            photo_path=F('contract__employee__profile_photo'),
        ).order_by('contract__employee__user__first_name')
        
    PAYSLIP_ORDERING_FIELDS = {
        'employeeName': 'contract__employee__last_name',
        'gross': 'gross_amount',
        'net': 'net_amount',
        'period': 'payroll_run__start_date',
        'createdAt': 'created_at',
    }

    @classmethod
    def _resolve_payslip_ordering(cls, ordering: str | None):
        if not ordering:
            return ['-created_at']
        desc = ordering.startswith('-')
        key = ordering[1:] if desc else ordering
        field = cls.PAYSLIP_ORDERING_FIELDS.get(key)
        if not field:
            return ['-created_at']
        return [('-' if desc else '') + field]

    @classmethod
    def list_payslips_annotated(cls, filters=None, ordering: str | None = None):
        qs = EmployeePayslip.objects.select_related('contract','contract__employee','payroll_run').prefetch_related('lines').annotate(
            employee_name=Concat('contract__employee__last_name', Value(' '), 'contract__employee__middle_name', Value(' '), 'contract__employee__first_name'),
            job_title=Subquery(EmployeePositionHistory.objects.filter(employee_id=OuterRef('contract__employee_id'), is_current=True).values('position__name')[:1]),
            org_unit=Subquery(EmployeePositionHistory.objects.filter(employee_id=OuterRef('contract__employee_id'), is_current=True).values('org_unit__name')[:1]),
            photo_path=F('contract__employee__profile_photo'),
        )
        if filters is not None:
            qs = filters.filter(qs)
        qs = qs.distinct()
        return qs.order_by(*cls._resolve_payslip_ordering(ordering))
        
    @classmethod
    def get_payroll_summary(cls, run_id: UUID) -> Dict[str, Any]:
        """
        Get financial summary of a payroll run, including DRC-specific breakdowns.
        
        Returns aggregated totals:
        - Total employees processed
        - Total gross salary
        - Total net salary (employee take-home)
        - Total employee deductions (Taxes + EE CNSS)
        - Total employer liabilities (ER CNSS + INPP + ONEM)
        - Total cost to company (CTC)
        """
        logger.debug("[PayrollRun] Getting payroll summary", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)
        payslips = run.payslips.all()

        # 1. Aggregate DRC-specific totals
        totals = payslips.aggregate(
            employee_count=Count('id'),
            total_gross=Sum('gross_amount'),
            total_net=Sum('net_amount'),
            total_adjustments=Sum('total_adjustments'),
            total_ipr=Sum('ipr_amount'),
            total_employee_cnss=Sum('cnss_amount'),
            total_inpp=Sum('inpp_amount'),
            total_onem=Sum('onem_amount'),
        )

        total_gross = totals.get('total_gross') or Decimal("0.00")
        total_net = totals.get('total_net') or Decimal("0.00")
        total_ipr = totals.get('total_ipr') or Decimal("0.00")
        total_ee_cnss = totals.get('total_employee_cnss') or Decimal("0.00")
        total_inpp = totals.get('total_inpp') or Decimal("0.00")
        total_onem = totals.get('total_onem') or Decimal("0.00")

        # 2. Charges patronales RÉELLES — agrégées depuis EmployerCharge (persistées à
        #    l'étape 6 avec les taux configurés : CNSS 5%+13%=18%, INPP, ONEM).
        #    Aucun ratio codé en dur (ex. l'ancien CNSS employeur ×8/5).
        er_agg = EmployerCharge.objects.filter(
            payslip__payroll_run_id=run_id
        ).values('contribution_type').annotate(total=Sum('amount'))
        er_by_type = {
            row['contribution_type']: (row['total'] or Decimal('0.00'))
            for row in er_agg
        }
        total_er_cnss = er_by_type.get('CNSS', Decimal('0.00'))
        # INPP/ONEM : valeur persistée si dispo, sinon repli sur les colonnes du payslip.
        total_inpp = er_by_type.get('INPP', total_inpp)
        total_onem = er_by_type.get('ONEM', total_onem)
        total_employer_liabilities = total_er_cnss + total_inpp + total_onem

        # 3. Total Cost to Company (CTC)
        total_cost_to_company = total_gross + total_employer_liabilities

        # 4. Adjustment lines breakdown
        lines = PayslipLine.objects.filter(
            payslip__payroll_run_id=run_id
        ).values('adjustment_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        )

        deductions_breakdown = {
            line['adjustment_type']: {
                'total': line['total'] or Decimal("0.00"),
                'count': line['count'],
            } for line in lines
        }

        return {
            "payroll_run": {
                "id": run.id,
                "code": run.code,
                "period": f"{run.start_date} to {run.end_date}",
                "status": run.status,
            },
            "summary": {
                "total_employees": totals.get('employee_count', 0),
                "total_gross_salary": total_gross,
                "total_net_salary": total_net,
                # Explicit DRC Breakdown
                "total_ipr_to_pay": total_ipr,          # For DGI
                "total_cnss_employee": total_ee_cnss,   # For CNSS
                "total_cnss_employer": total_er_cnss,   # For CNSS
                "total_inpp": total_inpp,               # For INPP
                "total_onem": total_onem,               # For ONEM
                # Global Metrics
                "total_employer_liabilities": total_employer_liabilities,
                "total_cost_to_company": total_cost_to_company,
            },
            "adjustments": deductions_breakdown,
        }

    @classmethod
    def get_payslip_detail(cls, payslip_id: UUID) -> Dict[str, Any]:
        """ Retrieves the full transactional detail of a single payslip. """
        logger.debug("[PayrollRun] Getting payslip detail", extra={"payslip_id": payslip_id})

        payslip = EmployeePayslip.objects.select_related(
            'contract',
            'contract__employee',
            'contract__employee__user',
            'payroll_run'
        ).prefetch_related('lines').get(id=payslip_id)

        # Compute additional fields for the detail schema
        employee = payslip.contract.employee
        
        return {
            "id": payslip.id,
            "payroll_run": payslip.payroll_run_id,
            "contract": payslip.contract_id,
            "base_salary_snapshot": payslip.base_salary_snapshot,
            "gross_amount": payslip.gross_amount,
            "cnss_amount": payslip.cnss_amount,
            "onem_amount": payslip.onem_amount,
            "inpp_amount": payslip.inpp_amount,
            "ipr_amount": payslip.ipr_amount,
            "housing_allowance": payslip.housing_allowance,
            "transport_allowance": payslip.transport_allowance,
            "total_adjustments": payslip.total_adjustments,
            "net_amount": payslip.net_amount,
            "taxable_base": payslip.taxable_base,
            "worked_days": payslip.worked_days,
            "worked_hours": payslip.worked_hours,
            "overtime_hours": payslip.overtime_hours,
            "paid_leave_days": payslip.paid_leave_days,
            "unpaid_leave_days": payslip.unpaid_leave_days,
            "contract_currency": payslip.contract_currency,
            "exchange_rate_used": payslip.exchange_rate_used,
            "currency": payslip.currency,
            "payment_method": payslip.payment_method,
            "paid_at": payslip.paid_at,
            "lines": list(payslip.lines.all()),
            # Nom via l'employé (user peut être None → ne pas planter).
            "employee_name": " ".join(p for p in (
                (getattr(employee, 'last_name', '') or ''),
                (getattr(employee, 'middle_name', '') or ''),
                (getattr(employee, 'first_name', '') or ''),
            ) if p) or getattr(employee, 'matricule', '') or '',
            "employee_id": employee.id,
            "net_after_advances": payslip.net_amount,
        }

    @classmethod
    def count_payslips_by_status(cls, run_id: UUID) -> Dict[str, int]:
        """
        Count payslips in a run by their generation status.
        """
        logger.debug("[PayrollRun] Counting payslips by status", extra={"run_id": run_id})

        # Verify run exists
        PayrollRun.objects.get(id=run_id)

        payslips = EmployeePayslip.objects.filter(payroll_run_id=run_id)

        return {
            "total": payslips.count(),
            "with_gross": payslips.exclude(gross_amount=0).count(),
            "without_gross": payslips.filter(gross_amount=0).count(),
        }

    @classmethod
    def get_run_contract_breakdown(cls, run_id: UUID) -> Dict[str, Any]:
        """
        Get a breakdown of payslips within a run by remuneration type.
        """
        logger.debug("[PayrollRun] Getting run contract breakdown", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)

        payslips = run.payslips.all()

        breakdown = {
            "total_payslips": payslips.count(),
            "by_remuneration_type": {},
        }

        # Breakdown by remuneration type (e.g., NET, GROSS)
        by_remuneration = payslips.values(
            'contract__remuneration_type'
        ).annotate(
            count=Count('id')
        )
        breakdown["by_remuneration_type"] = {
            item['contract__remuneration_type']: item['count'] for item in by_remuneration
        }

        return breakdown

