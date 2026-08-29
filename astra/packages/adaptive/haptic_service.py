class HapticService:
    """
    Device-independent abstraction for haptic feedback.
    Mocked for local desktop testing.
    """
    def play_pattern(self, pattern: str) -> bool:
        """
        Plays a haptic pattern.
        Supported: 'short', 'double', 'long', 'emergency_repeating'
        """
        valid_patterns = ["short", "double", "long", "emergency_repeating"]
        if pattern not in valid_patterns:
            return False
            
        # In a real implementation, this triggers OS/Device specific haptic motors.
        print(f"[HAPTIC_SERVICE] Triggered pattern: {pattern}")
        return True
