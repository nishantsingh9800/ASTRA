import pytest
from packages.agents.specialized_agents import ResearchAgent, CodingAgent, DocumentAgent
from packages.core.task_planner import TaskPlanner
from packages.memory.memory_manager import MemoryManager
from packages.device.capability_manager import CapabilityManager
from packages.device.hardware_adapters import DeviceAdapter, MockGlassesAdapter
from packages.presentation.astra_self_knowledge import AstraSelfKnowledge
from packages.presentation.presentation_manager import PresentationModeManager

class MockRouter:
    def route_request(self, mode, prompt, context):
        import json
        if "AI news" in prompt:
            return json.dumps({"type": "response", "text": "Mocked research result"})
        elif "Fix the failing test" in prompt:
            return json.dumps({"type": "response", "text": "Mocked code modification"})
        return json.dumps({"type": "response", "text": "Mocked result"})

def test_autonomous_task_loop():
    agents = [ResearchAgent(), CodingAgent(), DocumentAgent()]
    planner = TaskPlanner(agents, router=MockRouter())
    
    # Test a research flow
    res = planner.execute_goal("Search for the latest AI news and summarize", {})
    assert "Mocked research result" in res["final_response"]
    
    # Test a coding flow
    res2 = planner.execute_goal("Fix the failing test", {})
    assert "Mocked code modification" in res2["final_response"]

def test_memory_segregation():
    memory = MemoryManager()
    
    memory.add_to_working_memory("current_file", "test.py")
    memory.add_to_session_memory("user_name", "Nishant")
    memory.set_preference("verbosity", "CONCISE")
    
    assert memory.get_context_snapshot()["working"]["current_file"] == "test.py"
    
    # Simulate end of task
    memory.clear_working_memory()
    
    snapshot = memory.get_context_snapshot()
    assert "current_file" not in snapshot["working"]
    assert snapshot["session"]["user_name"] == "Nishant"
    assert snapshot["preferences"]["verbosity"] == "CONCISE"

def test_judge_mode_truthfulness():
    cap_manager = CapabilityManager()
    # Add a laptop but NO smart glasses
    laptop = DeviceAdapter("laptop_1", "Laptop Mock", "Windows")
    laptop.connect()
    cap_manager.register_device(laptop)
    
    self_knowledge = AstraSelfKnowledge(cap_manager)
    presentation = PresentationModeManager(self_knowledge)
    
    # Before activation, it should ignore judge questions
    assert presentation.handle_judge_question("Are smart glasses connected?") is None
    
    # Activate judge mode
    presentation.activate_mode()
    
    # It must truthfully say glasses are NOT connected
    ans = presentation.handle_judge_question("Are smart glasses connected?")
    assert "no smart-glass device is currently connected" in ans.lower()
    
    # Add glasses
    glasses = MockGlassesAdapter("g1")
    glasses.connect()
    cap_manager.register_device(glasses)
    
    # Now it must say they are connected
    ans2 = presentation.handle_judge_question("Are smart glasses connected?")
    assert "currently connected and active" in ans2.lower()

def test_demo_safe_mode():
    presentation = PresentationModeManager(AstraSelfKnowledge(CapabilityManager()))
    
    presentation.activate_mode()
    # Safe actions should pass
    assert presentation.check_safe_mode("web_search") is True
    # Destructive actions should fail
    assert presentation.check_safe_mode("delete_file") is False
    assert presentation.check_safe_mode("send_email") is False
    
    presentation.deactivate_mode()
    # Destructive actions allowed when not in demo mode (assuming standard permission gates apply elsewhere)
    assert presentation.check_safe_mode("delete_file") is True
