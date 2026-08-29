import re
from typing import Dict, Any, Optional
from packages.core.models import TargetType
from packages.core.website_registry import WebsiteRegistry

class LocalActionClassifier:
    """
    Lightweight, deterministic local classifier for simple UI and general tasks.
    Avoids expensive LLM calls for operations like clicking, opening apps, or basic queries.
    Replaces FastIntentClassifier.
    """
    def __init__(self):
        self.website_registry = WebsiteRegistry()
        # Define strict regex patterns for high confidence
        # Ordering matters: more specific patterns first.
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
            "click": [
                r"^(?:in [a-zA-Z0-9\s]+ )?click (?:on )?(?:the )?(.+)$",
                r"^(?:in [a-zA-Z0-9\s]+ )?tap (?:on )?(?:the )?(.+)$",
                r"^(?:in [a-zA-Z0-9\s]+ )?select (?:the )?(.+)$",
                r"^(?:in [a-zA-Z0-9\s]+ )?put (?:my )?cursor in (?:the )?(.+)$"
            ],
            "type_message": [
                r"^type[\s]+(.+)$",
                r"^write[\s]+(.+)$",
                r"^enter[\s]+(.+)$"
            ],
            "press_key": [
                r"^press[\s]+(.+)$",
                r"^hit[\s]+(.+)$"
            ],
            "search": [
                r"^(?:search|look) for[\s]+(.+?)[\s]+(?:in|on)[\s]+(.+)$",
                r"^find[\s]+(.+?)[\s]+(?:in|on)[\s]+(.+)$",
                r"^(?:search|look) for[\s]+(.+)$",
                r"^find[\s]+(.+)$",
                r"^(?:can you |could you |please )?(?:search|look) for[\s]+(.+?)(?: please)?$"
            ],
            "calculation": [
                r"^(?:calculate|what is|whats)[\s]+(.+)$",
                r"^perform[\s]+([\d\.\s\+\-\*\/(times)(into)(multiplied by)]+)$",
                r"^([\d\.\s\+\-\*\/]+)$" # Just math
            ]
        }
        
    def classify(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to map natural language to a fast path deterministic command.
        Returns a structured dictionary if successful, or None if ambiguous/complex.
        """
        text_lower = text.lower().strip().strip('.?!')
        
        # We can handle "in app do x" by extracting context, but simple regex handles the rest
        # Reject complex patterns that need Agent Planner
        if " and " in text_lower or " then " in text_lower or " while " in text_lower:
            # Check if it's just "search for x and y" - actually, better to defer to AGENT_PATH for safety
            if not text_lower.startswith("calculate ") and not text_lower.startswith("perform "):
                return None 
            
        # Match against patterns
        for action, regex_list in self.patterns.items():
            for pattern in regex_list:
                match = re.match(pattern, text_lower)
                if match:
                    target_or_query = match.group(1).strip()
                    
                    if action in ["open_application", "close_application", "focus_application"]:
                        # Check if it's a known website
                        if action == "open_application" and self.website_registry.is_known_website(target_or_query):
                            website_info = self.website_registry.resolve_website(target_or_query)
                            return {
                                "action": "open_website",
                                "target": website_info,
                                "target_type": TargetType.WEBSITE.value
                            }
                            
                        return {
                            "action": action,
                            "target": target_or_query,
                            "target_type": TargetType.APPLICATION.value
                        }
                    elif action == "click":
                        # For "In WhatsApp click on search bar", we could extract "WhatsApp" if we made a better regex.
                        # For simplicity, if it matches "in X click Y", we parse it.
                        app_context = None
                        in_match = re.match(r"^in ([a-zA-Z0-9\s]+) (?:click|tap|select|put)", text_lower)
                        if in_match:
                            app_context = in_match.group(1).strip()
                            
                        # The regex group 1 is always the target
                        return {
                            "action": action,
                            "target": target_or_query,
                            "target_type": TargetType.UNKNOWN.value,
                            "context_requirements": [f"application:{app_context}"] if app_context else []
                        }
                    elif action == "type_message":
                        return {
                            "action": action,
                            "message": target_or_query,
                            "target_type": TargetType.UNKNOWN.value
                        }
                    elif action == "press_key":
                        return {
                            "action": action,
                            "command": target_or_query, # e.g. "enter"
                            "target_type": TargetType.UNKNOWN.value
                        }
                    elif action == "search":
                        # If the regex matched two groups (e.g., query + in application)
                        query_val = target_or_query
                        app_context = None
                        if match.lastindex and match.lastindex >= 2:
                            query_val = match.group(1).strip()
                            app_context = match.group(2).strip()
                            
                        return {
                            "action": action,
                            "query": query_val,
                            "target_type": TargetType.UNKNOWN.value,
                            "context_requirements": [f"application:{app_context}"] if app_context else []
                        }
                    elif action == "calculation":
                        return {
                            "action": "calculation",
                            "command": target_or_query,
                            "target_type": TargetType.UNKNOWN.value
                        }
                        
        # If no strict match, fallback to AGENT_PATH
        return None
