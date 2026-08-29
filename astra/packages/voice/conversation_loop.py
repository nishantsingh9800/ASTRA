import time
import threading
from typing import Dict, Any
from packages.core import logger
from packages.voice.wake_word_engine import WakeWordEngine
from packages.voice.vad_engine import VADEngine
from packages.core.interfaces.stt_provider import STTProvider
from packages.core.interfaces.tts_provider import TTSProvider
from packages.core.interfaces.llm_provider import LLMProvider
from packages.core.interfaces.orchestrator import CoreOrchestrator
from packages.voice.audio_manager import AudioManager
from packages.core.conversation_turn_manager import ConversationTurnManager
from packages.voice.speech_manager import SpeechManager

class BargeInDetector:
    def __init__(self, audio_manager: AudioManager, vad_engine: VADEngine):
        self.audio = audio_manager
        self.vad = vad_engine
        self.is_interrupted = False
        self._thread = None
        self._stop_event = threading.Event()
        
    def _listen_loop(self):
        try:
            audio_stream = self.audio.start_recording()
            
            # Dynamic Echo Cancellation via thresholding
            original_margin = getattr(self.vad, 'speech_margin', 500.0)
            if hasattr(self.vad, 'speech_margin'):
                self.vad.speech_margin = original_margin * 3.0 
            
            for chunk in self.vad.filter_speech(audio_stream):
                if self._stop_event.is_set():
                    break
                logger.debug("[BargeIn] High-energy speech detected! Interrupting TTS.")
                self.is_interrupted = True
                break
                
            if hasattr(self.vad, 'speech_margin'):
                self.vad.speech_margin = original_margin
                
            self.audio.stop_recording()
        except Exception as e:
            logger.error(f"[BargeIn] Error: {e}")
            
    def start(self):
        self.is_interrupted = False
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        self._stop_event.set()
        self.audio.stop_recording()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

