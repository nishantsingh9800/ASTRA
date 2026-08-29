import json
import os
from typing import Dict, Any

class AccessibilityProfileManager:
    """
    Manages modular accessibility preferences and mode toggles.
    Persists configuration to a local JSON file to preserve privacy.
    """
    def __init__(self, config_path: str = "accessibility_profile.json"):
        self.config_path = config_path
        self._profile: Dict[str, Any] = self._load_profile()
        self._active_modes: Dict[str, bool] = {
            "focus_mode": False,
            "communication_mode": False,
            "study_mode": False,
            "step_by_step_mode": False,
            "simplification_mode": False
        }

    def _load_profile(self) -> Dict[str, Any]:
        """Loads profile from disk or returns defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "voice": True,
            "captions": False,
            "screen_reader": False,
            "camera_assistance": True,
            "ocr": True,
            "gesture": False,
            "sign_language": False,
            "aac": False,
            "switch_access": False,
            "eye_gaze": False,
            "haptic_feedback": True,
            "braille": False,
            "simplified_ui": False,
            "reading_mode": False
        }

    def save_profile(self) -> None:
        """Saves current profile to disk."""
        with open(self.config_path, "w") as f:
            json.dump(self._profile, f, indent=4)

    def set_feature(self, feature: str, enabled: bool) -> None:
        """Enables or disables a specific accessibility feature."""
        if feature in self._profile:
            self._profile[feature] = enabled
            self.save_profile()

    def get_feature(self, feature: str) -> bool:
        """Returns True if the feature is enabled."""
        return self._profile.get(feature, False)
        
    def toggle_mode(self, mode: str, enabled: bool) -> None:
        """Toggles temporary interaction modes (e.g., Focus Mode)."""
        if mode in self._active_modes:
            self._active_modes[mode] = enabled

    def get_mode(self, mode: str) -> bool:
        """Returns True if the mode is active."""
        return self._active_modes.get(mode, False)

    def delete_profile(self) -> None:
        """Deletes the local profile for privacy."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        self._profile = self._load_profile() # Reset to default
