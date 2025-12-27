from .preconditions import PreconditionRule
from .rules import AbsenceRule
from core.rules_engine import RuleResult, RuleEngine


class AttendanceRuleEngine(RuleEngine):
    """
    Attendance Rule Engine orchestrates rules in strict order.
    """

    DEFAULT_RULES = [
        PreconditionRule(),
        AbsenceRule(),
        # Future rules:
        # AggregationRule(),
        # WorkedBreakPaidRule(),
        # OvertimeUndertimeRule(),
        # StatusDeterminationRule()
    ]

    def __init__(self, rules=None):
        self.rules = rules or self.DEFAULT_RULES

    def run(self, context) -> list[RuleResult]:
        results: list[RuleResult] = []
        for rule in self.rules:
            result = rule.evaluate(context)
            if not isinstance(result, RuleResult):
                raise Exception(f"{rule.__class__.__name__} did not return a RuleResult")
            results.append(result)
        return results


# ----------------------------------------------------------------------
# Usage example (testable)
# from rules.attendance.context import RuleContext
# from rules.attendance.engine import AttendanceRuleEngine
# context = RuleContext(attendance_entry)
# engine = AttendanceRuleEngine()
# results = engine.run(context)
# print([r.message for r in results])
