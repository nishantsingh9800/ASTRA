import time
import pytest
from packages.voice.speech_manager import SpeechManager
from packages.core.conversation_turn_manager import ConversationTurnManager

def test_speech_manager_deduplication():
    manager = SpeechManager()
    
    # First message should pass
    res1 = manager.request_speech("YouTube is open.")
    assert res1 is not None
    manager.notify_speech_complete()
    
    # Second identical message within 5s should be dropped
    res2 = manager.request_speech("YouTube is open.")
    assert res2 is None
    
    # Different message should pass
    res3 = manager.request_speech("Calculator is open.")
    assert res3 is not None
    manager.notify_speech_complete()

def test_speech_manager_internal_events():
    manager = SpeechManager()
    
    # Normal internal event should be dropped
    res1 = manager.request_speech("Web query executed.", is_internal=True)
    assert res1 is None
    
    # DEBUG internal event should be dropped in NORMAL verbosity (default is dropped because priority="DEBUG" is filtered)
    res2 = manager.request_speech("Web query executed.", priority="DEBUG", is_internal=True)
    assert res2 is None
    
    # Explicit user result should pass
    res3 = manager.request_speech("I found five results.")
    assert res3 is not None
    manager.notify_speech_complete()

def test_speech_manager_priority_interruption():
    manager = SpeechManager()
    
    # Start speaking a normal message
    res1 = manager.request_speech("I found some results...")
    assert res1 is not None
    
    # A low priority message comes in, should be dropped
    res2 = manager.request_speech("Battery is at 90%", priority="LOW")
    assert res2 is None
    
    # A critical message comes in, should interrupt
    res3 = manager.request_speech("Fire alarm detected!", priority="CRITICAL")
    assert res3 is not None
    
def test_conversation_turn_manager_states():
    manager = ConversationTurnManager()
    
    assert manager.get_state() == "IDLE"
    
    manager.set_state("LISTENING")
    assert manager.get_state() == "LISTENING"
    
    manager.set_state("WAITING_FOR_USER")
    assert manager.get_state() == "WAITING_FOR_USER"
    
    # Simulate time passing for timeout (mocking time module would be better, but we can just test the timeout value)
    manager._last_activity_time = time.time() - 20 # 20 seconds ago
    assert manager.get_state() == "SLEEPING"
