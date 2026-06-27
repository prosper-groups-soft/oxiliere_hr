import logging
from decimal import Decimal
from typing  import Dict, Any
from uuid    import UUID

from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import QuerySet, Sum, Count, Q

from hr.payroll.models import (
    PayrollRun, 
    EmployeePayslip, 
    PayslipLine, 
    EmployeeContract
)
from .orchestrator    import PayrollOrchestrator
from hr.payroll.enums import PayrollStatus


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
            total_employee_cnss=Sum('employee_cnss_amount'),
            total_employer_cost=Sum('employer_total_cost'), # Total cost including INPP/ONEM
        )

        total_gross = aggregates.get("total_gross") or Decimal("0.00")
        total_net = aggregates.get("total_net") or Decimal("0.00")

        return {
            "id": run.id,
            "status": run.status,
            "period": f"{run.start_date} - {run.end_date}",
            "exchange_rate": run.exchange_rate_applied,
            "stats": {
                "total_count": total_payslips,
                "processed_count": processed_payslips,
                "pending_count": pending_payslips,
            },
            "financials": {
                "gross_total": total_gross,
                "net_total": total_net,
                "total_tax_deductions": total_gross - total_net,
                "employer_liability": aggregates.get("total_employer_cost") or Decimal("0.00"),
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

        # Check for existing runs with overlapping periods
        existing = PayrollRun.objects.filter(
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date),
            status__in=[PayrollStatus.DRAFT, PayrollStatus.PROCESSING]
        )
        if existing.exists():
            logger.warning("[PayrollRun] Overlapping run exists", extra={"start": start_date, "end": end_date})
            raise ValidationError("A payroll run already exists for this period")

        # Create run
        run = PayrollRun.objects.create(
            start_date=start_date,
            end_date=end_date,
            exchange_rate_applied=data.get('exchange_rate_applied'),
            status=PayrollStatus.DRAFT,
            created_by=actor,
        )

        logger.info(
            "[PayrollRun] Payroll run created",
            extra={"run_id": run.id, "period": f"{start_date} to {end_date}"}
        )
        return run

    @classmethod
    @transaction.atomic
    def update_payroll_run(cls, run_id: UUID, data: Dict[str, Any], actor=None) -> PayrollRun:
        """ Updates a draft payroll run's configuration. """
        logger.debug("[PayrollRun] Updating payroll run", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)

        if run.status != PayrollStatus.DRAFT:
            logger.warning(
                "[PayrollRun] Cannot update non-draft run",
                extra={"run_id": run_id, "status": run.status}
            )
            raise ValidationError(f"Cannot update run with status {run.status}")

        # Update fields
        if 'exchange_rate_applied' in data:
            run.exchange_rate_applied = data['exchange_rate_applied']

        run.updated_by = actor
        run.save()

        logger.info("[PayrollRun] Run updated", extra={"run_id": run_id})
        return run

    # ===== STATUS TRANSITIONS =====

    @classmethod
    @transaction.atomic
    def start_payroll_processing(cls, run_id: UUID, actor=None, orchestrator: PayrollOrchestrator=None) -> Dict[str, Any]:
        """ Initiates the calculation process for all eligible employee contracts. """
        logger.debug("[PayrollRun] Starting payroll processing", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)

        if run.status != PayrollStatus.DRAFT:
            logger.warning(
                "[PayrollRun] Cannot process non-draft run",
                extra={"run_id": run_id, "status": run.status}
            )
            raise ValidationError(f"Cannot process run with status {run.status}")

        # Count active contracts
        today = timezone.localdate()
        active_contracts = EmployeeContract.objects.filter(
            start_date__lte=today,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
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

        if run.status != PayrollStatus.VALIDATED:
            logger.warning(
                "[PayrollRun] Cannot complete run",
                extra={"run_id": run_id, "status": run.status}
            )
            raise ValidationError(f"Cannot complete run with status {run.status}. Must be VALIDATED.")

        # Verify payslips exist
        payslip_count = run.payslips.count()
        if payslip_count == 0:
            logger.warning("[PayrollRun] No payslips generated", extra={"run_id": run_id})
            raise ValidationError("Cannot complete run without payslips")

        run.status = PayrollStatus.PAID
        run.updated_by = actor
        run.save()

        logger.info("[PayrollRun] Run completed and marked PAID", extra={"run_id": run_id, "payslips": payslip_count})
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
        ).order_by('contract__employee__user__first_name')
        
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

        # 2. DRC Employer Liabilities Calculation
        # Employer CNSS (8%) is derived from Employee CNSS (5%) -> Ratio 8/5
        total_er_cnss = (total_ee_cnss * Decimal('8')) / Decimal('5')
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
            "base_salary_snapshot": payslip.base_salary_snapshot.amount if payslip.base_salary_snapshot else None,
            "gross_amount": payslip.gross_amount.amount if payslip.gross_amount else None,
            "cnss_amount": payslip.cnss_amount.amount if payslip.cnss_amount else None,
            "onem_amount": payslip.onem_amount.amount if payslip.onem_amount else None,
            "inpp_amount": payslip.inpp_amount.amount if payslip.inpp_amount else None,
            "ipr_amount": payslip.ipr_amount.amount if payslip.ipr_amount else None,
            "family_allowance": payslip.family_allowance.amount if payslip.family_allowance else None,
            "housing_allowance": payslip.housing_allowance.amount if payslip.housing_allowance else None,
            "transport_allowance": payslip.transport_allowance.amount if payslip.transport_allowance else None,
            "total_adjustments": payslip.total_adjustments.amount if payslip.total_adjustments else None,
            "net_amount": payslip.net_amount.amount if payslip.net_amount else None,
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
            "employee_name": f"{employee.user.first_name} {employee.user.last_name}",
            "employee_id": employee.id,
            "net_after_advances": payslip.net_amount.amount if payslip.net_amount else None,
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
        Get a breakdown of payslips within a run by contract demographics (remuneration type, payment period).
        """
        logger.debug("[PayrollRun] Getting run contract breakdown", extra={"run_id": run_id})

        run = PayrollRun.objects.get(id=run_id)

        payslips = run.payslips.all()

        breakdown = {
            "total_payslips": payslips.count(),
            "by_remuneration_type": {},
            "by_payment_period": {},
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

        # Breakdown by payment period (e.g., MONTHLY, BIWEEKLY)
        by_period = payslips.values(
            'contract__payment_period'
        ).annotate(
            count=Count('id')
        )
        breakdown["by_payment_period"] = {
            item['contract__payment_period']: item['count'] for item in by_period
        }

        return breakdown


