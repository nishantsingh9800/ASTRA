import audioop
from typing import Iterator
from packages.core import logger
from packages.voice.wake_word_engine import WakeWordEngine

class RealWakeWordEngine(WakeWordEngine):
    def __init__(self, energy_threshold: int = 600, required_hits: int = 2):
        self.energy_threshold = energy_threshold
        self.required_hits = required_hits

    def listen_for_wake_word(self, audio_stream: Iterator[bytes]) -> str:
        """
        Listens for a sudden spike in energy (like a clap or loud "Hey Astra!").
        Blocks until triggered.
        """
        logger.debug("[WakeWord] Listening for clap or loud noise...")
        hits = 0
        
        for chunk in audio_stream:
            # Calculate RMS energy of the chunk (assumes 16-bit PCM)
            rms = audioop.rms(chunk, 2)
            
            if rms > self.energy_threshold:
                hits += 1
                if hits >= self.required_hits:
                    return "loud_noise_or_clap"
            else:
                # Reset if it was just a transient pop
                if hits > 0:
                    hits -= 1
