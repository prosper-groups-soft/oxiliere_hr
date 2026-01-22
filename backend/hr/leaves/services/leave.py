import logging
from decimal import Decimal
from datetime import timedelta, date
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from functools import wraps

from hr.employees.models import Employee
from hr.leaves.enums import (
    LeaveCategory,
    LeaveStatus,
    LeaveTransactionTypes
)
from hr.leaves.models import (
    LeaveRequest,
    LeaveBalance,
    LeaveRecall,
    CircumstanceLeaveRule,
    LeaveCarryOver,
    LeaveTransaction
)
from hr.attendance.services import SchedulingService 
from .balance import BalanceService
from .consumption import LeaveConsumptionService


logger = logging.getLogger(__name__)


# --- Decorator for leave transitions ---
def leave_transition(action):
    """
    Decorator to handle leave request transitions:
    - Validates allowed transitions based on current status
    - Handles comment logging in French for audit trail
    - Wraps the transition in a DB transaction
    """
    def decorator(func):
        @wraps(func)
        @transaction.atomic
        def wrapper(self, leave_request: LeaveRequest, *args, **kwargs):
            target_status_map = {
                'approve': LeaveStatus.APPROVED,
                'reject': LeaveStatus.REJECTED,
                'cancel': LeaveStatus.CANCELLED,
                'mark_taken': LeaveStatus.TAKEN
            }
            target_status = target_status_map[action]
            current_status = leave_request.status
            valid_transitions = {
                LeaveStatus.PENDING: [LeaveStatus.APPROVED, LeaveStatus.REJECTED, LeaveStatus.CANCELLED],
                LeaveStatus.APPROVED: [LeaveStatus.CANCELLED, LeaveStatus.TAKEN]
            }
            if target_status not in valid_transitions.get(current_status, []):
                raise ValidationError(f"Cannot perform '{action}' from {current_status}")

            result = func(self, leave_request, *args, **kwargs)

            user = kwargs.get('user')
            reason = kwargs.get('reason')
            prefix_map = {
                'approve': "[APPROUVÉ]",
                'reject': "[REJETÉ]",
                'cancel': "[ANNULÉ]",
                'mark_taken': "[ARCHIVÉ]"
            }
            
            existing_comment = leave_request.comment or ""
            timestamp = timezone.now().date()
            if user:
                leave_request.comment = f"{existing_comment}\n{prefix_map[action]} Par {user} le {timestamp}."
            if reason:
                leave_request.comment += f"\nMotif : {reason}"

            leave_request.status = target_status
            leave_request.save(update_fields=["status", "comment"])
            return result
        return wrapper
    return decorator


