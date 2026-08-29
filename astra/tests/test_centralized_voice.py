import json
import pytest
from packages.network.device_manager import DeviceManager
from packages.network.distributed_task_state import DistributedTaskState
from packages.voice.speech_manager import SpeechManager
from packages.core.conversation_turn_manager import ConversationTurnManager
from packages.network.astra_server import AstraServer
from astra.tests.mock_android_client import MockAndroidClient

def test_centralized_voice_and_turn_management():
    manager = DeviceManager()
    state = DistributedTaskState()
    speech = SpeechManager()
    turn = ConversationTurnManager()
    server = AstraServer(manager, state, speech, turn)
    
    client = MockAndroidClient("phone_123")
    server.receive_payload(client.generate_pair_payload())
    
    # Simulate phone sending input when laptop is the active device
    assert turn.get_active_device() == "local_core"
    payload = json.dumps({"action": "user_input", "device_id": "phone_123", "data": {"text": "hello"}})
    res_str = server.receive_payload(payload)
    res = json.loads(res_str)
    
    # Should be rejected because phone is not the active turn endpoint
    assert res["status"] == "error"
    assert "Another device is currently active" in res["message"]
    
    # Change active device to phone
    turn.set_active_device("phone_123")
    
    # Now it should be processed and returned via the centralized SpeechManager
    res_str = server.receive_payload(payload)
    res = json.loads(res_str)
    
    assert res["status"] == "success"
    assert res["action"] == "play_speech"
    assert res["data"]["target_device"] == "phone_123"
    assert "Processed 'hello'" in res["data"]["text"]
    
    # Try sending another low priority speech request directly through the manager
    # Since SpeechManager is currently "speaking" the previous output at NORMAL priority,
    # a LOW priority request should be dropped.
    dropped_payload = speech.request_speech("this is low priority", priority="LOW")
    assert dropped_payload is None
    
    # But a CRITICAL priority should get through
    critical_payload = speech.request_speech("Fire alarm!", priority="CRITICAL")
    assert critical_payload is not None
