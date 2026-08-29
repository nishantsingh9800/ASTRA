import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from packages.core.core_orchestrator import CoreOrchestrator
from packages.core.task_planner import TaskPlanner
from packages.ai.model_router import ModelRouter
from packages.ai.gemini_provider import GeminiProvider
from packages.agents.specialized_agents import ResearchAgent, CodingAgent, OSAgent, BrowserAgent

def run_benchmark():
    print("Initializing ASTRA...")
    start_init = time.time()
    llm = GeminiProvider()
    router = ModelRouter(provider=llm)
    
    agents = [ResearchAgent(), CodingAgent(), OSAgent(), BrowserAgent()]
    planner = TaskPlanner(agents=agents, router=router)
    orchestrator = CoreOrchestrator(router=router, planner=planner)
    init_time = time.time() - start_init
    print(f"Initialization took {init_time:.3f}s")
    
    test_prompt = "Open Calculator."
    print(f"Testing baseline latency for: {test_prompt}")
    
    input_data = {
        "type": "voice",
        "text": test_prompt,
        "context": {"active_window": "Desktop"},
        "system_instruction": "Say something short."
    }
    
    start_exec = time.time()
    response = orchestrator.process_request(input_data)
    exec_time = time.time() - start_exec
    
    print(f"Total Latency: {exec_time:.3f}s")
    print(f"Result Status: {response.get('status')}")

if __name__ == "__main__":
    run_benchmark()
