import urllib.request
from typing import Dict, Any, Optional
from packages.core.interfaces.llm_provider import LLMProvider

class ModelRouter:
    """
    Routes requests to the configured AI provider.
    Now exclusively uses Gemini API for AI reasoning.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def _is_online(self) -> bool:
        """Check internet connectivity."""
        try:
            urllib.request.urlopen('http://clients3.google.com/generate_204', timeout=2)
            return True
        except:
            return False

    def route_request(self, task_type: str, prompt: str, context: Dict[str, Any]) -> str:
        """
        Route the request to the provider.
        If offline or provider is unavailable, returns a structured error.
        """
        import json
        
        if not self._is_online() or not self.provider.is_available():
            error_msg = getattr(self.provider, 'last_error', 'Gemini provider initialization failed.')
            if not error_msg:
                error_msg = 'Gemini provider initialization failed.'
                
            return json.dumps({
                "provider": "gemini",
                "status": "error",
                "message": "Gemini is offline." if not self._is_online() else error_msg
            })
            
        print("[Router] Routing to Gemini provider.")
        return self.provider.generate(prompt, context)
