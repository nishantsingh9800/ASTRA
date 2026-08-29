from typing import Dict, Any, Optional

class SensorFusion:
    """
    Fuses multiple raw sensors (e.g. Accelerometer + Gyroscope) into higher-level states.
    Routes critical inferred states to the SafetyEngine.
    """
    def __init__(self):
        self.fall_threshold = 15.0 # m/s2 simple mock threshold
        
    def process_imu_data(self, imu_payload: Dict[str, Any]) -> Optional[str]:
        """
        Takes raw IMU payload (as per Sensor Data Contract) and infers state.
        """
        if not imu_payload or imu_payload.get("sensor") != "IMU":
            return None
            
        value = imu_payload.get("value", {})
        accel = value.get("accel", [0.0, 9.81, 0.0])
        
        # Calculate magnitude (mocking simple vector length)
        magnitude = (accel[0]**2 + accel[1]**2 + accel[2]**2) ** 0.5
        
        if magnitude > self.fall_threshold:
            print("[SensorFusion] HIGH ACCELERATION DETECTED. Possible Fall!")
            # In a real system, this triggers Phase 6 SafetyEngine
            return "POSSIBLE_FALL"
            
        if magnitude > 11.0:
            return "WALKING"
            
        return "STATIONARY"
