from typing import Protocol, Any, Dict
from enum import Enum

class RiskLevel(Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class PermissionManager(Protocol):
    """
    Manages user permissions for various tool executions and system accesses.
    """
    def check_permission(self, action: str, context: Dict[str, Any]) -> bool:
        """Check if the system is allowed to perform a specific action."""
        ...

    def request_permission(self, action: str, reason: str) -> bool:
        """Request explicit permission from the user for an action."""
        ...
