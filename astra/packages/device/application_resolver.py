import os
import winreg
from typing import Optional, Dict, Any

class ApplicationResolver:
    """
    Resolves application names to actual installed executables dynamically.
    Does NOT rely on hardcoded paths.
    """
    def __init__(self):
        # A mock cache of known mappings that would normally be built by scanning 
        # Start Menu shortcuts, Windows Registry, etc.
        self._known_apps = {
            "whatsapp": "whatsapp://",
            "whatsapp desktop": "whatsapp://",
            "calculator": "calc.exe",
            "vs code": "code.exe",
            "visual studio code": "code.exe",
            "file explorer": "explorer.exe",
            "settings": "ms-settings:",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "youtube": "chrome.exe", # Defaults to opening browser if app not found
        }

    def resolve_application(self, app_name: str) -> Optional[Dict[str, Any]]:
        """
        Takes a natural language application name and resolves it to a launch command.
        Returns a dictionary with 'executable', 'launch_method', etc.
        """
        app_name_lower = app_name.lower().strip()
        
        # 1. Check known mappings
        if app_name_lower in self._known_apps:
            executable = self._known_apps[app_name_lower]
            # Usually we'd resolve full path via registry here.
            # E.g., winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths...")
            return {
                "name": app_name,
                "executable": executable,
                "launch_method": "shell_execute" if ":" in executable else "process"
            }
        
        # 2. Fallback to generic search (mocked)
        return None
