import pytest
from packages.accessibility.adaptive_input_manager import AdaptiveInputManager
from packages.accessibility.communication_manager import CommunicationManager
from packages.accessibility.sign_language_service import SignLanguageService, MockISLProvider
from packages.accessibility.gesture_service import GestureService
from packages.accessibility.aac_service import AACService

def test_adaptive_input_normalization():
    manager = AdaptiveInputManager()
    
    # Test text input normalization
    text_intent = manager.normalize_input("text", "Open Calculator", 1.0)
    assert text_intent["intent"] == "open_application"
    assert text_intent["target"] == "calculator"
    assert text_intent["source"] == "text"
    
    # Test AAC input normalization
    aac_intent = manager.normalize_input("aac", "open youtube", 1.0)
    assert aac_intent["intent"] == "open_application"
    assert "youtube" in aac_intent["target"]
    assert aac_intent["source"] == "aac"
    
def test_communication_manager_routing():
    comm = CommunicationManager()
    
    # Default profile: text, voice, visual
    response = comm.route_response("Calculator is open.")
    assert "text" in response["channels"]
    assert "voice" in response["channels"]
    assert "visual" in response["channels"]
    assert "sign" not in response["channels"]
    
    # Enable sign profile
    comm.update_profile({"sign": True})
    response_with_sign = comm.route_response("Hello")
    assert "sign" in response_with_sign["channels"]
    assert response_with_sign["payloads"]["sign"]["sign_sequence_request"] == "Hello"

def test_sign_language_service():
    provider = MockISLProvider()
    service = SignLanguageService(provider)
    
    # Add dummy landmarks
    for _ in range(15):
        service.add_frame([0, 1, 2])
        
    result = service.analyze_sequence()
    assert result == "open youtube"

def test_aac_service():
    aac = AACService()
    aac.select_word("I")
    
    predictions = aac.get_predictions()
    assert "need" in predictions
    
    aac.select_word("need")
    aac.select_word("help")
    
    assert aac.construct_message() == "I need help"
