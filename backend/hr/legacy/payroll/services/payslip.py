from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from hr.payroll.models import Payslip
from hr.choices import PayslipStatus, PaymentPeriod
from .salary_log import (
    SalaryLogWriterService, 
    SalaryLogReaderService
)
from .salary import SalaryReaderService


#-------------------- Payslip Reader Service --------------------#
class PayslipReaderService:
    """Service for retrieving and querying payslips."""

    @staticmethod
    def get_payslip_by_id(payslip_id):
        """Return a specific payslip by ID."""
        return Payslip.objects.filter(id=payslip_id).first()

    @staticmethod
    def get_payslips_by_status(status=None):
        """Return payslips optionally filtered by status."""
        qs = Payslip.objects.all()
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-start_date')

    @staticmethod
    def get_eligible_employees(payslip: Payslip):
        """Return employees eligible to be included in a payslip."""
        return payslip.get_eligible_employees()


#-------------------- Payslip Writer Service --------------------#
class PayslipWriterService:
    """
    Service responsible for managing payslips:
    - Creating payslips and assigning employees
    - Confirming payslips and generating salary logs
    - Delegating salary computations, contributions, bonuses, and advances
    - Marking payslips as paid and notifying employees
    This service orchestrates the workflow without directly implementing 
    business rules for salary calculations.
    """

    @staticmethod
    @transaction.atomic
    def create_payslip(
        start_date, 
        end_date, 
        payment_period=PaymentPeriod.MONTHLY, 
        employees=None
    ):
        """Create a new payslip and optionally assign employees."""
        payslip = Payslip(
            start_date=start_date, 
            end_date=end_date, 
            payment_period=payment_period
        )
        payslip.save()  # code auto-generated in save()
        if employees:
            payslip.employees.set(employees)
        return payslip

    @staticmethod
    @transaction.atomic
    def confirm_payslip(payslip: Payslip, user=None):
        """Confirm payslip and generate salary logs."""
        PayslipWriterService._validate_confirmable(payslip)
        payslip.status = PayslipStatus.CONFIRMED
        payslip.confirmed_date = timezone.now()
        payslip.save(update_fields=['status', 'confirmed_date'])

        salary_logs = PayslipWriterService._create_salary_logs_for_payslip(payslip)

        tx = None  # Placeholder for transaction (accounting)
        # tx = TransactionService.create_for_payslip(payslip, salary_logs, user=user)

        return salary_logs, tx

    @staticmethod
    @transaction.atomic
    def mark_as_paid(payslip: Payslip):
        """
        Mark payslip as paid and update all related salary logs, advances, 
        contributions, and bonuses.
        """
        if payslip.status != PayslipStatus.CONFIRMED:
            raise ValidationError("Only confirmed payslips can be paid.")

        payslip.status = PayslipStatus.PAID
        payslip.paid_date = timezone.now()
        payslip.save(update_fields=['status', 'paid_date'])

        # Process salary logs and mark each as paid
        salary_logs = SalaryLogReaderService.get_salary_logs_for_payslip(payslip.id)
        for log in salary_logs:
            # Compute salary including contributions, bonuses, and salary advances
            SalaryLogWriterService.compute_salary(log, commit=True)
            # Mark log as paid
            SalaryLogWriterService.mark_as_paid(log)

        PayslipWriterService.notify_payment(payslip)

    @staticmethod
    @transaction.atomic
    def cancel_payslip(payslip: Payslip):
        """Cancel a payslip if it has not been paid yet."""
        if payslip.status == PayslipStatus.PAID:
            raise ValidationError("Cannot cancel a payslip that has already been paid.")

        payslip.status = PayslipStatus.CANCELED
        payslip.canceled_date = timezone.now()
        payslip.save(update_fields=['status', 'canceled_date'])

    @staticmethod
    def notify_payment(payslip: Payslip):
        """Notify employees that the payslip has been paid."""
        for employee in payslip.employees.all():
            print(f"Notification sent to {employee.email} for payslip {payslip.start_date} - {payslip.end_date}")

    # -------------------- Helper methods -------------------- #

    @staticmethod
    def _validate_confirmable(payslip: Payslip):
        """Ensure payslip can be confirmed."""
        if payslip.status != PayslipStatus.REVIEW:
            raise ValidationError("Only payslips in review can be confirmed.")

    @staticmethod
    def _create_salary_logs_for_payslip(payslip: Payslip):
        """Generate SalaryLogs for eligible employees using dedicated services."""
        salary_logs = []
        employees = PayslipReaderService.get_eligible_employees(payslip)

        for employee in employees:
            salary = SalaryReaderService.get_active_salary(employee)

            is_temporary = salary and salary.contract_type != 'CDI'
            has_expired = is_temporary and salary.end_date < payslip.start_date

            if not salary or has_expired:
                continue


            log = SalaryLogWriterService.create_salary_log(
                salary=salary,
                payslip=payslip,
                start_date=payslip.start_date,
                end_date=payslip.end_date,
                commit=True
            )
            # Compute salary including contributions, bonuses, advances
            SalaryLogWriterService.compute_salary(log, commit=True)
            salary_logs.append(log)

        return salary_logs

