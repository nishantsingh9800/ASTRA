import os
import winreg
from typing import Optional, Dict, Any
from packages.core.application_registry import ApplicationRegistry

class ApplicationResolver:
    """
    Resolves application names to actual installed executables dynamically.
    Does NOT rely on hardcoded paths.
    """
    def __init__(self):
        self._registry = ApplicationRegistry()
        self._known_apps = {
            "whatsapp": "whatsapp://",
            "whatsapp desktop": "whatsapp://",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "vs code": "code.exe",
            "visual studio code": "code.exe",
            "code": "code.exe",
            "file explorer": "explorer.exe",
            "settings": "ms-settings:",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "youtube": "chrome.exe",
            "notepad": "notepad.exe",
            "terminal": "wt.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "paint": "mspaint.exe"
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
            return {
                "name": app_name,
                "executable": executable,
                "launch_method": "shell_execute" if ":" in executable else "process"
            }
        
        # 2. Dynamic resolution via ApplicationRegistry
        resolved = self._registry.resolve(app_name)
        if resolved:
            return {
                "name": app_name,
                "executable": resolved if (resolved.endswith(".exe") or ":" in resolved or resolved.endswith(".lnk")) else f"{resolved}.exe",
                "launch_method": "shell_execute" if ":" in resolved else "process"
            }
            
        return None
