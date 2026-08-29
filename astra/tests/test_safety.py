import pytest
from packages.safety.emergency_state_manager import EmergencyStateManager, EmergencyState
from packages.safety.safety_engine import SafetyEngine
from packages.safety.accident_detector import AccidentDetector
from packages.safety.sos_manager import SOSManager

def test_accident_detector_multi_signal():
    detector = AccidentDetector()
    
    # Single signal (weak)
    detector.receive_signal("camera", "fall_detected", 0.7)
    result1 = detector.evaluate_evidence()
    assert result1["confidence"] < 0.8
    assert result1["event"] == "unconfirmed_event"
    
    # Corroborating signal (strong)
    detector.receive_signal("accelerometer", "impact", 0.9)
    result2 = detector.evaluate_evidence()
    assert result2["confidence"] > 0.8
    assert result2["event"] == "possible_fall"
    assert "impact" in result2["evidence"]

def test_safety_engine_cancellation():
    state = EmergencyStateManager()
    engine = SafetyEngine(state)
    
    # Trigger verifying state
    state.transition_to(EmergencyState.VERIFYING)
    
    # User says "Cancel" via any modality
    engine.process_user_input({"intent": "cancel_emergency"})
    
    assert state.get_state() == EmergencyState.NORMAL

def test_sos_manager_verification():
    state = EmergencyStateManager()
    
    # Test successful dispatch
    manager_success = SOSManager(state, mock_fail=False)
    assert manager_success.dispatch_sos({"type": "fall"}) is True
    assert state.get_state() == EmergencyState.SOS_SENT
    
    # Test failed dispatch
    manager_fail = SOSManager(state, mock_fail=True)
    assert manager_fail.dispatch_sos({"type": "fall"}) is False
    assert state.get_state() == EmergencyState.SOS_FAILED
