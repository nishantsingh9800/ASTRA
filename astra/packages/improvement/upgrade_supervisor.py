from typing import Dict, Any, Optional
from packages.improvement.isolated_workspace import IsolatedWorkspace
from packages.improvement.release_manager import ReleaseManager

class UpgradeSupervisor:
    """
    The protected state machine that manages the release gates for any proposed candidate.
    """
    def __init__(self, workspace: IsolatedWorkspace, release_manager: ReleaseManager):
        self.workspace = workspace
        self.release_manager = release_manager

    def process_proposal(self, proposal: Dict[str, Any], inject_test_failure: bool = False, inject_health_failure: bool = False) -> bool:
        """
        Orchestrates the entire software engineering lifecycle for a proposal.
        """
        print(f"[UpgradeSupervisor] Processing Proposal {proposal['id']}")
        
        # 1. Isolate and Build
        candidate_id = self.workspace.create_candidate(proposal)
        
        # 2. Run automated tests (Unit, Integration, Regression, Benchmark, Security)
        tests_passed = self.workspace.run_tests(candidate_id, inject_failure=inject_test_failure)
        if not tests_passed:
            print(f"[UpgradeSupervisor] REJECTED. Tests failed for {candidate_id}.")
            return False
            
        print(f"[UpgradeSupervisor] ACCEPTED. Tests passed. Deploying {candidate_id}...")
        
        # 3. Deploy
        self.release_manager.deploy(candidate_id)
        
        # 4. Health Check
        is_healthy = self.release_manager.run_health_check(inject_failure=inject_health_failure)
        if not is_healthy:
            # 5. Rollback if unhealthy
            self.release_manager.rollback()
            return False
            
        # 6. Commit release
        self.release_manager.commit_release(proposal)
        return True
