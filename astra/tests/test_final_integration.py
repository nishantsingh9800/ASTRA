import pytest

# Core
from packages.core.conversation_turn_manager import ConversationTurnManager
from packages.core.task_planner import TaskPlanner

# Voice
from packages.voice.speech_manager import SpeechManager
from packages.voice.conversation_loop import ConversationLoop

# Device & Hardware
from packages.device.capability_manager import CapabilityManager
from packages.device.hardware_adapters import DeviceAdapter, MockGlassesAdapter

# Agents
from packages.agents.specialized_agents import ResearchAgent, CodingAgent

# Memory
from packages.memory.memory_manager import MemoryManager

# Presentation
from packages.presentation.astra_self_knowledge import AstraSelfKnowledge
from packages.presentation.presentation_manager import PresentationModeManager

# Improvement
from packages.improvement.isolated_workspace import IsolatedWorkspace
from packages.improvement.release_manager import ReleaseManager
from packages.improvement.upgrade_supervisor import UpgradeSupervisor

def test_end_to_end_voice_to_agent():
    """
    Tests: Voice Loop -> Task Planner -> Agent Execution -> Voice Response
    Ensuring no duplicate speech and proper state transition.
    """
    speech_mgr = SpeechManager()
    turn_mgr = ConversationTurnManager()
    
    class MockRouter:
        def route_request(self, mode, prompt, context):
            import json
            return json.dumps({"type": "response", "text": "Mocked research result"})

    # Mock an agent workflow
    planner = TaskPlanner([ResearchAgent()], router=MockRouter())
    
    # Simulate a voice request
    request = "Research latest AI news"
    
    # Process
    turn_mgr.set_state("PROCESSING")
    result = planner.execute_goal(request, {})
    
    # Simulate speech output
    turn_mgr.set_state("SPEAKING")
    speech_payload = speech_mgr.request_speech(result, priority="NORMAL", source="llm")
    speech_mgr.notify_speech_complete()
    turn_mgr.set_state("WAITING_FOR_USER")
    
    # Verify State
    assert turn_mgr.get_state() == "WAITING_FOR_USER"
    
    # Verify the speech manager only queued the final output
    assert len(speech_mgr._history) == 1
    assert "Mocked research result" in speech_mgr._history[0]["text"]["final_response"]


def test_strict_judge_mode():
    """
    Tests: Judge mode accurately pulls from runtime DeviceManager, avoiding hallucinations.
    """
    cap_manager = CapabilityManager()
    
    # Connect a laptop
    laptop = DeviceAdapter("l1", "Laptop Mock", "Windows")
    laptop.connect()
    cap_manager.register_device(laptop)
    
    # No glasses connected yet
    self_knowledge = AstraSelfKnowledge(cap_manager)
    presentation = PresentationModeManager(self_knowledge)
    presentation.activate_mode()
    
    ans = presentation.handle_judge_question("Are smart glasses connected?")
    assert "no smart-glass device is currently connected" in ans.lower()
    
    # Connect glasses
    glasses = MockGlassesAdapter("g1")
    glasses.connect()
    cap_manager.register_device(glasses)
    
    ans2 = presentation.handle_judge_question("Are smart glasses connected?")
    assert "currently connected and active" in ans2.lower()


def test_improvement_rollback_safety():
    """
    Tests: If an emergency update fails the health check, it rolls back immediately.
    """
    workspace = IsolatedWorkspace()
    manager = ReleaseManager()
    supervisor = UpgradeSupervisor(workspace, manager)
    
    proposal = {"id": "EMERGENCY-1"}
    
    # Inject a health check failure
    success = supervisor.process_proposal(proposal, inject_test_failure=False, inject_health_failure=True)
    
    assert success is False
    assert manager.current_version == "2.0.10"  # Rolled back
    assert manager.upgrade_history[-1]["action"] == "rollback"
