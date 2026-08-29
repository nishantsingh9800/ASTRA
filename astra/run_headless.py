import argparse
import time
import sys
sys.coinit_flags = 2  # Mandatory for PyWinAuto UIA backend in STA mode
import datetime
import atexit
import traceback
from packages.core import logger

def exit_handler():
    print("\nEXIT TYPE: atexit")
    print(f"EXIT CALLSITE: {traceback.extract_stack()}")
atexit.register(exit_handler)

# Core & Architecture
from packages.core.conversation_turn_manager import ConversationTurnManager
from packages.core.task_planner import TaskPlanner
from packages.core.core_orchestrator import CoreOrchestrator

# Voice & Conversation Loop
from packages.voice.speech_manager import SpeechManager
from packages.voice.conversation_loop import ConversationLoop
from packages.voice.audio_manager import AudioManager as AudioManagerInterface
from packages.voice.wake_word_engine import WakeWordEngine as WakeWordEngineInterface
from packages.voice.vad_engine import VADEngine as VADEngineInterface
from packages.voice.local_stt import LocalSTT
from packages.voice.local_tts import LocalTTS

from packages.voice.real_audio_manager import RealAudioManager
from packages.voice.real_wake_word import RealWakeWordEngine
from packages.voice.real_vad import RealVADEngine

# Device Management
from packages.device.capability_manager import CapabilityManager
from packages.device.hardware_adapters import DeviceAdapter

# AI & Agents
from packages.ai.model_router import ModelRouter
from packages.ai.gemini_provider import GeminiProvider
from packages.agents.specialized_agents import ResearchAgent, CodingAgent, OSAgent, BrowserAgent

def start_headless(device_id: str, device_name: str, device_type: str):
    logger.user_facing("ASTRA 2.0")
    logger.user_facing("────────────────────────────")
    logger.debug(f"Device: {device_name} ({device_type}) | ID: {device_id}")
    
    # 1. Initialize State Managers
    turn_mgr = ConversationTurnManager()
    speech_mgr = SpeechManager()
    
    # 2. Register this specific device's capabilities
    cap_manager = CapabilityManager()
    local_device = DeviceAdapter(device_id, device_name, device_type)
    local_device.connect()
    cap_manager.register_device(local_device)
    logger.debug(f"[Boot] Registered hardware capabilities for {device_name}")
    
    # Track status
    status = {
        "Gemini AI": "✓",
        "Voice": "✓",
        "Local Agent": "✓",
        "Vision": "unavailable", # Placeholder if no vision initialized here yet
        "Devices": "✓"
    }

    # 3. Initialize AI Router & Planner
    try:
        llm = GeminiProvider()
        if not llm.is_available():
            status["Gemini AI"] = "unavailable"
        router = ModelRouter(provider=llm)
    except Exception as e:
        status["Gemini AI"] = "unavailable"
        router = None
        logger.debug(f"Gemini AI init failed: {e}")
    
    try:
        agents = [ResearchAgent(), CodingAgent(), OSAgent(), BrowserAgent()]
        planner = TaskPlanner(agents=agents, router=router)
    except Exception as e:
        status["Local Agent"] = "disconnected"
        planner = None
        logger.debug(f"Local Agent init failed: {e}")
    
    # 4. Initialize Core Orchestrator
    orchestrator = CoreOrchestrator(router=router, planner=planner, turn_manager=turn_mgr)
    
    # 5. Initialize Hardware Sensors for Headless Loop
    try:
        audio = RealAudioManager()
        if audio.stream is None and getattr(audio, 'rate', None) is None:
            # If audio setup failed fundamentally
            pass
    except Exception as e:
        status["Voice"] = "unavailable"
        audio = None
        logger.debug(f"Mic init failed: {e}")
        
    try:
        wake = RealWakeWordEngine()
        vad = RealVADEngine(sample_rate=audio.rate if audio else 16000)
        stt = LocalSTT(sample_rate=audio.rate if audio else 16000)
        if not stt.is_available():
            status["Voice"] = "unavailable"
        tts = LocalTTS()
    except Exception as e:
        status["Voice"] = "unavailable"
        logger.debug(f"Voice pipeline init failed: {e}")
        wake = vad = stt = tts = None
    
    # 6. Start the Headless Conversation Loop
    if audio and wake and vad and stt and tts:
        # Determine Greeting
        hour = datetime.datetime.now().hour
        if hour < 12:
            time_greet = "Good morning"
        elif hour < 17:
            time_greet = "Good afternoon"
        else:
            time_greet = "Good evening"
            
        if status["Gemini AI"] == "unavailable":
            greeting = f"{time_greet}! I'm Astra. I'm ready for local tasks, but my cloud AI connection is currently unavailable."
        else:
            greeting = f"{time_greet}! I'm Astra, your personal AI assistant. I'm up and running and ready to help."
            
        loop = ConversationLoop(
            audio, wake, vad, stt, tts, orchestrator, turn_manager=turn_mgr, speech_manager=speech_mgr, startup_greeting=greeting
        )
    else:
        loop = None

    # Print startup status
    for key, val in status.items():
        if val == "✓":
            logger.user_facing(f"● {key} Ready")
        else:
            logger.user_facing(f"○ {key} {val}")
            
    logger.user_facing("")
            
    if status["Voice"] == "unavailable":
        logger.user_facing("Microphone unavailable. Voice input is disabled.\n")
    
    try:
        if loop:
            # In a real environment, this blocks and runs the infinite audio processing loop.
            logger.debug("[BOOT] entering startup")
            logger.debug("[BOOT] starting ConversationLoop")
            loop.start()
            logger.debug("[BOOT] ConversationLoop exited! Main loop returned.")
        else:
            logger.error("Core systems failed to initialize. Exiting.")
            logger.user_facing("[SHUTDOWN] reason: FATAL_SYSTEM_ERROR")
            logger.user_facing("[SHUTDOWN] requested")
    except KeyboardInterrupt:
        logger.user_facing("\n[SHUTDOWN] requested")
        logger.user_facing("[SHUTDOWN] reason: EXTERNAL_TERMINATION")
        # loop.stop()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal unhandled exception: {e}")
        logger.user_facing("[SHUTDOWN] requested")
        logger.user_facing("[SHUTDOWN] reason: FATAL_SYSTEM_ERROR")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ASTRA 2.0 Headlessly")
    parser.add_argument("--id", type=str, default="local_01", help="Unique ID for this device")
    parser.add_argument("--name", type=str, default="Headless Node", help="Friendly name of the device")
    parser.add_argument("--type", type=str, default="Headless", help="Type of device (e.g. RaspberryPi, Server, Wearable)")
    
    args = parser.parse_args()
    
    start_headless(args.id, args.name, args.type)
