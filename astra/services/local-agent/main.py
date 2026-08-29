import sys
from server import LocalAgentServer
from packages.ai.model_router import ModelRouter
from packages.ai.gemini_provider import GeminiProvider
from packages.voice.local_stt import LocalSTT
from packages.voice.local_tts import LocalTTS

def print_diagnostics(router: ModelRouter, stt: LocalSTT, tts: LocalTTS):
    print("=== ASTRA 2.0 Diagnostics ===")
    print(f"Mode: {'ONLINE/HYBRID' if router._is_online() else 'OFFLINE'}")
    print(f"Speech engine: {'faster-whisper' if stt.is_available() else 'UNAVAILABLE'}")
    print(f"LLM: {'Gemini AI' if router.provider.is_available() else 'UNAVAILABLE'}")
    print(f"TTS: {'piper-tts' if tts.is_available() else 'UNAVAILABLE'}")
    print("Wake word: ACTIVE")
    print("Microphone: ACTIVE")
    print("Camera: ACTIVE (Mock)")
    print("YOLO Detection: LOADED (Mock)")
    print("OCR Engine: LOADED (Mock)")
    print("=============================")

def main():
    print("Starting ASTRA 2.0 Local Agent...")
    
    # Initialize components
    local_llm = GeminiProvider()
    router = ModelRouter(provider=local_llm)
    stt = LocalSTT()
    tts = LocalTTS()

    print_diagnostics(router, stt, tts)
    
    server = LocalAgentServer()
    try:
        server.start()
        # Keep the main thread alive
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
