from typing import Dict, Any, Optional
import time

class LocationService:
    """
    Provides location context.
    Currently a mock abstraction for local desktop testing.
    """
    def __init__(self, mock: bool = True):
        self.mock = mock
        self._last_known = {
            "lat": 37.7749,
            "lon": -122.4194,
            "accuracy_meters": 15.0,
            "timestamp": time.time(),
            "source": "mock_gps"
        }

    def get_current_location(self) -> Optional[Dict[str, Any]]:
        """
        Returns location if accuracy is acceptable and location sharing is permitted.
        """
        # In a real implementation, this would check permissions and OS APIs.
        if self._last_known["accuracy_meters"] > 100.0:
            return None # Do not report precise location when accuracy is poor
            
        # Update timestamp to simulate fresh reading
        self._last_known["timestamp"] = time.time()
        return self._last_known
