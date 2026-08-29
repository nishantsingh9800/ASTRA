from typing import Any, Dict
from packages.safety.emergency_state_manager import EmergencyStateManager, EmergencyState

class SafetyEngine:
    """
    Central controller for the safety subsystem.
    Listens to the AccidentDetector and user inputs to drive the state machine.
    """
    def __init__(self, state_manager: EmergencyStateManager, countdown_seconds: int = 20):
        self.state_manager = state_manager
        self.countdown_seconds = countdown_seconds
        self._countdown_remaining = 0

    def trigger_incident(self, confidence: float, evidence: list) -> None:
        """Called when AccidentDetector finds a credible threat."""
        if confidence > 0.8:
            self.state_manager.transition_to(EmergencyState.POSSIBLE_INCIDENT)
            self.state_manager.transition_to(EmergencyState.VERIFYING)
            # In a real loop, this would trigger TTS: "Are you okay?"

    def start_countdown(self) -> None:
        """Begins the countdown if no user response."""
        self.state_manager.transition_to(EmergencyState.COUNTDOWN)
        self._countdown_remaining = self.countdown_seconds

    def process_user_input(self, normalized_intent: Dict[str, Any]) -> None:
        """
        Receives normalized intents (from Voice, Sign, AAC).
        Allows cancellation.
        """
        intent = normalized_intent.get("intent")
        current_state = self.state_manager.get_state()
        
        if current_state in [EmergencyState.VERIFYING, EmergencyState.COUNTDOWN]:
            if intent in ["cancel_emergency", "confirm_safe"]:
                self.state_manager.transition_to(EmergencyState.CANCELLED)
                self.state_manager.transition_to(EmergencyState.NORMAL)
            elif intent == "trigger_sos":
                self.state_manager.transition_to(EmergencyState.ESCALATING)

    def escalate(self) -> None:
        """Forces escalation (e.g. countdown expired or silent SOS)."""
        self.state_manager.transition_to(EmergencyState.ESCALATING)
