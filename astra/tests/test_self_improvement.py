import pytest
from packages.improvement.telemetry import TelemetryTracker
from packages.improvement.failure_analysis import FailureAnalyzer
from packages.improvement.improvement_engine import ImprovementEngine
from packages.improvement.isolated_workspace import IsolatedWorkspace
from packages.improvement.release_manager import ReleaseManager
from packages.improvement.upgrade_supervisor import UpgradeSupervisor

def test_telemetry_threshold():
    telemetry = TelemetryTracker()
    analyzer = FailureAnalyzer(telemetry)
    engine = ImprovementEngine(analyzer)
    
    # 2 failures (Threshold is 3)
    telemetry.record_failure("browser.open", "timeout")
    telemetry.record_failure("browser.open", "timeout")
    assert engine.generate_proposal() is None
    
    # 3rd failure breaches threshold
    telemetry.record_failure("browser.open", "timeout")
    proposal = engine.generate_proposal()
    
    assert proposal is not None
    assert proposal["problem"] == "Tool browser.open failed 3 times."
    assert "timeout" in proposal["proposed_change"].lower()

def test_upgrade_supervisor_success():
    proposal = {"id": "PROP-1", "problem": "Test", "root_cause": "Test", "proposed_change": "Test", "expected_benefit": "Test", "status": "CANDIDATE"}
    
    workspace = IsolatedWorkspace()
    manager = ReleaseManager()
    supervisor = UpgradeSupervisor(workspace, manager)
    
    # Successful pipeline
    success = supervisor.process_proposal(proposal, inject_test_failure=False, inject_health_failure=False)
    assert success is True
    assert manager.current_version == "2.0.10.1-candidate"
    assert manager.upgrade_history[-1]["action"] == "release"

def test_upgrade_supervisor_test_failure():
    proposal = {"id": "PROP-2"}
    workspace = IsolatedWorkspace()
    manager = ReleaseManager()
    supervisor = UpgradeSupervisor(workspace, manager)
    
    # Tests fail in isolated workspace -> No deployment happens
    success = supervisor.process_proposal(proposal, inject_test_failure=True, inject_health_failure=False)
    assert success is False
    assert manager.current_version == "2.0.10" # Unchanged
    assert len(manager.upgrade_history) == 0

def test_upgrade_supervisor_health_rollback():
    proposal = {"id": "PROP-3"}
    workspace = IsolatedWorkspace()
    manager = ReleaseManager()
    supervisor = UpgradeSupervisor(workspace, manager)
    
    # Tests pass, deployment happens, BUT health check fails
    success = supervisor.process_proposal(proposal, inject_test_failure=False, inject_health_failure=True)
    assert success is False
    # Version should have rolled back
    assert manager.current_version == "2.0.10"
    assert manager.upgrade_history[-1]["action"] == "rollback"
