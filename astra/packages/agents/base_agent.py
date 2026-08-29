from typing import Dict, Any, List

class AstraAgent:
    """
    Base interface for all specialized ASTRA agents.
    """
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities

    def can_handle(self, task_type: str) -> bool:
        return task_type in self.capabilities

    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a specific task based on context.
        Must be implemented by subclasses.
        """
        raise NotImplementedError
