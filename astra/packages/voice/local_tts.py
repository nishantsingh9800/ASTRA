import os
import tempfile
from typing import Iterator
from packages.core.interfaces.tts_provider import TTSProvider

class LocalTTS(TTSProvider):
    """
    Local implementation of TTS.
    Returns complete WAV file bytes so RealAudioManager can play it asynchronously and allow barge-in.
    """
    def __init__(self, voice_model: str = "en_US-lessac-medium"):
        self.voice_model = voice_model
        self._available = True
        self._interrupted = False

    def synthesize(self, text: str) -> bytes:
        if not self._available:
            raise RuntimeError("Local TTS unavailable.")
            
        import pyttsx3
        print(f"[TTS] Synthesizing: '{text}'")
        engine = pyttsx3.init()
        
        temp_wav = tempfile.mktemp(suffix=".wav")
        engine.save_to_file(text, temp_wav)
        engine.runAndWait()
        
        wav_bytes = b""
        if os.path.exists(temp_wav):
            with open(temp_wav, "rb") as f:
                wav_bytes = f.read()
            os.remove(temp_wav)
            
        return wav_bytes

    def synthesize_stream(self, text_stream: Iterator[str]) -> Iterator[bytes]:
        if not self._available:
            raise RuntimeError("Local TTS unavailable.")
        self._interrupted = False
        
        for text_chunk in text_stream:
            if self._interrupted:
                break
            yield self.synthesize(text_chunk)

    def is_available(self) -> bool:
        return self._available

    def stop(self) -> None:
        self._interrupted = True
