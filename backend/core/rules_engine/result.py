from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class RuleResult:
    """
    Represents the outcome of a single rule evaluation.
    """
    passed: bool                     # True if the rule passed
    message: str = ""                 # Optional human-readable message
    data: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

