from typing import Dict, Any, Optional
from packages.presentation.astra_self_knowledge import AstraSelfKnowledge

class PresentationModeManager:
    """
    Manages the 'Judge Mode' or 'Presentation Mode'.
    When active, intercepts questions about Astra and formats the response using live data.
    Also enables DemoSafeMode.
    """
    def __init__(self, self_knowledge: AstraSelfKnowledge):
        self.self_knowledge = self_knowledge
        self.is_presentation_mode = False
        self.demo_safe_mode_active = False

    def activate_mode(self):
        print("[PresentationManager] ACTIVATING PRESENTATION / JUDGE MODE.")
        self.is_presentation_mode = True
        self.demo_safe_mode_active = True
        
    def deactivate_mode(self):
        print("[PresentationManager] DEACTIVATING PRESENTATION / JUDGE MODE.")
        self.is_presentation_mode = False
        self.demo_safe_mode_active = False

    def handle_judge_question(self, question: str) -> Optional[str]:
        """
        Intercepts questions about Astra itself and formulates a truthful, runtime-grounded response.
        Returns None if the question is not a judge question.
        """
        if not self.is_presentation_mode:
            return None
            
        q_lower = question.lower()
        snapshot = self.self_knowledge.generate_runtime_snapshot()
        
        if "what are you" in q_lower or "what is astra" in q_lower:
            return f"I am {snapshot['identity']}, a {snapshot['architecture']}"
            
        if "offline" in q_lower:
            return f"Yes, my offline capabilities are: {snapshot['offline_capabilities']}."
            
        if "smart glasses" in q_lower:
            status = snapshot['smart_glasses_status']
            if status == "Active":
                return "Yes, smart glasses are currently connected and active."
            return "Smart-glass support is implemented at the device architecture level, but no smart-glass device is currently connected."
            
        if "what devices" in q_lower:
            devices = ", ".join(snapshot['connected_devices']) if snapshot['connected_devices'] else "none"
            return f"Currently connected devices: {devices}."
            
        if "limitation" in q_lower or "safety" in q_lower:
            return f"My known limitations: {snapshot['known_limitations']}"
            
        return None

    def check_safe_mode(self, action: str) -> bool:
        """
        In DemoSafeMode, all destructive or external communication actions are rejected.
        """
        if self.demo_safe_mode_active:
            unsafe_actions = ["delete_file", "overwrite_config", "send_email", "send_message", "commit_code"]
            if action in unsafe_actions:
                print(f"[DemoSafeMode] BLOCKED unsafe action '{action}' during presentation.")
                return False
        return True
