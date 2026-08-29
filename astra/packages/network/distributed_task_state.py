import time
from typing import Dict, Any, Optional

class DistributedTaskState:
    """
    A synchronized key-value store for active tasks across the Astra ecosystem.
    Handles conflict resolution using timestamps (last writer wins).
    """
    def __init__(self):
        # Format: { "key": {"value": Any, "timestamp": float, "writer": str} }
        self._state: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._state:
            return self._state[key]["value"]
        return None

    def set(self, key: str, value: Any, writer_id: str) -> None:
        """
        Updates the state. Overwrites unconditionally since it's the local core.
        In a distributed system, this timestamp is used by clients to resolve sync conflicts.
        """
        self._state[key] = {
            "value": value,
            "timestamp": time.time(),
            "writer": writer_id
        }

    def sync_from_remote(self, key: str, value: Any, remote_timestamp: float, writer_id: str) -> bool:
        """
        Applies a remote update only if the remote timestamp is newer than the local one.
        Returns True if the update was applied.
        """
        if key not in self._state:
            self._state[key] = {
                "value": value,
                "timestamp": remote_timestamp,
                "writer": writer_id
            }
            return True
            
        if remote_timestamp > self._state[key]["timestamp"]:
            self._state[key] = {
                "value": value,
                "timestamp": remote_timestamp,
                "writer": writer_id
            }
            return True
            
        return False

    def get_full_state(self) -> Dict[str, Dict[str, Any]]:
        """Returns the full state dictionary for initial client sync."""
        return self._state
