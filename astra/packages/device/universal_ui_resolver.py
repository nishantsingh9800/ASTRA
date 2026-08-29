import time
import re
from typing import Dict, Any, Optional
import pywinauto
from packages.core.models import UITarget
from packages.core import logger

class UniversalUIResolver:
    """
    Dynamically interrogates Windows UI Automation trees to resolve 
    natural language UI targets across arbitrary applications.
    """
    def __init__(self):
        pass

    def _get_active_window(self) -> Optional[pywinauto.WindowSpecification]:
        try:
            # We connect to the foreground window
            # pywinauto handles this gracefully via active() if supported, 
            # or by inspecting the top level window.
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return None
            app = pywinauto.Application(backend="uia").connect(handle=hwnd)
            return app.window(handle=hwnd)
        except Exception as e:
            logger.error(f"[UniversalUIResolver] Failed to get active window: {e}")
            return None

    def resolve(self, target_description: str, context: Dict[str, Any]) -> UITarget:
        """
        Attempts to find a structured UI element in the active window.
        """
        target_lower = target_description.lower().strip()
        timestamp = time.time()
        active_app = context.get("active_application", "Unknown")
        
        main_window = self._get_active_window()
        if not main_window:
            # Fallback when UIA can't attach
            return UITarget(
                target_type="UNKNOWN",
                name=target_description,
                control_type="Unknown",
                application=active_app,
                confidence="LOW",
                timestamp=timestamp
            )
            
        try:
            # Semantic mapping
            element = None
            control_type = "Unknown"
            
            if "search" in target_lower or "find" in target_lower:
                control_type = "Edit"
                # Try specific title first
                try:
                    element = main_window.child_window(control_type="Edit", title_re=".*(Search|Find|query|Address).*")
                    if not element.exists(timeout=0.2):
                        element = None
                except Exception:
                    element = None
                
                # Fallback to any edit field
                if not element:
                    element = main_window.child_window(control_type="Edit")
                    
            elif "send" in target_lower or "submit" in target_lower:
                control_type = "Button"
                element = main_window.child_window(control_type="Button", title_re=".*(Send|Submit).*")
            elif "address" in target_lower:
                control_type = "Edit"
                element = main_window.child_window(control_type="Edit", title_re=".*(Address|URL|search).*")
            else:
                control_type = "Any"
                element = main_window.child_window(title_re=f".*{target_description}.*", flags=re.IGNORECASE)
                
            if element and element.exists(timeout=0.5):
                return UITarget(
                    target_type=control_type,
                    name=target_description,
                    control_type=control_type,
                    application=active_app,
                    confidence="HIGH",
                    element_ref=element,
                    timestamp=timestamp
                )
        except Exception as e:
            logger.debug(f"[UniversalUIResolver] Dynamic resolution failed: {e}")
            
        # Return LOW confidence if not found, allowing fallback/clarification
        return UITarget(
            target_type="UNKNOWN",
            name=target_description,
            control_type="Unknown",
            application=active_app,
            confidence="LOW",
            timestamp=timestamp
        )
