from typing import Protocol, Any, Dict, List

class MemoryManager(Protocol):
    """
    Manages short-term and long-term memory for ASTRA 2.0.
    Separates working memory, session memory, and persistent preferences.
    """
    def remember(self, key: str, value: Any, memory_type: str = "session") -> None:
        """Store a piece of information in memory."""
        ...

    def recall(self, query: str, memory_type: str = "session") -> List[Dict[str, Any]]:
        """Retrieve related information based on a query."""
        ...

    def forget(self, key: str, memory_type: str = "session") -> None:
        """Remove a piece of information from memory."""
        ...
