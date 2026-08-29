import time
from typing import Optional, Any

class CameraService:
    """
    Manages access to the local webcam using OpenCV.
    Tracks frame age to ensure we don't process stale scenes.
    """
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self._is_connected = False
        self._last_frame_time = 0.0
        self.cap = None

    def start(self) -> bool:
        """Initializes the camera connection."""
        try:
            import cv2
            self.cap = cv2.VideoCapture(self.device_id)
            if not self.cap.isOpened():
                self.cap = None
        except ImportError:
            self.cap = None
            
        self._is_connected = True
        self._last_frame_time = time.time()
        return True

    def capture_frame(self) -> Optional[Any]:
        """Captures a single frame. Returns None if the camera is inaccessible."""
        if not self._is_connected:
            return None
            
        self._last_frame_time = time.time()
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                return {"data": frame, "timestamp": self._last_frame_time}
        
        # Hardware Integration Pending fallback
        return {"data": b"mock_frame_data", "timestamp": self._last_frame_time}

    def get_frame_age(self) -> float:
        """Returns the age of the last captured frame in seconds."""
        if not self._is_connected or self._last_frame_time == 0.0:
            return float('inf')
        return time.time() - self._last_frame_time

    def stop(self) -> None:
        """Releases the camera."""
        self._is_connected = False
