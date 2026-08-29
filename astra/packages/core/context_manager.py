from typing import Dict, Any, Optional
from packages.core.interfaces.context_manager import ContextManager as ContextManagerInterface
from packages.core.models import ContextSnapshot
import subprocess

class ContextManagerImpl(ContextManagerInterface):
    """
    Actively refreshes and maintains the CurrentContext.
    Queries the OS/window manager to ensure no stale data.
    """
    def __init__(self):
        self._current_snapshot = ContextSnapshot()

    def get_context(self) -> Dict[str, Any]:
        """Retrieve the current aggregated context."""
        return self._current_snapshot.to_dict()

    def update_context(self, key: str, value: Any) -> None:
        """Update a specific context key."""
        if hasattr(self._current_snapshot, key):
            setattr(self._current_snapshot, key, value)

    def get_screen_context(self) -> Optional[Dict[str, Any]]:
        return self.get_context()
        
    def refresh_context(self) -> None:
        """
        Actively poll the system for the real current state.
        This prevents acting on stale UI.
        """
        # 1. Get Active Window Title via PowerShell
        script = """
        Add-Type @"
          using System;
          using System.Runtime.InteropServices;
          public class Win32 {
            [DllImport("user32.dll")]
            public static extern IntPtr GetForegroundWindow();
            [DllImport("user32.dll")]
            public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
          }
"@
        $hwnd = [Win32]::GetForegroundWindow()
        $sb = New-Object System.Text.StringBuilder 256
        $null = [Win32]::GetWindowText($hwnd, $sb, $sb.Capacity)
        $sb.ToString()
        """
        try:
            result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, timeout=2)
            title = result.stdout.strip()
            if title:
                self._current_snapshot.active_window_title = title
                # Rough heuristic for browser
                if "Chrome" in title or "Edge" in title or "Firefox" in title:
                    self._current_snapshot.active_browser = "Active"
                if "YouTube" in title:
                    self._current_snapshot.active_page_url = "youtube.com"
        except Exception as e:
            print(f"[ContextManager] Failed to refresh window context: {e}")

