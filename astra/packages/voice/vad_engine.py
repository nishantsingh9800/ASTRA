from typing import Protocol, Iterator, Tuple

class VADEngine(Protocol):
    """
    Voice Activity Detection.
    Determines if audio contains human speech, and detects natural end-of-turn.
    """
    def filter_speech(self, audio_stream: Iterator[bytes]) -> Iterator[bytes]:
        """Yields only the segments of the stream that contain speech."""
        ...

    def detect_end_of_turn(self, audio_stream: Iterator[bytes], pause_threshold_ms: int = 1500) -> bytes:
        """
        Consumes the stream until a natural pause indicates the user has finished speaking.
        Returns the aggregated audio buffer for the turn.
        """
        ...
