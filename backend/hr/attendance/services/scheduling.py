from __future__ import annotations
from collections import defaultdict
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
    ShiftPeriod,
    EmploymentScheme,
    ShiftAssignment,
    RotationPattern,
)
# Integration of caching layers
from .cache import AttendanceCacheService

from hr.calendar.models import CalendarEvent
from hr.calendar.enums import CalendarEventStatus, CalendarEventRecurrence, CalendarEventType


class SchedulingService:
    """ Manages work schedules, policy assignments, and working day calculations. """
    
    @staticmethod
    def _sync_detail_periods(detail: ShiftDetail, cfg: dict | None):
        """
        Synchronizes the related ShiftPeriod records of a ShiftDetail
        and updates the aggregate/derived fields on ShiftDetail.
        """
        # Delete existing periods for this day
        detail.periods.all().delete()

        if cfg is None or not cfg.get("work", False):
            # Non-working day
            detail.start_time = "08:00"
            detail.end_time = "17:00"
            detail.break_start_time = None
            detail.break_duration = timedelta(minutes=0)
            detail.is_working_day = False
            detail.save()
            return

        periods_data = cfg.get("periods", [])
        
        # Save new periods
        for p_cfg in periods_data:
            ShiftPeriod.objects.create(
                shift_detail=detail,
                name=p_cfg.get("name", ""),
                period_type=p_cfg.get("period_type", "WORK"),
                start_time=p_cfg["start_time"],
                end_time=p_cfg["end_time"]
            )

        # Compute aggregate start_time, end_time, break_start_time, break_duration
        work_periods = [p for p in periods_data if p.get("period_type", "WORK") == "WORK"]
        break_periods = [p for p in periods_data if p.get("period_type", "WORK") == "BREAK"]

        if work_periods:
            work_periods.sort(key=lambda x: x["start_time"])
            detail.start_time = work_periods[0]["start_time"]
            detail.end_time = work_periods[-1]["end_time"]
        else:
            detail.start_time = "08:00"
            detail.end_time = "17:00"

        if break_periods:
            break_periods.sort(key=lambda x: x["start_time"])
            detail.break_start_time = break_periods[0]["start_time"]
            
            # Compute total break duration
            total_break_min = 0
            for b in break_periods:
                try:
                    sh, sm = map(int, b["start_time"].split(":")[:2])
                    eh, em = map(int, b["end_time"].split(":")[:2])
                    duration_min = (eh * 60 + em) - (sh * 60 + sm)
                    if duration_min > 0:
                        total_break_min += duration_min
                except Exception:
                    pass
            detail.break_duration = timedelta(minutes=total_break_min)
        else:
            detail.break_start_time = None
            detail.break_duration = timedelta(minutes=0)

        detail.is_working_day = True
        detail.save()

    @staticmethod
    @transaction.atomic
    def create_full_policy(name: str, weekly_target_hours: int, daily_configs: dict, description: str = ""):
        """
        Creates a comprehensive ShiftPolicy along with its 7-day ShiftDetail configuration.
        """
        # 1. Create the parent Policy
        policy = ShiftPolicy.objects.create(
            name=name,
            description=description,
            weekly_target_hours=weekly_target_hours
        )

        # 2. Create the 7 days (ShiftDetail) and sync their periods
        for day_code, _ in WeekdayEnum.choices:
            cfg = daily_configs.get(day_code, None)

            detail = ShiftDetail.objects.create(
                policy=policy,
                weekday=day_code,
                start_time="08:00",
                end_time="17:00",
                break_start_time=None,
                break_duration=timedelta(minutes=0),
                is_working_day=False,
            )
            
            SchedulingService._sync_detail_periods(detail, cfg)
        
        return policy

    @staticmethod
    @transaction.atomic
    def delete_policy(policy: ShiftPolicy):
        """ Hard-deletes a ShiftPolicy and its related details/periods. """
        policy.delete()

    @staticmethod
    @transaction.atomic
    def delete_assignment(assignment: EmploymentScheme):
        """ Hard-deletes an EmploymentScheme (policy assignment). """
        assignment.delete()

    @staticmethod
    @transaction.atomic
    def update_assignment(assignment: EmploymentScheme, **fields):
        """ Updates an existing assignment with only the provided fields.

        Special behaviour:
        - If override_policy_id is explicitly set to None, ALL override fields
          are cleared (dates, recurrence, etc.).
        - If policy_id is provided, the ShiftPolicy is looked up and set.
        - Other None fields are ignored (not updated).
        """
        # Detect explicit removal of the override
        if 'override_policy_id' in fields and fields['override_policy_id'] is None:
            assignment.override_policy = None
            assignment.override_valid_from = None
            assignment.override_valid_until = None
            assignment.override_recurrence = 'NONE'
            assignment.override_recurrence_count = None

        # Update scalar fields with correct model field names
        field_map = {
            'policy_id': 'policy_id',
            'start_date': 'valid_from',
            'end_date': 'valid_until',
            'recurrence': 'recurrence',
            'override_valid_from': 'override_valid_from',
            'override_valid_until': 'override_valid_until',
            'override_recurrence': 'override_recurrence',
            'override_recurrence_count': 'override_recurrence_count',
        }
        for input_field, model_field in field_map.items():
            if input_field in fields:
                setattr(assignment, model_field, fields[input_field])

        # Handle override_policy by id (validate existence)
        if 'override_policy_id' in fields and fields['override_policy_id'] is not None:
            try:
                assignment.override_policy = ShiftPolicy.objects.get(id=fields['override_policy_id'])
            except ShiftPolicy.DoesNotExist:
                raise ValidationError(f"Override policy {fields['override_policy_id']} not found")

        # Handle base policy_id by id (validate existence, same as override)
        if 'policy_id' in fields and fields['policy_id'] is not None:
            try:
                assignment.policy = ShiftPolicy.objects.get(id=fields['policy_id'])
            except ShiftPolicy.DoesNotExist:
                raise ValidationError(f"Policy {fields['policy_id']} not found")

        assignment.save()
        AttendanceCacheService.clear_employee_cache(assignment.employee)
        return assignment

    @staticmethod
    def list_assignments():
        """ Returns all active EmploymentSchemes with related employee and policy. """
        return EmploymentScheme.objects.filter(
            is_active=True
        ).select_related('employee', 'policy').order_by('-valid_from')

    @staticmethod
    @transaction.atomic
    def update_policy_details(policy: ShiftPolicy, daily_configs: dict):
        """
        Updates the 7-day ShiftDetail configuration for an existing ShiftPolicy.
        Updates the fields of the existing ShiftDetail records instead of deleting them,
        to prevent cascading deletion of ShiftAssignments.
        """
        from hr.enums import WeekdayEnum
        for day_code, _ in WeekdayEnum.choices:
            cfg = daily_configs.get(day_code, None)

            detail, created = ShiftDetail.objects.get_or_create(
                policy=policy,
                weekday=day_code,
                defaults={
                    "start_time": "08:00",
                    "end_time": "17:00",
                    "break_start_time": None,
                    "break_duration": timedelta(minutes=0),
                    "is_working_day": False,
                }
            )

            SchedulingService._sync_detail_periods(detail, cfg)

    @staticmethod
    @transaction.atomic
    def assign_policy_to_employee(
        employee, 
        policy: ShiftPolicy, 
        start_date: date, 
        end_date: date = None,
        recurrence: str = "NONE",
        override_policy: ShiftPolicy = None,
        override_valid_from: date = None,
        override_valid_until: date = None,
        override_recurrence: str = "NONE",
        override_recurrence_count: int = None,
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
            recurrence=recurrence,
            is_active=True,
            override_policy=override_policy,
            override_valid_from=override_valid_from,
            override_valid_until=override_valid_until,
            override_recurrence=override_recurrence or "NONE",
            override_recurrence_count=override_recurrence_count,
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

        day_name = target_date.strftime('%A').upper()
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
                day_name = day_to_assign.strftime('%A').upper()
                
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
                    day_name = current_day.strftime('%A').upper()

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

    # ------------------------------------------------------------------
    # Working Days Breakdown (detailed, with reasons)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_holiday_map(start_date: date, end_date: date, country_code: str) -> dict[date, dict]:
        """
        Builds a map of date → {event_name, event_type} for all non-workable
        CalendarEvents within the given range.
        Handles both one-time and yearly recurring events.
        """
        holiday_map: dict[date, dict] = {}

        events = CalendarEvent.objects.filter(
            Q(country_code=country_code) | Q(country_code__isnull=True),
            is_workable=False,
            status=CalendarEventStatus.APPROVED
        )

        for event in events:
            evt_info = {
                'name': event.name,
                'event_type': event.event_type,
            }

            if event.recurrent == CalendarEventRecurrence.YEARLY:
                # Expand across all years in range
                for year in range(start_date.year, end_date.year + 1):
                    try:
                        ev_start = date(year, event.start_date.month, event.start_date.day)
                        duration = (event.end_date - event.start_date).days if event.end_date else 0
                        ev_end = ev_start + timedelta(days=duration)

                        curr_h = max(start_date, ev_start)
                        while curr_h <= min(end_date, ev_end):
                            holiday_map[curr_h] = evt_info
                            curr_h += timedelta(days=1)
                    except ValueError:
                        continue
            else:
                # One-time event
                ev_end = event.end_date or event.start_date
                curr_h = max(start_date, event.start_date)
                while curr_h <= min(end_date, ev_end):
                    holiday_map[curr_h] = evt_info
                    curr_h += timedelta(days=1)

        return holiday_map

    @staticmethod
    def get_working_days_breakdown(employee, start_date: date, end_date: date) -> dict:
        """
        Returns a detailed day-by-day breakdown of working status for a date range.

        Returns:
        {
            'working_days': int,       # Days that are actually worked
            'calendar_days': int,      # Total days in range (inclusive)
            'excluded': {
                'public_holidays': [str],   # Dates excluded due to public holidays
                'closures': [str],          # Dates excluded due to company closures
                'non_working_policy_days': [str],  # Dates off per shift policy
                'total_excluded': int,      # Sum of all excluded
            },
            'day_details': [{
                'date': str,             # ISO date YYYY-MM-DD
                'day_name': str,         # e.g. 'Monday'
                'is_working': bool,
                'reason': str,           # 'working' | 'public_holiday' | 'company_closure' | 'non_working_day' | 'no_scheme'
                'event_type': str | None,   # CalendarEventType or None
                'event_name': str | None,   # Name of the holiday/closure
                'start_time': str | None,   # HH:MM
                'end_time': str | None,     # HH:MM
            }]
        }
        """
        if start_date > end_date:
            return {
                'working_days': 0,
                'calendar_days': 0,
                'excluded': {
                    'public_holidays': [],
                    'closures': [],
                    'non_working_policy_days': [],
                    'total_excluded': 0,
                },
                'day_details': [],
            }

        country_code = getattr(employee, 'nationality', 'CD')
        calendar_days = (end_date - start_date).days + 1

        # Pre-fetch holidays
        holiday_map = SchedulingService._build_holiday_map(start_date, end_date, country_code)

        # Pre-fetch ShiftAssignments
        assignments_map = {
            a.date: a.shift_detail
            for a in ShiftAssignment.objects.filter(
                employee=employee, date__range=[start_date, end_date]
            ).select_related('shift_detail')
        }

        working_days = 0
        day_details = []
        excluded = {
            'public_holidays': [],
            'closures': [],
            'non_working_policy_days': [],
        }

        curr = start_date
        while curr <= end_date:
            entry = {
                'date': curr.isoformat(),
                'day_name': curr.strftime('%A').upper(),
                'is_working': False,
                'reason': '',
                'event_type': None,
                'event_name': None,
                'start_time': None,
                'end_time': None,
            }

            # Tier 0: Public Holidays / Company Closures
            if curr in holiday_map:
                evt = holiday_map[curr]
                entry['event_name'] = evt['name']
                entry['event_type'] = evt['event_type']

                if evt['event_type'] == CalendarEventType.PUBLIC_HOLIDAY:
                    entry['reason'] = 'public_holiday'
                    excluded['public_holidays'].append(curr.isoformat())
                elif evt['event_type'] == CalendarEventType.COMPANY_EVENT:
                    entry['reason'] = 'company_closure'
                    excluded['closures'].append(curr.isoformat())
                else:
                    # Any other non-workable event
                    entry['reason'] = 'public_holiday'
                    excluded['public_holidays'].append(curr.isoformat())

                day_details.append(entry)
                curr += timedelta(days=1)
                continue

            # Tier 1: Manual Override (ShiftAssignment)
            if curr in assignments_map:
                sd = assignments_map[curr]
                if sd.is_working_day:
                    entry['is_working'] = True
                    entry['reason'] = 'working'
                    entry['start_time'] = str(sd.start_time)[:5]
                    entry['end_time'] = str(sd.end_time)[:5]
                    working_days += 1
                else:
                    entry['reason'] = 'non_working_day'
                    excluded['non_working_policy_days'].append(curr.isoformat())

                day_details.append(entry)
                curr += timedelta(days=1)
                continue

            # Tier 2: Standard Policy (EmploymentScheme)
            scheme = SchedulingService.get_active_scheme_for_date(employee, curr)
            if not scheme:
                entry['reason'] = 'no_scheme'
                excluded['non_working_policy_days'].append(curr.isoformat())
                day_details.append(entry)
                curr += timedelta(days=1)
                continue

            day_name = curr.strftime('%A').upper()
            details = AttendanceCacheService.get_shift_details(scheme.policy)
            match = next((d for d in details if d.weekday == day_name), None)

            if match and match.is_working_day:
                entry['is_working'] = True
                entry['reason'] = 'working'
                entry['start_time'] = str(match.start_time)[:5]
                entry['end_time'] = str(match.end_time)[:5]
                working_days += 1
            else:
                entry['reason'] = 'non_working_day'
                excluded['non_working_policy_days'].append(curr.isoformat())

            day_details.append(entry)
            curr += timedelta(days=1)

        excluded['total_excluded'] = calendar_days - working_days

        return {
            'working_days': working_days,
            'calendar_days': calendar_days,
            'excluded': excluded,
            'day_details': day_details,
        }

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

        day_name = target_date.strftime('%A').upper()
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

