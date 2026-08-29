import os
from flask import Flask, send_from_directory, request, jsonify

# Core & Architecture
from packages.core.task_planner import TaskPlanner
from packages.core.core_orchestrator import CoreOrchestrator
from packages.device.capability_manager import CapabilityManager
from packages.device.hardware_adapters import DeviceAdapter

# AI & Agents
from packages.ai.model_router import ModelRouter
from packages.ai.gemini_provider import GeminiProvider
from packages.agents.specialized_agents import ResearchAgent, CodingAgent, OSAgent, BrowserAgent

app = Flask(__name__, static_folder='static')

# Initialize ASTRA Core once globally for the server
print("=== Initializing ASTRA 2.0 Backend ===")
cap_manager = CapabilityManager()
local_device = DeviceAdapter("web_01", "Web Interface", "Browser")
local_device.connect()
cap_manager.register_device(local_device)

llm = GeminiProvider()
router = ModelRouter(provider=llm)
agents = [ResearchAgent(), CodingAgent(), OSAgent(), BrowserAgent()]
planner = TaskPlanner(agents=agents, router=router)

orchestrator = CoreOrchestrator(router=router, planner=planner)
print("=== ASTRA 2.0 Backend Ready ===")

@app.route('/')
def index():
    """Serve the main UI html."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    """Serve static CSS/JS files."""
    return send_from_directory(app.static_folder, path)

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint to handle chat messages."""
    data = request.json
    user_text = data.get("message", "")
    
    if not user_text:
        return jsonify({"error": "Empty message"}), 400
        
    print(f"\n[WebUI] Received: {user_text}")
    
    # Process through the orchestrator
    try:
        response_payload = orchestrator.process_request({
            "type": "text", 
            "text": user_text,
            "context": {"source": "web_ui"}
        })
        
        reply = response_payload.get("result", "")
        # fallback if result format varies
        if not reply:
            reply = response_payload.get("response", "I have processed your request.")
            
        print(f"[WebUI] Responding: {reply}")
        return jsonify({"response": reply})
        
    except Exception as e:
        print(f"[WebUI] Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\nStarting ASTRA UI Server on http://127.0.0.1:5000")
    # debug=False to avoid re-initializing the model router twice
    app.run(host='127.0.0.1', port=5000, debug=False)
