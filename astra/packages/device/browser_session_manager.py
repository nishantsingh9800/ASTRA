import subprocess
import time
import urllib.parse
from typing import Dict, Any, Optional

class BrowserSessionManager:
    """
    Manages browser sessions by keeping track of the intended context,
    and navigating via shell commands.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserSessionManager, cls).__new__(cls)
            cls._instance.active_context = {
                "browser": None,
                "page": None,
                "url": None,
                "domain": None
            }
        return cls._instance

    def navigate(self, target: Dict[str, Any]) -> bool:
        """Navigates the current tab to a URL."""
        url = target.get("url")
        if not url:
            return False
            
        subprocess.Popen(["powershell", "-Command", f"Start-Process '{url}'"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        self.active_context["url"] = url
        self.active_context["page"] = target.get("name")
        self.active_context["domain"] = target.get("domain")
        
        # Attempt to determine browser (we assume default browser is being used)
        self.active_context["browser"] = "DefaultBrowser"
        return True

    def search_website(self, query: str, target: Optional[Dict[str, Any]] = None) -> bool:
        """
        Executes a search using the current active tab context or the specific target.
        """
        if target:
            # specific website search
            name = target.get("name", "").lower()
            if name == "youtube":
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            else:
                domain = target.get("domain", "")
                search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}+site%3A{domain}"
        else:
            # fallback to current context
            page = str(self.active_context.get("page", "")).lower()
            if page == "youtube":
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            else:
                search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
                
        subprocess.Popen(["powershell", "-Command", f"Start-Process '{search_url}'"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                         
        # We don't reset the page name, just the url, assuming we stay on the same site.
        self.active_context["url"] = search_url
        return True

    def get_active_context(self) -> Dict[str, Any]:
        return self.active_context
