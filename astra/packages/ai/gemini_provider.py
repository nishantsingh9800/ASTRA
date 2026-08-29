import os
import json
import urllib.request
from typing import Dict, Any, Generator
from packages.core.interfaces.llm_provider import LLMProvider

class GeminiProvider(LLMProvider):
    """
    Connects to the Gemini API as the sole reasoning provider.
    """
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
        self._available = False
        self.last_error = ""
        self.health_check()

    def _is_online(self) -> bool:
        """Check internet connectivity."""
        try:
            urllib.request.urlopen('http://clients3.google.com/generate_204', timeout=2)
            return True
        except:
            return False

    def health_check(self) -> bool:
        """Checks if we are online and have an API key."""
        from packages.core import logger
        if not self._is_online():
            self._available = False
            logger.debug("[GeminiProvider] Network offline check failed.")
            return False
            
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            self._available = False
            self.last_error = "GEMINI_API_KEY environment variable is missing."
            logger.debug("[GeminiProvider] GEMINI_API_KEY environment variable is missing.")
            return False
            
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            # Make a minimal real request to verify model and key
            chat = client.chats.create(model=self.model_name)
            chat.send_message("ping")
            self._available = True
            self.last_error = ""
            return True
        except Exception as e:
            self._available = False
            self.last_error = str(e)
            error_msg = str(e).lower()
            if "api_key" in error_msg or "403" in error_msg or "unauthorized" in error_msg or "defaultcredentials" in error_msg:
                error_type = "AUTHENTICATION_ERROR"
            elif "not found" in error_msg or "404" in error_msg:
                error_type = "MODEL_ERROR"
            elif "429" in error_msg or "quota" in error_msg:
                error_type = "RATE_LIMIT"
            else:
                error_type = "API_ERROR"
            logger.debug(f"[GeminiProvider] Initialization failed: {error_type} - {e}")
            return False

    def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        import time
        if getattr(self, "cooldown_until", 0) > time.time():
            return json.dumps({
                "status": "error",
                "provider": "gemini",
                "error_type": "RATE_LIMIT",
                "retryable": False,
                "message": "Gemini API is on cooldown due to quota exhaustion."
            })
            
        if not self._available:
            if not self.health_check():
                return json.dumps({
                    "provider": "Gemini API",
                    "status": "unavailable",
                    "reason": "offline" if not self._is_online() else "missing_api_key_or_dependency"
                })
        
        try:
            from google import genai
            api_key = os.environ.get("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            
            print(f"[GeminiProvider] Reasoning (model: {self.model_name})...")
            chat = client.chats.create(model=self.model_name)
            response = chat.send_message(prompt)
            text = response.text
            
            # Extract JSON if requested
            if "JSON" in prompt and ("tool_call" in prompt or "response" in prompt or "action" in prompt):
                text = text.strip()
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                    
                # Extract first JSON object or array
                start_obj = text.find('{')
                start_arr = text.find('[')
                
                # Determine which comes first (object or array)
                start = -1
                if start_obj != -1 and start_arr != -1:
                    start = min(start_obj, start_arr)
                else:
                    start = max(start_obj, start_arr)
                    
                if start != -1:
                    end_char = '}' if start == start_obj else ']'
                    end = text.rfind(end_char) + 1
                    if end != 0:
                        json_str = text[start:end]
                        try:
                            json.loads(json_str)
                            return json_str
                        except json.JSONDecodeError:
                            print(f"[GeminiProvider] Warning: Output was not pure JSON. Raw: {json_str}")
                            if start == start_obj:
                                return '{"type": "response", "text": "I encountered an error planning the task."}'
                            else:
                                return '[{"action": "generic_task", "target": "unknown"}]'
                
                if "action" in prompt and "target_type" in prompt:
                    # Likely intent parsing failed
                    return '{"action": "unknown", "target_type": "UNKNOWN"}'
                elif "tool_call" in prompt:
                    return '{"type": "response", "text": "I could not formulate a plan."}'
                else:
                    return '{"type": "response", "text": "Task error."}'

            return text
            
        except Exception as e:
            from packages.core import logger
            logger.debug(f"[GeminiProvider] API Error: {e}")
            
            error_msg = str(e).lower()
            if "api_key" in error_msg or "403" in error_msg or "unauthorized" in error_msg or "invalid_argument" in error_msg:
                error_type = "AUTHENTICATION_ERROR"
                self._available = False
                self.last_error = str(e)
            elif "429" in error_msg or "quota" in error_msg:
                error_type = "RATE_LIMIT"
                import time
                self.cooldown_until = time.time() + 60.0 # 1 minute cooldown
            else:
                error_type = "API_ERROR"
                
            return json.dumps({
                "status": "error",
                "provider": "gemini",
                "error_type": error_type,
                "retryable": False,
                "message": str(e)
            })

    def generate_stream(self, prompt: str, context: Dict[str, Any]) -> Generator[str, None, None]:
        if not self._available:
            if not self.health_check():
                raise RuntimeError("Gemini AI is unavailable.")
                
        try:
            from google import genai
            api_key = os.environ.get("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            
            chat = client.chats.create(model=self.model_name)
            response = chat.send_message_stream(prompt)
            for chunk in response:
                yield chunk.text
        except Exception as e:
            raise RuntimeError(f"Stream Error: {e}")

    def is_available(self) -> bool:
        return self._available
