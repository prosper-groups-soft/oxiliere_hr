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
    LeaveCarryOver
)
from hr.utils import carry_over_expiration_date


logger = logging.getLogger(__name__)


class BalanceService:

    @transaction.atomic
    @staticmethod
    def init_employee_balance(employee, year: int = None):
        """
        Initializes annual leave balance with precise pro-rata logic.
        """
        if not year:
            year = timezone.now().year

        policy = LeavePolicy.objects.filter(country_code=employee.nationality).first()
        if not policy:
            logger.error(f"No LeavePolicy found for {employee.nationality}")
            return None

        # --- IMPROVEMENT: Precise Pro-rata calculation ---
        if employee.hire_date.year == year:
            # Calculate days from hire date to end of year
            end_of_year = date(year, 12, 31)
            total_days_in_year = (end_of_year - date(year, 1, 1)).days + 1
            days_worked = (end_of_year - employee.hire_date).days + 1
            
            # (Standard Days / 365) * Days actually present
            base_days = (Decimal(str(policy.standard_annual_days)) / Decimal(total_days_in_year)) * days_worked
            # Standard rounding for HR: 2 decimal places
            base_days = base_days.quantize(Decimal("0.01"))
        else:
            base_days = Decimal(str(policy.standard_annual_days))

        # Seniority logic (remains mostly same but ensured ordering)
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
        
        # Carry-over logic triggered only once per year initialization
        if created and policy.allows_carry_over:
            BalanceService.create_carry_over(employee, year, policy)
        
        return balance

    @staticmethod
    def check_eligibility(employee, requested_days: Decimal, year: int) -> bool:
        """
        Verify if employee can take a leave.
        Uses select_for_update to prevent double-spending leave days
        during concurrent requests.
        """
        # Lock the balance row during check
        balance = LeaveBalance.objects.select_for_update().filter(employee=employee, year=year).first()
        if not balance:
            # We don't want to init inside a check if possible, but if we do, it's atomic
            balance = BalanceService.init_employee_balance(employee, year)

        # Sum carry_over with lock
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
        Identifies remaining leave days from the previous year and creates or updates 
        a carry-over record based on the company's leave policy.
        """
        # Create or update the carry-over from the previous year according to the policy
        prev_balance = LeaveBalance.objects.filter(
            employee=employee,
            year=year - 1
        ).first()
        if not prev_balance:
            return

        remaining = prev_balance.remaining_days
        if remaining <= 0 or not policy.allows_carry_over:
            return

        days = min(
            remaining,
            Decimal(str(policy.max_carry_over_days))
        )

        # Define the expiration date according to the policy
        expiration_date = carry_over_expiration_date(year, policy.carry_over_expiration_month)

        LeaveCarryOver.objects.update_or_create(
            employee=employee,
            source_year=year - 1,
            defaults={
                "days": days,
                "expires_at": expiration_date,
            }
        )

