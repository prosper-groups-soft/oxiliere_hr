import logging
from uuid     import UUID
from typing   import List
from injector import inject

from django.core.exceptions import ValidationError
from ninja import Query
from ninja.pagination import paginate
from ninja_extra      import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra,
    PaginatedResponseSchema
)
from oxutils.permissions.perms import ScopePermission
from hr.services.cache_helpers import cache_api_response, invalidate_cache_prefix

from hr.payroll.models  import PayrollRun
from hr.payroll.schemas import (
    PayrollRunCreateIn,
    PayrollRunOut,
    PayrollRunDetailOut,
    PayrollRunUpdateIn,
    PayrollRunListFilterIn,
    EmployeePayslipOut,
    EmployeePayslipDetailOut,
    PayslipGenerationStatusOut,
    PayrollRunSummaryOut,
    PayrollRunPresenceOut,
    PayslipListFilterIn,
)
from hr.payroll.services.orchestrator import PayrollOrchestrator
from hr.payroll.services.payroll_run  import PayrollRunService

# Cache integration
from hr.services.cache_helpers import cache_api_response


logger = logging.getLogger(__name__)


@api_controller('/payroll/runs', tags=['Payroll Runs'])
class PayrollRunController(ControllerBase):
    """
    Payslip controller.

    Manages employee payslips:
    - Generate payslips for a run
    - Review and approve payslips
    - Generate payroll reports
    - Manage payroll status (DRAFT → PROCESSING → COMPLETED)
    """

    @inject
    def __init__(
        self,
        payroll_run_service: PayrollRunService,
        orchestrator: PayrollOrchestrator,
    ):
        self.payroll_run_service = payroll_run_service
        self.orchestrator = orchestrator

    @http_get('/', response=PaginatedResponseSchema[PayrollRunOut], permissions=[ScopePermission('payroll:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_payroll_runs(self, filters: PayrollRunListFilterIn = Query(...), ordering: str | None = Query(None)):  # type: ignore[reportCallIssue]
        """
        List payroll runs with filtering and pagination.
        
        Supports filtering by:
        - Status (DRAFT, PROCESSING, COMPLETED, CANCELLED) — ou statut métier de
          liste (draft / processing / closed / error), voir PayrollRunListFilterIn
        - Period (month/year)
        - Payment method
        - Date range
        - Tri serveur via `ordering` (period, status, employeeCount, grossTotal,
          createdAt ; préfixer par '-' pour un ordre décroissant).
        """
        logger.debug("[Payroll Run] Listing runs", extra={"filters": filters.model_dump(), "ordering": ordering})

        qs = self.payroll_run_service.list_runs_annotated(filters=filters, ordering=ordering)
        return [self.payroll_run_service.serialize_run(run) for run in qs]

    @http_get('/{run_id}/', response=PayrollRunDetailOut, permissions=[ScopePermission('payroll:r')])
    @cache_api_response(timeout=60*60*24, key_prefix="payroll_run_detail", user_specific=False)
    def get_payroll_run_detail(self, run_id: UUID):
        """
        Retrieve detailed information about a payroll run.
        
        Includes:
        - Run metadata (period, status, payment method)
        - Payslip count and status breakdown
        - Total salaries (gross, net, deductions)
        - Processing statistics
        """
        logger.debug("[Payroll Run] Getting run detail", extra={"run_id": run_id})

        try:
            run = self.payroll_run_service.get_run_detail(run_id)
            return run

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

    @http_get('/{run_id}/presence/', response=PayrollRunPresenceOut, permissions=[ScopePermission('payroll:r')])
    def get_payroll_run_presence(self, run_id: UUID):
        """
        Aperçu de présence des employés éligibles d'un run (préparation de paie).

        Pour chaque employé retenu par la sélection et éligible sur la période,
        renvoie jours travaillés, heures, absences, congés et jours de présence
        non finalisés — la source de vérité que le calcul utilisera.
        """
        logger.debug("[Payroll Run] Getting presence preview", extra={"run_id": run_id})
        try:
            return self.payroll_run_service.get_presence_preview(run_id)
        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

    @http_get('/{run_id}/payslips/', response=PaginatedResponseSchema[EmployeePayslipOut], permissions=[ScopePermission('payroll:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    @cache_api_response(timeout=60*60, key_prefix="payroll_run_payslips", user_specific=False)
    def list_payslips_in_run(self, run_id: UUID):
        """
        List all payslips belonging to a specific payroll run.
        Returns payslips with status, gross, net, and deduction details.
        """
        logger.debug("[Payroll Run] Listing payslips in run", extra={"run_id": run_id})

        try:
            qs = self.payroll_run_service.get_payslips_for_run(run_id)
            return qs

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

    @http_get('/{run_id}/summary/', response=PayrollRunSummaryOut, permissions=[ScopePermission('payroll:r')])
    @cache_api_response(timeout=60*60, key_prefix="payroll_run_summary", user_specific=False)
    def get_payroll_run_summary(self, run_id: UUID):
        """
        Get financial summary of a payroll run.
        
        Returns aggregated totals:
        - Total employees processed
        - Total gross salary
        - Total deductions (taxes, contributions, advances)
        - Total net salary
        - Total allowances
        """
        logger.debug("[Payroll Run] Getting run summary", extra={"run_id": run_id})

        try:
            summary = self.payroll_run_service.get_payroll_summary(run_id)
            return summary

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

    @http_get('/payslips/{payslip_id}/', response=EmployeePayslipDetailOut, permissions=[ScopePermission('payroll:r')])
    @cache_api_response(timeout=60*60, key_prefix="payslip_detail", user_specific=True)
    def get_payslip_detail(self, payslip_id: UUID):
        """
        Retrieve full details for a single payslip.
        
        Returns:
        - All financial components (Gross, Net, Taxes, Contributions)
        - Individual line items (details of allowances, etc.)
        - Employee and contract snapshots
        """
        logger.debug("[Payroll Run] Getting payslip detail", extra={"payslip_id": payslip_id})

        try:
            payslip = self.payroll_run_service.get_payslip_detail(payslip_id)
            return payslip

        except Exception as e:
            logger.warning("[Payroll Run] Payslip not found", extra={"payslip_id": payslip_id, "error": str(e)})
            return self.create_response(
                {"detail": "Payslip not found"},
                status_code=404,
            )

    @http_post('/', response={201: PayrollRunOut}, permissions=[ScopePermission('payroll:w')])
    def create_payroll_run(self, data: PayrollRunCreateIn):
        """
        Create a new payroll run (set period and parameters).
        This creates a draft run ready for payslip generation.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Payroll Run] Creating payroll run", extra={"actor": actor})

        try:
            run = self.payroll_run_service.create_payroll_run(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info(
                "[Payroll Run] Payroll run created",
                extra={"run_id": run.id, "period": f"{run.start_date} to {run.end_date}"},
            )
            invalidate_cache_prefix('payroll_runs_list')
            return 201, self.payroll_run_service.serialize_run(run)

        except ValidationError as e:
            logger.warning("[Payroll Run] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{run_id}/', response=PayrollRunOut, permissions=[ScopePermission('payroll:u')])
    def update_payroll_run(self, run_id: UUID, data: PayrollRunUpdateIn):
        """
        Update payroll run parameters (only in DRAFT status).
        Cannot update runs that are already PROCESSING or COMPLETED.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Payroll Run] Updating payroll run", extra={"run_id": run_id})

        try:
            run = self.payroll_run_service.update_payroll_run(
                run_id=run_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            logger.info("[Payroll Run] Run updated successfully", extra={"run_id": run_id})
            return self.payroll_run_service.serialize_run(run)

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Payroll Run] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/{run_id}/process', response={202: PayslipGenerationStatusOut}, permissions=[ScopePermission('payroll:w')])
    def process_payroll_run(self, run_id: UUID):
        """
        Process a payroll run (DRAFT → PROCESSING → VALIDATED).
        
        Generates payslips for all active employee contracts by delegating to PayrollOrchestrator.
        The orchestrator handles all salary calculations and bulletin generation.
        
        Returns:
        - Status: VALIDATED (if successful)
        - Total employees processed
        - Total payslips generated
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Payroll Run] Processing payroll run", extra={"run_id": run_id, "actor": actor})

        try:
            status = self.payroll_run_service.start_payroll_processing(
                run_id=run_id,
                actor=actor,
                orchestrator=self.orchestrator,
            )
            logger.info(
                "[Payroll Run] Processing started",
                extra={"run_id": run_id, "task_id": status.get('task_id')},
            )
            invalidate_cache_prefix('payroll_runs_list')
            invalidate_cache_prefix('payroll_run_detail')
            invalidate_cache_prefix('payroll_run_payslips')
            # Le summary est mis en cache 60 min : un GET pendant l'état DRAFT
            # (0 bulletin) le figeait à zéro. On l'invalide au calcul pour que le
            # frontend relise les vrais totaux après génération.
            invalidate_cache_prefix('payroll_run_summary')
            return 202, status

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Payroll Run] Cannot process run", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/{run_id}/complete', response=PayrollRunOut, permissions=[ScopePermission('payroll:a')])
    def complete_payroll_run(self, run_id: UUID):
        """
        Mark a payroll run as PAID (finalize and lock).
        This locks the run and prevents further modifications.
        All payslips must be generated before completion (requires VALIDATED status).
        Status transition: VALIDATED → PAID
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Payroll Run] Completing payroll run", extra={"run_id": run_id, "actor": actor})

        try:
            run = self.payroll_run_service.complete_payroll_run(
                run_id=run_id,
                actor=actor,
            )
            logger.info("[Payroll Run] Run completed", extra={"run_id": run_id})
            invalidate_cache_prefix('payroll_runs_list')
            invalidate_cache_prefix('payroll_run_detail')
            return self.payroll_run_service.serialize_run(run)

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Payroll Run] Cannot complete run", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/{run_id}/review', response=PayrollRunOut, permissions=[ScopePermission('payroll:r')])
    def review_payroll_run(self, run_id: UUID):
        """
        Move a processed run into the review stage.
        Status transition: VALIDATED → REVIEWED.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Payroll Run] Reviewing payroll run", extra={"run_id": run_id, "actor": actor})

        try:
            run = self.payroll_run_service.review_payroll_run(
                run_id=run_id,
                actor=actor,
            )
            logger.info("[Payroll Run] Run reviewed", extra={"run_id": run_id})
            invalidate_cache_prefix('payroll_runs_list')
            invalidate_cache_prefix('payroll_run_detail')
            return self.payroll_run_service.serialize_run(run)

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Payroll Run] Cannot review run", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/{run_id}/approve', response=PayrollRunOut, permissions=[ScopePermission('payroll:r')])
    def approve_payroll_run(self, run_id: UUID):
        """
        Approve a reviewed run, ready for payment.
        Status transition: REVIEWED → APPROVED.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Payroll Run] Approving payroll run", extra={"run_id": run_id, "actor": actor})

        try:
            run = self.payroll_run_service.approve_payroll_run(
                run_id=run_id,
                actor=actor,
            )
            logger.info("[Payroll Run] Run approved", extra={"run_id": run_id})
            invalidate_cache_prefix('payroll_runs_list')
            invalidate_cache_prefix('payroll_run_detail')
            return self.payroll_run_service.serialize_run(run)

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Payroll Run] Cannot approve run", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/{run_id}/cancel', response=PayrollRunOut, permissions=[ScopePermission('payroll:a')])
    def cancel_payroll_run(self, run_id: UUID):
        """
        Cancel a payroll run (mark as CANCELLED).
        Allows re-processing with corrected parameters.
        Only DRAFT or PROCESSING runs can be cancelled.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Payroll Run] Cancelling payroll run", extra={"run_id": run_id, "actor": actor})

        try:
            run = self.payroll_run_service.cancel_payroll_run(
                run_id=run_id,
                actor=actor,
            )
            logger.info("[Payroll Run] Run cancelled", extra={"run_id": run_id})
            invalidate_cache_prefix('payroll_runs_list')
            invalidate_cache_prefix('payroll_run_detail')
            return self.payroll_run_service.serialize_run(run)

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Payroll Run] Cannot cancel run", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)


@api_controller('/payroll/payslips', tags=['Payslips'])
class PayslipController(ControllerBase):
    """Bulletins globaux : paginés, filtrables par run, triables, recherchables."""

    @inject
    def __init__(self, payroll_run_service: PayrollRunService):
        self.payroll_run_service = payroll_run_service

    @http_get('/', response=PaginatedResponseSchema[EmployeePayslipOut], permissions=[ScopePermission('payroll:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_payslips(self, filters: PayslipListFilterIn = Query(...), ordering: str | None = Query(None)):  # type: ignore[reportCallIssue]
        """Liste globale des bulletins. `run_id` filtre par run (par défaut tous). Tri via `ordering`."""
        qs = self.payroll_run_service.list_payslips_annotated(filters=filters, ordering=ordering)
        return qs

