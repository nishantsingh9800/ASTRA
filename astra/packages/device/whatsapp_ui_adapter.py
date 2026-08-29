import time
from typing import Dict, Any, Optional
import pywinauto
from packages.core import logger

class WhatsAppUIAdapter:
    """
    Adapter for locating and interacting with the WhatsApp Windows App search bar dynamically.
    """
    def __init__(self):
        self.app = None
        self.main_window = None

    def _connect(self) -> bool:
        """Attempts to connect to the active WhatsApp window."""
        try:
            self.app = pywinauto.Application(backend="uia").connect(title_re=".*WhatsApp.*", timeout=2)
            self.main_window = self.app.top_window()
            return True
        except pywinauto.findwindows.ElementNotFoundError:
            logger.error("[WhatsAppUIAdapter] WhatsApp window not found.")
            return False
        except Exception as e:
            logger.error(f"[WhatsAppUIAdapter] Error connecting: {e}")
            return False

    def find_search_bar(self) -> Optional[Any]:
        """
        Interrogates the UI tree to find the Search field.
        Returns the pywinauto wrapper element if found, or None.
        """
        if not self._connect():
            return None

        try:
            # WhatsApp's search bar is typically an Edit control.
            # Names can be "Search" or "Search or start new chat".
            search_element = self.main_window.child_window(control_type="Edit", title_re=".*Search.*")
            
            # Verify if it actually exists in the tree
            if search_element.exists(timeout=1):
                logger.debug("[WhatsAppUIAdapter] UIA successfully located search field.")
                return search_element
        except Exception as e:
            logger.debug(f"[WhatsAppUIAdapter] Primary UIA search failed: {e}")
            
        return None

    def click_and_verify(self) -> Dict[str, Any]:
        """
        Attempts to click the search bar and verify focus.
        If UIA fails, uses the Ctrl+F fallback.
        """
        search_element = self.find_search_bar()
        
        if search_element:
            try:
                # 1. Bring window to foreground
                self.main_window.set_focus()
                time.sleep(0.1)
                
                # 2. Click the element
                search_element.click_input()
                time.sleep(0.2)
                
                # 3. Verify focus
                if search_element.has_keyboard_focus():
                    logger.debug("[WhatsAppUIAdapter] Verification PASS: Search field has keyboard focus.")
                    return {"status": "success", "message": "Clicked WhatsApp search bar (UIA)."}
                else:
                    # Retry with generic set_focus
                    search_element.set_focus()
                    if search_element.has_keyboard_focus():
                        return {"status": "success", "message": "Clicked WhatsApp search bar (UIA Focus)."}
            except Exception as e:
                logger.error(f"[WhatsAppUIAdapter] UIA click failed: {e}")
                
        # FALLBACK: Use Native Keyboard Shortcut Ctrl+F
        logger.debug("[WhatsAppUIAdapter] Using Ctrl+F Fallback...")
        if self._connect():
            try:
                self.main_window.set_focus()
                time.sleep(0.1)
                self.main_window.type_keys("^f") # Ctrl + F
                time.sleep(0.3)
                
                # We can't strictly verify UIA focus if we couldn't find the element, 
                # but we can assume success if the window received the keystroke.
                return {"status": "success", "message": "Focused WhatsApp search bar (Ctrl+F Fallback)."}
            except Exception as e:
                logger.error(f"[WhatsAppUIAdapter] Fallback failed: {e}")
                
        return {"status": "error", "failure_category": "UI_TARGET_NOT_FOUND", "message": "Could not locate the WhatsApp search bar."}
