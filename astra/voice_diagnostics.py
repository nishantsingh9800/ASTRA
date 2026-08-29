import os
import sys
import time
import math
import audioop
import threading
from typing import Iterator

# Append astra directory to sys.path so we can import packages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from packages.voice.real_audio_manager import RealAudioManager
from packages.voice.real_vad import RealVADEngine
from packages.voice.local_stt import LocalSTT

def draw_level_bar(rms: int, max_rms: int = 4000, width: int = 40) -> str:
    """Draws a visual audio level bar."""
    if rms == 0:
        return "[" + " " * width + "]"
    
    # Scale RMS logarithmically to fit width
    level = int((math.log10(rms + 1) / math.log10(max_rms + 1)) * width)
    level = min(width, max(0, level))
    
    bar = "#" * level + " " * (width - level)
    return f"[{bar}] {rms:04d}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("Initializing Voice Diagnostics Mode...")
    
    # Initialize components
    try:
        audio = RealAudioManager()
        vad = RealVADEngine()
        stt = LocalSTT()
    except Exception as e:
        print(f"FAILED TO INITIALIZE COMPONENTS: {e}")
        return

    # Diagnostics state
    state = {
        "device": "Default Microphone",
        "permission": "GRANTED",
        "stream": "INACTIVE",
        "rate": audio.rate,
        "channels": audio.channels,
        "rms": 0,
        "frames": 0,
        "last_frame_ts": "N/A",
        "speech_state": "SILENCE",
        "turn_start": "N/A",
        "turn_end": "N/A",
        "duration": "0.0s",
        "partial": "",
        "final": "",
        "confidence": "N/A",
        "status": "Ready",
        "error": ""
    }

    def ui_loop():
        while True:
            clear_screen()
            print("============================================================")
            print("               ASTRA VOICE DIAGNOSTIC MODE                  ")
            print("============================================================\n")
            
            print("[ MICROPHONE ]")
            print(f"Device:      {state['device']}")
            print(f"Permission:  {state['permission']}")
            print(f"Stream:      {state['stream']}")
            print(f"Sample Rate: {state['rate']} Hz")
            print(f"Channels:    {state['channels']}")
            print(f"Frames Rcvd: {state['frames']}")
            print(f"Last Frame:  {state['last_frame_ts']}")
            if state['error']:
                print(f"ERROR:       {state['error']}")
            print(f"Level:       {draw_level_bar(state['rms'])}\n")
            
            print("[ VAD ]")
            print(f"State:       {state['speech_state']}")
            print(f"Turn Start:  {state['turn_start']}")
            print(f"Turn End:    {state['turn_end']}")
            print(f"Duration:    {state['duration']}\n")
            
            print("[ STT ]")
            print(f"Partial:     {state['partial']}")
            print(f"Final:       {state['final']}")
            print(f"Confidence:  {state['confidence']}\n")
            
            print("============================================================")
            print(f"Status: {state['status']}")
            print("============================================================")
            print("Press Ctrl+C to exit.")
            time.sleep(0.1)

    ui_thread = threading.Thread(target=ui_loop, daemon=True)
    ui_thread.start()

    try:
        state['stream'] = "ACTIVE"
        state['status'] = "Listening for speech..."
        audio_stream = audio.start_recording()
        
        # We'll manually pull from the stream to update the UI
        # and buffer it into the VAD engine
        
        while True:
            # Wait for VAD to detect start of speech
            audio_buffer = bytearray()
            has_spoken = False
            silence_start = None
            silence_limit = vad.silence_limit_seconds
            start_time = None
            
            state['speech_state'] = "SILENCE"
            
            for chunk in audio_stream:
                state['frames'] += 1
                state['last_frame_ts'] = time.strftime('%H:%M:%S', time.localtime())
                
                rms = audioop.rms(chunk, 2)
                state['rms'] = rms
                
                audio_buffer.extend(chunk)
                
                if rms > vad.energy_threshold:
                    if not has_spoken:
                        state['speech_state'] = "SPEECH DETECTED"
                        start_time = time.time()
                        state['turn_start'] = time.strftime('%H:%M:%S', time.localtime())
                        state['turn_end'] = "..."
                        state['duration'] = "..."
                        state['status'] = "Recording speech..."
                        state['final'] = ""
                        state['confidence'] = ""
                    has_spoken = True
                    silence_start = None
                else:
                    if has_spoken:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > silence_limit:
                            state['speech_state'] = "END OF TURN"
                            state['turn_end'] = time.strftime('%H:%M:%S', time.localtime())
                            state['duration'] = f"{time.time() - start_time:.1f}s"
                            break
                            
                # Display partial logic (mock for now until faster-whisper streams)
                if has_spoken and len(audio_buffer) % (audio.rate * 2) < 2048:
                    state['partial'] = f"Recording... ({len(audio_buffer)} bytes)"
                    
            if has_spoken:
                state['status'] = "Transcribing..."
                final_audio = bytes(audio_buffer)
                
                # Send to STT
                try:
                    result = stt.transcribe(final_audio)
                    # If STT returns a dict with confidence
                    if isinstance(result, dict):
                        state['final'] = result.get('text', '')
                        state['confidence'] = result.get('confidence', 'HIGH')
                    else:
                        state['final'] = result
                        state['confidence'] = "UNKNOWN"
                        
                    if not state['final']:
                        state['final'] = "[Empty Transcript]"
                except Exception as e:
                    state['final'] = f"[STT Error: {e}]"
                
                state['status'] = "Listening for speech..."
                state['partial'] = ""
                
    except KeyboardInterrupt:
        state['status'] = "Exiting..."
        time.sleep(0.5)
        sys.exit(0)
    except Exception as e:
        state['error'] = str(e)
        state['stream'] = "ERROR"
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
