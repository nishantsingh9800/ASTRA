from typing import Protocol, Iterator, Optional

class WakeWordEngine(Protocol):
    """
    Lightweight engine to detect the "Hey Astra" wake phrase or optional clap patterns.
    """
    def listen_for_wake_word(self, audio_stream: Iterator[bytes]) -> str:
        """
        Blocks and processes the stream until a wake word or pattern is detected.
        Returns the trigger type (e.g., 'hey_astra', 'clap').
        """
        ...
