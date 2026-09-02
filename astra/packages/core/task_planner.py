from typing import Dict, Any, List
from packages.agents.base_agent import AstraAgent
from packages.core.models import Intent, TargetType, FailureCategory

class TaskPlanner:
    """
    Implements the autonomous task loop: GOAL -> PLAN -> EXECUTE -> VERIFY -> REPLAN
    Upgraded for ASTRA 2.0 to enforce strict Intent parsing and Verification.
    """
    def __init__(self, agents: List[AstraAgent], router=None, context_manager=None, verification_engine=None):
        self.agents = agents
        self.router = router
        self.context_manager = context_manager
        self.verification_engine = verification_engine
        self.current_plan: List[Dict[str, Any]] = []
        
    def _route_to_agent(self, action: str, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Finds the appropriate specialized agent for the task step."""
        for agent in self.agents:
            if agent.can_handle(action):
                return agent.execute(step, context)
                
        print(f"[TaskPlanner] No specialized agent found for {action}. Executing generically.")
        return {"status": "error", "verification": {"passed": False}, "details": f"No agent can handle {action}."}

    def execute_goal(self, intent: Intent, context: Dict[str, Any], turn_id: int = 0) -> Dict[str, Any]:
        """
        The autonomous execution loop (ReAct).
        Expects a structured Intent rather than raw text.
        """
        import json
        import time
        results = []
        max_steps = 5
        step_count = 0

        if isinstance(intent, str):
            intent = Intent(action="execute", target_type=TargetType.UNKNOWN, raw_text=intent)

        while step_count < max_steps:
            step_count += 1
            print(f"\n[TaskPlanner] --- Step {step_count} ---")
            
            if self.context_manager:
                self.context_manager.refresh_context()
                context = self.context_manager.get_context()
            
            # Fast fail if provider error occurred during intent parsing
            if intent.action == "provider_error":
                print(f"[TaskPlanner] Intent parsing failed due to provider error: {intent.raw_text}")
                return {
                    "intent": intent.to_dict(),
                    "results": results,
                    "final_response": "My AI service isn't available right now.",
                    "status": "FAILED"
                }
                
            if self.router:
                # STALE TURN CHECK BEFORE AI CALL
                if getattr(self, "turn_manager", None) and not self.turn_manager.is_turn_active(turn_id):
                    print(f"[TurnGuard] Ignored stale task execution step for turn {turn_id}")
                    return {
                        "intent": intent.to_dict(),
                        "results": results,
                        "final_response": "I stopped that task.",
                        "status": "CANCELLED"
                    }
                    
                prompt = f"""
                You are ASTRA, an autonomous agent.
                Goal Intent: {json.dumps(intent.to_dict())}
                Current Context: {json.dumps(context)}
                Observation History: {json.dumps(results, indent=2)}
                
                Decide the next action to take to achieve the goal.
                If you need to use a tool, output a single JSON object:
                {{"type": "tool_call", "action": "<action_name>", "target": "<target>", "query": "<query>", "command": "<command>"}}
                
                Valid tool actions:
                - "open_application" (target: name)
                - "close_application" (target: name)
                - "focus_application" (target: name)
                - "calculation" (command: math expression)
                - "open_website" (target: website name or url)
                - "youtube_search" (query: exact search term)
                - "website_search" (target: website name, query: exact search term)
                - "browser_search_current_page" (query: exact search term)
                - "web_search" (query: exact search term)
                - "file_search" (query: exact search term)
                - "contact_search" (target: app name, query: person name)
                - "type_message" (target: app name, message: string to type)
                
                IMPORTANT RULES:
                1. You MUST respect the intent.target_type! If intent.target_type is WEBSITE, you MUST use "website_search", "youtube_search", or "open_website" with target name.
                2. Do NOT use web_search (which searches DuckDuckGo/Google) if a specific target (like YouTube, Wikipedia) is requested. 
                3. Always specify the target explicitly if required by the tool.
                4. CRITICAL: If the intent involves sending a message to a contact, but no message text is provided in the Intent or Context, DO NOT invent a message. You must output a JSON response asking the user "What would you like me to send?" and STOP.
                
                If the goal has been fully achieved or cannot be achieved, or if you need to ask the user a clarifying question (like the message body), output a single JSON object with your final conversational response to the user:
                {{"type": "response", "text": "Your natural language response here."}}
                
                Output ONLY valid JSON. Do not add conversational text outside the JSON.
                """
                
                try:
                    response_text = self.router.route_request("complex", prompt, {})
                    action_json = json.loads(response_text)
                    
                    if action_json.get("status") == "error" and action_json.get("provider") == "gemini":
                        print(f"[TaskPlanner] Provider error during planning: {action_json.get('message')}")
                        return {
                            "intent": intent.to_dict(),
                            "results": results,
                            "final_response": "My AI service isn't available right now.",
                            "status": "FAILED"
                        }
                    
                    msg_type = action_json.get("type")
                    if msg_type == "response":
                        print(f"[TaskPlanner] Final Response Reached: {action_json.get('text')}")
                        
                        # Determine if this was actually successful or if it's a failure response
                        # If we have tool results and the last one failed, it's a failure.
                        # If intent was unknown, it's a failure.
                        # Determine if this was actually successful or if it's a failure response
                        is_success = True
                        if intent.action in ["unknown", "provider_error"]:
                            is_success = False
                        
                        # If any tool in the chain failed and wasn't recovered, it's likely a failure
                        if results and results[-1].get("result", {}).get("status") == "error":
                            is_success = False
                        
                        # Semantic check of the response
                        final_text = action_json.get("text", "")
                        lower_text = final_text.lower()
                        failure_keywords = ["could not", "couldn't", "failed", "error", "issue", "sorry, i cannot", "unable to", "don't know"]
                        if any(k in lower_text for k in failure_keywords):
                            is_success = False
                            
                        return {
                            "intent": intent.to_dict(),
                            "results": results,
                            "final_response": action_json.get("text"),
                            "status": "COMPLETED" if is_success else "FAILED"
                        }
                    elif msg_type == "tool_call":
                        action_name = action_json.get("action")
                        
                        # PLAN VALIDATION
                        if intent.target_type == TargetType.WEBSITE and action_name == "web_search":
                            print("[TaskPlanner] Plan Validation Failed: Cannot substitute web_search for WEBSITE intent.")
                            if intent.target and "youtube" in str(intent.target).lower():
                                action_name = "youtube_search"
                            else:
                                action_name = "website_search"
                            action_json["action"] = action_name
                            
                        # STALE TURN CHECK BEFORE EXECUTION
                        if getattr(self, "turn_manager", None) and not self.turn_manager.is_turn_active(turn_id):
                            print(f"[TurnGuard] Ignored stale tool call {action_name} for turn {turn_id}")
                            return {
                                "intent": intent.to_dict(),
                                "results": results,
                                "final_response": "I cancelled the previous task.",
                                "status": "CANCELLED"
                            }
                            
                        print(f"[TaskPlanner] Decided tool call: {action_name}")
                        step_result = self._route_to_agent(action_name, action_json, context)
                        
                        # EXTERNAL VERIFICATION ENGINE
                        if self.verification_engine:
                            v_passed, v_details = self.verification_engine.verify_action(action_name, action_json)
                            if not v_passed:
                                step_result["status"] = "error"
                                step_result["failure_category"] = FailureCategory.VERIFICATION_FAILURE.value
                                step_result["details"] = v_details
                            else:
                                step_result["status"] = "success"
                                step_result["verification"] = {"passed": True, "details": v_details}
                                
                        # Store in history
                        results.append({
                            "tool_call": action_json,
                            "result": step_result
                        })
                        
                        # Update context
                        context[f"last_action"] = action_name
                        if step_result.get("status") == "success":
                            print(f"[TaskPlanner] Tool {action_name} succeeded.")
                            
                            # Preserve Target Context across loop steps
                            if action_name in ["open_website", "open_application", "focus_application"]:
                                context["active_page"] = action_json.get("target")
                                context["active_target"] = action_json.get("target")
                                
                            if self.context_manager:
                                self.context_manager.refresh_context()
                        else:
                            print(f"[TaskPlanner] Tool {action_name} failed. Attempting recovery next turn.")
                            time.sleep(1) # Backoff
                            
                    else:
                        print(f"[TaskPlanner] Unrecognized JSON format: {action_json}")
                        return {
                            "intent": intent.to_dict(),
                            "results": results,
                            "final_response": "I couldn't process the plan for that task.",
                            "status": "FAILED"
                        }
                        
                except json.JSONDecodeError as e:
                    print(f"[TaskPlanner] Non-JSON response from planner: {response_text}")
                    return {
                        "intent": intent.to_dict(),
                        "results": results,
                        "final_response": "I encountered an error understanding the plan.",
                        "status": "FAILED"
                    }
                except Exception as e:
                    print(f"[TaskPlanner] Error parsing ReAct step: {e}")
                    return {
                        "intent": intent.to_dict(),
                        "results": results,
                        "final_response": "I encountered a system issue while planning.",
                        "status": "FAILED"
                    }
            else:
                # Mock fallback
                break
                
        return {
            "intent": intent.to_dict(),
            "results": results,
            "final_response": "I encountered an issue and could not complete the task.",
            "status": "FAILED"
        }
