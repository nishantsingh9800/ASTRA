from typing import Protocol, Iterator

class TTSProvider(Protocol):
    """
    Interface for Text-to-Speech synthesis.
    """
    def synthesize(self, text: str) -> bytes:
        """Synthesize a complete string into audio bytes."""
        ...

    def synthesize_stream(self, text_stream: Iterator[str]) -> Iterator[bytes]:
        """Synthesize an incoming stream of text into streaming audio bytes."""
        ...

    def is_available(self) -> bool:
        """Check if this provider is currently available."""
        ...

    def stop(self) -> None:
        """Interrupt any ongoing synthesis/playback."""
        ...
