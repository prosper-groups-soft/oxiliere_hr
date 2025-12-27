from typing import List, Optional, Iterable, Callable
from .base import BaseRule
from .result import RuleResult
from .exceptions import RuleEngineException


class RuleEngine:
    """
    Orchestrates rules evaluation against a context.

    Responsibilities:
    - Execute rules in order
    - Collect RuleResult
    - Propagate business / precondition exceptions
    - Wrap unexpected technical exceptions
    """

    def __init__(self, rules: Optional[Iterable[BaseRule]] = None):
        self._rules: List[BaseRule] = list(rules) if rules else []

    # Rule registration
    def register_rule(self, rule: BaseRule) -> None:
        """Register a single rule."""
        self._rules.append(rule)

    def register_rules(self, rules: Iterable[BaseRule]) -> None:
        """Register multiple rules."""
        self._rules.extend(rules)

    def clear_rules(self) -> None:
        """Remove all registered rules."""
        self._rules.clear()

    # Execution
    def run(
        self,
        context,
        *,
        rules: Optional[Iterable[BaseRule]] = None,
        stop_on_failure: bool = False,
        exception_handler: Optional[Callable[[BaseRule, Exception], None]] = None,
    ) -> List[RuleResult]:
        """
        Execute rules against the given context.

        Parameters:
            context:
                RuleContext instance (read-only for rules)

            rules:
                Optional subset of rules to execute.
                If None, all registered rules are executed.

            stop_on_failure:
                Stop execution when a rule returns RuleResult(passed=False).

            exception_handler:
                Optional callback invoked on RuleEngineException
                before propagation.

        Raises:
            RuleEngineException:
                - Any business or precondition exception raised by rules
                - Any unexpected exception wrapped as RuleEngineException
        """
        results: List[RuleResult] = []
        rules_to_run = list(rules) if rules is not None else self._rules

        for rule in rules_to_run:
            try:
                result = rule.evaluate(context)

                if not isinstance(result, RuleResult):
                    raise RuleEngineException(
                        f"{rule.__class__.__name__} did not return a RuleResult"
                    )

                results.append(result)

                if stop_on_failure and not result.passed:
                    break

            except RuleEngineException as exc:
                # Business / precondition exception → propagate
                if exception_handler:
                    exception_handler(rule, exc)
                raise

            except Exception as exc:
                # Unexpected technical error → wrap & propagate
                wrapped = RuleEngineException(
                    f"Unhandled exception in rule {rule.__class__.__name__}"
                )
                if exception_handler:
                    exception_handler(rule, wrapped)
                raise wrapped from exc

        return results

    # Introspection
    @property
    def rules(self) -> List[BaseRule]:
        """Return registered rules (read-only copy)."""
        return list(self._rules)

