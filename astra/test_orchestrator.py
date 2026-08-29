import sys
import os
import time

# Add current dir to path to import packages correctly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from packages.core import logger
os.environ["ASTRA_LOG_LEVEL"] = "DEBUG"

from packages.core.core_orchestrator import CoreOrchestrator
from packages.ai.model_router import ModelRouter
from packages.core.task_planner import TaskPlanner
from packages.agents.specialized_agents import BrowserAgent, OSAgent, ResearchAgent

print("Initializing ASTRA Core Orchestrator for Golden Tests...")
from packages.ai.gemini_provider import GeminiProvider
llm = GeminiProvider()
router = ModelRouter(provider=llm)
agents = [BrowserAgent(), OSAgent(), ResearchAgent()]
planner = TaskPlanner(agents=agents, router=router)
orchestrator = CoreOrchestrator(router=router, planner=planner)

tests = [
    "Open Calculator.",
    "Open WhatsApp.",
    "Open YouTube.",
    "Calculate 245 times 38.",
    "Open YouTube and search for Main Hoon Na."
]

for idx, test in enumerate(tests):
    print(f"\n{'='*80}\nTEST {idx+1}: {test}\n{'='*80}")
    result = orchestrator.process_request({"text": test})
    time.sleep(2)
