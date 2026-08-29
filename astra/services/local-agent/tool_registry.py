from typing import Protocol, Any, Dict, Callable

class ToolRegistry(Protocol):
    """
    Registry for all tools available to the ASTRA local agent.
    Ensures that only registered, verified tools can be executed.
    """
    def register_tool(self, name: str, handler: Callable[..., Any], metadata: Dict[str, Any]) -> None:
        """Register a new tool."""
        ...

    def get_tool(self, name: str) -> Callable[..., Any]:
        """Retrieve a tool by name."""
        ...

    def execute_tool(self, name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool safely, verifying its registration."""
        ...
