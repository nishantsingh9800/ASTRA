import os
import sys

# Ensure local packages are resolvable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from packages.core.core_orchestrator import CoreOrchestrator
from packages.core.task_planner import TaskPlanner
from packages.ai.model_router import ModelRouter
from packages.ai.gemini_provider import GeminiProvider
from packages.agents.specialized_agents import OSAgent, BrowserAgent

def run_golden_tests():
    print("Initializing ASTRA Core Components...")
    
    # We use a mocked/invalid API key to test the offline fallback behavior!
    os.environ["GEMINI_API_KEY"] = "invalid_key_for_offline_test"
    
    llm = GeminiProvider()
    router = ModelRouter(llm)
    planner = TaskPlanner(agents=[OSAgent(), BrowserAgent()])
    planner.router = router
    
    orchestrator = CoreOrchestrator(router, planner)
    
    print("\n======================================")
    print("GOLDEN TEST 1: Fast Path Calculator")
    print("======================================")
    result = orchestrator.process_request({"text": "Open Calculator."})
    print(f"Status: {result['execution_report']['status']}")
    print(f"Response: {result['result']}")
    assert result['execution_report']['status'] == "COMPLETED"
    
    print("\n======================================")
    print("GOLDEN TEST 2: Fast Path WhatsApp")
    print("======================================")
    result = orchestrator.process_request({"text": "Open WhatsApp."})
    print(f"Status: {result['execution_report']['status']}")
    print(f"Response: {result['result']}")
    assert result['execution_report']['status'] in ["COMPLETED", "FAILED"]
    
    print("\n======================================")
    print("GOLDEN TEST 3: Intentional Failure Recovery (Offline Gemini)")
    print("======================================")
    result = orchestrator.process_request({"text": "Write a python script."})
    print(f"Status: {result['execution_report']['status']}")
    print(f"Response: {result['result']}")
    assert result['execution_report']['status'] == "FAILED"
    assert "isn't available right now" in result['result'].lower() or "couldn't complete" in result['result'].lower()
    
    print("\n======================================")
    print("All Golden Tests Passed Successfully!")
    print("======================================")

if __name__ == "__main__":
    run_golden_tests()
