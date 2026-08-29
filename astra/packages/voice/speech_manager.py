import time
from enum import Enum
from typing import Dict, Any, Optional, List
from packages.core import logger

class AcknowledgementPolicy(Enum):
    NONE = "NONE"
    SHORT = "SHORT"
    REQUIRED = "REQUIRED"

class SpeechManager:
    """
    Centralized authority for all spoken output across the ASTRA ecosystem.
    Controls queue, priority, interruption, deduplication, and verbosity.
    """
    def __init__(self):
        self._is_speaking = False
        self._current_priority = "LOW"
        self._priority_levels = {"DEBUG": 0, "BACKGROUND": 1, "LOW": 2, "NORMAL": 3, "HIGH": 4, "CRITICAL": 5}
        
        self._history: List[Dict[str, Any]] = []
        self._dedup_window = 5.0 # seconds
        
        self._verbosity = "NORMAL" # Can be CONCISE, NORMAL, DETAILED
        self._ack_policy = AcknowledgementPolicy.NONE

    def set_verbosity(self, level: str):
        self._verbosity = level

    def set_acknowledgement_policy(self, policy: AcknowledgementPolicy):
        self._ack_policy = policy

    def generate_acknowledgement(self, transcript: str) -> Optional[str]:
        """
        Generates an acknowledgement based on policy and transcript.
        Returns None if no acknowledgement is needed.
        """
        if self._ack_policy == AcknowledgementPolicy.NONE:
            return None
            
        if self._ack_policy == AcknowledgementPolicy.SHORT:
            return "Okay."
            
        if self._ack_policy == AcknowledgementPolicy.REQUIRED:
            return "Understood."
            
        return None

    def request_speech(self, text: str, priority: str = "NORMAL", target_device: str = "local_core", source: str = "general", is_internal: bool = False) -> Optional[Dict[str, Any]]:
        """
        Evaluates if the speech should be spoken based on current priority, deduplication, and verbosity state.
        Returns the payload to send to the target device if approved, else None.
        """
        req_level = self._priority_levels.get(priority, 2)
        cur_level = self._priority_levels.get(self._current_priority, 2)
        
        # 1. Filter internal events
        if is_internal and priority != "DEBUG":
            logger.debug(f"[SpeechManager] Dropped internal event: '{text}'")
            return None
            
        # 2. Filter DEBUG in normal usage
        if priority == "DEBUG":
            logger.debug(f"[SpeechManager] Dropped DEBUG message: '{text}'")
            return None
            
        # 3. Deduplication (don't repeat the exact same text within 5 seconds)
        current_time = time.time()
        for past_msg in reversed(self._history):
            if current_time - past_msg["timestamp"] > self._dedup_window:
                break
            if past_msg["text"] == text:
                logger.debug(f"[SpeechManager] Dropped duplicate speech: '{text}'")
                return None

        # 4. Priority Override / Interruption
        # If we are already speaking something more important, drop this request (unless critical)
        if self._is_speaking and req_level <= cur_level and req_level < self._priority_levels["CRITICAL"]:
            logger.debug(f"[SpeechManager] Dropped speech request '{text}' due to priority constraints (Currently speaking {self._current_priority}).")
            return None
            
        if self._is_speaking and req_level > cur_level:
            logger.debug(f"[SpeechManager] INTERRUPTING current speech for priority {priority}!")
            # In a real system, send a stop signal to TTS before continuing
            
        self._is_speaking = True
        self._current_priority = priority
        
        payload = {
            "action": "play_speech",
            "target_device": target_device,
            "text": text,
            "priority": priority,
            "timestamp": current_time
        }
        
        self._history.append(payload)
        
        logger.debug(f"[SpeechManager] Authorized speech for {target_device} (Priority: {priority}): {text}")
        return payload
        
    def notify_speech_complete(self):
        self._is_speaking = False
        self._current_priority = "LOW"
        
    def interrupt(self):
        """Called when User starts speaking to stop Astra."""
        if self._is_speaking:
            logger.debug("[SpeechManager] Speech INTERRUPTED by user barge-in.")
            self._is_speaking = False
            self._current_priority = "LOW"
            
    def cancel_current_speech(self):
        """Cancels all active speech states (alias for interrupt)."""
        self.interrupt()
