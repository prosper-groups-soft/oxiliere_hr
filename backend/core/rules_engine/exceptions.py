

class RuleEngineException(Exception):
    """Base exception for all rule engine errors."""
    pass

class PreconditionFailedError(RuleEngineException):
    """Raised when a precondition for a rule fails."""
    pass

class RuleEvaluationError(RuleEngineException):
    """Raised when a rule cannot be evaluated correctly."""
    pass

