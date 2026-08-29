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
