from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import logging
from django.utils import timezone
from django.db.models import F, Sum
from django.db import transaction

from hr.leaves.models import (
    LeaveBalance, 
    LeavePolicy, 
    SeniorityRule,
    LeaveCarryOver,
    LeaveTransaction
)

from hr.leaves.utils import get_carry_over_expiration_date
from hr.leaves.enums import LeaveTransactionTypes


logger = logging.getLogger(__name__)


class BalanceService:
    """ Manages employee leave entitlements, pro-rata calculations, and carry-overs. """

    @transaction.atomic
    @staticmethod
    def init_employee_balance(employee, year: int = None):
        """
        Initializes the annual leave balance for an employee.
        Adjusts the entitlement proportionally if the employee joined mid-year.
        """
        if not year:
            year = timezone.now().year

        policy = LeavePolicy.objects.filter(country_code=employee.nationality).first()
        if not policy:
            logger.error(f"No active LeavePolicy for {employee.nationality}")
            return None

        # Pro-rata calculation for the first year of employment
        if employee.hire_date.year == year:
            end_of_year = date(year, 12, 31)
            total_days_in_year = (end_of_year - date(year, 1, 1)).days + 1
            days_worked = (end_of_year - employee.hire_date).days + 1
            
            base_days = (Decimal(str(policy.standard_annual_days)) / Decimal(total_days_in_year)) * days_worked
            base_days = base_days.quantize(Decimal("0.01"))
        else:
            base_days = Decimal(str(policy.standard_annual_days))

        # Additional days based on length of service
        seniority_years = relativedelta(date(year, 12, 31), employee.hire_date).years
        bonus = SeniorityRule.objects.filter(
            policy=policy, 
            years_of_service__lte=seniority_years
        ).order_by('-years_of_service').first()
        
        bonus_days = Decimal(str(bonus.bonus_days if bonus else 0))

        balance, created = LeaveBalance.objects.update_or_create(
            employee=employee,
            year=year,
            defaults={
                'base_entitlement': base_days,
                'seniority_bonus': bonus_days,
            }
        )
    
        if created:
            LeaveTransaction.objects.create(
                employee=employee,
                year=year,
                amount=base_days + bonus_days,
                transaction_type=LeaveTransactionTypes.EARN,
                reason=f"Annual entitlement for {year} (Base: {base_days}, Seniority: {bonus_days})"
            )

            # Trigger carry-over from previous year if allowed
            if policy.allows_carry_over:
                BalanceService.create_carry_over(employee, year, policy)
        
        return balance

    @staticmethod
    def check_eligibility(employee, requested_days: Decimal, year: int) -> bool:
        """
        Confirms if an employee has sufficient combined balance (annual + carry-overs)
        to cover a requested period.
        """
        balance = LeaveBalance.objects.select_for_update().filter(employee=employee, year=year).first()
        if not balance:
            balance = BalanceService.init_employee_balance(employee, year)

        carry = LeaveCarryOver.objects.select_for_update().filter(
            employee=employee,
            expires_at__gte=timezone.now().date(),
        ).aggregate(
            available=Sum(F("days") - F("used_days"))
        )["available"] or Decimal("0")

        return (balance.remaining_days + carry) >= requested_days

    @transaction.atomic
    @staticmethod
    def create_carry_over(employee, year: int, policy: LeavePolicy):
        """
        Transfers unused leave days from the previous year to the current year,
        subject to policy limits and expiration dates.
        """
        prev_balance = LeaveBalance.objects.filter(
            employee=employee,
            year=year - 1
        ).first()
        
        if not prev_balance or not policy.allows_carry_over:
            return

        remaining = prev_balance.remaining_days
        if remaining <= 0:
            return

        days = min(remaining, Decimal(str(policy.max_carry_over_days)))

        expiration_date = get_carry_over_expiration_date(
            year, 
            policy.carry_over_expiration_month
        )

        LeaveCarryOver.objects.update_or_create(
            employee=employee,
            source_year=year - 1,
            defaults={
                "days": days,
                "expires_at": expiration_date,
            }
        )

        LeaveTransaction.objects.create(
            employee=employee,
            year=year,
            amount=days,
            transaction_type=LeaveTransactionTypes.CARRY_OVER,
            reason=f"Days carried over from {year-1}"
        )

