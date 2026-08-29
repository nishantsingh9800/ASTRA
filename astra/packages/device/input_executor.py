import time
from typing import Dict, Any
from packages.core.models import UITarget, UIAction
from packages.core import logger

class InputExecutor:
    """
    Executes actual hardware/OS-level input actions on resolved UI targets.
    """
    
    def _verify_focus(self, element: Any) -> bool:
        if hasattr(element, "has_keyboard_focus"):
            return element.has_keyboard_focus()
        return False
        
    def execute(self, action: UIAction, target: UITarget, data: Any = None) -> Dict[str, Any]:
        """
        Executes the specified action on the target.
        """
        if not target.element_ref:
            return {"status": "error", "message": "UITarget lacks an actionable element reference.", "failure_category": "UI_TARGET_NOT_FOUND"}
            
        element = target.element_ref
        
        try:
            if action == UIAction.CLICK:
                element.set_focus()
                time.sleep(0.1)
                element.click_input()
                time.sleep(0.2)
                
                # Contextual verification: check if it received focus
                if self._verify_focus(element):
                    return {"status": "success", "message": "Clicked and verified focus."}
                else:
                    # Some buttons don't hold keyboard focus, but for search fields they must
                    if "Edit" in target.control_type or "search" in target.name.lower():
                        return {"status": "error", "message": "Failed to verify focus on input field.", "failure_category": "VERIFICATION_FAILURE"}
                    return {"status": "success", "message": "Clicked successfully (focus unverifiable)."}
                    
            elif action == UIAction.TYPE:
                element.set_focus()
                time.sleep(0.1)
                if not self._verify_focus(element):
                     # Try clicking it if focus fails
                     element.click_input()
                     time.sleep(0.1)
                if data:
                    element.type_keys(str(data), with_spaces=True)
                    return {"status": "success", "message": f"Typed '{data}' successfully."}
                return {"status": "error", "message": "No data provided to type."}
                
            elif action == UIAction.PRESS:
                # Key press can be sent to the focused window/element
                element.set_focus()
                time.sleep(0.1)
                key_map = {
                    "enter": "{ENTER}",
                    "escape": "{ESC}",
                    "tab": "{TAB}",
                }
                key = key_map.get(str(data).lower(), str(data))
                element.type_keys(key)
                return {"status": "success", "message": f"Pressed {data} successfully."}
                
            elif action == UIAction.SCROLL:
                # Basic scroll implementation
                element.set_focus()
                element.type_keys("{PGDN}") # Simplistic fallback
                return {"status": "success", "message": "Scrolled successfully."}
                
            elif action == UIAction.FOCUS:
                element.set_focus()
                if self._verify_focus(element):
                    return {"status": "success", "message": "Focused successfully."}
                return {"status": "error", "message": "Failed to verify focus.", "failure_category": "VERIFICATION_FAILURE"}
                
        except Exception as e:
            logger.error(f"[InputExecutor] Action {action} failed: {e}")
            return {"status": "error", "message": f"Action failed: {e}", "failure_category": "EXECUTOR_FAILURE"}
            
        return {"status": "error", "message": f"Unsupported action: {action}"}
