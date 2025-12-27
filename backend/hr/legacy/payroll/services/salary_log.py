from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from hr.payroll.models import (
    SalaryLog, 
    Salary, 
    SocialContribution, 
    Bonus
)
from hr.attendance.models import Attendance
from .salary_advance import (
    SalaryAdvanceReaderService, 
    SalaryAdvanceWriterService
)


class SalaryLogReaderService:
    """
    Service for reading/retrieving salary logs.
    """

    @staticmethod
    def get_salary_logs_for_employee(employee_id, start_date=None, end_date=None):
        """Return salary logs for an employee, optionally filtered by period."""
        qs = SalaryLog.objects.filter(salary__employee_id=employee_id)
        if start_date:
            qs = qs.filter(end_date__gte=start_date)
        if end_date:
            qs = qs.filter(start_date__lte=end_date)
        return qs.order_by('-start_date')

    @staticmethod
    def get_salary_log_by_id(log_id):
        """Return a specific salary log by ID."""
        return SalaryLog.objects.filter(id=log_id).first()

    @staticmethod
    def get_unpaid_salary_logs():
        """Return all unpaid salary logs."""
        return SalaryLog.objects.filter(is_paid=False).order_by('start_date')
    
    @staticmethod
    def get_salary_logs_for_payslip(payslip_id):
        """Return all salary logs for a given payslip."""
        return SalaryLog.objects.filter(payslip_id=payslip_id).order_by('start_date')



class SalaryLogWriterService:
    """
    Service for creating, updating, and computing salary logs.
    All business logic is centralized here.
    """

    @staticmethod
    @transaction.atomic
    def create_salary_log(salary: Salary, payslip, start_date, end_date, commit=True):
        """Create a salary log for a given salary and payslip."""
        log = SalaryLog(
            salary=salary,
            payslip=payslip,
            start_date=start_date,
            end_date=end_date,
            total_payment=0,
            total_contributions=0,
            total_bonus=0,
            is_paid=False,
            confirmed=False
        )
        if commit:
            log.save()
            SalaryLogWriterService.compute_salary(log)
        return log

    @staticmethod
    @transaction.atomic
    def compute_salary(log: SalaryLog, override=False, commit=True):
        """Compute payment, advances, contributions, bonuses."""
        if log.is_paid and not override:
            return log

        # Hours worked
        log.hours_worked = AttendanceWriterService.compute_hours(
            log.salary.employee, log.start_date, log.end_date, log.salary.pay_overtime
        )

        # Base salary
        if log.salary.payment_type == 'FIXED':
            log.total_payment = log.salary.base_salary
        elif log.salary.payment_type == 'HOURLY':
            hours = (log.hours_worked.total_seconds() / 3600) if log.hours_worked else 0
            log.total_payment = log.salary.hourly_rate * hours

        # Apply salary advance via service
        salary_advance = SalaryAdvanceReaderService.get_active_advance_for_employee(log.salary.employee)
        if salary_advance:
            repayment = SalaryAdvanceWriterService.apply_repayment(
                salary_advance=salary_advance,
                available_amount=log.total_payment
            )
            log.salary_advance = repayment
            if repayment:
                log.total_payment -= repayment.amount

        # Contributions via service
        contributions = ContributionService.get_applicable(log.salary.employee, log.end_date)
        log.social_contributions.set(contributions)
        log.total_contributions = sum([c.get_amount(log.total_payment) for c in contributions])
        log.total_payment -= log.total_contributions

        # Bonuses via service
        bonuses = BonusService.get_applicable(log.salary.employee)
        log.bonus.set(bonuses)
        log.total_bonus = sum([b.amount for b in bonuses])
        log.total_payment += log.total_bonus

        if commit:
            log.save()
        return log

    @staticmethod
    @transaction.atomic
    def confirm_payment(log: SalaryLog):
        log.confirmed = True
        log.confirmed_at = timezone.now()
        log.save()
        return log

    @staticmethod
    @transaction.atomic
    def mark_as_paid(log: SalaryLog):
        log.is_paid = True
        log.paid_at = timezone.now()
        log.save()
        return log
