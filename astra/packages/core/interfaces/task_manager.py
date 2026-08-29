from typing import Protocol, Any, Dict, List

class TaskManager(Protocol):
    """
    Manages the lifecycle, tracking, and execution of high-level user tasks.
    Every action-based request becomes a task.
    """
    def create_task(self, request: str, context: Dict[str, Any]) -> str:
        """Create a new task and return its ID."""
        ...

    def update_task_status(self, task_id: str, status: str, details: Dict[str, Any]) -> None:
        """Update the status and details of a running task."""
        ...

    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent task history."""
        ...
