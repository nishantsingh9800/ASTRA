from typing import Protocol, Any, Dict, Optional

class SessionManager(Protocol):
    """
    Manages active ASTRA 2.0 sessions.
    Handles activation, deactivation, and turn-taking logic (barge-in, end-of-turn).
    """
    def start_session(self, activation_trigger: str) -> str:
        """Start a new session and return the session ID."""
        ...

    def end_session(self, session_id: str) -> None:
        """End an active session."""
        ...

    def get_active_session(self) -> Optional[Dict[str, Any]]:
        """Retrieve details of the currently active session."""
        ...
