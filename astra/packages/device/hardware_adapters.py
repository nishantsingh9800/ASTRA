import time
from typing import Dict, Any, List

class DeviceAdapter:
    """Base interface for all hardware adapters."""
    def __init__(self, device_id: str, name: str, platform: str):
        self.device_id = device_id
        self.name = name
        self.platform = platform
        self.capabilities: List[str] = []
        self.is_connected = False

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self.is_connected = False

    def request_capability(self, capability: str) -> Any:
        raise NotImplementedError

class MockGlassesAdapter(DeviceAdapter):
    """Simulates Smart Glasses (HARDWARE_INTEGRATION_PENDING)"""
    def __init__(self, device_id: str):
        super().__init__(device_id, "Smart Glasses Mock", "Wearable")
        self.capabilities = ["CAMERA", "MICROPHONE", "SPEAKER", "DISPLAY"]
        
    def request_capability(self, capability: str) -> Any:
        if not self.is_connected:
            return None
        if capability == "CAMERA":
            return {"status": "success", "frame": "mock_glasses_frame_data", "timestamp": time.time()}
        return None

class MockWearableAdapter(DeviceAdapter):
    """Simulates a wrist wearable/sensor node (HARDWARE_INTEGRATION_PENDING)"""
    def __init__(self, device_id: str):
        super().__init__(device_id, "Wrist Wearable Mock", "Wearable")
        self.capabilities = ["IMU", "HAPTICS", "HEART_RATE"]
        
    def request_capability(self, capability: str) -> Any:
        if not self.is_connected:
            return None
        if capability == "IMU":
            return {
                "sensor": "IMU",
                "value": {"accel": [0.0, 9.81, 0.0], "gyro": [0.0, 0.0, 0.0]},
                "unit": "m/s2, rad/s",
                "timestamp": time.time(),
                "accuracy": "high",
                "deviceId": self.device_id
            }
        return None
