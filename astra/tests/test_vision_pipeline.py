import pytest
from packages.vision.scene_manager import SceneManager
from packages.vision.spatial_reasoner import SpatialReasoner

def test_scene_manager_temporal_validation():
    # Require 2 hits to validate, 2 misses to drop
    manager = SceneManager(required_hits=2, max_misses=2)
    
    # Frame 1: Detection of chair (id 1)
    detections = [{"id": 1, "class": "chair", "confidence": 0.9}]
    manager.update_scene(detections)
    
    # Still unvalidated (hits = 1)
    assert len(manager.get_validated_scene()) == 0
    
    # Frame 2: Detection of chair again
    manager.update_scene(detections)
    
    # Validated (hits = 2)
    validated = manager.get_validated_scene()
    assert len(validated) == 1
    assert validated[0]["class"] == "chair"
    
    # Frame 3: Miss (empty detections)
    manager.update_scene([])
    
    # Still validated (misses = 1)
    assert len(manager.get_validated_scene()) == 1
    
    # Frame 4: Miss again
    manager.update_scene([])
    
    # Dropped (misses = 2 >= max_misses)
    assert len(manager.get_validated_scene()) == 0

def test_spatial_reasoner():
    reasoner = SpatialReasoner(frame_width=640, frame_height=480)
    
    # Center X = 100 (< 213) -> left
    left_bbox = [50, 100, 150, 200]
    assert reasoner.determine_position(left_bbox) == "left"
    
    # Center X = 500 (> 426) -> right
    right_bbox = [450, 100, 550, 200]
    assert reasoner.determine_position(right_bbox) == "right"
    
    # Center X = 320 (middle) -> ahead
    ahead_bbox = [250, 100, 390, 200]
    assert reasoner.determine_position(ahead_bbox) == "ahead"
