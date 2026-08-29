import time
import pytest
from packages.device.hardware_adapters import MockGlassesAdapter, MockWearableAdapter, DeviceAdapter
from packages.device.capability_manager import CapabilityManager
from packages.device.sensor_fusion import SensorFusion

def test_capability_routing():
    manager = CapabilityManager()
    
    # Register mock glasses and mock phone
    glasses = MockGlassesAdapter("glasses_123")
    glasses.connect()
    manager.register_device(glasses)
    
    # Generic mock phone adapter
    phone = DeviceAdapter("phone_123", "Phone Mock", "Android")
    phone.capabilities = ["CAMERA", "GPS"]
    phone.connect()
    # Provide a simple request_capability mock for phone
    phone.request_capability = lambda cap: {"status": "success", "device": "phone"} if phone.is_connected else None
    manager.register_device(phone)
    
    # Request CAMERA. Glasses has priority 1, Phone has priority 2.
    res = manager.request_capability("CAMERA")
    assert res is not None
    assert "frame" in res  # Comes from Glasses mock
    
    # Disconnect glasses, test fallback
    glasses.disconnect()
    res2 = manager.request_capability("CAMERA")
    assert res2 is not None
    assert res2.get("device") == "phone" # Comes from Phone mock
    
    # Disconnect phone, should fail
    phone.disconnect()
    res3 = manager.request_capability("CAMERA")
    assert res3 is None
    
def test_device_discovery():
    manager = CapabilityManager()
    
    glasses = MockGlassesAdapter("g1")
    glasses.connect()
    
    wearable = MockWearableAdapter("w1")
    # Intentional: do not connect wearable
    
    manager.register_device(glasses)
    manager.register_device(wearable)
    
    connected = manager.get_connected_devices()
    assert "Smart Glasses Mock" in connected
    assert "Wrist Wearable Mock" not in connected

def test_sensor_data_contract_and_fusion():
    wearable = MockWearableAdapter("w1")
    wearable.connect()
    
    # Get IMU data
    imu_data = wearable.request_capability("IMU")
    assert imu_data is not None
    assert imu_data["sensor"] == "IMU"
    assert "timestamp" in imu_data
    assert "unit" in imu_data
    
    # Test fusion logic (Normal)
    fusion = SensorFusion()
    state = fusion.process_imu_data(imu_data)
    assert state in ["STATIONARY", "WALKING"] # Default gravity is 9.81, so it should be stationary
    
    # Mock a fall (High acceleration)
    fall_data = {
        "sensor": "IMU",
        "value": {"accel": [0.0, 25.0, 0.0]},
        "unit": "m/s2, rad/s",
        "timestamp": time.time(),
        "accuracy": "high",
        "deviceId": "w1"
    }
    
    fall_state = fusion.process_imu_data(fall_data)
    assert fall_state == "POSSIBLE_FALL"
