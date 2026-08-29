from typing import Protocol, Dict, Any, Generator

class LLMProvider(Protocol):
    """
    Interface for Language Model generation.
    Can be implemented by Local or Cloud providers.
    """
    def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a complete string response."""
        ...

    def generate_stream(self, prompt: str, context: Dict[str, Any]) -> Generator[str, None, None]:
        """Generate a streaming response, yielding tokens as they arrive."""
        ...

    def is_available(self) -> bool:
        """Check if this provider is currently available."""
        ...
