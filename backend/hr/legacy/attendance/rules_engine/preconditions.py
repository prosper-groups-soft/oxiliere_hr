from typing import List, Callable
from core.rules_engine import BaseRule, RuleResult
from .context import AttendanceRuleContext
from .exceptions import (
    PreconditionFailedError,
    AttendanceClosedError,
    MissingAttendanceSettingsError,
    InvalidTimeBlockError,
    AttendanceInClosedPeriodError,
    OverlappingTimeBlockError,
)
from attendance.models import ClosingAttendance


class PreconditionRule(BaseRule):
    """
    Executes a dynamic list of precondition checks.
    Each precondition is a callable accepting the context.
    """

    def __init__(self, preconditions: List[Callable[[AttendanceRuleContext], None]] = None):
        # Default preconditions if none provided
        if preconditions is None:
            preconditions = [
                self._check_entry_exists,
                self._check_attendance_open,
                self._check_settings_exist,
                self._check_timeblocks_valid,
                self._check_timeblocks_overlap,
                self._check_period_not_closed,
            ]
        self.preconditions = preconditions

    def evaluate(self, context: AttendanceRuleContext) -> RuleResult:
        for check in self.preconditions:
            check(context)
        return RuleResult(passed=True, message="All preconditions passed")

    # ---------------- Precondition methods ---------------- #

    @staticmethod
    def _check_entry_exists(context: AttendanceRuleContext) -> None:
        if context.attendance_entry is None:
            raise PreconditionFailedError("AttendanceEntry does not exist")

    @staticmethod
    def _check_attendance_open(context: AttendanceRuleContext) -> None:
        if context.attendance_entry.attendance.closed:
            raise AttendanceClosedError("Attendance is already closed")

    @staticmethod
    def _check_settings_exist(context: AttendanceRuleContext) -> None:
        if context.settings is None:
            raise MissingAttendanceSettingsError("AttendanceSettings missing")

    @staticmethod
    def _check_timeblocks_valid(context: AttendanceRuleContext) -> None:
        for tb in context.time_blocks:
            if tb.start_time >= tb.end_time:
                raise InvalidTimeBlockError(
                    f"Invalid TimeBlock {tb.id}: start_time >= end_time"
                )

    @staticmethod
    def _check_timeblocks_overlap(context: AttendanceRuleContext) -> None:
        sorted_blocks = sorted(context.time_blocks, key=lambda tb: tb.start_time)
        for i in range(1, len(sorted_blocks)):
            prev = sorted_blocks[i - 1]
            curr = sorted_blocks[i]
            if prev.end_time > curr.start_time:
                raise OverlappingTimeBlockError(
                    f"TimeBlocks overlap for employee {context.attendance_entry.employee}: "
                    f"{prev.start_time}-{prev.end_time} and {curr.start_time}-{curr.end_time}"
                )

    @staticmethod
    def _check_period_not_closed(context: AttendanceRuleContext) -> None:
        if ClosingAttendance.objects.filter(date__gte=context.date).exists():
            raise AttendanceInClosedPeriodError(
                "Attendance is in a closed period"
            )

