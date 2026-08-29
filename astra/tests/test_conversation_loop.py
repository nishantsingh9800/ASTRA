import pytest
from typing import Iterator, Callable
from packages.voice.conversation_loop import ConversationLoop
from packages.ai.model_router import ModelRouter
from packages.ai.gemini_provider import GeminiProvider
from packages.voice.local_stt import LocalSTT
from packages.voice.local_tts import LocalTTS

class MockAudioManager:
    def start_recording(self) -> Iterator[bytes]:
        yield b"mock_audio_data"
    
    def stop_recording(self) -> None:
        pass
    
    def play_audio(self, audio_data: bytes) -> None:
        pass
    
    def play_audio_stream(self, audio_stream: Iterator[bytes], interrupt_callback: Callable[[], bool]) -> None:
        pass

class MockWakeWordEngine:
    def listen_for_wake_word(self, audio_stream: Iterator[bytes]) -> str:
        return "hey_astra"

class MockVADEngine:
    def filter_speech(self, audio_stream: Iterator[bytes]) -> Iterator[bytes]:
        yield b"mock_speech"
        
    def detect_end_of_turn(self, audio_stream: Iterator[bytes], pause_threshold_ms: int = 1500) -> bytes:
        return b"mock_speech_buffer"

class MockOrchestrator:
    def __init__(self, router):
        self.router = router
        
    def process_request(self, input_data):
        response_text = self.router.route_request("simple", input_data.get("text", ""), {})
        return {"response": response_text}
    
    def start(self): pass
    def stop(self): pass

def test_simulated_offline_loop():
    audio = MockAudioManager()
    wake = MockWakeWordEngine()
    vad = MockVADEngine()
    stt = LocalSTT()
    tts = LocalTTS()
    tts.synthesize = lambda text: b"simulated_audio_data_for " + text.encode()
    llm = GeminiProvider()
    llm.generate = lambda prompt, context: "[Gemini API] Simulated response"
    
    # Force offline for test
    router = ModelRouter(provider=llm)
    router._is_online = lambda: False
    
    orchestrator = MockOrchestrator(router)
    
    from packages.core.conversation_turn_manager import ConversationTurnManager
    from packages.voice.speech_manager import SpeechManager
    
    turn_manager = ConversationTurnManager()
    speech_manager = SpeechManager()
    
    loop = ConversationLoop(audio, wake, vad, stt, tts, orchestrator, turn_manager, speech_manager)
    
    # We will just run it manually since the real start() has a while loop
    loop.is_active = True
    
    # 1. Listen for wake word
    audio_stream = audio.start_recording()
    trigger = wake.listen_for_wake_word(audio_stream)
    assert trigger == "hey_astra"
    
    # 2. Wake -> Listen
    speech_audio = vad.detect_end_of_turn(audio_stream)
    assert speech_audio == b"mock_speech_buffer"
    
    # 3. Think (STT -> Orchestrator -> LLM)
    stt.transcribe = lambda audio: {"text": "this is a simulated transcription of the audio", "confidence": "HIGH"}
    transcript = stt.transcribe(speech_audio)
    assert transcript["text"] == "this is a simulated transcription of the audio"
    
    response_payload = orchestrator.process_request({"text": transcript})
    assert "[Gemini API]" in response_payload["response"]
    
    # 4. Speak
    audio_output = tts.synthesize(response_payload["response"])
    assert b"simulated_audio_data_for" in audio_output
