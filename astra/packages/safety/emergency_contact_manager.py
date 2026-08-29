from typing import List, Dict, Any, Optional

class EmergencyContactManager:
    """
    Manages priority lists of contacts and their preferred notification channels.
    """
    def __init__(self):
        self._contacts: List[Dict[str, Any]] = [
            {"name": "Caregiver", "channel": "sms", "priority": 1, "target": "mock_number"}
        ]

    def get_primary_contact(self) -> Optional[Dict[str, Any]]:
        """Returns the highest priority contact."""
        if not self._contacts:
            return None
        return sorted(self._contacts, key=lambda c: c["priority"])[0]

    def add_contact(self, name: str, channel: str, target: str, priority: int) -> None:
        self._contacts.append({"name": name, "channel": channel, "priority": priority, "target": target})
