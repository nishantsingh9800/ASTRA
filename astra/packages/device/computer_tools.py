from typing import Dict, Any
from .application_resolver import ApplicationResolver
from .window_manager import WindowManager

class ComputerTools:
    """
    Binds the core OS/Browser methods into the schema required by Astra's ToolRegistry.
    Enforces the OBSERVE -> ACTION -> VERIFY loop.
    """
    def __init__(self, resolver: ApplicationResolver, window_manager: WindowManager):
        self.resolver = resolver
        self.window_manager = window_manager

    def open_application(self, app_name: str) -> Dict[str, Any]:
        """
        Tool schema mapping for opening native Windows apps.
        """
        print(f"[ComputerTools] Request to open: {app_name}")
        
        # 1. UNDERSTAND/RESOLVE
        app_info = self.resolver.resolve_application(app_name)
        if not app_info:
            return {
                "success": False,
                "error": f"Could not resolve application: {app_name}"
            }
            
        import os
        import subprocess
        import time

        # 2. ACTION
        print(f"[ComputerTools] Launching {app_info['executable']} via {app_info['launch_method']}")
        try:
            if app_info['launch_method'] == 'shell_execute':
                os.startfile(app_info['executable'])
            else:
                subprocess.Popen(app_info['executable'], shell=True)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to launch application: {e}"
            }
        
        # 3. VERIFY
        # E.g. wait for window to exist, get its HWND
        time.sleep(2.0)  # Wait for window to appear
        window_info = self.window_manager.find_window(executable=app_info['executable'], title_regex=app_info['name'])
        
        if window_info:
            self.window_manager.update_context(window_info['hwnd'], app_info['executable'], window_info['title'])
            return {
                "success": True,
                "status": "launched",
                "action": "open_application",
                "target": app_info['executable'],
                "observedState": f"Window '{window_info['title']}' is active."
            }
        
        return {
            "success": False,
            "error": "Application launched but window was not detected during verification."
        }
