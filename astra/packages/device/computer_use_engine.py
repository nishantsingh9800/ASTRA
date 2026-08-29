from typing import Dict, Any, Optional
from packages.core.models import UITarget, UIAction
from packages.device.universal_ui_resolver import UniversalUIResolver
from packages.device.input_executor import InputExecutor
from packages.core import logger

class ComputerUseEngine:
    """
    Universal Computer Use Engine.
    Orchestrates UI Target Resolution -> Input Execution -> Verification.
    """
    def __init__(self):
        self.resolver = UniversalUIResolver()
        self.executor = InputExecutor()

    def execute_ui_action(self, action: UIAction, target_description: str, context: Dict[str, Any], data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes a deterministic UI action on a natural language target.
        """
        logger.info(f"[ComputerUseEngine] Request: {action} on '{target_description}' with context {context.get('active_application')}")
        
        # 1. Resolve Target
        target = self.resolver.resolve(target_description, context)
        
        if target.confidence == "LOW" or target.target_type == "UNKNOWN":
            return {
                "status": "error",
                "message": f"I couldn't locate the '{target_description}'.",
                "failure_category": "UI_TARGET_NOT_FOUND"
            }
            
        # 2. Stale Target Protection
        import time
        if time.time() - target.timestamp > 5.0:
            logger.warning("[ComputerUseEngine] Target stale. Discarding.")
            return {
                "status": "error",
                "message": "The screen changed before I could act.",
                "failure_category": "STALE_TARGET"
            }
            
        # 3. Execute Action
        if action == UIAction.SEARCH:
            # Multi-step action for universal search
            # 3.1 Focus/Click
            res_focus = self.executor.execute(UIAction.CLICK, target)
            if res_focus.get("status") == "error":
                return {"status": "error", "message": "I couldn't activate the search field.", "failure_category": "UI_ACTION_FAILED"}
                
            # 3.2 Type query
            if not data:
                return {"status": "error", "message": "I didn't get a query to search for.", "failure_category": "ARGUMENT_FAILURE"}
                
            res_type = self.executor.execute(UIAction.TYPE, target, data=data)
            if res_type.get("status") == "error":
                return {"status": "error", "message": "I couldn't type into the search field.", "failure_category": "UI_ACTION_FAILED"}
                
            # 3.3 Submit (Press Enter)
            res_submit = self.executor.execute(UIAction.PRESS, target, data="ENTER")
            if res_submit.get("status") == "error":
                return {"status": "error", "message": "I couldn't submit the search.", "failure_category": "UI_ACTION_FAILED"}
                
            return {"status": "success", "message": "Search completed."}
        else:
            result = self.executor.execute(action, target, data=data)
            return result
