from typing import Dict, Any, Optional
from packages.adaptive.accessibility_profile_manager import AccessibilityProfileManager

class NotificationFilter:
    """
    Intercepts incoming system alerts and filters them based on the Accessibility Profile.
    Classifies urgency.
    """
    def __init__(self, profile_manager: AccessibilityProfileManager):
        self.profile = profile_manager

    def filter_notification(self, title: str, content: str, urgency: str) -> Optional[Dict[str, Any]]:
        """
        Returns the notification if it should be spoken/displayed, otherwise None.
        Urgency levels: BACKGROUND, LOW, NORMAL, HIGH, CRITICAL
        """
        if self.profile.get_mode("focus_mode"):
            if urgency in ["BACKGROUND", "LOW", "NORMAL"]:
                return None # Drop non-critical in focus mode
                
        # Example environmental filter (from Phase 4)
        if "obstacle" in content.lower() and urgency == "HIGH":
            return {"title": title, "content": content, "urgency": urgency}
            
        # Default allow
        return {"title": title, "content": content, "urgency": urgency}
