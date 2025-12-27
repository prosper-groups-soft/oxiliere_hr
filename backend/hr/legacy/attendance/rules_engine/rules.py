from datetime import timedelta
from core.rules_engine import BaseRule, PreconditionFailedError
from core.rules_engine import BaseRule, RuleResult
from hr.attendance.enums import AttendanceStatus


class AbsenceRule(BaseRule):
    """
    Determine ABSENT / EXCUSED status based on TimeBlocks and leave.
    """
    def evaluate(self, context) -> RuleResult:
        entry = context.attendance_entry
        # No TimeBlocks
        if not context.time_blocks:
            if entry.leave:
                entry.status = AttendanceStatus.EXCUSED.value
                return RuleResult(passed=True, message="Marked as EXCUSED", data={"status": entry.status})
            else:
                entry.status = AttendanceStatus.ABSENT.value
                return RuleResult(passed=True, message="Marked as ABSENT", data={"status": entry.status})

        # TimeBlocks exist => normal calculation, defer to next rules
        return RuleResult(passed=True, message="Attendance present, continue evaluation")


class NoTimeBlocksRule(BaseRule):
    """
    If the AttendanceEntry has no TimeBlock:
        - EXCUSED if leave exists
        - ABSENT otherwise
    """

    def evaluate(self, context):
        entry = context.entry
        if not entry.time_blocks.exists():
            if entry.leave:
                entry.status = AttendanceStatus.EXCUSED.value
                return {'passed': True, 'message': 'Marked EXCUSED due to leave', 'data': {}}
            else:
                entry.status = AttendanceStatus.ABSENT.value
                return {'passed': True, 'message': 'Marked ABSENT due to no time blocks', 'data': {}}
        return {'passed': True, 'message': 'TimeBlocks exist', 'data': {}}


class ComputeWorkedHoursRule(BaseRule):
    """
    Computes total worked, break, and paid time based on TimeBlocks.
    """

    def evaluate(self, context):
        entry = context.entry
        if not entry.time_blocks.exists():
            raise PreconditionFailedError("Cannot compute hours: no TimeBlocks found.")

        total_worked = timedelta(0)
        total_break = timedelta(0)
        total_paid = timedelta(0)

        for block in entry.time_blocks.all():
            if not block.duration:
                block.duration = timedelta(
                    hours=block.end_time.hour - block.start_time.hour,
                    minutes=block.end_time.minute - block.start_time.minute
                )
            if block.type == 'WORK':
                total_worked += block.duration
            elif block.type == 'BREAK':
                total_break += block.duration
            if block.paid:
                total_paid += block.duration

        entry.total_worked = total_worked
        entry.total_break = total_break
        entry.total_paid = total_paid
        entry.total_hours = total_worked

        # Overtime and undertime can be computed vs schedule_day.hours
        schedule_hours = context.schedule_day.hours if context.schedule_day else timedelta(0)
        if total_worked > schedule_hours:
            entry.overtime = total_worked - schedule_hours
            entry.undertime = timedelta(0)
        else:
            entry.undertime = schedule_hours - total_worked
            entry.overtime = timedelta(0)

        return {'passed': True, 'message': 'Worked hours computed', 'data': {}}

