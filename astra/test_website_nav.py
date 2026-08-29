import sys
from packages.core.core_orchestrator import CoreOrchestrator
from packages.ai.model_router import ModelRouter
from packages.ai.gemini_provider import GeminiProvider

def test():
    print("Initializing...")
    llm = GeminiProvider()
    router = ModelRouter(provider=llm)
    
    from packages.agents.specialized_agents import ResearchAgent, CodingAgent, OSAgent, BrowserAgent
    from packages.core.task_planner import TaskPlanner
    agents = [ResearchAgent(), CodingAgent(), OSAgent(), BrowserAgent()]
    planner = TaskPlanner(agents=agents, router=router)
    
    orchestrator = CoreOrchestrator(router=router, planner=planner)
    
    print("\n--- TEST 1: Open YouTube ---")
    req1 = {"type": "text", "text": "Open YouTube."}
    res1 = orchestrator.process_request(req1)
    print("\nResult 1:", res1.get("result"))
    if res1.get("execution_report"):
        print("Status:", res1["execution_report"].get("status"))
        
    print("\n--- TEST 2: Search for Main Hoon Na ---")
    req2 = {"type": "text", "text": "Search for Main Hoon Na."}
    res2 = orchestrator.process_request(req2)
    print("\nResult 2:", res2.get("result"))
    if res2.get("execution_report"):
        print("Status:", res2["execution_report"].get("status"))

    print("\n--- TEST 3: Open Gmail ---")
    req3 = {"type": "text", "text": "Open Gmail."}
    res3 = orchestrator.process_request(req3)
    print("\nResult 3:", res3.get("result"))

if __name__ == "__main__":
    test()
