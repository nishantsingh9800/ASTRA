import time

class ConversationTurnManager:
    """
    Manages turn-taking across all devices in the ecosystem.
    Prevents duplicate responses if both devices are active simultaneously.
    Implements a rigorous state machine to enforce conversational flow.
    """
    STATES = ["IDLE", "LISTENING", "PROCESSING", "EXECUTING", "SPEAKING", "INTERRUPTED", "WAITING_FOR_USER", "SLEEPING"]
    
    def __init__(self):
        self._active_device = "local_core"
        self._current_state = "IDLE"
        self._last_activity_time = time.time()
        self._inactivity_timeout = 15.0 # seconds
        self._current_turn_id = 1

    def increment_turn(self) -> int:
        """Forces the conversation to roll forward, invalidating previous pending actions."""
        self._current_turn_id += 1
        print(f"[TurnManager] Turn rolled forward to: {self._current_turn_id}")
        return self._current_turn_id
        
    def get_current_turn_id(self) -> int:
        """Returns the active conversation turn ID."""
        return self._current_turn_id
        
    def is_turn_active(self, turn_id: int) -> bool:
        """Checks if a given turn ID is still the active turn."""
        return turn_id == self._current_turn_id

    def set_state(self, new_state: str) -> bool:
        if new_state not in self.STATES:
            return False
            
        print(f"[TurnManager] State change: {self._current_state} -> {new_state}")
        self._current_state = new_state
        self._last_activity_time = time.time()
        return True
        
    def get_state(self) -> str:
        # Check for timeout if we are waiting for the user
        if self._current_state == "WAITING_FOR_USER":
            if time.time() - self._last_activity_time > self._inactivity_timeout:
                print("[TurnManager] Inactivity timeout reached. Dropping to SLEEPING.")
                self.set_state("SLEEPING")
                
        return self._current_state

    def set_active_device(self, device_id: str) -> None:
        """Sets the primary interaction endpoint."""
        self._active_device = device_id
        
    def get_active_device(self) -> str:
        return self._active_device

    def should_process_input(self, device_id: str) -> bool:
        """
        Determines if the given device should be allowed to drive the conversation.
        """
        return device_id == self._active_device

