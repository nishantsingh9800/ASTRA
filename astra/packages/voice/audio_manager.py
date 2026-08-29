from typing import Protocol, Iterator, Callable

class AudioManager(Protocol):
    """
    Manages raw audio I/O from the system's microphone and speaker.
    Handles device selection and stream management.
    """
    def start_recording(self) -> Iterator[bytes]:
        """Start capturing audio from the microphone."""
        ...

    def stop_recording(self) -> None:
        """Stop capturing audio."""
        ...

    def play_audio(self, audio_data: bytes) -> None:
        """Play a complete audio buffer."""
        ...

    def play_audio_stream(self, audio_stream: Iterator[bytes], interrupt_callback: Callable[[], bool]) -> None:
        """Play an audio stream, allowing for interruption (barge-in)."""
        ...
