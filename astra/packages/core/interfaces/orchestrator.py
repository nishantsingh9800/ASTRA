from typing import Protocol, Any, Dict

class CoreOrchestrator(Protocol):
    """
    Central brain of ASTRA 2.0. Manages the lifecycle of requests.
    """
    def process_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming request from the user/UI.
        Validates the request, determines intent, delegates to TaskManager, and returns the verified result.
        """
        ...

    def start(self) -> None:
        """Start the orchestrator and all its managed services."""
        ...

    def stop(self) -> None:
        """Stop the orchestrator gracefully."""
        ...
