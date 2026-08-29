from typing import Protocol, Any, Callable, TypeVar

T = TypeVar('T')

class EventBus(Protocol):
    """
    Central event bus for ASTRA 2.0 communication.
    """
    def publish(self, topic: str, data: Any) -> None:
        """Publish an event to a topic."""
        ...

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> None:
        """Subscribe to an event topic."""
        ...

    def unsubscribe(self, topic: str, handler: Callable[[Any], None]) -> None:
        """Unsubscribe from an event topic."""
        ...
