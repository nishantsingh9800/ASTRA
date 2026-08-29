import os
import time
from packages.voice.local_tts import LocalTTS
from packages.voice.local_stt import LocalSTT

def run_stt_benchmark():
    print("Initializing STT and TTS...")
    tts = LocalTTS()
    stt = LocalSTT(sample_rate=16000)
    
    # Synthesize "Open WhatsApp."
    print("Synthesizing test audio...")
    wav_bytes = tts.synthesize("Open WhatsApp.")
    
    print("Running STT Benchmark (20 iterations)...")
    correct_count = 0
    total_latency = 0.0
    
    for i in range(20):
        start = time.time()
        result = stt.transcribe(wav_bytes, sample_rate=16000, channels=1)
        latency = time.time() - start
        total_latency += latency
        
        transcript = result.get("text", "").strip() if isinstance(result, dict) else result.strip()
        confidence = result.get("confidence", "UNKNOWN") if isinstance(result, dict) else "UNKNOWN"
        
        print(f"[{i+1}/20] Latency: {latency:.3f}s | Confidence: {confidence} | Transcript: '{transcript}'")
        
        if "whatsapp" in transcript.lower() and "open" in transcript.lower() and "throw up" not in transcript.lower():
            correct_count += 1
            
    avg_latency = total_latency / 20.0
    accuracy = (correct_count / 20.0) * 100
    
    print("\n--- BENCHMARK RESULTS ---")
    print(f"Correct Transcript Percentage: {accuracy}%")
    print(f"Average Latency: {avg_latency:.3f}s")
    
if __name__ == "__main__":
    run_stt_benchmark()
