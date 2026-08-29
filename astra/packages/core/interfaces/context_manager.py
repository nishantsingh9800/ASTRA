from typing import Protocol, Any, Dict, Optional

class ContextManager(Protocol):
    """
    Maintains the current context of the user, environment, and system state.
    """
    def get_context(self) -> Dict[str, Any]:
        """Retrieve the current aggregated context."""
        ...

    def update_context(self, key: str, value: Any) -> None:
        """Update a specific context key."""
        ...

    def get_screen_context(self) -> Optional[Dict[str, Any]]:
        """Retrieve current screen/application context if available."""
        ...
