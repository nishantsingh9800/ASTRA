from typing import Dict, Any, Optional
from packages.improvement.failure_analysis import FailureAnalyzer

class ImprovementEngine:
    """
    Evaluates Root Causes and creates formal Improvement Proposals.
    """
    def __init__(self, failure_analyzer: FailureAnalyzer):
        self.analyzer = failure_analyzer
        self.proposals = []

    def generate_proposal(self) -> Optional[Dict[str, Any]]:
        root_cause_data = self.analyzer.analyze()
        if not root_cause_data:
            return None
            
        proposal = {
            "id": f"PROP-{len(self.proposals) + 1}",
            "problem": root_cause_data["symptom"],
            "root_cause": root_cause_data["root_cause"],
            "proposed_change": f"Increase timeout for {root_cause_data['tool']} and add exponential backoff.",
            "expected_benefit": f"Fewer {root_cause_data['tool']} failures.",
            "status": "CANDIDATE"
        }
        
        print(f"[ImprovementEngine] Generated Proposal: {proposal['id']} - {proposal['proposed_change']}")
        self.proposals.append(proposal)
        return proposal
