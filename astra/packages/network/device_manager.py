import time
from typing import Dict, Any, Optional

class DeviceManager:
    """
    Maintains a registry of connected devices and their capabilities.
    Enforces per-device permissions.
    """
    def __init__(self):
        self._devices: Dict[str, Dict[str, Any]] = {}
        # Core desktop agent is implicitly registered
        self._devices["local_core"] = {
            "deviceName": "Laptop Astra",
            "platform": "Windows",
            "onlineStatus": True,
            "capabilities": ["screen", "microphone", "computerControl"],
            "permissions": {"screen": True, "microphone": True, "computerControl": True},
            "lastSeen": time.time()
        }

    def register_device(self, device_id: str, payload: Dict[str, Any]) -> None:
        """Registers a remote device (e.g. Android client)."""
        self._devices[device_id] = {
            "deviceName": payload.get("deviceName", "Unknown Device"),
            "platform": payload.get("platform", "Unknown"),
            "onlineStatus": True,
            "capabilities": payload.get("capabilities", []),
            "permissions": payload.get("permissions", {}),
            "lastSeen": time.time()
        }

    def update_heartbeat(self, device_id: str) -> None:
        if device_id in self._devices:
            self._devices[device_id]["lastSeen"] = time.time()
            self._devices[device_id]["onlineStatus"] = True

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        return self._devices.get(device_id)

    def check_permission(self, device_id: str, capability: str) -> bool:
        """
        Returns True if the requested capability is explicitly permitted for the device.
        """
        device = self.get_device(device_id)
        if not device:
            return False
            
        if capability not in device["capabilities"]:
            return False
            
        return device["permissions"].get(capability, False)

    def get_all_devices(self) -> Dict[str, Dict[str, Any]]:
        return self._devices
