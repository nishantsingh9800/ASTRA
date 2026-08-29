import json
import asyncio
from typing import Dict, Any, Callable
from packages.network.device_manager import DeviceManager
from packages.network.distributed_task_state import DistributedTaskState
from packages.voice.speech_manager import SpeechManager
from packages.core.conversation_turn_manager import ConversationTurnManager

class AstraServer:
    """
    Mock implementation of the Astra Core Server.
    In a real environment, this would be an asyncio WebSocket server.
    For this test phase, it exposes direct method calls to simulate receiving network payloads.
    """
    def __init__(self, device_manager: DeviceManager, task_state: DistributedTaskState, speech_manager: SpeechManager, turn_manager: ConversationTurnManager):
        self.device_manager = device_manager
        self.task_state = task_state
        self.speech_manager = speech_manager
        self.turn_manager = turn_manager
        self._mock_responses: Dict[str, Any] = {}

    def receive_payload(self, payload_str: str) -> str:
        """Simulates receiving a JSON payload over a websocket."""
        try:
            payload = json.loads(payload_str)
            action = payload.get("action")
            device_id = payload.get("device_id")
            
            if action == "pair":
                return self._handle_pair(device_id, payload.get("data", {}))
            elif action == "sync_state":
                return self._handle_sync(device_id, payload.get("data", {}))
            elif action == "sensor_response":
                return self._handle_sensor_response(payload.get("data", {}))
            elif action == "user_input":
                return self._handle_user_input(device_id, payload.get("data", {}))
            else:
                return json.dumps({"status": "error", "message": "Unknown action"})
                
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def _handle_pair(self, device_id: str, data: Dict[str, Any]) -> str:
        self.device_manager.register_device(device_id, data)
        # Return current shared state on successful pair
        return json.dumps({
            "status": "success", 
            "action": "pair_accepted",
            "state_dump": self.task_state.get_full_state()
        })

    def _handle_sync(self, device_id: str, data: Dict[str, Any]) -> str:
        key = data.get("key")
        value = data.get("value")
        timestamp = data.get("timestamp")
        
        if key and timestamp:
            applied = self.task_state.sync_from_remote(key, value, timestamp, device_id)
            return json.dumps({"status": "success", "applied": applied})
        return json.dumps({"status": "error", "message": "Invalid sync payload"})

    def request_remote_sensor(self, target_device_id: str, sensor: str) -> Any:
        """
        Simulates the Core requesting a remote sensor (e.g., GPS).
        Returns the simulated response if permissions allow.
        """
        if not self.device_manager.check_permission(target_device_id, sensor):
            return {"status": "error", "message": "Permission denied by remote device"}
            
        # In a real system, this sends a payload to the websocket and yields until response.
        # Here we just check our mock responses dictionary.
        return self._mock_responses.get(f"{target_device_id}_{sensor}", {"status": "pending"})
        
    def inject_mock_sensor_response(self, device_id: str, sensor: str, data: Any) -> None:
        """Helper for testing."""
        self._mock_responses[f"{device_id}_{sensor}"] = data

    def _handle_user_input(self, device_id: str, data: Dict[str, Any]) -> str:
        """
        Handles user input from any device, enforcing turn taking and routing responses through the SpeechManager.
        """
        # 1. Enforce turn taking (Phase 8 Architecture Constraint)
        if not self.turn_manager.should_process_input(device_id):
            return json.dumps({"status": "error", "message": "Ignored: Another device is currently active."})
            
        # 2. Process input (Mocked)
        text_input = data.get("text", "")
        response_text = f"Processed '{text_input}' on Astra Core."
        
        # 3. Route output through central SpeechManager (Phase 8 Architecture Constraint)
        # We do NOT let the client just speak whatever it wants. It must receive an authorized payload.
        speech_payload = self.speech_manager.request_speech(response_text, priority="NORMAL", target_device=device_id)
        
        if speech_payload:
            return json.dumps({"status": "success", "action": "play_speech", "data": speech_payload})
        else:
            return json.dumps({"status": "success", "action": "none", "message": "Speech suppressed by priority."})
