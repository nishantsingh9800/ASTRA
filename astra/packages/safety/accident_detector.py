from typing import Dict, Any, List

class AccidentDetector:
    """
    Aggregates multi-signal evidence to determine if an accident occurred.
    Enforces the 'Do not use a single AI guess' rule.
    """
    def __init__(self):
        self._recent_signals: List[Dict[str, Any]] = []

    def receive_signal(self, source: str, signal_type: str, confidence: float) -> None:
        """Collects raw signals (e.g., from accelerometer, camera, mic)."""
        self._recent_signals.append({
            "source": source,
            "type": signal_type,
            "confidence": confidence
        })

    def evaluate_evidence(self) -> Dict[str, Any]:
        """
        Evaluates collected signals.
        Only returns high confidence if multiple corroborating signals exist.
        """
        if not self._recent_signals:
            return {"confidence": 0.0, "event": None, "evidence": []}
            
        evidence_sources = {sig["source"] for sig in self._recent_signals}
        
        # Rule: Needs at least 2 distinct sources (e.g. impact + camera)
        if len(evidence_sources) > 1:
            confidence = sum(sig["confidence"] for sig in self._recent_signals) / len(self._recent_signals)
            return {
                "confidence": min(confidence + 0.2, 1.0), # Boost confidence for multi-signal
                "event": "possible_fall",
                "evidence": [sig["type"] for sig in self._recent_signals]
            }
            
        # Single signal is inherently weak
        return {
            "confidence": 0.4,
            "event": "unconfirmed_event",
            "evidence": [self._recent_signals[0]["type"]]
        }
