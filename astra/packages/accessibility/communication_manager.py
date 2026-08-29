from typing import List, Dict, Any

class CommunicationManager:
    """
    Unified multimodal output routing system.
    Determines how to deliver the Orchestrator's response back to the user based on their Accessibility Profile.
    """
    def __init__(self):
        self._active_profile = {
            "voice": True,
            "text": True,
            "sign": False,
            "visual": True
        }

    def update_profile(self, profile: Dict[str, bool]) -> None:
        """Updates the active modalities for output."""
        self._active_profile.update(profile)

    def route_response(self, text_response: str) -> Dict[str, Any]:
        """
        Takes the internal text response from the Astra core and routes it to the configured output channels.
        """
        output = {
            "channels": [],
            "payloads": {}
        }

        if self._active_profile.get("text"):
            output["channels"].append("text")
            output["payloads"]["text"] = text_response

        if self._active_profile.get("voice"):
            output["channels"].append("voice")
            output["payloads"]["voice"] = {"text_to_speak": text_response}

        if self._active_profile.get("visual"):
            output["channels"].append("visual")
            output["payloads"]["visual"] = {"display_alert": text_response}

        if self._active_profile.get("sign"):
            output["channels"].append("sign")
            # In a full implementation, this triggers the SignLanguageOutputProvider (Avatar)
            output["payloads"]["sign"] = {"sign_sequence_request": text_response}

        return output
