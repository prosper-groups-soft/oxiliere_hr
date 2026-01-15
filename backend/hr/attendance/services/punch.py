from __future__ import annotations
from datetime import datetime, timedelta
from django.db import transaction
from hr.attendance.models import (
    TimePunch, 
    TimeSheet, 
    DailyRegister
)
from hr.enums import PunchType


class PunchService:
    """
    Service responsible for recording and managing raw time punches.
    Handles the logic of connecting punches to the correct Daily Timesheets.
    """

    @staticmethod
    @transaction.atomic
    def record_punch(
        employee, 
        timestamp: datetime, 
        punch_type: PunchType = PunchType.WORK, 
        is_manual: bool = False
    ) -> TimePunch:
        """
        Records a clock-in or clock-out event.
        Automatically resolves which TimeSheet the punch belongs to.
        """
        # 1. Identify the target TimeSheet (considering Night Shifts)
        timesheet = PunchService.get_effective_timesheet_for_punch(employee, timestamp)

        # 2. Logic: If there is an open punch (no end_at), close it before opening a new one
        open_punch = TimePunch.objects.filter(
            timesheet=timesheet, 
            end_at__isnull=True
        ).order_by('-start_at').first()

        if open_punch:
            # If the user is clocking in the same type twice, we just update the end_at
            # or if they are switching (Work -> Break), we close the previous segment.
            open_punch.end_at = timestamp
            open_punch.save()
            
            # If the action was just to "Clock-out", we stop here.
            # In a real system, you might want a logic to decide if a new punch starts.
            # Here we assume a new punch is created only if it's a new status.

        # 3. Create the new punch segment
        return TimePunch.objects.create(
            timesheet=timesheet,
            punch_type=punch_type,
            start_at=timestamp,
            is_manual_entry=is_manual
        )

    @staticmethod
    def get_effective_timesheet_for_punch(employee, timestamp: datetime) -> TimeSheet:
        """
        Determines the correct TimeSheet for a punch.
        If a punch occurs early in the morning (e.g., 02:00 AM), it checks if it 
        belongs to a Night Shift started the previous day.
        """
        target_date = timestamp.date()
        
        # Check if there's an ongoing sheet from yesterday (Night Shift case)
        yesterday = target_date - timedelta(days=1)
        yesterday_sheet = TimeSheet.objects.filter(
            employee=employee, 
            register__date=yesterday
        ).first()

        if yesterday_sheet:
            # If yesterday had a night shift policy and there is an open punch there
            has_open_punch = TimePunch.objects.filter(
                timesheet=yesterday_sheet, 
                end_at__isnull=True
            ).exists()
            
            if has_open_punch:
                return yesterday_sheet

        # Otherwise, get or create the TimeSheet for today
        # Note: In a production environment, use a DailyRegister service to get_or_create
        register, _ = DailyRegister.objects.get_or_create(date=target_date)
        timesheet, _ = TimeSheet.objects.get_or_create(
            employee=employee, 
            register=register
        )
        return timesheet

    @staticmethod
    def adjust_punch(
        punch: TimePunch, 
        start_at: datetime = None, 
        end_at: datetime = None
    ) -> TimePunch:
        """
        Manually adjust a punch segment. Forces the manual entry flag.
        """
        if start_at:
            punch.start_at = start_at
        if end_at:
            punch.end_at = end_at
            
        punch.is_manual_entry = True
        punch.save()
        return punch

