import pytest
import os
from packages.adaptive.accessibility_profile_manager import AccessibilityProfileManager
from packages.adaptive.cognitive_support_service import CognitiveSupportService
from packages.adaptive.reading_assistant import ReadingAssistant
from packages.adaptive.notification_filter import NotificationFilter

def test_accessibility_profile_manager():
    manager = AccessibilityProfileManager(config_path="test_profile.json")
    
    # Test setting feature
    manager.set_feature("braille", True)
    assert manager.get_feature("braille") is True
    
    # Test toggling mode
    manager.toggle_mode("focus_mode", True)
    assert manager.get_mode("focus_mode") is True
    
    # Cleanup
    manager.delete_profile()
    assert not os.path.exists("test_profile.json")

def test_cognitive_support_service():
    service = CognitiveSupportService()
    
    steps = service.simplify_task("Submit assignment")
    assert len(steps) == 3
    
    assert service.get_next_step() == "Open assignment portal."
    assert service.get_next_step() == "Find course."
    assert service.repeat_last_step() == "Find course."
    
    assert "3rd-grade reading level" in service.get_injected_prompt(True)

def test_reading_assistant():
    assistant = ReadingAssistant()
    
    text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
    assistant.load_document("doc.txt", text)
    
    assert assistant.get_next_paragraph() == "Paragraph 1."
    
    state = assistant.get_current_state()
    assert state["position"] == 1
    assert state["total_paragraphs"] == 3

def test_notification_filter():
    manager = AccessibilityProfileManager(config_path="test_filter.json")
    filter = NotificationFilter(manager)
    
    # Normal mode - allow normal urgency
    assert filter.filter_notification("Ping", "Message", "NORMAL") is not None
    
    # Focus mode - drop normal urgency
    manager.toggle_mode("focus_mode", True)
    assert filter.filter_notification("Ping", "Message", "NORMAL") is None
    
    # Focus mode - allow critical
    assert filter.filter_notification("Fire", "Alarm", "CRITICAL") is not None
    
    manager.delete_profile()
