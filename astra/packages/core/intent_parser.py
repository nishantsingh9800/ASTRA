import json
from typing import Dict, Any, List
from packages.core.models import Intent, TargetType, TaskGraph, Task, TaskStatus, TaskPriority
from packages.ai.model_router import ModelRouter

class IntentParser:
    """
    Parses natural language into a structured Intent object.
    Ensures that targets like YOUTUBE are preserved explicitly.
    """
    def __init__(self, router: ModelRouter):
        self.router = router

    def parse(self, text: str, context: Dict[str, Any]) -> Intent:
        prompt = f"""
        You are an NLU engine for ASTRA.
        Extract the explicit user intent from the text into a structured JSON format.
        
        Text: "{text}"
        Current Context: {json.dumps(context)}
        
        Valid TargetTypes: {', '.join([t.value for t in TargetType])}
        
        RULES:
        1. "Search YouTube for X" -> action: "search", target_type: "WEBSITE", query: "X", target: "youtube"
        2. "Search this page for X" -> action: "search", target_type: "CURRENT_PAGE", query: "X"
        3. "Open WhatsApp" -> action: "open_application", target_type: "APPLICATION", target: "WhatsApp"
        4. "Open YouTube" -> action: "open_website", target_type: "WEBSITE", target: "youtube"
        5. "Open Chrome" -> action: "open_application", target_type: "BROWSER", target: "Chrome"
        6. What is ahead?" -> action: "query_vision", target_type: "UNKNOWN"
        7. Do NOT guess generic WEB if the user specified a specific site (WEBSITE) or app (APPLICATION).
        
        Output ONLY valid JSON matching this structure:
        {{
            "action": "<string>",
            "target_type": "<TargetType>",
            "target": "<string or null>",
            "query": "<string or null>",
            "context_requirements": ["list", "of", "required", "contexts"]
        }}
        """
        
        try:
            # We route this specifically as a 'simple' classification task. 
            # In real offline operation, this could map to a fast local model.
            response = self.router.route_request("simple", prompt, {})
            
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                from packages.core import logger
                logger.debug(f"[IntentParser] Provider returned non-JSON: {response}")
                return Intent(
                    action="unknown",
                    target_type=TargetType.UNKNOWN,
                    raw_text=text
                )

            # Check if this is a structured error from the provider
            if isinstance(data, dict) and data.get("status") == "error":
                from packages.core import logger
                logger.debug(f"[IntentParser] Provider error: {data}")
                return Intent(
                    action="provider_error",
                    target_type=TargetType.UNKNOWN,
                    raw_text=data.get("message", "Unknown provider error")
                )
            
            # Map string back to Enum safely
            t_type_str = data.get("target_type", "UNKNOWN")
            try:
                t_type = TargetType[t_type_str.upper()]
            except KeyError:
                t_type = TargetType.UNKNOWN
                
            return Intent(
                action=data.get("action", "unknown"),
                target_type=t_type,
                target=data.get("target"),
                query=data.get("query"),
                context_requirements=data.get("context_requirements", []),
                raw_text=text
            )
        except Exception as e:
            print(f"[IntentParser] Failed to parse intent: {e}")
            return Intent(
                action="unknown",
                target_type=TargetType.UNKNOWN,
                raw_text=text
            )

    def parse_graph(self, text: str, context: Dict[str, Any]) -> TaskGraph:
        """
        Parses a complex multi-task query into a TaskGraph.
        """
        prompt = f"""
        You are an NLU engine for ASTRA.
        The user has provided a complex request that may contain multiple tasks.
        Decompose the request into independent and dependent tasks.
        Identify the resources required for each task (e.g. 'browser', 'WhatsApp', 'calculator').
        Identify dependencies (if Task B needs Task A to finish first, list Task A's ID in Task B's dependencies).
        
        Text: "{text}"
        Current Context: {json.dumps(context)}
        
        Output ONLY valid JSON matching this structure:
        {{
            "tasks": [
                {{
                    "task_id": "T1",
                    "goal": "string describing what to do",
                    "action": "open_application, open_website, calculation, web_search, contact_search, send_message, etc",
                    "target_type": "WEB, WEBSITE, APPLICATION, BROWSER, etc",
                    "target": "WhatsApp, youtube, etc",
                    "query": "search term or person name (e.g. Kishan)",
                    "command": "math expression if calculation",
                    "message": "message to type",
                    "priority": "NORMAL",
                    "dependencies": [],
                    "resources": ["WhatsApp"]
                }}
            ]
        }}
        
        CRITICAL RULE FOR CONTACT SEARCH / SEND MESSAGE:
        If sending a message or searching a person on an app, `target` is the application (e.g. "WhatsApp"), and `query` MUST contain the person's name (e.g. "Kishan"). Do NOT leave `query` blank. If no message is provided, leave `message` blank.
        """
        
        graph = TaskGraph()
        try:
            response = self.router.route_request("complex", prompt, {})
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                from packages.core import logger
                logger.error(f"[IntentParser] Non-JSON from parse_graph: {response}")
                return graph
                
            if isinstance(data, dict) and data.get("status") == "error":
                # Provider error
                error_task = Task(
                    task_id="error",
                    goal=data.get("message", "My AI service isn't available right now."),
                    action="provider_error",
                    target_type=TargetType.UNKNOWN,
                    status=TaskStatus.FAILED,
                    priority=TaskPriority.NORMAL
                )
                graph.add_task(error_task)
                return graph
                
            tasks_data = data.get("tasks", [])
            for t_data in tasks_data:
                t_type_str = t_data.get("target_type", "UNKNOWN")
                try:
                    t_type = TargetType[t_type_str.upper()]
                except KeyError:
                    t_type = TargetType.UNKNOWN
                    
                priority_str = t_data.get("priority", "NORMAL")
                try:
                    priority = TaskPriority[priority_str.upper()]
                except KeyError:
                    priority = TaskPriority.NORMAL
                
                task = Task(
                    task_id=t_data.get("task_id", "T_unknown"),
                    goal=t_data.get("goal", ""),
                    action=t_data.get("action", "unknown"),
                    target_type=t_type,
                    target=t_data.get("target"),
                    query=t_data.get("query"),
                    command=t_data.get("command"),
                    message=t_data.get("message"),
                    status=TaskStatus.PENDING,
                    priority=priority,
                    dependencies=t_data.get("dependencies", []),
                    resources=t_data.get("resources", [])
                )
                graph.add_task(task)
                
            return graph
        except Exception as e:
            print(f"[IntentParser] Failed to parse task graph: {e}")
            return graph

