from typing import Dict, Any
from packages.core.interfaces.orchestrator import CoreOrchestrator as CoreOrchestratorInterface
from packages.core.task_planner import TaskPlanner
from packages.ai.model_router import ModelRouter
from packages.core.intent_parser import IntentParser
from packages.core.context_manager import ContextManagerImpl
from packages.device.verification_engine_impl import VerificationEngineImpl
from packages.core.local_action_classifier import LocalActionClassifier
from packages.core.application_registry import ApplicationRegistry
from packages.agents.specialized_agents import OSAgent
from packages.core.cognitive_brain import CognitiveIntentEngine
from packages.core.entity_resolver import EntityResolver
from packages.core.models import ConfidenceLevel

class CoreOrchestrator(CoreOrchestratorInterface):
    """
    Central brain of ASTRA 2.0. Manages the lifecycle of requests.
    Upgraded to use strict Intent Parsing and Context Refreshing.
    """
    def __init__(self, router: ModelRouter, planner: TaskPlanner = None, turn_manager=None):
        self.router = router
        self.planner = planner
        self.turn_manager = turn_manager
        self.intent_parser = IntentParser(router)
        self.context_manager = ContextManagerImpl()
        self.verification_engine = VerificationEngineImpl()
        self.fast_classifier = LocalActionClassifier()
        self.app_registry = ApplicationRegistry()
        self.os_agent = OSAgent()
        self.cognitive_brain = CognitiveIntentEngine(router, self.app_registry)
        self.entity_resolver = EntityResolver()
        
        # Inject dependencies into planner if not already set
        if self.planner:
            if not self.planner.context_manager:
                self.planner.context_manager = self.context_manager
            if not self.planner.verification_engine:
                self.planner.verification_engine = self.verification_engine
            if self.turn_manager:
                self.planner.turn_manager = self.turn_manager

    def process_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming request from the user/UI.
        Validates the request, determines intent, delegates to TaskManager, and returns the verified result.
        """
        print(f"[Orchestrator] Processing request: {input_data}")
        text = input_data.get("text", "")
        turn_id = input_data.get("turn_id", 0)
        
        if self.planner and text:
            # 1. Refresh global context
            self.context_manager.refresh_context()
            current_context = self.context_manager.get_context()
            
            # 2. Cognitive Brain Normalization
            from packages.core import logger
            cognitive_result = self.cognitive_brain.normalize(text, current_context)
            
            logger.debug("\n--- COGNITIVE TRACE ---")
            logger.debug(f"RAW: {cognitive_result.raw_transcript}")
            logger.debug(f"NORMALIZED: {cognitive_result.normalized_transcript}")
            logger.debug(f"CONFIDENCE: {cognitive_result.confidence.value}")
            logger.debug(f"REASONING: {cognitive_result.reasoning}")
            logger.debug("-----------------------")
            
            # Capture cognitive clarification but don't immediately fail.
            pending_clarification = None
            if cognitive_result.confidence == ConfidenceLevel.LOW or cognitive_result.clarification_question:
                pending_clarification = cognitive_result.clarification_question or "I didn't quite catch that. Could you clarify?"
                # DO NOT RETURN YET - Let LocalActionClassifier and Agent Path attempt it
                
            text = cognitive_result.normalized_transcript
            
            # 2.5 Entity Resolution
            resolved_entities, text, entity_confidence, entity_clarification = self.entity_resolver.resolve(text, current_context)
            
            # If Entity Resolver has a hard ambiguity (e.g., "Kishan Singh or Kishan Gupta?")
            if entity_confidence == ConfidenceLevel.LOW and entity_clarification:
                return {"status": "success", "result": entity_clarification}
            
            # STALE TURN CHECK
            if self.turn_manager and not self.turn_manager.is_turn_active(turn_id):
                return {"status": "error", "message": "Turn superseded during cognitive processing."}
            
            # 3. Fast Path Check
            fast_action = self.fast_classifier.classify(text)
            if fast_action:
                print(f"[Orchestrator] FAST PATH selected: {fast_action}")
                original_target = fast_action.get("target")
                
                if original_target:
                    # Only resolve target if it is a single app command
                    if fast_action.get("action") == "open_application" and isinstance(original_target, str):
                        fast_action["target"] = self.app_registry.resolve(original_target)
                
                step_result = self.os_agent.execute(fast_action, current_context)
                
                is_success = False
                final_response = "I encountered an issue."
                if self.verification_engine:
                    # Restore original target for verification to check window title properly
                    verification_action = fast_action.copy()
                    if original_target:
                        verification_action["target"] = original_target
                        
                    v_passed, v_details = self.verification_engine.verify_action(fast_action["action"], verification_action)
                    if v_passed:
                        is_success = True
                        if fast_action["action"] == "open_application":
                             final_response = f"{str(original_target).title()} is open."
                        elif fast_action["action"] in ["open_all_applications", "open_multiple_applications"]:
                             final_response = step_result.get("result") or step_result.get("message") or "Applications opened."
                        elif fast_action["action"] == "close_all_applications":
                             final_response = step_result.get("result") or step_result.get("message") or "Applications closed."
                        elif fast_action["action"] == "open_website":
                             target_name = fast_action.get("target", {}).get("name", "Website") if isinstance(fast_action.get("target"), dict) else str(fast_action.get("target", "Website"))
                             final_response = f"{target_name.title()} is opened."
                        elif fast_action["action"] == "youtube_search":
                             final_response = f"Searching YouTube for '{fast_action.get('query')}'."
                        elif fast_action["action"] == "web_search":
                             final_response = f"Searching the web for '{fast_action.get('query')}'."
                        elif fast_action["action"] in ["get_time", "get_date", "take_screenshot", "volume_control"]:
                             final_response = step_result.get("result", "Done.")
                        elif fast_action["action"] == "close_application":
                             final_response = f"{str(original_target).title()} is closed."
                        elif fast_action["action"] == "calculation":
                             final_response = f"The answer is {step_result.get('result', '')}"
                        elif fast_action["action"] == "click":
                             final_response = "Done."
                        elif fast_action["action"] == "type_message":
                             final_response = "Typed."
                        elif fast_action["action"] == "search":
                             final_response = "Searching."
                        else:
                             final_response = step_result.get("result") or step_result.get("message") or "Done."
                    else:
                        is_success = False
                        final_response = f"I tried to execute the command, but verification failed: {v_details}"
                else:
                    is_success = step_result.get("status") in ["dispatched", "success"]
                    final_response = "Done."
                    
                execution_report = {
                    "intent": fast_action,
                    "results": [{"tool_call": fast_action, "result": step_result}],
                    "final_response": final_response,
                    "status": "COMPLETED" if is_success else "FAILED",
                    "path": "FAST_PATH"
                }
                return {"status": "success", "result": final_response, "execution_report": execution_report}
            
            # 3. Extract Intent explicitly (AGENT PATH)
            text_lower = text.lower()
            if " and " in text_lower or " then " in text_lower or " while " in text_lower:
                # MULTI TASK PATH
                print("[Orchestrator] MULTI-TASK PATH detected.")
                task_graph = self.intent_parser.parse_graph(text, current_context)
                
                # Execute using TaskManager
                from packages.core.task_manager import TaskManager
                self.task_manager = TaskManager(max_parallel_tasks=1) # Strictly serialized to prevent UI/focus race conditions
                
                def _planner_callback(task):
                    # We can't directly use command/message on Intent, so we can embed in raw_text or just use it.
                    intent = Intent(
                        action=task.action, 
                        target_type=task.target_type, 
                        target=task.target, 
                        query=task.query or task.command or task.message, 
                        raw_text=task.goal
                    )
                    # Create isolated context for task
                    task_context = current_context.copy()
                    return self.planner.execute_goal(intent, context=task_context, turn_id=turn_id)
                
                # Check stale turn before launching task graph
                if self.turn_manager and not self.turn_manager.is_turn_active(turn_id):
                    return {"status": "error", "message": "Turn superseded before multi-task execution."}
                    
                execution_report = self.task_manager.execute_graph(task_graph, _planner_callback)
                
                # Aggregate response
                results = execution_report.get("task_results", {})
                success_goals = []
                failed_goals = []
                for tid, res in results.items():
                    if res.get("status") == "COMPLETED":
                        if res.get("result") and res.get("result") != "Done.":
                            success_goals.append(res.get("result"))
                        else:
                            success_goals.append(f"{res.get('goal')} completed.")
                    else:
                        failed_goals.append(f"could not {res.get('goal')}")
                        
                if not results:
                    # E.g. Intent parser failed completely or hit provider error but didn't return a task
                    final_response = "I couldn't plan any tasks for that request."
                elif success_goals and failed_goals:
                    final_response = " ".join(success_goals) + f" But I {', and '.join(failed_goals)}."
                elif success_goals:
                    final_response = " ".join(success_goals)
                elif failed_goals:
                    final_response = f"I failed to complete your request. I {', and '.join(failed_goals)}."
                else:
                    final_response = "Task execution completed."
                    
                execution_report["final_response"] = final_response
            else:
                # SINGLE TASK PATH
                intent = self.intent_parser.parse(text, current_context)
                print(f"[Orchestrator] AGENT PATH. Extracted Intent: {intent.to_dict()}")
                
                # Check stale turn before planning
                if self.turn_manager and not self.turn_manager.is_turn_active(turn_id):
                    return {"status": "error", "message": "Turn superseded before planning."}
                
                # If intent parser fails and we had a pending cognitive clarification, throw the clarification.
                if intent.action in ["unknown", "provider_error"] and pending_clarification:
                    return {"status": "success", "result": pending_clarification}
                    
                # Execute Plan based on Intent
                execution_report = self.planner.execute_goal(intent, context=current_context, turn_id=turn_id)
                
            final_response = execution_report.get("final_response", "Task execution completed.")
            
            from packages.core import logger
            if logger.is_debug():
                logger.debug("\n============================================================")
                logger.debug("TASK EXECUTION TRACE")
                logger.debug("============================================================")
                logger.debug(f"Transcript:\n{text}\n")
                
                intent_dict = execution_report.get("intent", {})
                logger.debug(f"Intent:\n{intent_dict.get('action')}\n")
                logger.debug(f"Target:\n{intent_dict.get('target')}\n")
                
                results = execution_report.get("results", [])
                for idx, res in enumerate(results):
                    tool = res.get("tool_call", {})
                    exec_res = res.get("result", {})
                    
                    logger.debug(f"Plan (Step {idx+1}):\n{tool.get('action')}\n")
                    logger.debug(f"Tool:\n{tool.get('action')}\n")
                    logger.debug(f"Arguments:\n{tool}\n")
                    
                    logger.debug(f"Executor Result:\n{exec_res.get('details', exec_res.get('status'))}\n")
                    
                    verification = exec_res.get("verification", {})
                    v_pass = "PASS" if verification.get("passed") else "FAIL"
                    logger.debug(f"Verification:\n{v_pass} - {verification.get('details', '')}\n")
                
                task_status = execution_report.get("status", "FAILED")
                logger.debug(f"Task Status:\n{task_status}\n")
                logger.debug(f"Final Response:\n{final_response}\n")
                logger.debug("============================================================\n")

            return {"status": "success", "result": final_response, "execution_report": execution_report}
            
        # Fallback if no planner
        if self.router:
            result = self.router.route_request("simple", text, {})
            return {"status": "success", "result": result}
            
        return {"status": "error", "message": "No router or planner configured"}

    def start(self) -> None:
        """Start the orchestrator and all its managed services."""
        print("[Orchestrator] Started.")

    def stop(self) -> None:
        """Stop the orchestrator gracefully."""
        print("[Orchestrator] Stopped.")

