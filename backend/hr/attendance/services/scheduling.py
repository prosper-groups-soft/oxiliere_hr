from __future__ import annotations
from datetime   import date, timedelta
from django.db  import transaction
from django.db.models import Q
from django.core.exceptions   import ValidationError
from django.utils.translation import gettext_lazy as _

from hr.enums import WeekdayEnum
from hr.calendar.services import CalendarService

from hr.attendance.models import (
    ShiftPolicy, 
    ShiftDetail, 
    EmploymentScheme,
    ShiftAssignment,
    RotationPattern,
)
# Integration of caching layers
from .cache import AttendanceCacheService


class SchedulingService:
    """
    Service responsible for managing employee work schedules, policy assignments,
    and calculating expected working days with high-performance caching.
    """
    
    @staticmethod
    @transaction.atomic
    def create_full_policy(name: str, weekly_target_hours: int, daily_configs: dict):
        """
        Creates a comprehensive ShiftPolicy along with its 7-day ShiftDetail configuration.
        daily_configs should be a dictionary such as:
        {
            'monday': {'start': '08:00', 'end': '17:00', 'break_start': '12:00', 'break_dur': 45, 'work': True},
            'saturday': {'start': '09:00', 'end': '12:00', 'break_start': None, 'break_dur': 0, 'work': True},
            # ... etc
        }
        Logic:
        1. Persists the master ShiftPolicy with the total target hours.
        2. Iterates through all possible weekdays defined in WeekdayEnum.
        3. Applies custom daily configurations (start/end/break) or defaults to a 
           non-working day if the day is missing from daily_configs.
        """
        # 1. Create the parent Policy
        policy = ShiftPolicy.objects.create(
            name=name,
            weekly_target_hours=timedelta(hours=weekly_target_hours)
        )

        # 2. Create the 7 days (ShiftDetail)
        for day_code, _ in WeekdayEnum.choices:
            # Fallback to default parameters if the day is not in the input config
            cfg = daily_configs.get(day_code, {
                'start': '08:00', 'end': '17:00', 
                'break_start': '12:00', 'break_dur': 60, 
                'work': False 
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
        Links an employee to a ShiftPolicy for a specific time period.
        
        Overlap Management Logic:
        - Prevents date inconsistency (start must be before end).
        - Identifies existing active schemes that conflict with the new date range.
        - Shortens previous schemes to end the day before the new one starts.
        - Deactivates older schemes that are completely superseded by the new one.
        - Clears the employee's attendance cache to ensure new policy rules take immediate effect.
        """
        if end_date and start_date >= end_date:
            raise ValidationError(_("Start date must be before end date."))

        # Identify overlapping active schemes
        overlap_query = Q(employee=employee, is_active=True)
        if end_date:
            overlap_query &= Q(valid_from__lt=end_date) & (Q(valid_until__gt=start_date) | Q(valid_until__isnull=True))
        else:
            overlap_query &= (Q(valid_until__gt=start_date) | Q(valid_until__isnull=True))

        existing_schemes = EmploymentScheme.objects.filter(overlap_query)

        for scheme in existing_schemes:
            if scheme.valid_from < start_date:
                # Truncate existing scheme to avoid overlap
                scheme.valid_until = start_date - timedelta(days=1)
                scheme.save()
            else:
                # Deactivate scheme if it starts after the new one
                scheme.is_active = False
                scheme.save()

        # INVALIDATION: Ensure stale schedule data is removed from Redis
        AttendanceCacheService.clear_employee_cache(employee)

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
        Finds the contractually active EmploymentScheme for a given date.
        Uses select_related('policy') to minimize SQL JOINs when accessing policy details.
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
        Determines what an employee is supposed to do on a specific date based on a 3-tier hierarchy.
        
        Priority Hierarchy:
        0. Global Calendar: Check if it's a Public Holiday (overrides everything).
        1. Manual Override: Check for a specific ShiftAssignment (specific day planning).
        2. Default Policy: Retrieve the standard ShiftDetail from the active policy.
        
        Performance: Uses cached shift details for tier 2 to avoid repeated DB scans.
        """
        # Tier 0: Public Holidays / Company Closures
        country_code = getattr(employee, 'nationality', 'CD') 
        if CalendarService.is_non_working_day(target_date, country_code):
            return None

        # Tier 1: Manual Assignment / Single Day Override
        assignment = ShiftAssignment.objects.filter(
            employee=employee, 
            date=target_date
        ).select_related('shift_detail').first()
        
        if assignment:
            return assignment.shift_detail

        # Tier 2: Recurring Shift Policy
        scheme = cls.get_active_scheme_for_date(employee, target_date)
        if not scheme:
            return None

        # CACHE ACCESS: Retrieve all 7 days of the policy from Redis at once
        day_name = target_date.strftime('%A').lower()
        details = AttendanceCacheService.get_shift_details(scheme.policy)
        
        # Match the current day in the cached list using Python (O(1) complexity)
        return next((d for d in details if d.weekday == day_name and d.is_working_day), None)

    @staticmethod
    def get_weekly_planning(employee, start_date: date):
        """
        Compiles a 7-day schedule view for an employee starting from a given date.
        Returns a structured list of dictionaries for UI/API consumption.
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
        Boolean helper to quickly verify if an employee is required to work on a specific date.
        """
        schedule = SchedulingService.get_expected_schedule(employee, target_date)
        return schedule is not None and schedule.is_working_day
    
    @staticmethod
    @transaction.atomic
    def apply_rotation(employee, start_date: date, num_weeks: int, weekly_patterns: list[ShiftPolicy]):
        """
        Applies a shift policy rotation to an employee by generating ShiftAssignments.
                
        Example:
            If weekly_patterns = [Morning_Policy, Afternoon_Policy]
            Week 1 will be assigned Morning_Policy
            Week 2 will be assigned Afternoon_Policy
            Week 3 will return to Morning_Policy, and so on.
        
        weekly_patterns: list of ShiftPolicy objects to rotate through.
        
        Optimizations:
        1. Pre-fetches all ShiftDetails for all policies in the rotation using the cache service.
        2. Uses bulk_create/update logic instead of individual database hits.
        3. Clears employee cache once at the end.
        """
        num_patterns = len(weekly_patterns)
        
        # 1. Pre-fetch all details for all involved policies in one go (via Cache)
        # We create a map {(policy_id, weekday): detail} for O(1) access
        details_map = {}
        for policy in weekly_patterns:
            policy_details = AttendanceCacheService.get_shift_details(policy)
            for d in policy_details:
                details_map[(policy.id, d.weekday)] = d

        assignments_to_sync = []
        current_date = start_date

        for week_idx in range(num_weeks):
            current_policy = weekly_patterns[week_idx % num_patterns]
            
            for i in range(7):
                day_to_assign = current_date + timedelta(days=i)
                day_name = day_to_assign.strftime('%A').lower()
                
                detail = details_map.get((current_policy.id, day_name))
                if detail:
                    # We use ShiftAssignment objects for bulk operations
                    assignments_to_sync.append(
                        ShiftAssignment(
                            employee=employee,
                            date=day_to_assign,
                            shift_detail=detail
                        )
                    )
            
            current_date += timedelta(days=7)

        # 2. Sync with database: Delete existing in range and bulk create new ones
        # This is often faster than update_or_create in a loop for large rotations
        end_date = start_date + timedelta(weeks=num_weeks)
        ShiftAssignment.objects.filter(
            employee=employee, 
            date__range=[start_date, end_date - timedelta(days=1)]
        ).delete()
        
        ShiftAssignment.objects.bulk_create(assignments_to_sync)

        # 3. Invalidate cache once
        AttendanceCacheService.clear_employee_cache(employee)

    @staticmethod
    @transaction.atomic
    def backfill_rotations(look_ahead_days: int = 30):
        """
        System-wide task: Generates ShiftAssignments for all active rotations.
        
        Optimizations:
        1. Uses select_related to avoid N+1 on employees.
        2. Moves the day-loop inside the rotation loop (corrected logic).
        3. Uses the Cache Service to avoid hitting ShiftDetail table repeatedly.
        """
        active_rotations = RotationPattern.objects.filter(is_active=True).select_related('employee')
        today = date.today()
        global_limit = today + timedelta(days=look_ahead_days)

        for rotation in active_rotations:
            # Determine processing range
            effective_end_limit = min(global_limit, rotation.end_date) if rotation.end_date else global_limit
            if effective_end_limit < today:
                continue

            # Fetch existing dates to respect manual overrides (we don't overwrite them)
            existing_dates = set(
                ShiftAssignment.objects.filter(
                    employee=rotation.employee,
                    date__range=[today, effective_end_limit]
                ).values_list('date', flat=True)
            )

            # Pre-fetch details for this rotation's policies via Cache
            details_map = {}
            for p_id in rotation.policies:
                policy_details = AttendanceCacheService.get_shift_details(p_id)
                for d in policy_details:
                    if d.is_working_day:
                        details_map[(p_id, d.weekday)] = d

            assignments_to_create = []
            current_day = today

            # Loop through days for this specific rotation
            while current_day <= effective_end_limit:
                if current_day not in existing_dates and current_day >= rotation.start_date:
                    # Rotation logic: which week are we in?
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
            
            # Bulk save for this employee
            if assignments_to_create:
                ShiftAssignment.objects.bulk_create(assignments_to_create)
                # Invalidate this employee's cache
                AttendanceCacheService.clear_employee_cache(rotation.employee)

    @staticmethod
    def count_working_days_for_employee(employee, start_date: date, end_date: date) -> int:
        """
        Counts the total number of expected working days within a date range.
        
        OPTIMIZATION - Bulk Fetching:
        Instead of running 1 SQL query per day in a loop (N+1 problem), this method
        fetches all manual overrides for the entire period in a single query and
        processes the logic in-memory.
        """
        if start_date > end_date:
            return 0

        # Pre-fetch all overrides for the period to avoid DB hits inside the loop
        assignments_map = {
            a.date: a.shift_detail 
            for a in ShiftAssignment.objects.filter(
                employee=employee, date__range=[start_date, end_date]
            ).select_related('shift_detail')
        }

        count = 0
        curr = start_date
        while curr <= end_date:
            # Use the optimized internal helper to process each day
            if SchedulingService._is_working_day_optimized(employee, curr, assignments_map):
                count += 1
            curr += timedelta(days=1)
        return count

    @staticmethod
    def _is_working_day_optimized(employee, target_date: date, assignments_map: dict) -> bool:
        """
        Internal high-performance version of is_working_day.
        Accepts a pre-fetched 'assignments_map' to eliminate database queries during 
        range-based calculations (e.g., monthly stats or leave requests).
        """
        # Check Holiday first (Tier 0)
        country_code = getattr(employee, 'nationality', 'CD') 
        if CalendarService.is_non_working_day(target_date, country_code):
            return False

        # Check pre-fetched assignments (Tier 1)
        if target_date in assignments_map:
            return assignments_map[target_date].is_working_day

        # Check Active Policy (Tier 2) via Cache
        scheme = SchedulingService.get_active_scheme_for_date(employee, target_date)
        if not scheme:
            return False

        day_name = target_date.strftime('%A').lower()
        details = AttendanceCacheService.get_shift_details(scheme.policy)
        return any(d.weekday == day_name and d.is_working_day for d in details)

    @staticmethod
    def get_working_days_by_year(employee, start_date: date, end_date: date) -> dict[int, int]:
        """
        Aggregates working days per calendar year for a given range.
        Useful for calculating leave balances when a request spans across two years.
        Example output: {2025: 5, 2026: 2}
        """
        results = {}
        if start_date > end_date:
            return results

        curr = start_date
        while curr <= end_date:
            # Note: For even better performance on very long ranges, this could be 
            # further optimized to use the assignments_map logic.
            if SchedulingService.is_working_day(employee, curr):
                year = curr.year
                results[year] = results.get(year, 0) + 1
            curr += timedelta(days=1)
        return results

