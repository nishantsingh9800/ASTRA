from typing import Dict, Any, List

class VisionConfidenceManager:
    """
    Enforces the 'Absolute No-Guess Rule'.
    Filters out low-confidence detections and translates uncertain states.
    """
    def __init__(self, confidence_threshold: float = 0.6):
        self.confidence_threshold = confidence_threshold

    def filter_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes detections below the confidence threshold."""
        return [d for d in detections if d.get("confidence", 0.0) >= self.confidence_threshold]

    def format_scene_response(self, validated_objects: List[Dict[str, Any]], camera_health: bool = True) -> str:
        """
        Formats the final response based on validated, high-confidence objects.
        Adheres to uncertainty fallback if camera health is bad.
        """
        if not camera_health:
            return "Sorry, I can't tell what's ahead right now."
            
        if not validated_objects:
            # We don't say "path is clear" because absence of detection != safety
            return "I don't detect any specific objects right now."
            
        descriptions = []
        for obj in validated_objects:
            descriptions.append(f"a {obj['class']} to the {obj.get('position', 'unknown')}")
            
        return f"I see {', '.join(descriptions)}."
