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
    """ Manages work schedules, policy assignments, and working day calculations. """
    
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
        """ Assigns a shift policy to an employee, automatically resolving date overlaps. """
        if end_date and start_date >= end_date:
            raise ValidationError(_("Start date must be before end date."))

        overlap_query = Q(employee=employee, is_active=True)
        if end_date:
            overlap_query &= Q(valid_from__lt=end_date) & (Q(valid_until__gt=start_date) | Q(valid_until__isnull=True))
        else:
            overlap_query &= (Q(valid_until__gt=start_date) | Q(valid_until__isnull=True))

        existing_schemes = EmploymentScheme.objects.filter(overlap_query)

        for scheme in existing_schemes:
            if scheme.valid_from < start_date:
                scheme.valid_until = start_date - timedelta(days=1)
                scheme.save()
            else:
                scheme.is_active = False
                scheme.save()

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
        """ Retrieves the active employment scheme for a specific date. """
        return EmploymentScheme.objects.filter(
            employee=employee,
            is_active=True,
            valid_from__lte=target_date
        ).filter(
            Q(valid_until__gte=target_date) | Q(valid_until__isnull=True)
        ).select_related('policy').first()

    @classmethod
    def get_expected_schedule(cls, employee, target_date: date) -> ShiftDetail | None:
        """ Determines the expected work schedule using calendar settings and manual overrides. """
        # Tier 0: Public Holidays
        country_code = getattr(employee, 'nationality', 'CD') 
        if CalendarService.is_non_working_day(target_date, country_code):
            return None

        # Tier 1: Manual Overrides
        assignment = ShiftAssignment.objects.filter(
            employee=employee, 
            date=target_date
        ).select_related('shift_detail').first()
        
        if assignment:
            return assignment.shift_detail

        # Tier 2: Standard Policy
        scheme = cls.get_active_scheme_for_date(employee, target_date)
        if not scheme:
            return None

        day_name = target_date.strftime('%A').lower()
        details = AttendanceCacheService.get_shift_details(scheme.policy)
        
        return next((d for d in details if d.weekday == day_name and d.is_working_day), None)

    @staticmethod
    def get_weekly_planning(employee, start_date: date):
        """ Generates a 7-day schedule overview for an employee. """
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
        """ Checks if an employee is scheduled to work on a specific date. """
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
        """
        num_patterns = len(weekly_patterns)
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
                    assignments_to_sync.append(
                        ShiftAssignment(
                            employee=employee,
                            date=day_to_assign,
                            shift_detail=detail
                        )
                    )
            
            current_date += timedelta(days=7)

        end_date = start_date + timedelta(weeks=num_weeks)
        ShiftAssignment.objects.filter(
            employee=employee, 
            date__range=[start_date, end_date - timedelta(days=1)]
        ).delete()
        
        ShiftAssignment.objects.bulk_create(assignments_to_sync)
        AttendanceCacheService.clear_employee_cache(employee)

    @staticmethod
    @transaction.atomic
    def backfill_rotations(look_ahead_days: int = 30):
        """ Automated task to populate shift assignments for active rotations. """
        active_rotations = RotationPattern.objects.filter(is_active=True).select_related('employee')
        today = date.today()
        global_limit = today + timedelta(days=look_ahead_days)

        for rotation in active_rotations:
            effective_end_limit = min(global_limit, rotation.end_date) if rotation.end_date else global_limit
            if effective_end_limit < today:
                continue

            existing_dates = set(
                ShiftAssignment.objects.filter(
                    employee=rotation.employee,
                    date__range=[today, effective_end_limit]
                ).values_list('date', flat=True)
            )

            details_map = {}
            for p_id in rotation.policies:
                policy_details = AttendanceCacheService.get_shift_details(p_id)
                for d in policy_details:
                    if d.is_working_day:
                        details_map[(p_id, d.weekday)] = d

            assignments_to_create = []
            current_day = today

            while current_day <= effective_end_limit:
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
                AttendanceCacheService.clear_employee_cache(rotation.employee)

    @staticmethod
    def count_working_days_for_employee(employee, start_date: date, end_date: date) -> int:
        """ Calculates total working days within a date range using optimized lookups. """
        if start_date > end_date:
            return 0

        assignments_map = {
            a.date: a.shift_detail 
            for a in ShiftAssignment.objects.filter(
                employee=employee, date__range=[start_date, end_date]
            ).select_related('shift_detail')
        }

        count = 0
        curr = start_date
        while curr <= end_date:
            if SchedulingService._is_working_day_optimized(employee, curr, assignments_map):
                count += 1
            curr += timedelta(days=1)
        return count

    @staticmethod
    def _is_working_day_optimized(employee, target_date: date, assignments_map: dict) -> bool:
        """ Optimized internal check for working days using pre-fetched data. """
        country_code = getattr(employee, 'nationality', 'CD') 
        if CalendarService.is_non_working_day(target_date, country_code):
            return False

        if target_date in assignments_map:
            return assignments_map[target_date].is_working_day

        scheme = SchedulingService.get_active_scheme_for_date(employee, target_date)
        if not scheme:
            return False

        day_name = target_date.strftime('%A').lower()
        details = AttendanceCacheService.get_shift_details(scheme.policy)
        return any(d.weekday == day_name and d.is_working_day for d in details)

    @staticmethod
    def get_working_days_by_year(employee, start_date: date, end_date: date) -> dict[int, int]:
        """ Aggregates working days per year for multi-year periods. """
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

