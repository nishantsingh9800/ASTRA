from typing import Dict, Any

class ReleaseManager:
    """
    Handles deployment, post-deployment health checks, and rollback.
    """
    def __init__(self):
        self.current_version = "2.0.10"
        self.upgrade_history = []
        self.last_known_good = self.current_version
        
    def deploy(self, candidate_id: str) -> str:
        """
        Mocks deployment of a candidate.
        """
        print(f"[ReleaseManager] Deploying {candidate_id}...")
        self.current_version = f"{self.current_version}.1-candidate"
        return self.current_version

    def run_health_check(self, inject_failure: bool = False) -> bool:
        """
        Simulates verifying all core components (Voice, Vision, Safety) post-deployment.
        """
        print("[ReleaseManager] Running full health check...")
        return not inject_failure

    def rollback(self):
        """
        Restores the last known good configuration if health checks fail.
        """
        print(f"[ReleaseManager] Health check FAILED. Rolling back to {self.last_known_good}...")
        self.current_version = self.last_known_good
        self.upgrade_history.append({"action": "rollback", "restored_version": self.current_version})

    def commit_release(self, proposal: Dict[str, Any]):
        """
        Finalizes the deployment if health checks pass.
        """
        self.last_known_good = self.current_version
        self.upgrade_history.append({
            "action": "release",
            "proposal": proposal["id"],
            "version": self.current_version
        })
        print(f"[ReleaseManager] Release successful. Current version is {self.current_version}")
