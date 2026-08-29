from typing import Protocol, Iterator, Optional

class STTProvider(Protocol):
    """
    Interface for Speech-to-Text conversion.
    """
    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe a complete audio buffer into text."""
        ...

    def transcribe_stream(self, audio_stream: Iterator[bytes]) -> Iterator[str]:
        """Transcribe an incoming stream of audio, yielding partial/final results."""
        ...

    def is_available(self) -> bool:
        """Check if this provider is currently available."""
        ...
