import json
import re
from typing import Dict, Any, Optional
from packages.core.models import CognitiveResult, ConfidenceLevel
from packages.core.application_registry import ApplicationRegistry
from packages.ai.model_router import ModelRouter
from packages.core import logger

class CognitiveIntentEngine:
    """
    Intelligent layer between STT transcript and intent execution.
    Fixes speech errors, resolves contextual references, and normalizes intent.
    """
    def __init__(self, router: ModelRouter, app_registry: ApplicationRegistry):
        self.router = router
        self.app_registry = app_registry
        
    def normalize(self, raw_transcript: str, context: Dict[str, Any]) -> CognitiveResult:
        """
        Takes raw STT output and normalizes it.
        Uses local fast resolvers first, falling back to Gemini for ambiguity.
        """
        # Clean text
        text_lower = raw_transcript.lower().strip().strip('.?!')
        
        # 1. Try Local Fast Resolve for simple common mistakes
        local_result = self._local_fast_resolve(text_lower, raw_transcript)
        if local_result:
            logger.debug(f"[CognitiveBrain] Fast Local Match: {local_result.normalized_transcript}")
            return local_result
            
        # 2. Use Gemini Brain
        return self._gemini_resolve(raw_transcript, context)

    def _local_fast_resolve(self, text_lower: str, raw_transcript: str) -> Optional[CognitiveResult]:
        """Handles deterministic or simple phonetic corrections."""
        # Check basic aliases
        aliases = self.app_registry.get_known_aliases()
        
        # Simple match for "open <app>"
        open_match = re.match(r"^(?:can you )?(?:please )?(?:open|launch|start) (.+)$", text_lower)
        if open_match:
            app_target = open_match.group(1).strip()
            
            # Direct match
            if app_target in aliases:
                target = app_target
                return CognitiveResult(
                    raw_transcript=raw_transcript,
                    normalized_transcript=f"Open {target.title()}.",
                    confidence=ConfidenceLevel.HIGH,
                    reasoning="Exact alias match"
                )
                
            # Phonetic/Fuzzy
            phonetic_fixes = {
                "what's app": "whatsapp",
                "whats up": "whatsapp",
                "you tube": "youtube",
                "vs code": "visual studio code",
                "face book": "facebook",
                "excel sheet": "excel"
            }
            if app_target in phonetic_fixes:
                target = phonetic_fixes[app_target]
                return CognitiveResult(
                    raw_transcript=raw_transcript,
                    normalized_transcript=f"Open {target.title()}.",
                    confidence=ConfidenceLevel.HIGH,
                    reasoning="Phonetic alias match"
                )
                
        return None
        
    def _gemini_resolve(self, raw_transcript: str, context: Dict[str, Any]) -> CognitiveResult:
        """Uses LLM to perform semantic correction and context resolution."""
        prompt = f"""
        You are the Cognitive Intent Brain for ASTRA.
        Your job is to read a raw voice transcript and understand what the user MEANT.
        Correct mispronunciations, stuttering, incomplete sentences, and resolve context (e.g. "it", "this", "there", "the first one").
        
        Raw Transcript: "{raw_transcript}"
        Current Context: {json.dumps(context)}
        Available Apps: {self.app_registry.get_known_aliases()}
        
        RULES:
        1. If the user misspoke (e.g., "what's app" -> WhatsApp, "you tube" -> YouTube, "my own hona" -> Main Hoon Na on YouTube if context implies music/search), correct it.
        2. If the user says "Click the search bar" and they are on YouTube, the intent is click YouTube's search bar.
        3. If the user corrects themselves mid-sentence ("Open WhatsApp- actually Calculator"), the normalized text is "Open Calculator".
        4. If the intent is highly ambiguous or you lack evidence, set confidence to LOW and provide a clarification_question.
        5. DO NOT GUESS arbitrarily if evidence is weak.
        6. DO NOT invent targets.
        7. If confidence is HIGH or MEDIUM, provide the normalized_transcript.
        
        Output ONLY valid JSON:
        {{
            "normalized_transcript": "Corrected and resolved text, e.g. Open Calculator.",
            "confidence": "HIGH", // HIGH, MEDIUM, LOW
            "clarification_question": null, // or a question like "Did you mean WhatsApp?" if uncertain
            "reasoning": "Explain why you made this correction or why it's ambiguous."
        }}
        """
        
        try:
            response = self.router.route_request("complex", prompt, {})
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                logger.error(f"[CognitiveBrain] Non-JSON from Gemini: {response}")
                return CognitiveResult(
                    raw_transcript=raw_transcript,
                    normalized_transcript=raw_transcript,
                    confidence=ConfidenceLevel.LOW,
                    clarification_question="I'm having trouble understanding. Could you repeat that?",
                    reasoning="LLM JSON Decode Error"
                )
                
            confidence_str = data.get("confidence", "LOW").upper()
            try:
                confidence = ConfidenceLevel[confidence_str]
            except KeyError:
                confidence = ConfidenceLevel.LOW
                
            return CognitiveResult(
                raw_transcript=raw_transcript,
                normalized_transcript=data.get("normalized_transcript", raw_transcript),
                confidence=confidence,
                clarification_question=data.get("clarification_question"),
                reasoning=data.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"[CognitiveBrain] Gemini resolution failed: {e}")
            return CognitiveResult(
                raw_transcript=raw_transcript,
                normalized_transcript=raw_transcript,
                confidence=ConfidenceLevel.LOW,
                clarification_question="I'm having trouble understanding. Could you repeat that?",
                reasoning=str(e)
            )
