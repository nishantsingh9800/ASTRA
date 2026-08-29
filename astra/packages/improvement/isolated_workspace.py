from typing import Dict, Any

class IsolatedWorkspace:
    """
    Simulates a Git branch where candidate code is built and tested without affecting production.
    """
    def __init__(self):
        self.active_candidates = {}

    def create_candidate(self, proposal: Dict[str, Any]) -> str:
        """
        Creates a git branch for the proposal.
        """
        candidate_id = f"candidate-{proposal['id']}"
        import subprocess
        try:
            # Check if we are in a git repo
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True)
            subprocess.run(["git", "checkout", "-b", candidate_id], check=True, capture_output=True)
            print(f"[IsolatedWorkspace] Created real git branch {candidate_id}")
        except Exception:
            print(f"[IsolatedWorkspace] Git not available or not a repository. Using mock sandbox for {candidate_id}")
            
        self.active_candidates[candidate_id] = {
            "proposal": proposal,
            "status": "BUILT",
            "test_results": None
        }
        return candidate_id
        
    def run_tests(self, candidate_id: str, inject_failure: bool = False) -> bool:
        """
        Mocks running unit, integration, and regression tests.
        """
        print(f"[IsolatedWorkspace] Running tests for {candidate_id}...")
        
        # We can simulate test failure via inject_failure flag
        passed = not inject_failure
        
        self.active_candidates[candidate_id]["test_results"] = "PASS" if passed else "FAIL"
        return passed
