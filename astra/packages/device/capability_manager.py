from typing import Dict, Any, Optional, List
from packages.device.hardware_adapters import DeviceAdapter

class CapabilityManager:
    """
    Routes abstract capability requests (e.g. CAMERA) to the best available authorized device.
    """
    def __init__(self):
        self._devices: List[DeviceAdapter] = []
        # Default priority: Glasses > Phone > Laptop
        self._priorities = {
            "Smart Glasses Mock": 1,
            "Phone Mock": 2,
            "Laptop Mock": 3,
            "Wrist Wearable Mock": 1
        }

    def register_device(self, adapter: DeviceAdapter):
        self._devices.append(adapter)

    def request_capability(self, capability: str) -> Optional[Any]:
        """
        Finds the highest priority connected device with the capability and routes the request.
        """
        capable_devices = [
            dev for dev in self._devices 
            if dev.is_connected and capability in dev.capabilities
        ]
        
        if not capable_devices:
            print(f"[CapabilityManager] No connected device provides capability: {capability}")
            return None
            
        # Sort by priority (lower number is higher priority)
        capable_devices.sort(key=lambda d: self._priorities.get(d.name, 99))
        
        best_device = capable_devices[0]
        print(f"[CapabilityManager] Routing {capability} request to {best_device.name}")
        return best_device.request_capability(capability)
        
    def get_connected_devices(self) -> List[str]:
        return [dev.name for dev in self._devices if dev.is_connected]
