from typing import Dict, Any

class AdaptiveInputManager:
    """
    Normalizes disparate inputs (Voice, Sign, AAC, Gesture) into a unified NormalizedUserIntent.
    Ensures the downstream Orchestrator does not need to care about the input modality.
    """
    def __init__(self):
        pass

    def normalize_input(self, source: str, raw_data: Any, confidence: float = 1.0) -> Dict[str, Any]:
        """
        Converts raw input from various modalities into a standard intent dictionary.
        """
        intent_payload = {
            "source": source,
            "confidence": confidence,
            "intent": "unknown",
            "target": None,
            "raw": raw_data
        }
        
        # Simple mock intent extraction for Phase 5 scaffolding
        if isinstance(raw_data, str):
            text = raw_data.lower()
            if "open" in text:
                intent_payload["intent"] = "open_application"
                # very naive extraction for test
                parts = text.split("open")
                if len(parts) > 1:
                    intent_payload["target"] = parts[1].strip()
            elif "help" in text:
                intent_payload["intent"] = "request_help"
            else:
                intent_payload["intent"] = "conversation"
                
        return intent_payload
