from typing import Dict, Any

class TelemetryTracker:
    """
    Collects safe, aggregate metrics for task success and failure.
    """
    def __init__(self):
        # Maps tool name to success/failure counts
        self.tool_metrics: Dict[str, Dict[str, int]] = {}
        
    def record_success(self, tool_name: str):
        if tool_name not in self.tool_metrics:
            self.tool_metrics[tool_name] = {"success": 0, "failure": 0}
        self.tool_metrics[tool_name]["success"] += 1
        
    def record_failure(self, tool_name: str, context: str):
        if tool_name not in self.tool_metrics:
            self.tool_metrics[tool_name] = {"success": 0, "failure": 0}
        self.tool_metrics[tool_name]["failure"] += 1
        
    def get_metrics(self) -> Dict[str, Any]:
        return self.tool_metrics
