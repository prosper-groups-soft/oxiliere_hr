from core.rules_engine import (
    PreconditionFailedError,
    RuleEvaluationError
)



# Préconditions
class AttendanceClosedError(PreconditionFailedError):
    """Raised when an attendance sheet is already closed and cannot be modified."""

class MissingAttendanceSettingsError(PreconditionFailedError):
    """Raised when AttendanceSettings singleton is missing."""

class InvalidTimeBlockError(PreconditionFailedError):
    """Raised when a TimeBlock has invalid start/end times."""

class AttendanceInClosedPeriodError(PreconditionFailedError):
    """Raised when the attendance entry is within a closed period (ClosingAttendance)."""



# Evaluation / Calculs
class AbsenceRuleError(RuleEvaluationError):
    """Raised when the AbsenceRule cannot determine ABSENT / EXCUSED status."""

class AggregationRuleError(RuleEvaluationError):
    """Raised when calculating total_worked, total_break, or total_paid fails."""

class OvertimeRuleError(RuleEvaluationError):
    """Raised when calculating overtime fails."""

class StatusDeterminationError(RuleEvaluationError):
    """Raised when the final status cannot be determined correctly."""



# TimeBlock spécifiques
class OverlappingTimeBlockError(PreconditionFailedError):
    """Raised when TimeBlocks overlap (should not happen in professional setup)."""

class InvalidBlockTypeError(RuleEvaluationError):
    """Raised when a TimeBlock has an unexpected type not handled by rules."""
