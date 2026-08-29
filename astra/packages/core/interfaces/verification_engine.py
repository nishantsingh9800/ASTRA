from typing import Protocol, Any, Dict, Tuple

class VerificationEngine(Protocol):
    """
    Enforces the fundamental architectural rule: The AI's statement is NEVER proof that something happened.
    Only verified real-world state establishes success.
    """
    def verify_action(self, action_type: str, expected_state: Dict[str, Any], timeout: float = 5.0) -> Tuple[bool, str]:
        """
        Verify that an action actually had the expected effect on the system/world.
        Returns a tuple of (is_successful, reason_if_failed).
        """
        ...
