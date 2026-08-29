import json
import pytest
from packages.network.device_manager import DeviceManager
from packages.network.distributed_task_state import DistributedTaskState
from packages.network.astra_server import AstraServer
from astra.tests.mock_android_client import MockAndroidClient
from packages.voice.speech_manager import SpeechManager
from packages.core.conversation_turn_manager import ConversationTurnManager

def test_device_pairing_and_permissions():
    manager = DeviceManager()
    state = DistributedTaskState()
    speech = SpeechManager()
    turn = ConversationTurnManager()
    server = AstraServer(manager, state, speech, turn)
    
    client = MockAndroidClient("phone_123")
    
    # Simulate client connecting
    response_str = server.receive_payload(client.generate_pair_payload())
    response = json.loads(response_str)
    
    assert response["status"] == "success"
    assert response["action"] == "pair_accepted"
    
    # Verify Device Manager state
    device = manager.get_device("phone_123")
    assert device is not None
    assert device["platform"] == "Android"
    
    # Test capability negotiation
    assert manager.check_permission("phone_123", "gps") is True
    assert manager.check_permission("phone_123", "camera") is False # User denied camera
    assert manager.check_permission("phone_123", "laser_beam") is False # Doesn't exist

def test_distributed_task_sync():
    state = DistributedTaskState()
    
    # Core modifies state
    state.set("current_task", "research_laptops", "local_core")
    
    # Remote client tries to update with older timestamp (should be rejected)
    rejected = state.sync_from_remote("current_task", "buy_apples", state.get_full_state()["current_task"]["timestamp"] - 10, "phone_123")
    assert rejected is False
    assert state.get("current_task") == "research_laptops"
    
    # Remote client tries to update with newer timestamp (should be accepted)
    accepted = state.sync_from_remote("current_task", "buy_apples", state.get_full_state()["current_task"]["timestamp"] + 10, "phone_123")
    assert accepted is True
    assert state.get("current_task") == "buy_apples"

def test_remote_sensor_request():
    manager = DeviceManager()
    state = DistributedTaskState()
    speech = SpeechManager()
    turn = ConversationTurnManager()
    server = AstraServer(manager, state, speech, turn)
    
    client = MockAndroidClient("phone_123")
    server.receive_payload(client.generate_pair_payload())
    
    # Mocking a valid GPS response
    server.inject_mock_sensor_response("phone_123", "gps", {"status": "success", "lat": 1.2, "lon": 3.4})
    
    # Requesting permitted sensor (GPS)
    gps_res = server.request_remote_sensor("phone_123", "gps")
    assert gps_res["status"] == "success"
    assert gps_res["lat"] == 1.2
    
    # Requesting denied sensor (Camera)
    cam_res = server.request_remote_sensor("phone_123", "camera")
    assert cam_res["status"] == "error"
    assert "Permission denied" in cam_res["message"]