class ConversationLoop:
    """
    Manages the offline voice interaction loop:
    Listen for Wake Word -> Record user speech -> STT -> LLM -> TTS -> Speaker
    Also handles barge-in interrupts and state tracking.
    """
    def __init__(self,
                 audio_manager: AudioManager,
                 wake_engine: WakeWordEngine,
                 vad_engine: VADEngine,
                 stt: STTProvider,
                 tts: TTSProvider,
                 orchestrator: CoreOrchestrator,
                 turn_manager: ConversationTurnManager,
                 speech_manager: SpeechManager,
                 startup_greeting: str = None):
        self.audio = audio_manager
        self.wake_engine = wake_engine
        self.vad = vad_engine
        self.stt = stt
        self.tts = tts
        self.orchestrator = orchestrator
        self.turn_manager = turn_manager
        self.speech_manager = speech_manager
        self.is_active = False
        self.startup_greeting = startup_greeting
        
        self.barge_in = BargeInDetector(self.audio, self.vad)

    def _play_with_barge_in(self, audio_output: bytes) -> bool:
        """Plays audio while listening for interrupts. Returns True if interrupted."""
        self.barge_in.start()
        
        # Give the microphone a split second to start recording before blasting TTS
        time.sleep(0.1) 
        
        try:
            self.audio.play_audio_stream([audio_output], interrupt_callback=lambda: self.barge_in.is_interrupted)
        finally:
            self.barge_in.stop()
            
        return self.barge_in.is_interrupted

    def start(self):
        self.is_active = True
        logger.debug("[ConversationLoop] Starting offline conversation loop...")
        
        if self.startup_greeting:
            logger.debug("[BOOT] startup greeting requested")
            logger.user_facing("Astra:")
            logger.user_facing(f"\"{self.startup_greeting}\"\n")
            self.turn_manager.set_state("SPEAKING")
            audio_output = self.tts.synthesize(self.startup_greeting)
            self._play_with_barge_in(audio_output)
            logger.debug("[BOOT] startup greeting returned")
            time.sleep(0.5)

        logger.debug("[BOOT] ConversationLoop started")
        self.turn_manager.set_state("SLEEPING")
        
        # Diagnostic tracing for exit bug
        import threading
        logger.debug("[BOOT] Startup greeting complete")
        logger.debug(f"[BOOT] Current state: {self.turn_manager.get_state()}")
        logger.debug(f"[BOOT] ConversationLoop alive: {'YES' if self.is_active else 'NO'}")
        logger.debug(f"[BOOT] WakeWordListener alive: {'YES' if self.wake_engine else 'NO'}")
        logger.debug("[BOOT] Shutdown event: NOT SET")
        logger.debug(f"[BOOT] Main thread alive: {'YES' if threading.current_thread() == threading.main_thread() else 'NO'}")
        logger.debug("[BOOT] entering persistent wait")
        logger.debug("[BOOT] main lifecycle alive")
        
        while self.is_active:
            try:
                current_state = self.turn_manager.get_state()
                
                # 1. Listen for wake word if sleeping
                if current_state == "SLEEPING":
                    logger.debug("[ConversationLoop] Waiting for wake word...")
                    time.sleep(0.5) # Prevent TTS echo from immediately triggering the wake word
                    audio_stream = self.audio.start_recording()
                    trigger = self.wake_engine.listen_for_wake_word(audio_stream)
                    logger.debug(f"[ConversationLoop] Wake word triggered by: {trigger}")
                    self.audio.stop_recording()  # CLEAR OLD BUFFER BEFORE LISTENING FOR SPEECH
                    
                    # Acknowledge the wake word naturally
                    self.turn_manager.set_state("SPEAKING")
                    audio_output = self.tts.synthesize("Yes?")
                    self._play_with_barge_in(audio_output)
                    
                    time.sleep(0.2) # Allow OS buffers to flush fully
                    self.turn_manager.set_state("LISTENING")
                
                # 2. Listen for speech
                elif current_state == "WAITING_FOR_USER" or current_state == "LISTENING":
                    current_turn_id = self.turn_manager.increment_turn()
                    logger.debug(f"[ConversationLoop] Listening for user command... (Turn {current_turn_id})")
                    self.turn_manager.set_state("LISTENING")
                    
                    audio_stream = self.audio.start_recording()
                    speech_audio = self.vad.detect_end_of_turn(audio_stream)
                    self.audio.stop_recording()
                    
                    if not speech_audio:
                        logger.debug("[ConversationLoop] No speech detected.")
                        # Let the turn manager handle timeout to SLEEPING on next loop
                        self.turn_manager.set_state("WAITING_FOR_USER")
                        continue
    
                    # 3. Think (STT + LLM via Orchestrator)
                    self.turn_manager.set_state("PROCESSING")
                    
                    # 2. SAVE A TEMPORARY DEBUG AUDIO SAMPLE
                    import wave
                    sample_rate = getattr(self.audio, 'rate', 16000)
                    channels = getattr(self.audio, 'channels', 1)
                    
                    with wave.open("debug_audio.wav", "wb") as wf:
                        wf.setnchannels(channels)
                        wf.setsampwidth(2) # 16-bit
                        wf.setframerate(sample_rate)
                        wf.writeframes(speech_audio)
                    logger.debug(f"[ConversationLoop] Saved debug_audio.wav ({len(speech_audio)} bytes)")
                        
                    stt_result = self.stt.transcribe(speech_audio, sample_rate=sample_rate, channels=channels)
                    
                    if isinstance(stt_result, dict):
                        transcript = stt_result.get("text", "")
                        confidence = stt_result.get("confidence", "LOW")
                    else:
                        transcript = stt_result
                        confidence = "UNKNOWN"
                        
                    logger.debug(f"[ConversationLoop] User said: {transcript} (Confidence: {confidence})")
                    
                    # STALE TURN CHECK #1: If turn rolled forward during STT, drop it
                    if not self.turn_manager.is_turn_active(current_turn_id):
                        logger.debug(f"[TurnGuard] Ignored stale STT result for turn {current_turn_id}")
                        continue
                    
                    if not transcript.strip():
                        logger.debug("[ConversationLoop] Empty transcript. Going back to sleep.")
                        self.turn_manager.set_state("SLEEPING")
                        continue
                        
                    if confidence == "LOW":
                        logger.debug("[ConversationLoop] Confidence too low. Asking for repetition.")
                        self.turn_manager.set_state("SPEAKING")
                        audio_output = self.tts.synthesize("I didn't catch that clearly. Could you repeat it?")
                        self._play_with_barge_in(audio_output)
                        self.turn_manager.set_state("WAITING_FOR_USER")
                        continue
                    
                    # Handle explicit shutdown commands directly
                    shutdown_phrases = ["close yourself", "shutdown astra", "exit astra", "shut down astra"]
                    if any(phrase in transcript.lower().strip().strip('.') for phrase in shutdown_phrases):
                        logger.user_facing("> " + transcript + "\n")
                        logger.user_facing("[System] Shutdown reason: USER_REQUESTED")
                        self.turn_manager.set_state("SPEAKING")
                        audio_output = self.tts.synthesize("Goodbye.")
                        self._play_with_barge_in(audio_output)
                        self.is_active = False
                        break
    
                    self.turn_manager.set_state("EXECUTING")
                    
                    if logger.is_debug():
                        logger.debug("\n============================================================")
                        logger.debug("7. END-OF-TURN DEBUGGING")
                        logger.debug("============================================================")
                        logger.debug(f"FINAL TRANSCRIPT: {transcript}")
                        logger.debug("DECISION: ACCEPT")
                        logger.debug("============================================================\n")
                    
                    logger.user_facing(f"> {transcript}\n")
                    
                    # Execute orchestrator
                    logger.debug(f"[TurnGuard] Executing Turn {current_turn_id}")
                    orchestrator_result = self.orchestrator.process_request({
                        "text": transcript,
                        "turn_id": current_turn_id
                    })
                    
                    # STALE TURN CHECK #2: Post-orchestration
                    if not self.turn_manager.is_turn_active(current_turn_id):
                        logger.debug(f"[TurnGuard] Ignored stale orchestrator result for turn {current_turn_id}")
                        continue
                    
                    if orchestrator_result.get("status") == "success":
                        response_text = orchestrator_result.get("result", "")
                        logger.user_facing(f"Astra:\n\"{response_text}\"\n")
                    else:
                        response_text = "I couldn't complete that."
                        logger.error(f"[ConversationLoop] Orchestrator failed: {orchestrator_result.get('message', 'Unknown error')}")
                        logger.user_facing(f"Astra:\n\"{response_text}\"\n")
                    
                    # 4. Speak
                    if response_text:
                        self.turn_manager.set_state("SPEAKING")
                        speech_payload = self.speech_manager.request_speech(response_text, priority="NORMAL", source="llm")
                        
                        if speech_payload:
                            audio_output = self.tts.synthesize(speech_payload["text"])
                            interrupted = self._play_with_barge_in(audio_output)
                            self.speech_manager.notify_speech_complete()
                            if interrupted:
                                logger.user_facing("[System: TTS Interrupted by user]\n")
                                self.turn_manager.increment_turn()
                                self.speech_manager.interrupt()
                                self.turn_manager.set_state("LISTENING")
                                continue
                            
                    # 5. Return to silent listening
                    self.turn_manager.set_state("WAITING_FOR_USER")
                    
            except Exception as e:
                import traceback
                logger.error(f"[ConversationLoop] Error during processing: {e}\n{traceback.format_exc()}")
                
                self.turn_manager.set_state("SPEAKING")
                audio_output = self.tts.synthesize("I encountered a system error, but I'm still listening.")
                self._play_with_barge_in(audio_output)
                self.turn_manager.set_state("LISTENING")
                
            time.sleep(0.1)

    def stop(self):
        self.is_active = False
