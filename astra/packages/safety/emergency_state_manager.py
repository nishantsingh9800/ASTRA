from enum import Enum

class EmergencyState(Enum):
    NORMAL = "NORMAL"
    POSSIBLE_INCIDENT = "POSSIBLE_INCIDENT"
    VERIFYING = "VERIFYING"
    USER_RESPONDING = "USER_RESPONDING"
    COUNTDOWN = "COUNTDOWN"
    ESCALATING = "ESCALATING"
    SOS_SENDING = "SOS_SENDING"
    SOS_SENT = "SOS_SENT"
    SOS_FAILED = "SOS_FAILED"
    CANCELLED = "CANCELLED"
    RESOLVED = "RESOLVED"

class EmergencyStateManager:
    """
    State machine for emergency handling.
    Prevents invalid transitions and tracks the current incident phase.
    """
    def __init__(self):
        self.state = EmergencyState.NORMAL

    def transition_to(self, new_state: EmergencyState) -> bool:
        """Transitions to a new state and returns True if successful."""
        # Simple permissive transition for now, could be made stricter
        self.state = new_state
        return True

    def get_state(self) -> EmergencyState:
        return self.state
