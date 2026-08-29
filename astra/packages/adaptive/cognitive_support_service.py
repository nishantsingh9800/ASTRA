from typing import List, Dict, Any, Optional

class CognitiveSupportService:
    """
    Manages task simplification and step-by-step logic.
    Maintains session memory for cognitive assistance.
    """
    def __init__(self):
        self._current_task_steps: List[str] = []
        self._current_step_index: int = 0
        self._last_action: Optional[str] = None

    def simplify_task(self, task_description: str) -> List[str]:
        """
        In a real implementation, this would call the LLM to break a complex task into steps.
        Mock implementation for testing.
        """
        self._current_task_steps = [
            "Open assignment portal.",
            "Find course.",
            "Select assignment."
        ]
        self._current_step_index = 0
        return self._current_task_steps

    def get_next_step(self) -> Optional[str]:
        """Returns the next step in the current task."""
        if self._current_step_index < len(self._current_task_steps):
            step = self._current_task_steps[self._current_step_index]
            self._current_step_index += 1
            self._last_action = step
            return step
        return None

    def repeat_last_step(self) -> Optional[str]:
        """Repeats the previous step."""
        return self._last_action

    def get_injected_prompt(self, is_simplified: bool) -> str:
        """Returns the system prompt to inject for simplification mode."""
        if is_simplified:
            return "Output your response at a 3rd-grade reading level. Use simple language and short sentences."
        return ""
