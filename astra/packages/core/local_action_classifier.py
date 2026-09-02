import re
from typing import Dict, Any, Optional
from packages.core.models import TargetType
from packages.core.website_registry import WebsiteRegistry

class LocalActionClassifier:
    """
    Lightweight, deterministic local classifier for UI, system, and web tasks.
    Enables instant offline execution without mandatory cloud LLM dependency.
    """
    def __init__(self):
        self.website_registry = WebsiteRegistry()
        
        self.patterns = {
            # YouTube search patterns (including compound "open youtube and search for X")
            "youtube_search": [
                r"^(?:open|launch|go to)[\s]+(?:the[\s]+)?(?:youtube|yt)[\s]+(?:and[\s]+)?(?:search|look)[\s]+(?:for[\s]+)?(.+)$",
                r"^(?:search|look)[\s]+(?:for[\s]+)?(.+?)[\s]+(?:on|in)[\s]+(?:the[\s]+)?(?:youtube|yt)$",
                r"^(?:search|look)[\s]+(?:the[\s]+)?(?:youtube|yt)[\s]+(?:for[\s]+)?(.+)$",
                r"^(?:play|watch)[\s]+(.+?)[\s]+(?:on|in)[\s]+(?:the[\s]+)?(?:youtube|yt)$",
                r"^(?:play|watch)[\s]+(.+)$"
            ],
            
            # Google / Web search patterns
            "web_search": [
                r"^(?:open|launch|go to)[\s]+(?:google|duckduckgo|bing)[\s]+(?:and[\s]+)?(?:search|look)[\s]+(?:for[\s]+)?(.+)$",
                r"^(?:search|look)[\s]+(?:for[\s]+)?(.+?)[\s]+(?:on|in)[\s]+(?:google|duckduckgo|bing)$",
                r"^(?:search|look)[\s]+(?:the[\s]+)?(?:google|duckduckgo|bing)[\s]+(?:for[\s]+)?(.+)$",
                r"^(?:google|web search|search web for)[\s]+(.+)$",
                r"^(?:search|look) for[\s]+(.+)$",
                r"^(?:can you |could you |please )?(?:search|look) for[\s]+(.+?)(?: please)?$"
            ],
            
            # System utilities (Time, Date, Screenshot, Volume)
            "get_time": [
                r"^(?:what is |what's |tell me )?(?:the )?(?:current )?time(?: is it)?(?:\s+now)?$",
                r"^time$"
            ],
            "get_date": [
                r"^(?:what is |what's |tell me )?(?:the )?(?:today's |current )?date(?: is it)?(?:\s+today)?$",
                r"^date$"
            ],
            "take_screenshot": [
                r"^(?:take|capture|grab)[\s]+(?:a[\s]+)?(?:screenshot|screen capture|screen|snapshot)$",
                r"^screenshot$"
            ],
            "volume_control": [
                r"^(mute|unmute)[\s]+(?:the[\s]+)?volume$",
                r"^(increase|raise|turn up|decrease|lower|turn down)[\s]+(?:the[\s]+)?volume$"
            ],
            
            # Application and website open commands
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
            
            # UI actions
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
            "calculation": [
                r"^(?:open|launch|start)[\s]+(?:calculator|calc)[\s]+(?:and[\s]+)?(?:calculate|solve|do)[\s]+(.+)$",
                r"^(?:calculate|what is|whats|solve|compute)[\s]+(.+)$",
                r"^perform[\s]+([\d\.\s\+\-\*\/(times)(into)(plus)(minus)(multiplied by)(divided by)]+)$",
                r"^([\d\.\s\+\-\*\/x\^]+)$"
            ]
        }
        
    def classify(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to map natural language to a fast path deterministic command.
        Returns a structured dictionary if successful, or None if ambiguous/complex.
        """
        text_lower = text.lower().strip().strip('.?!')
        
        # Check specific patterns in order of specificity
        for action, regex_list in self.patterns.items():
            for pattern in regex_list:
                match = re.match(pattern, text_lower)
                if match:
                    # Match group extracting
                    target_or_query = match.group(1).strip() if match.groups() else ""
                    
                    if action == "youtube_search":
                        return {
                            "action": "youtube_search",
                            "query": target_or_query,
                            "target_type": TargetType.WEBSITE.value,
                            "target": "youtube"
                        }
                    elif action == "web_search":
                        return {
                            "action": "web_search",
                            "query": target_or_query,
                            "target_type": TargetType.WEB.value
                        }
                    elif action == "get_time":
                        return {
                            "action": "get_time",
                            "target_type": TargetType.UNKNOWN.value
                        }
                    elif action == "get_date":
                        return {
                            "action": "get_date",
                            "target_type": TargetType.UNKNOWN.value
                        }
                    elif action == "take_screenshot":
                        return {
                            "action": "take_screenshot",
                            "target_type": TargetType.UNKNOWN.value
                        }
                    elif action == "volume_control":
                        return {
                            "action": "volume_control",
                            "command": target_or_query,
                            "target_type": TargetType.UNKNOWN.value
                        }
                    
                    elif any(text_lower.startswith(prefix) for prefix in ["type ", "press ", "click ", "scroll ", "perform "]):
                        return {
                            "action": "perform_ui_action",
                            "command": text_lower,
                            "target_type": TargetType.UNKNOWN.value
                        }

                    elif action in ["open_application", "close_application", "focus_application"]:
                        # Remove "the " prefix if user said "open the calculator"
                        if target_or_query.startswith("the "):
                            target_or_query = target_or_query[4:].strip()
                            
                        # Check if user wants to open all applications
                        if action == "open_application" and (
                            target_or_query.lower() in ["all", "all applications", "all apps", "all the applications", "all application", "all the apps", "all the application", "all of them", "everything", "all my apps", "every app", "every application"] or
                            "all application" in text_lower or "all apps" in text_lower or "all the apps" in text_lower or "all the applications" in text_lower
                        ):
                            return {
                                "action": "open_all_applications",
                                "target": "all",
                                "target_type": TargetType.APPLICATION.value
                            }
                            
                        # Check if user wants to close all applications
                        if action == "close_application" and (
                            target_or_query.lower() in ["all", "all applications", "all apps", "all the applications", "all application", "everything", "all of them"] or
                            "all application" in text_lower or "all apps" in text_lower
                        ):
                            return {
                                "action": "close_all_applications",
                                "target": "all",
                                "target_type": TargetType.APPLICATION.value
                            }

                        # Check if it's a known website
                        if action == "open_application" and self.website_registry.is_known_website(target_or_query):
                            website_info = self.website_registry.resolve_website(target_or_query)
                            return {
                                "action": "open_website",
                                "target": website_info,
                                "target_type": TargetType.WEBSITE.value
                            }
                            
                        # Check if multiple applications are requested (e.g. "notepad and calculator", "chrome, calc, and notepad")
                        if action == "open_application" and (" and " in target_or_query or "," in target_or_query or " & " in target_or_query):
                            return {
                                "action": "open_multiple_applications",
                                "target": target_or_query,
                                "target_type": TargetType.APPLICATION.value
                            }
                            
                        return {
                            "action": action,
                            "target": target_or_query,
                            "target_type": TargetType.APPLICATION.value
                        }
                    elif action == "click":
                        app_context = None
                        in_match = re.match(r"^in ([a-zA-Z0-9\s]+) (?:click|tap|select|put)", text_lower)
                        if in_match:
                            app_context = in_match.group(1).strip()
                            
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
                            "command": target_or_query,
                            "target_type": TargetType.UNKNOWN.value
                        }
                    elif action == "calculation":
                        return {
                            "action": "calculation",
                            "command": target_or_query,
                            "target_type": TargetType.UNKNOWN.value
                        }
                        
        return None
