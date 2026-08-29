from typing import Dict, Any, List

class MemoryManager:
    """
    Manages segregated memory structures: Working, Session, Preference, and Long-Term.
    """
    def __init__(self):
        self.working_memory: Dict[str, Any] = {}
        self.session_memory: Dict[str, Any] = {}
        self.preference_memory: Dict[str, Any] = {}
        self.long_term_memory: Dict[str, Any] = {}
        self.task_history: List[Dict[str, Any]] = []

    def add_to_working_memory(self, key: str, value: Any):
        """Temporary state for the current task."""
        self.working_memory[key] = value

    def clear_working_memory(self):
        """Called when a goal is completed to start fresh for the next one."""
        self.working_memory.clear()

    def add_to_session_memory(self, key: str, value: Any):
        """Persists across the active session (e.g. recent conversation context)."""
        self.session_memory[key] = value

    def set_preference(self, key: str, value: Any):
        """User preferences that cross sessions (e.g. 'Keep answers short')."""
        self.preference_memory[key] = value

    def remember_explicit(self, key: str, value: Any):
        """Explicitly committed long-term memory."""
        self.long_term_memory[key] = value

    def forget_explicit(self, key: str):
        """Removes from long-term memory."""
        if key in self.long_term_memory:
            del self.long_term_memory[key]
            
    def record_task_step(self, action: str, result: str):
        """Appends to the session task history."""
        self.task_history.append({"action": action, "result": result})

    def get_context_snapshot(self) -> Dict[str, Any]:
        """Provides the current memory context for the LLM."""
        return {
            "working": self.working_memory,
            "session": self.session_memory,
            "preferences": self.preference_memory,
            "long_term": self.long_term_memory
        }
