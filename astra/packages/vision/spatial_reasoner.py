from typing import Dict, Any

class SpatialReasoner:
    """
    Translates 2D bounding boxes into relative spatial descriptions.
    """
    def __init__(self, frame_width: int = 640, frame_height: int = 480):
        self.width = frame_width
        self.height = frame_height

    def determine_position(self, bbox: list[int]) -> str:
        """
        Takes [x1, y1, x2, y2] and returns a spatial string like "left", "center", "right".
        """
        x1, _, x2, _ = bbox
        center_x = (x1 + x2) / 2
        
        # Simple thirds logic
        if center_x < self.width / 3:
            return "left"
        elif center_x > 2 * self.width / 3:
            return "right"
        else:
            return "ahead"

    def analyze_object(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Adds spatial reasoning data to a detected object."""
        obj_copy = obj.copy()
        obj_copy["position"] = self.determine_position(obj["bbox"])
        return obj_copy
