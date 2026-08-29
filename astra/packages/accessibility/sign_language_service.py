from typing import Any, List, Dict, Optional

class SignLanguageProvider:
    """Abstract interface for different sign languages (ASL, ISL)."""
    def process_sequence(self, temporal_landmarks: List[Any]) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

class MockISLProvider(SignLanguageProvider):
    """Mock implementation for testing."""
    def process_sequence(self, temporal_landmarks: List[Any]) -> Optional[Dict[str, Any]]:
        # Mock logic to return a sign intent
        if len(temporal_landmarks) > 10:
            return {"phrase": "open youtube", "confidence": 0.88}
        return None

class SignLanguageService:
    """
    Translates sequences of skeletal landmarks into semantic phrases/intents.
    """
    def __init__(self, provider: SignLanguageProvider, confidence_threshold: float = 0.7):
        self.provider = provider
        self.confidence_threshold = confidence_threshold
        self._landmark_buffer: List[Any] = []

    def add_frame(self, landmarks: Any) -> None:
        """Adds frame landmarks to the temporal buffer."""
        if landmarks:
            self._landmark_buffer.append(landmarks)
            
    def analyze_sequence(self) -> Optional[str]:
        """
        Attempts to translate the current buffer into an intent phrase.
        Returns the phrase, an uncertainty message, or None.
        """
        if not self._landmark_buffer:
            return None
            
        result = self.provider.process_sequence(self._landmark_buffer)
        self._landmark_buffer.clear() # Clear after attempt
        
        if not result:
            return None
            
        if result["confidence"] < self.confidence_threshold:
            return "I didn't catch that sign clearly."
            
        return result["phrase"]