class LeaveRequestService:
    """
    Service for managing leave requests with automatic transitions.

    Lifecycle of a leave request:
        PENDING ── APPROVED ──> TAKEN (after end_date)
           │
           └─ REJECTED
        APPROVED ── CANCELLED
        PENDING ── CANCELLED
    """

    @transaction.atomic
    def create_request(self, employee: Employee, data, creator):
        """
        Create a new leave request.

        Steps:
        1. Compute total working days.
        2. Validate overlap with existing requests.
        3. Validate employee balance (annual or circumstance leave).
        4. Create the leave request record with PENDING status.
        """
        category = data.get('category')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        attachment = data.get('attachment')

        days_total = Decimal(str(SchedulingService.count_working_days_for_employee(
            employee, start_date, end_date
        )))

        if days_total <= 0:
            raise ValidationError("The period selected does not contain any working days.")

        self._check_overlap(employee, start_date, end_date)

        if category == LeaveCategory.ANNUAL:
            self._validate_annual_balance(employee, start_date, end_date, days_total)
        elif category == LeaveCategory.CIRCUMSTANCE:
            self._validate_circumstance(data, days_total)

        circumstance_type = data.get('circumstance_type') if category == LeaveCategory.CIRCUMSTANCE else None

        return LeaveRequest.objects.create(
            employee=employee,
            category=category,
            circumstance_type=circumstance_type,
            start_date=start_date,
            end_date=end_date,
            requested_days=days_total,
            attachment=attachment,
            status=LeaveStatus.PENDING,
            created_by=creator,
            comment=data.get('comment', '')
        )

    @leave_transition('approve')
    def approve_request(self, leave_request: LeaveRequest, user=None, reason=None):
        """
        Approve a pending leave request.
        - Consumes annual leave balance if category is ANNUAL.
        - Adds an approval comment automatically.
        """
        if leave_request.category == LeaveCategory.ANNUAL:
            self._consume_annual_leave(leave_request, user)
        return leave_request

    @leave_transition('cancel')
    def cancel_request(self, leave_request: LeaveRequest, user=None, reason=None):
        """Cancel a pending leave request."""
        if leave_request.category == LeaveCategory.ANNUAL and leave_request.status == LeaveStatus.APPROVED:
            self._refund_annual_leave(leave_request, user)
        return leave_request

    @leave_transition('reject')
    def reject_request(self, leave_request: LeaveRequest, user=None, reason=None):
        """Reject a pending leave request and log the rejection comment."""
        return leave_request

    @leave_transition('mark_taken')
    def mark_taken_request(self, leave_request: LeaveRequest):
        """Mark an approved leave as TAKEN after its end date."""
        return leave_request

    # --- Internal Balance Management ---

    def _consume_annual_leave(self, leave_request: LeaveRequest, actor):
        """
        Deduct days and create consumption transactions.
        """
        days_per_year = SchedulingService.get_working_days_by_year(
            leave_request.employee, leave_request.start_date, leave_request.end_date
        )

        for year, days in days_per_year.items():
            amount = Decimal(str(days))
            LeaveConsumptionService.consume(leave_request.employee, year, amount)
            
            # Audit Trail
            LeaveTransaction.objects.create(
                employee=leave_request.employee,
                year=year,
                amount=-amount,  # Negative for debit
                transaction_type=LeaveTransactionTypes.CONSUME,
                leave_request=leave_request,
                reason=f"Leave approved: {leave_request.start_date} to {leave_request.end_date}",
                created_by=actor
            )

    def _refund_annual_leave(self, leave_request: LeaveRequest, actor):
        """
        Refund days and create refund transactions.
        """
        days_per_year = SchedulingService.get_working_days_by_year(
            leave_request.employee, leave_request.start_date, leave_request.end_date
        )

        for year, days in days_per_year.items():
            amount = Decimal(str(days))
            self._refund_balance(leave_request.employee, year, amount, leave_request, actor)

    def _refund_balance(self, employee, year, days, leave_request, actor):
        """
        Smart refund logic: Annual Balance first, then CarryOver (LIFO-like).
        """
        remaining = Decimal(str(days))
        total_to_refund = remaining

        # 1. Refund to annual balance
        balance = LeaveBalance.objects.select_for_update().get(employee=employee, year=year)
        can_refund_to_annual = balance.used_days 
        refund_to_annual = min(can_refund_to_annual, remaining)
        
        if refund_to_annual > 0:
            balance.used_days -= refund_to_annual
            balance.save(update_fields=["used_days"])
            remaining -= refund_to_annual

        # 2. Refund to CarryOver
        if remaining > 0:
            carry_overs = LeaveCarryOver.objects.select_for_update().filter(
                employee=employee, source_year__lt=year 
            ).order_by("-source_year")

            for co in carry_overs:
                if remaining <= 0: break
                used = co.used_days
                if used <= 0: continue
                
                refund_to_co = min(used, remaining)
                co.used_days -= refund_to_co
                co.save(update_fields=["used_days"])
                remaining -= refund_to_co

        # Audit Trail (One entry per year)
        LeaveTransaction.objects.create(
            employee=employee,
            year=year,
            amount=total_to_refund,
            transaction_type=LeaveTransactionTypes.REFUND,
            leave_request=leave_request,
            reason=f"Refund for cancelled/recalled leave",
            created_by=actor
        )

    @transaction.atomic
    def recall_employee(self, leave_request: LeaveRequest, recall_date: date, reason: str, recalled_by):
        """
        Handles employee recall with balance restoration.
        """
        if leave_request.status != LeaveStatus.APPROVED:
            raise ValidationError("Only approved requests can be recalled.")
        
        original_days_per_year = SchedulingService.get_working_days_by_year(
            leave_request.employee, leave_request.start_date, leave_request.end_date
        )
        
        actual_end_date = recall_date - timedelta(days=1)
        actual_days_per_year = SchedulingService.get_working_days_by_year(
            leave_request.employee, leave_request.start_date, actual_end_date
        )

        for year, total_planned in original_days_per_year.items():
            actually_taken = actual_days_per_year.get(year, 0)
            to_restore = Decimal(str(total_planned - actually_taken))
            
            if to_restore > 0 and leave_request.category == LeaveCategory.ANNUAL:
                self._refund_balance(leave_request.employee, year, to_restore, leave_request, recalled_by)

        leave_request.end_date = actual_end_date
        leave_request.requested_days = sum(actual_days_per_year.values())
        leave_request.save(update_fields=["end_date", "requested_days"])

        return LeaveRecall.objects.create(
            leave_request=leave_request,
            recall_date=recall_date,
            reason=reason,
            recalled_by=recalled_by
        )

    # --- Validators & Helpers ---

    def _check_overlap(self, employee, start_date, end_date):
        """Check for overlapping leave requests."""
        conflicting = LeaveRequest.objects.filter(
            employee=employee,
            status__in=[LeaveStatus.PENDING, LeaveStatus.APPROVED],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        if conflicting.exists():
            raise ValidationError("This request overlaps with an existing pending/approved leave.")

    def _validate_annual_balance(self, employee, start_date, end_date, days_total):
        """Validate annual leave balance."""
        days_per_year = SchedulingService.get_working_days_by_year(employee, start_date, end_date)
        for year, days in days_per_year.items():
            if not BalanceService.check_eligibility(employee, Decimal(str(days)), year):
                raise ValidationError(f"Insufficient balance for year {year}.")

    def _validate_circumstance(self, data, days_total):
        """Validate circumstance leave balance."""
        circ_type = data.get('circumstance_type')
        if not circ_type:
            raise ValidationError("Circumstance type is mandatory.")
        rule = CircumstanceLeaveRule.objects.filter(type=circ_type).first()
        if rule and days_total > Decimal(str(rule.duration_days)):
            raise ValidationError(f"Max {rule.duration_days} days allowed for this category.")

    # --- HR update ---
    @transaction.atomic
    def update_request_by_hr(self, leave_request: LeaveRequest, new_data, hr_user):
        """
        HR modifies a leave request:
        - Cancels the old request for audit trail.
        - Creates a new request with updated data.
        """
        logger.info(f"HR {hr_user} modifying request {leave_request.id}. Substitution in progress.")
        self.cancel_request(leave_request, user=hr_user)
        updated_data = {
            'category': leave_request.category,
            'circumstance_type': leave_request.circumstance_type,
            'start_date': leave_request.start_date,
            'end_date': leave_request.end_date,
            'attachment': leave_request.attachment,
            'comment': f"{leave_request.comment}\nSubstitue la demande {leave_request.id}. " + new_data.get('comment', '')
        }
        updated_data.update(new_data)
        return self.create_request(leave_request.employee, updated_data, hr_user)

    # --- Add or replace attachment ---
    @transaction.atomic
    def add_attachment(self, leave_request: LeaveRequest, file_obj, user):
        """
        Add or replace an attachment for a leave request.
        - Not allowed if leave is already approved or archived.
        """
        if leave_request.status in [LeaveStatus.APPROVED, LeaveStatus.TAKEN]:
            raise ValidationError("Cannot modify attachments on an approved or archived leave.")
        
        leave_request.attachment = file_obj
        existing_comment = leave_request.comment or ""
        leave_request.comment = f"{existing_comment}\n[DOC] Pièce jointe ajoutée par {user} le {timezone.now().date()}."
        leave_request.save()
        logger.info(f"Attachment updated for request {leave_request.id}")
        return leave_request

