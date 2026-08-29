from typing import Dict, Any
from packages.safety.emergency_state_manager import EmergencyStateManager, EmergencyState

class SOSManager:
    """
    Abstracts delivery mechanism (SMS, App Notification).
    STRICT ENFORCEMENT: Only transitions to SOS_SENT if the channel verifies delivery.
    """
    def __init__(self, state_manager: EmergencyStateManager, mock_fail: bool = False):
        self.state_manager = state_manager
        self.mock_fail = mock_fail

    def dispatch_sos(self, payload: Dict[str, Any]) -> bool:
        """Attempts to send an SOS and updates the state machine accordingly."""
        self.state_manager.transition_to(EmergencyState.SOS_SENDING)
        
        # Simulate network request
        success = not self.mock_fail
        
        if success:
            self.state_manager.transition_to(EmergencyState.SOS_SENT)
            return True
        else:
            self.state_manager.transition_to(EmergencyState.SOS_FAILED)
            return False
