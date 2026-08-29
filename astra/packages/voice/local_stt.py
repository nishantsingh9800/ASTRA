import os
import math
from typing import Iterator
from packages.core import logger
from packages.core.interfaces.stt_provider import STTProvider

class LocalSTT(STTProvider):
    """
    Local implementation of STT using faster-whisper for high accuracy.
    """
    def __init__(self, model_size: str = "base.en", sample_rate: int = 16000):
        self.model_size = model_size
        self.sample_rate = sample_rate
        self._available = True
        self.model = None
        
        try:
            from faster_whisper import WhisperModel
            if logger.is_debug():
                logger.debug("\n============================================================")
                logger.debug("10. VERIFY ACTIVE STT ENGINE")
                logger.debug("============================================================")
                logger.debug("STT ENGINE: faster-whisper")
                logger.debug(f"STT MODEL: {self.model_size}")
                logger.debug("LOCAL/CLOUD: LOCAL")
                logger.debug("LANGUAGE: en")
                logger.debug("DEVICE: cpu (int8)")
                logger.debug("INITIALIZED: True")
                logger.debug("============================================================\n")
            # Run on CPU with int8 quantization for speed, can be upgraded to CUDA later
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            logger.debug("[STT] Model loaded successfully.")
        except Exception as e:
            logger.error(f"[STT] Failed to load faster-whisper: {e}")
            self._available = False

    def transcribe(self, audio_data: bytes, sample_rate: int = 44100, channels: int = 1) -> dict:
        """
        Transcribes the raw audio data and returns a dictionary with 'text' and 'confidence'.
        """
        import time
        import audioop
        start_time = time.time()
        
        if not self._available or not self.model:
            raise RuntimeError("Local STT unavailable.")
            
        import numpy as np
        
        try:
            duration = len(audio_data) / (sample_rate * 2 * channels)
            rms = audioop.rms(audio_data, 2)
            peak = audioop.maxpp(audio_data, 2)
            if logger.is_debug():
                logger.debug("\n============================================================")
                logger.debug("11. VERIFY STT INPUT")
                logger.debug("============================================================")
                logger.debug(f"STT INPUT (Before Resampling):")
                logger.debug(f"  Duration: {duration:.2f}s")
                logger.debug(f"  Bytes: {len(audio_data)}")
                logger.debug(f"  Sample Rate: {sample_rate}Hz")
                logger.debug(f"  Channels: {channels}")
                logger.debug(f"  RMS: {rms}")
                logger.debug(f"  Peak: {peak}")
                
                if duration < 0.5:
                    logger.warn("  [WARNING] Audio duration is unexpectedly tiny!")
                logger.debug("============================================================\n")

            # Channel conversion (stereo to mono)
            if channels == 2:
                logger.debug("[STT] Converting stereo to mono...")
                audio_data = audioop.tomono(audio_data, 2, 0.5, 0.5)

            # Resampling to 16kHz
            if sample_rate != 16000:
                logger.debug(f"[STT] Resampling audio from {sample_rate}Hz to 16000Hz...")
                audio_data, _ = audioop.ratecv(audio_data, 2, 1, sample_rate, 16000, None)

            # Convert raw bytes to 16-bit int
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            # Normalize to float32
            audio_float32 = audio_np.astype(np.float32) / 32768.0
            
            # Transcribe
            # Use initial_prompt to prime the model for common app names and commands
            initial_prompt = "Open WhatsApp. Search for Kishan. Open YouTube. Calculate 2 times 2. What is ahead?"
            segments, info = self.model.transcribe(
                audio_float32, 
                beam_size=5, 
                language="en", 
                initial_prompt=initial_prompt
            )
            
            text = ""
            total_prob = 0.0
            total_no_speech_prob = 0.0
            count = 0
            
            for segment in segments:
                text += segment.text + " "
                total_prob += math.exp(segment.avg_logprob)
                total_no_speech_prob += segment.no_speech_prob
                count += 1
                
            text = text.strip()
            
            # Remove hallucinations like "Open WhatsApp. Open WhatsApp." 
            # (Whisper sometimes repeats the prompt if audio has long trailing silence)
            import re
            text = re.sub(r'(.+?)\s+\1', r'\1', text, flags=re.IGNORECASE)
            
            avg_prob = (total_prob / count) if count > 0 else 0
            avg_no_speech = (total_no_speech_prob / count) if count > 0 else 1.0
            
            # --- QUALITY GATE ---
            is_valid = True
            gate_reason = "Passed"
            quality = "ACCEPTABLE"
            
            if duration < 0.4:
                is_valid = False
                gate_reason = "Audio too short (<0.4s)"
            elif avg_no_speech > 0.6:
                is_valid = False
                gate_reason = f"High no_speech_prob ({avg_no_speech:.2f})"
            elif count == 0 or not text:
                is_valid = False
                gate_reason = "Empty transcript"
            else:
                # Check for hallucinated words or short junk
                text_clean = text.lower().strip().strip('.?!')
                words = text_clean.split()
                
                filler_words = ["oh", "you", "yeah", "hm", "uh", "um", "okay", "ok", "ah", "hmm"]
                if len(words) <= 2 and all(w in filler_words for w in words):
                    if avg_prob < 0.8: # Higher threshold for filler words
                        is_valid = False
                        gate_reason = f"Filler phrase '{text}' with avg_prob {avg_prob:.2f} < 0.8"
                
                if len(words) == 1 and avg_prob < 0.5:
                    is_valid = False
                    gate_reason = "Single word with low confidence"

            if not is_valid:
                quality = "INVALID"
                confidence = "LOW"
                text = "" # Discard hallucination
            elif avg_prob > 0.7 and avg_no_speech < 0.1:
                quality = "GOOD"
                confidence = "HIGH"
            else:
                quality = "ACCEPTABLE"
                confidence = "MEDIUM"
                
            latency = time.time() - start_time
            if logger.is_debug():
                logger.debug("\n============================================================")
                logger.debug("12. VERIFY STT OUTPUT (QUALITY GATE) & 26. TRANSCRIPT")
                logger.debug("============================================================")
                logger.debug(f"RAW STT OUTPUT: {text}")
                logger.debug(f"Avg Prob: {avg_prob:.4f} | No Speech Prob: {avg_no_speech:.4f}")
                logger.debug(f"Gate Status: {quality} ({gate_reason})")
                logger.debug(f"STT CONFIDENCE: {confidence}")
                logger.debug(f"LATENCY: {latency:.2f}s")
                logger.debug("============================================================\n")
            
            return {
                "text": text,
                "confidence": confidence,
                "prob": avg_prob
            }
            
        except Exception as e:
            logger.error(f"[STT] Transcription error: {e}")
            return {"text": "", "confidence": "LOW"}

    def transcribe_stream(self, audio_stream: Iterator[bytes]) -> Iterator[str]:
        if not self._available:
            raise RuntimeError("Local STT unavailable.")
        yield "..."

    def is_available(self) -> bool:
        return self._available

