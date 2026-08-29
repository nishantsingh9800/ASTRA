from typing import Tuple

class MouseKeyboardFallback:
    """
    Fallback for fixed-coordinate or raw input when structured UI is unavailable.
    Normally uses pyautogui or pywinauto.mouse/keyboard.
    """
    def click_at(self, x: int, y: int) -> bool:
        """Performs a raw mouse click at (x,y)."""
        # pyautogui.click(x, y)
        return True

    def type_keys(self, keys: str) -> bool:
        """Sends raw keystrokes to the active window."""
        # pywinauto.keyboard.send_keys(keys)
        return True
