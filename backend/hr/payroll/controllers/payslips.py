"""
PAYROLL RUN CONTROLLER

Manages payroll processing cycles:
- Create payroll runs (monthly, bi-weekly, etc.)
- Process payslips for a run
- Review and approve payslips
- Generate payroll reports
- Manage payroll status (DRAFT → PROCESSING → COMPLETED)
"""

import logging
from typing import List
from uuid import UUID
from injector import inject

from django.core.exceptions import ValidationError
from ninja import Query
from ninja.pagination import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)
from oxutils.pagination.cursor import CursorPagination

from hr.payroll.models import PayrollRun
from hr.payroll.schemas import (
    PayrollRunCreateIn,
    PayrollRunOut,
    PayrollRunDetailOut,
    PayrollRunUpdateIn,
    PayrollRunListFilterIn,
    EmployeePayslipOut,
    PayslipGenerationStatusOut,
)
from hr.payroll.services.orchestrator import PayrollOrchestrator
from hr.payroll.services.payroll_run import PayrollRunService


logger = logging.getLogger(__name__)


@api_controller('/payroll/runs', tags=['Payroll Runs'])
class PayrollRunController(ControllerBase):
    """
    Payroll cycle management and execution.
    
    Responsibilities:
    - Create payroll runs (set period, payment method, status)
    - Process runs (generate payslips for all active contracts)
    - Review payslips before approval
    - Lock runs for processing
    - Generate payroll reports and analytics
    """

    @inject
    def __init__(
        self,
        payroll_run_service: PayrollRunService,
        orchestrator: PayrollOrchestrator,
    ):
        self.payroll_run_service = payroll_run_service
        self.orchestrator = orchestrator

    @http_get('/', response=List[PayrollRunOut])
    @paginate(CursorPagination)
    def list_payroll_runs(self, filters: PayrollRunListFilterIn = Query(...)):
        """
        List payroll runs with filtering and pagination.
        
        Supports filtering by:
        - Status (DRAFT, PROCESSING, COMPLETED, CANCELLED)
        - Period (month/year)
        - Payment method
        - Date range
        """
        logger.debug("[Payroll Run] Listing runs", extra={"filters": filters.model_dump()})

        qs = PayrollRun.objects.all().order_by('-period_end')

        # Apply filters
        return filters.filter(qs)

    @http_get('/{run_id}', response=PayrollRunDetailOut)
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

    @http_get('/{run_id}/payslips', response=List[EmployeePayslipOut])
    @paginate(CursorPagination)
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

    @http_get('/{run_id}/summary', response=dict)
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

    @http_post('/', response={201: PayrollRunOut})
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
                extra={"run_id": run.id, "period": f"{run.period_start} to {run.period_end}"},
            )
            return 201, run

        except ValidationError as e:
            logger.warning("[Payroll Run] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{run_id}', response=PayrollRunOut)
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
            return run

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Payroll Run] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/{run_id}/process', response={202: PayslipGenerationStatusOut})
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

    @http_post('/{run_id}/complete', response=PayrollRunOut)
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
            return run

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Payroll Run] Cannot complete run", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/{run_id}/cancel', response=PayrollRunOut)
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
            return run

        except PayrollRun.DoesNotExist:
            logger.warning("[Payroll Run] Run not found", extra={"run_id": run_id})
            return self.create_response(
                {"detail": "Payroll run not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Payroll Run] Cannot cancel run", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

