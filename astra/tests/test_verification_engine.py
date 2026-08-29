from typing import Any, Dict, Tuple

class SimpleVerificationEngine:
    def verify_action(self, action_type: str, expected_state: Dict[str, Any], timeout: float = 5.0) -> Tuple[bool, str]:
        # For testing, we'll just check if a magic key 'success' is True
        if expected_state.get('success'):
            return True, "State matched expected conditions."
        return False, "Failed to verify state."

def test_verification_success():
    engine = SimpleVerificationEngine()
    success, reason = engine.verify_action("dummy_action", {"success": True})
    assert success is True

def test_verification_failure():
    engine = SimpleVerificationEngine()
    success, reason = engine.verify_action("dummy_action", {"success": False})
    assert success is False
    assert reason == "Failed to verify state."
