from packages.core.task_planner import TaskPlanner
from packages.core.models import Intent, TargetType

def test():
    planner = TaskPlanner(agents=[])
    
    # Mocking the router directly inside the planner by subclassing or monkey patching
    class MockRouter:
        def route_request(self, task_type, prompt, context):
            # Return a response that simulates failure
            return '{"type": "response", "text": "I encountered an issue trying to open the app."}'
            
    planner.router = MockRouter()
    
    intent = Intent(action="open", target_type=TargetType.APPLICATION, target="Chrome", raw_text="Open Chrome")
    result = planner.execute_goal(intent, {})
    print("Result Status:", result["status"])
    print("Final Response:", result["final_response"])

if __name__ == "__main__":
    test()
