from abc import ABC, abstractmethod
from .result import RuleResult


class BaseRule(ABC):
    """
    Abstract base class for all rules.
    Each rule must implement `evaluate(context)` and return RuleResult.
    """

    @abstractmethod
    def evaluate(self, context) -> RuleResult:
        """
        Evaluate the rule against the provided context.
        
        Raises:
            Exception if preconditions are not met.
        
        Returns:
            RuleResult: outcome of the rule.
        """
        pass

