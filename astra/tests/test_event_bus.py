from typing import Any
# Assuming a mock implementation for testing, since EventBus is just a Protocol
class SimpleEventBus:
    def __init__(self):
        self._subscribers = {}

    def publish(self, topic: str, data: Any) -> None:
        if topic in self._subscribers:
            for handler in self._subscribers[topic]:
                handler(data)

    def subscribe(self, topic: str, handler: Any) -> None:
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Any) -> None:
        if topic in self._subscribers and handler in self._subscribers[topic]:
            self._subscribers[topic].remove(handler)

def test_event_bus_publish_subscribe():
    bus = SimpleEventBus()
    received_data = []

    def dummy_handler(data):
        received_data.append(data)

    bus.subscribe("test_topic", dummy_handler)
    bus.publish("test_topic", {"key": "value"})

    assert len(received_data) == 1
    assert received_data[0] == {"key": "value"}
