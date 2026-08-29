import time
from typing import Dict, Any, List

class SafetyEventLogger:
    """
    Logs emergency state transitions and evidence securely.
    """
    def __init__(self):
        self._logs: List[Dict[str, Any]] = []

    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Records an event with a timestamp."""
        self._logs.append({
            "timestamp": time.time(),
            "type": event_type,
            "details": details
        })

    def get_logs(self) -> List[Dict[str, Any]]:
        return self._logs
