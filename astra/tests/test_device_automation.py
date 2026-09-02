import pytest
from packages.device.application_resolver import ApplicationResolver
from packages.device.window_manager import WindowManager
from packages.device.computer_tools import ComputerTools

def test_application_resolver_native():
    resolver = ApplicationResolver()
    
    # Test resolving WhatsApp
    result = resolver.resolve_application("WhatsApp")
    assert result is not None
    assert result["executable"] == "whatsapp://"
    
    # Test resolving Calculator
    result = resolver.resolve_application("Calculator")
    assert result is not None
    assert result["executable"] == "calc.exe"

def test_computer_tools_open_and_verify():
    resolver = ApplicationResolver()
    wm = WindowManager()
    tools = ComputerTools(resolver, wm)
    
    # Simulate opening an app
    result = tools.open_application("VS Code")
    
    # Verify the result follows the OBSERVE -> ACTION -> VERIFY strict requirement
    assert result["success"] is True
    assert result["target"] == "code.exe"
    assert "observedState" in result
    
    # Verify context was updated
    context = wm.get_active_context()
    assert context["activeApplication"] == "code.exe"
    assert "Mock Window" in context["activeWindow"]

def test_open_all_and_multiple_applications():
    from packages.core.local_action_classifier import LocalActionClassifier
    from packages.core.application_registry import ApplicationRegistry
    from packages.agents.specialized_agents import OSAgent

    classifier = LocalActionClassifier()
    registry = ApplicationRegistry()

    # 1. Test "open all applications"
    res_all = classifier.classify("open all applications")
    assert res_all is not None
    assert res_all["action"] == "open_all_applications"
    assert res_all["target"] == "all"

    res_all_apps = classifier.classify("launch all apps")
    assert res_all_apps is not None
    assert res_all_apps["action"] == "open_all_applications"

    # 2. Test "open multiple applications"
    res_multi = classifier.classify("open notepad and calculator")
    assert res_multi is not None
    assert res_multi["action"] == "open_multiple_applications"
    assert "notepad" in res_multi["target"]
    assert "calculator" in res_multi["target"]

    # 3. Test multi-app parsing
    parsed = registry.parse_multiple("chrome, vs code and notepad")
    assert "chrome" in parsed
    assert "vs code" in parsed
    assert "notepad" in parsed

    # 4. Test OSAgent execution
    agent = OSAgent()
    exec_res = agent.execute({"action": "open_all_applications", "target": "all"}, {})
    assert exec_res["status"] == "success"
    assert len(exec_res.get("opened_apps", [])) > 0
