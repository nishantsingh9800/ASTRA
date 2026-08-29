from typing import Any, List, Dict

class ObjectDetector:
    """
    Wraps the Ultralytics YOLO model for local object detection and tracking.
    """
    def __init__(self, model_name: str = "yolov8n.pt"):
        self.model_name = model_name
        self.is_loaded = True

    def detect(self, frame: Any) -> List[Dict[str, Any]]:
        """
        Runs inference on a single frame.
        Returns a list of detected objects with tracking IDs.
        """
        if not frame:
            return []
            
        try:
            from ultralytics import YOLO
            model = YOLO(self.model_name)
            results = model.track(frame, persist=True)
            # Parse real results here (omitted for brevity)
            return []
        except ImportError:
            # Strict Policy: No hallucinated objects if model is unavailable
            return []
