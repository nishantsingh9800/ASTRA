import audioop
import time
from collections import deque
from typing import Iterator
from packages.core import logger
from packages.voice.vad_engine import VADEngine

class RealVADEngine(VADEngine):
    def __init__(self, silence_limit_seconds: float = 1.5, sample_rate: int = 16000, pre_roll_ms: int = 800):
        self.silence_limit_seconds = silence_limit_seconds
        self.sample_rate = sample_rate
        self.pre_roll_ms = pre_roll_ms
        
        self.noise_floor = 200.0  # Initial guess
        self.speech_margin = 300.0 # RMS above noise floor to be considered speech

    def filter_speech(self, audio_stream: Iterator[bytes]) -> Iterator[bytes]:
        """Yields chunks of audio that contain speech."""
        for chunk in audio_stream:
            rms = audioop.rms(chunk, 2)
            if rms > self.noise_floor + self.speech_margin:
                yield chunk

    def detect_end_of_turn(self, audio_stream: Iterator[bytes], pause_threshold_ms: int = 1500) -> bytes:
        """
        Records audio with pre-roll, dynamic noise floor, and dynamic trailing silence.
        """
        logger.debug("[VAD] Listening to speech turn...")
        
        # 16-bit PCM = 2 bytes per sample.
        bytes_per_ms = int(self.sample_rate * 2 / 1000)
        max_pre_roll_bytes = bytes_per_ms * self.pre_roll_ms
        
        pre_roll_buffer = deque(maxlen=max_pre_roll_bytes)
        audio_buffer = bytearray()
        
        silence_start = None
        has_spoken = False
        speech_start_time = None
        
        base_silence_limit = pause_threshold_ms / 1000.0

        for chunk in audio_stream:
            rms = audioop.rms(chunk, 2)
            
            # Update dynamic noise floor continuously if it's very quiet
            if rms < self.noise_floor * 1.5:
                self.noise_floor = (self.noise_floor * 0.95) + (rms * 0.05)
                # prevent dropping too low
                self.noise_floor = max(50.0, self.noise_floor)
                
            dynamic_threshold = self.noise_floor + self.speech_margin
            
            if not has_spoken:
                # Add to pre-roll
                for byte in chunk:
                    pre_roll_buffer.append(byte)
            else:
                audio_buffer.extend(chunk)
            
            if rms > dynamic_threshold:
                if not has_spoken:
                    speech_start_time = time.time()
                    logger.debug(f"\n[VAD] Speech detected at {speech_start_time} (RMS: {rms:.1f}, Noise Floor: {self.noise_floor:.1f})")
                    # Push pre-roll into main buffer
                    audio_buffer.extend(bytes(pre_roll_buffer))
                    pre_roll_buffer.clear()
                    
                has_spoken = True
                silence_start = None  # Reset silence timer
            else:
                if has_spoken:
                    if silence_start is None:
                        silence_start = time.time()
                    else:
                        # Allow longer pauses if they've spoken a lot (hesitation)
                        speech_length = len(audio_buffer) / (self.sample_rate * 2)
                        dynamic_limit = base_silence_limit + (0.5 if speech_length > 2.0 else 0)
                        
                        current_silence = time.time() - silence_start
                        if current_silence > dynamic_limit:
                            speech_end_time = time.time()
                            total_duration = speech_end_time - speech_start_time
                            if logger.is_debug():
                                logger.debug("\n============================================================")
                                logger.debug("6. VAD DEBUGGING (END OF TURN)")
                                logger.debug("============================================================")
                                logger.debug(f"Speech Duration: {total_duration:.2f}s")
                                logger.debug(f"Recorded Bytes: {len(audio_buffer)}")
                                logger.debug("============================================================\n")
                            break
                        
            # If 10s of absolute silence before speaking, timeout
            if not has_spoken:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > 10.0:
                    logger.debug("[VAD] Turn timed out (no speech).")
                    break
                
        return bytes(audio_buffer)
