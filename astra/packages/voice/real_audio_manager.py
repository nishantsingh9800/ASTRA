import pyaudio
import audioop
import time
from typing import Iterator, Callable, Dict, List, Optional, Any
from packages.core import logger
from packages.voice.audio_manager import AudioManager

class RealAudioManager(AudioManager):
    def __init__(self, chunk: int = 1024, format: int = pyaudio.paInt16, channels: int = 1):
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.p = pyaudio.PyAudio()
        self.device_index = None
        self.rate = 16000 # default fallback
        
        import threading
        self._pa_lock = threading.Lock()
        
        self._is_recording = False
        self.stream = None
        
        # AGC settings
        self.target_rms = 2000
        self.max_gain = 5.0
        self.current_gain = 1.0
        
        self.auto_select_microphone()

    def list_microphones(self) -> List[Dict[str, Any]]:
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        mics = []
        for i in range(0, numdevices):
            device_info = self.p.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                mics.append({
                    "index": i,
                    "name": device_info.get('name'),
                    "sampleRate": int(device_info.get('defaultSampleRate'))
                })
        return mics

    def auto_select_microphone(self):
        try:
            default_info = self.p.get_default_input_device_info()
            self.device_index = default_info.get('index')
            self.rate = int(default_info['defaultSampleRate'])
            
            if logger.is_debug():
                logger.debug("\n============================================================")
                logger.debug("19. MICROPHONE DEVICE LOGGING")
                logger.debug("============================================================")
                logger.debug(f"Device Name: {default_info.get('name', 'Unknown')}")
                logger.debug(f"Device ID: {self.device_index}")
                logger.debug(f"Sample Rate: {self.rate} Hz")
                logger.debug(f"Channels: {self.channels}")
                logger.debug("============================================================\n")
        except Exception as e:
            self.rate = 44100
            logger.warn(f"[RealAudioManager] Falling back to sample rate: {self.rate}Hz ({e})")

    def set_microphone(self, index: int):
        device_info = self.p.get_device_info_by_host_api_device_index(0, index)
        self.device_index = index
        self.rate = int(device_info.get('defaultSampleRate'))
        logger.debug(f"[RealAudioManager] Microphone explicitly set to: {device_info.get('name')} (Index: {index})")

    def _apply_agc(self, audio_data: bytes) -> bytes:
        # AGC disabled: Modifying gain mid-speech heavily distorts raw waveforms 
        # and leads to severe STT misrecognitions/hallucinations.
        return audio_data

    def start_recording(self) -> Iterator[bytes]:
        """Start capturing audio from the microphone."""
        stream_ref = None
        try:
            with self._pa_lock:
                stream_ref = self.p.open(format=self.format,
                                          channels=self.channels,
                                          rate=self.rate,
                                          input=True,
                                          input_device_index=self.device_index,
                                          frames_per_buffer=self.chunk)
                self.stream = stream_ref
        except Exception as e:
            logger.error(f"[RealAudioManager] Critical Error opening microphone stream: {e}")
            return
            
        self._is_recording = True
        consecutive_errors = 0
        
        try:
            while self._is_recording:
                try:
                    data = stream_ref.read(self.chunk, exception_on_overflow=False)
                    
                    if not data or all(b == 0 for b in data[:100]):
                        consecutive_errors += 1
                    else:
                        consecutive_errors = 0
                        
                    if consecutive_errors > 50:
                        logger.error("[RealAudioManager] Critical microphone failure: Stream returned only silence.")
                        break
                        
                    data = self._apply_agc(data)
                    yield data
                except Exception as e:
                    # Ignore GeneratorExit as it's normal when iteration stops
                    if isinstance(e, GeneratorExit):
                        break
                    logger.error(f"[RealAudioManager] Error reading stream: {e}")
                    consecutive_errors += 1
                    if consecutive_errors > 5:
                        break
        finally:
            with self._pa_lock:
                if stream_ref:
                    try:
                        stream_ref.stop_stream()
                        stream_ref.close()
                    except:
                        pass
                if self.stream == stream_ref:
                    self.stream = None

    def stop_recording(self) -> None:
        """Stop capturing audio by signaling the loop to end."""
        self._is_recording = False

    def play_audio(self, audio_data: bytes) -> None:
        """Play a complete audio buffer synchronously."""
        try:
            import wave
            import io
            
            # Check if it's a WAV file by inspecting the header
            if audio_data.startswith(b"RIFF"):
                with wave.open(io.BytesIO(audio_data), 'rb') as wf:
                    rate = wf.getframerate()
                    channels = wf.getnchannels()
                    width = wf.getsampwidth()
                    format = self.p.get_format_from_width(width)
                    raw_data = wf.readframes(wf.getnframes())
            else:
                rate = 16000
                channels = self.channels
                format = self.format
                raw_data = audio_data
                
            with self._pa_lock:
                stream = self.p.open(format=format,
                                     channels=channels,
                                     rate=rate,
                                     output=True)
            stream.write(raw_data)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            logger.error(f"[RealAudioManager] Error playing audio: {e}")

    def play_audio_stream(self, audio_stream: Iterator[bytes], interrupt_callback: Callable[[], bool]) -> None:
        """Play an audio stream, allowing for interruption (barge-in)."""
        try:
            import wave
            import io
            stream = None
            
            for chunk in audio_stream:
                if interrupt_callback and interrupt_callback():
                    logger.debug("[RealAudioManager] Audio playback INTERRUPTED by user barge-in.")
                    break
                    
                if chunk.startswith(b"RIFF"):
                    with wave.open(io.BytesIO(chunk), 'rb') as wf:
                        rate = wf.getframerate()
                        channels = wf.getnchannels()
                        width = wf.getsampwidth()
                        format = self.p.get_format_from_width(width)
                        raw_data = wf.readframes(wf.getnframes())
                else:
                    rate = 16000
                    channels = self.channels
                    format = self.format
                    raw_data = chunk
                    
                if stream is None:
                    with self._pa_lock:
                        stream = self.p.open(format=format,
                                             channels=channels,
                                             rate=rate,
                                             output=True)
                                         
                # Write in smaller chunks to allow responsive interruption
                chunk_size = 4096
                for i in range(0, len(raw_data), chunk_size):
                    if interrupt_callback and interrupt_callback():
                        logger.debug("[RealAudioManager] Audio playback INTERRUPTED by user barge-in.")
                        break
                    stream.write(raw_data[i:i+chunk_size])
                
            if stream:
                stream.stop_stream()
                stream.close()
        except Exception as e:
            logger.error(f"[RealAudioManager] Error playing audio stream: {e}")
