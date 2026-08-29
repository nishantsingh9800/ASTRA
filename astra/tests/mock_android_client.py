import json
import time
from typing import Dict, Any

class MockAndroidClient:
    """
    Simulates the Android client app connecting to the Astra Core.
    """
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.capabilities = ["camera", "gps", "haptics", "microphone"]
        # In this mock, the user denied camera permission but allowed GPS
        self.permissions = {"camera": False, "gps": True, "haptics": True, "microphone": True}
        
    def generate_pair_payload(self) -> str:
        """Generates the JSON payload to pair with the server."""
        payload = {
            "action": "pair",
            "device_id": self.device_id,
            "data": {
                "deviceName": "User's Pixel Phone",
                "platform": "Android",
                "capabilities": self.capabilities,
                "permissions": self.permissions
            }
        }
        return json.dumps(payload)

    def generate_sync_payload(self, key: str, value: Any) -> str:
        """Simulates the Android app pushing a state change."""
        payload = {
            "action": "sync_state",
            "device_id": self.device_id,
            "data": {
                "key": key,
                "value": value,
                "timestamp": time.time()
            }
        }
        return json.dumps(payload)
