from __future__ import annotations
from datetime import date, timedelta
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from hr.enums import WeekdayEnum
from hr.calendar.services import CalendarService

from hr.attendance.models import (
    ShiftPolicy, 
    ShiftDetail, 
    EmploymentScheme,
    ShiftAssignment,
    RotationPattern
)


class SchedulingService:
    """
    Service responsible for managing employee work schedules and policy assignments.
    """
    
    @staticmethod
    @transaction.atomic
    def create_full_policy(name: str, weekly_target_hours: int, daily_configs: dict):
        """
        Creates a policy and its customized details for each day.
        
        daily_configs should be a dictionary such as:
        {
            'monday': {'start': '08:00', 'end': '17:00', 'break_start': '12:00', 'break_dur': 45, 'work': True},
            'saturday': {'start': '09:00', 'end': '12:00', 'break_start': None, 'break_dur': 0, 'work': True},
            # ... etc
        }
        """
        # 1. Create the parent Policy
        policy = ShiftPolicy.objects.create(
            name=name,
            weekly_target_hours=timedelta(hours=weekly_target_hours)
        )

        # 2. Create the 7 days (ShiftDetail)
        for day_code, _ in WeekdayEnum.choices:
            # Retrieve daily config or apply default values
            cfg = daily_configs.get(day_code, {
                'start': '08:00', 'end': '17:00', 
                'break_start': '12:00', 'break_dur': 45, 
                'work': False # Default to non-working if not specified
            })

            ShiftDetail.objects.create(
                policy=policy,
                weekday=day_code,
                start_time=cfg['start'],
                end_time=cfg['end'],
                break_start_time=cfg['break_start'],
                break_duration=timedelta(minutes=cfg['break_dur']),
                is_working_day=cfg['work']
            )
        
        return policy

    @staticmethod
    @transaction.atomic
    def assign_policy_to_employee(
        employee, 
        policy: ShiftPolicy, 
        start_date: date, 
        end_date: date = None
    ) -> EmploymentScheme:
        """
        Assigns a ShiftPolicy to an employee. 
        Automatically handles overlapping periods by deactivating or adjusting 
        existing schemes.
        """
        # 1. Validation: Ensure start_date is before end_date
        if end_date and start_date >= end_date:
            raise ValidationError(_("Start date must be before end date."))

        # 2. Collision Management:
        # Find any existing schemes that overlap with the new period
        overlap_query = Q(employee=employee, is_active=True)
        if end_date:
            overlap_query &= Q(valid_from__lt=end_date) & (Q(valid_until__gt=start_date) | Q(valid_until__isnull=True))
        else:
            overlap_query &= (Q(valid_until__gt=start_date) | Q(valid_until__isnull=True))

        existing_schemes = EmploymentScheme.objects.filter(overlap_query)

        for scheme in existing_schemes:
            # Logic: If a new policy starts, we close the previous one the day before
            if scheme.valid_from < start_date:
                scheme.valid_until = start_date.replace(day=start_date.day - 1) # Simplified logic
                # Note: In production, use a more robust date subtraction
                scheme.save()
            else:
                # If the new policy completely covers or starts before an old one, 
                # we deactivate the old one to avoid conflicts.
                scheme.is_active = False
                scheme.save()

        # 3. Create the new assignment
        return EmploymentScheme.objects.create(
            employee=employee,
            policy=policy,
            valid_from=start_date,
            valid_until=end_date,
            is_active=True
        )

    @staticmethod
    def get_active_scheme_for_date(employee, target_date: date) -> EmploymentScheme | None:
        """
        Retrieves the EmploymentScheme active for a specific employee on a given date.
        """
        return EmploymentScheme.objects.filter(
            employee=employee,
            is_active=True,
            valid_from__lte=target_date
        ).filter(
            Q(valid_until__gte=target_date) | Q(valid_until__isnull=True)
        ).select_related('policy').first()

    @classmethod
    def get_expected_schedule(cls, employee, target_date: date) -> ShiftDetail | None:
        """
        Retrieves the scheduled planning with Holiday awareness.
        Hierarchy:
        1. Check if the date is a Public Holiday/Company Closing (Global override).
        2. Check for a ShiftAssignment (Specific planning override).
        3. Retrieve the ShiftDetail from the active ShiftPolicy.
        """
        # --- NEW PRIORITY 0: Global Calendar Holidays ---
        # If the day is a holiday in the employee's country, no work is expected.
        # Assuming employee has a 'country_code' field, otherwise use default.
        country_code = getattr(employee, 'country_code', 'CD') 
        if CalendarService.is_non_working_day(target_date, country_code):
            return None

        # --- PRIORITY 1: Specific Override ---
        assignment = ShiftAssignment.objects.filter(
            employee=employee, 
            date=target_date
        ).select_related('shift_detail').first()
        
        if assignment:
            return assignment.shift_detail

        # --- PRIORITY 2: Default Policy ---
        scheme = cls.get_active_scheme_for_date(employee, target_date)
        if not scheme:
            return None

        day_name = target_date.strftime('%A').lower()
        return ShiftDetail.objects.filter(
            policy=scheme.policy,
            weekday=day_name,
            is_working_day=True
        ).first()

    @staticmethod
    def get_weekly_planning(employee, start_date: date):
        """
        Generates a dictionary representing the employee's scheduled 
        planning for the upcoming 7 days.
        """
        planning = []
        for i in range(7):
            current_day = start_date + timedelta(days=i)
            detail = SchedulingService.get_expected_schedule(employee, current_day)
            
            day_info = {
                "date": current_day,
                "is_working": False,
                "shift": None
            }

            if detail:
                day_info.update({
                    "is_working": detail.is_working_day,
                    "start": detail.start_time,
                    "end": detail.end_time,
                    "break_start": detail.break_start_time,
                    "break_limit": detail.break_duration,
                })
            
            planning.append(day_info)
        return planning

    @staticmethod
    def is_working_day(employee, target_date: date) -> bool:
        """
        Simple check to see if an employee is supposed to work on a specific date.
        """
        schedule = SchedulingService.get_expected_schedule(employee, target_date)
        return schedule is not None and schedule.is_working_day


    @staticmethod
    @transaction.atomic
    def apply_rotation(employee, start_date: date, num_weeks: int, weekly_patterns: list[ShiftPolicy]):
        """
        Applies a shift policy rotation to an employee.
        
        Example:
            If weekly_patterns = [Morning_Policy, Afternoon_Policy]
            Week 1 will be assigned Morning_Policy
            Week 2 will be assigned Afternoon_Policy
            Week 3 will return to Morning_Policy, and so on.
        
        weekly_patterns: list of ShiftPolicy objects to rotate through.
        """
        current_date = start_date
        num_patterns = len(weekly_patterns)

        for week_idx in range(num_weeks):
            # Select the policy based on the week index (modulo)
            current_policy = weekly_patterns[week_idx % num_patterns]
            
            # For each day of the week
            for i in range(7):
                day_to_assign = current_date + timedelta(days=i)
                day_name = day_to_assign.strftime('%A').lower()
                
                # Retrieve the corresponding detail from the selected policy
                detail = ShiftDetail.objects.filter(
                    policy=current_policy, 
                    weekday=day_name
                ).first()

                if detail:
                    # Create or update the override (Assignment)
                    ShiftAssignment.objects.update_or_create(
                        employee=employee,
                        date=day_to_assign,
                        defaults={'shift_detail': detail}
                    )
            
            # Move to the next week
            current_date += timedelta(days=7)

    @staticmethod
    @transaction.atomic
    def backfill_rotations(look_ahead_days: int = 30):
        """
        Generates ShiftAssignments for active rotations.
        Optimized with bulk_create and minimized SQL queries.
        """
        # Fetch only active rotations with employee details preloaded
        active_rotations = RotationPattern.objects.filter(is_active=True).select_related('employee')
        today = date.today()
        global_limit = today + timedelta(days=look_ahead_days)

        for rotation in active_rotations:
            # The effective limit is either the look-ahead period or the rotation's end date
            effective_end_limit = global_limit
            if rotation.end_date:
                effective_end_limit = min(global_limit, rotation.end_date)
            
            # Skip if the rotation has already ended relative to today
            if rotation.end_date and rotation.end_date < today:
                continue

            # Fetch already scheduled dates to avoid duplicates and respect manual overrides
            existing_dates = set(
                ShiftAssignment.objects.filter(
                    employee=rotation.employee,
                    date__range=[today, effective_end_limit]
                ).values_list('date', flat=True)
            )

            # Map shift details to memory to avoid redundant queries in the loop
            details_map = {(d.policy_id, d.weekday): d for d in ShiftDetail.objects.filter(
                policy_id__in=rotation.policies, is_working_day=True
            )}

            assignments_to_create = []
            current_day = today

        while current_day <= effective_end_limit:
            # Generate only if:
            # 1. The date is not already scheduled (respect manual changes)
            # 2. The date is within the rotation's start date
            if current_day not in existing_dates and current_day >= rotation.start_date:
                
                weeks_diff = (current_day - rotation.start_date).days // 7
                policy_idx = weeks_diff % len(rotation.policies)
                policy_id = rotation.policies[policy_idx]
                day_name = current_day.strftime('%A').lower()

                detail = details_map.get((policy_id, day_name))
                if detail:
                    assignments_to_create.append(
                        ShiftAssignment(
                            employee=rotation.employee,
                            date=current_day,
                            shift_detail=detail
                        )
                    )
            
            current_day += timedelta(days=1)
        
        if assignments_to_create:
            ShiftAssignment.objects.bulk_create(assignments_to_create)

    @staticmethod
    def count_working_days_for_employee(employee, start_date: date, end_date: date) -> int:
        """
        Calculates the exact number of days an employee was supposed to work
        between two dates, accounting for their specific shift policy and holidays.
        """
        if start_date > end_date:
            return 0

        count = 0
        curr = start_date
        while curr <= end_date:
            if SchedulingService.is_working_day(employee, curr):
                count += 1
            curr += timedelta(days=1)
        return count

    @staticmethod
    def get_working_days_by_year(employee, start_date: date, end_date: date) -> dict[int, int]:
        """
        Returns a breakdown of working days per calendar year.
        Crucial for leave requests spanning across December and January.
        Example: {2025: 3, 2026: 2}
        """
        results = {}
        if start_date > end_date:
            return results

        curr = start_date
        while curr <= end_date:
            if SchedulingService.is_working_day(employee, curr):
                year = curr.year
                results[year] = results.get(year, 0) + 1
            curr += timedelta(days=1)
        return results

