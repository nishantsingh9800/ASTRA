from typing import Protocol, Any, Dict, Tuple
from .permission_manager import RiskLevel

class SafetyEngine(Protocol):
    """
    Evaluates the safety of intended actions before they are executed.
    Defends against prompt injection and unsafe commands.
    """
    def evaluate_action(self, action: str, parameters: Dict[str, Any]) -> Tuple[bool, RiskLevel, str]:
        """
        Evaluate if an action is safe to execute.
        Returns (is_safe, risk_level, reason).
        """
        ...
