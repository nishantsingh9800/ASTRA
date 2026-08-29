import time
from typing import List, Dict, Any

class SceneManager:
    """
    Maintains the authoritative state of the physical environment.
    Applies temporal validation to prevent hallucinating objects from single noisy frames.
    """
    def __init__(self, required_hits: int = 3, max_misses: int = 5):
        self.required_hits = required_hits
        self.max_misses = max_misses
        # dict of object ID to state: {"hits": int, "misses": int, "data": Dict}
        self._tracked_objects: Dict[int, Dict[str, Any]] = {}
        self.last_update_time = 0.0

    def update_scene(self, detected_objects: List[Dict[str, Any]]) -> None:
        """Updates internal scene state based on new frame detections."""
        current_ids = {obj["id"] for obj in detected_objects}
        
        # 1. Update existing and add new
        for obj in detected_objects:
            obj_id = obj["id"]
            if obj_id in self._tracked_objects:
                self._tracked_objects[obj_id]["hits"] += 1
                self._tracked_objects[obj_id]["misses"] = 0
                self._tracked_objects[obj_id]["data"] = obj
            else:
                self._tracked_objects[obj_id] = {"hits": 1, "misses": 0, "data": obj}
                
        # 2. Increment misses for objects not seen
        for tracked_id in list(self._tracked_objects.keys()):
            if tracked_id not in current_ids:
                self._tracked_objects[tracked_id]["misses"] += 1
                if self._tracked_objects[tracked_id]["misses"] >= self.max_misses:
                    del self._tracked_objects[tracked_id]
                    
        self.last_update_time = time.time()

    def get_validated_scene(self) -> List[Dict[str, Any]]:
        """Returns only objects that have passed the temporal threshold."""
        return [
            track["data"] 
            for track in self._tracked_objects.values() 
            if track["hits"] >= self.required_hits
        ]
