import pytest
from packages.core.cognitive_brain import CognitiveIntentEngine
from packages.core.application_registry import ApplicationRegistry
from packages.core.models import ConfidenceLevel

class MockRouter:
    def route_request(self, category, prompt, context):
        if "what is that" in prompt.lower():
            return '{"normalized_transcript": "What is on the screen?", "confidence": "HIGH", "reasoning": "Contextually referring to screen."}'
        elif "open the calendar" in prompt.lower():
            return '{"normalized_transcript": "open the calendar", "confidence": "LOW", "clarification_question": "Did you mean the Calendar app or something else?", "reasoning": "Ambiguous."}'
        return '{"normalized_transcript": "unknown", "confidence": "LOW", "clarification_question": "Can you repeat that?"}'

def test_local_fast_resolve():
    registry = ApplicationRegistry()
    engine = CognitiveIntentEngine(None, registry)
    
    # Phonetic
    res1 = engine.normalize("Open what's app.", {})
    assert res1.confidence == ConfidenceLevel.HIGH
    assert res1.normalized_transcript == "Open Whatsapp."
    
    # Exact alias
    res2 = engine.normalize("Can you please open calculator", {})
    assert res2.confidence == ConfidenceLevel.HIGH
    assert res2.normalized_transcript == "Open Calculator."
    
    # No match
    res3 = engine._local_fast_resolve("open some random app", "open some random app")
    assert res3 is None

def test_gemini_resolve():
    registry = ApplicationRegistry()
    router = MockRouter()
    engine = CognitiveIntentEngine(router, registry)
    
    # High confidence fallback
    res1 = engine.normalize("what is that?", {})
    assert res1.confidence == ConfidenceLevel.HIGH
    assert res1.normalized_transcript == "What is on the screen?"
    
    # Low confidence ambiguity
    res2 = engine.normalize("open the calendar", {})
    assert res2.confidence == ConfidenceLevel.LOW
    assert res2.clarification_question == "Did you mean the Calendar app or something else?"
