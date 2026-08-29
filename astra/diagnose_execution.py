import os
import sys
import json

# Append astra directory to sys.path so we can import packages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from packages.core.core_orchestrator import CoreOrchestrator
from packages.core.task_planner import TaskPlanner
from packages.ai.model_router import ModelRouter
from packages.ai.gemini_provider import GeminiProvider
from packages.agents.specialized_agents import ResearchAgent, CodingAgent, OSAgent, BrowserAgent

def run_diagnostics(test_prompt: str):
    print(f"\n============================================================")
    print(f" DIAGNOSING TASK EXECUTION")
    print(f"============================================================")
    print(f"User Input: {test_prompt}\n")
    
    llm = GeminiProvider()
    router = ModelRouter(provider=llm)
    
    agents = [ResearchAgent(), CodingAgent(), OSAgent(), BrowserAgent()]
    planner = TaskPlanner(agents=agents, router=router)
    orchestrator = CoreOrchestrator(router=router, planner=planner)
    
    print("[1] STARTING PIPELINE")
    
    input_data = {
        "type": "voice",
        "text": test_prompt,
        "context": {"active_window": "Desktop"},
        "system_instruction": "Say something short."
    }
    
    print(f"\n[2] ORCHESTRATOR REQUEST:")
    print(json.dumps(input_data, indent=2))
    
    try:
        response = orchestrator.process_request(input_data)
        print(f"\n[3] FINAL RESPONSE PAYLOAD:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"\n[3] ERROR DURING PIPELINE: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_diagnostics(" ".join(sys.argv[1:]))
    else:
        run_diagnostics("Open Calculator.")
        run_diagnostics("Calculate 245 times 38.")
        run_diagnostics("Open YouTube and search for Main Hoon Na.")
