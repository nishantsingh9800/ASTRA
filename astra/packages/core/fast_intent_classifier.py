import re
from typing import Dict, Any, Optional
from packages.core.models import Intent, TargetType

class FastIntentClassifier:
    """
    Lightweight, deterministic local classifier for simple tasks.
    Avoids expensive LLM calls for operations like opening apps or basic queries.
    """
    def __init__(self):
        # Define strict regex patterns for high confidence
        self.patterns = {
            "open_application": [
                r"^(?:open|launch|start|run|go to)[\s]+(.+)$",
                r"^(?:can you |could you |please )?(?:open|launch|start|run|go to)[\s]+(.+?)(?: please)?$"
            ],
            "close_application": [
                r"^(?:close|kill|stop|terminate|exit)[\s]+(.+)$",
                r"^(?:can you |could you |please )?(?:close|kill|stop|terminate|exit)[\s]+(.+?)(?: please)?$"
            ],
            "focus_application": [
                r"^(?:focus|switch to|bring up)[\s]+(.+)$"
            ],
            "calculation": [
                r"^(?:calculate|what is|whats)[\s]+(.+)$",
                r"^([\d\.\s\+\-\*\/]+)$" # Just math
            ]
        }
        
    def classify(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to map natural language to a fast path deterministic command.
        Returns a structured dictionary if successful, or None if ambiguous/complex.
        """
        text_lower = text.lower().strip().strip('.?!')
        
        # Reject complex patterns
        if " and " in text_lower or " then " in text_lower or " while " in text_lower or " search " in text_lower:
            return None # Complex multi-step task or search, defer to AGENT_PATH
            
        # Match against patterns
        for action, regex_list in self.patterns.items():
            for pattern in regex_list:
                match = re.match(pattern, text_lower)
                if match:
                    target_or_query = match.group(1).strip()
                    
                    # For apps, we need a clean target
                    if action in ["open_application", "close_application", "focus_application"]:
                        return {
                            "action": action,
                            "target": target_or_query,
                            "target_type": TargetType.APPLICATION.value
                        }
                    elif action == "calculation":
                        return {
                            "action": "calculation",
                            "command": target_or_query,
                            "target_type": TargetType.UNKNOWN.value
                        }
                        
        # If no strict match, fallback to AGENT_PATH
        return None
