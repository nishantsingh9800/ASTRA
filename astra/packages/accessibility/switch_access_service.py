from typing import List, Callable, Any, Optional

class SwitchAccessService:
    """
    Manages auto-scanning and single-switch interactions for UI selection.
    """
    def __init__(self, scan_interval_ms: int = 1500):
        self.scan_interval_ms = scan_interval_ms
        self._options: List[Any] = []
        self._current_index: int = 0
        self._is_scanning: bool = False

    def load_options(self, options: List[Any]) -> None:
        """Loads a list of UI elements to scan through."""
        self._options = options
        self._current_index = 0

    def next_option(self) -> None:
        """Advances the highlight to the next option."""
        if not self._options:
            return
        self._current_index = (self._current_index + 1) % len(self._options)

    def select_current(self) -> Optional[Any]:
        """Triggered by the switch press. Returns the currently highlighted option."""
        if not self._options:
            return None
        return self._options[self._current_index]

    def get_highlighted(self) -> Optional[Any]:
        """Returns the currently highlighted option for UI rendering."""
        if not self._options:
            return None
        return self._options[self._current_index]
