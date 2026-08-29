from typing import Dict, Any
from packages.device.capability_manager import CapabilityManager

class AstraSelfKnowledge:
    """
    Registry for dynamic runtime state generation.
    Prevents Astra from hallucinating features or hardware states during demonstrations.
    """
    def __init__(self, capability_manager: CapabilityManager):
        self.capability_manager = capability_manager
        # We would normally inject ModelRouter and ConnectivityManager here as well
        
    def generate_runtime_snapshot(self) -> Dict[str, Any]:
        """
        Gathers live data from the system rather than using static prompts.
        """
        connected_devices = self.capability_manager.get_connected_devices()
        
        has_glasses = any("Glasses" in d for d in connected_devices)
        has_wearable = any("Wearable" in d for d in connected_devices)
        
        return {
            "identity": "ASTRA 2.0",
            "architecture": "Device-independent, multimodal agent backed by Gemini API.",
            "current_platform": "Windows (Core)",
            "connected_devices": connected_devices,
            "smart_glasses_status": "Active" if has_glasses else "Not connected",
            "wearable_status": "Active" if has_wearable else "Not connected",
            "offline_capabilities": "Enabled (Local TTS, STT, Wake Word)",
            "current_phase": "Phase 10: Advanced Agents",
            "known_limitations": "Does not silently execute destructive actions. Requires explicit hardware permissions."
        }
