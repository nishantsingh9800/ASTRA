import pytest
import time
from packages.core.models import Task, TaskGraph, TargetType, TaskStatus
from packages.core.task_manager import TaskManager
from packages.core.resource_manager import ResourceManager

def test_resource_manager():
    rm = ResourceManager()
    assert rm.acquire("t1", ["browser"]) == True
    assert rm.acquire("t2", ["calculator"]) == True
    assert rm.acquire("t3", ["browser"]) == False # Conflict
    
    rm.release("t1")
    assert rm.acquire("t3", ["browser"]) == True

def test_task_graph_dependencies():
    g = TaskGraph()
    t1 = Task(task_id="t1", goal="open app", action="open", target_type=TargetType.APPLICATION, status=TaskStatus.PENDING)
    t2 = Task(task_id="t2", goal="calculate", action="calculate", target_type=TargetType.UNKNOWN, dependencies=["t1"], status=TaskStatus.PENDING)
    
    g.add_task(t1)
    g.add_task(t2)
    
    ready = g.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].task_id == "t1"
    
    t1.status = TaskStatus.COMPLETED
    ready = g.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].task_id == "t2"

def test_task_manager_parallel_execution():
    g = TaskGraph()
    t1 = Task(task_id="t1", goal="task1", action="open", target_type=TargetType.APPLICATION, resources=["r1"])
    t2 = Task(task_id="t2", goal="task2", action="open", target_type=TargetType.APPLICATION, resources=["r2"])
    
    g.add_task(t1)
    g.add_task(t2)
    
    tm = TaskManager(max_parallel_tasks=2)
    
    def dummy_planner(task):
        time.sleep(0.5)
        return {"status": "success", "result": f"{task.task_id} done"}
        
    start_time = time.time()
    res = tm.execute_graph(g, dummy_planner)
    end_time = time.time()
    
    assert res["status"] == "COMPLETED"
    assert res["task_results"]["t1"]["result"] == "t1 done"
    assert res["task_results"]["t2"]["result"] == "t2 done"
    
    # Should take ~0.5s because they run in parallel, not 1.0s
    assert (end_time - start_time) < 0.9

def test_task_manager_partial_failure():
    g = TaskGraph()
    t1 = Task(task_id="t1", goal="task1", action="open", target_type=TargetType.APPLICATION)
    t2 = Task(task_id="t2", goal="task2", action="open", target_type=TargetType.APPLICATION)
    
    g.add_task(t1)
    g.add_task(t2)
    
    tm = TaskManager()
    
    def dummy_planner(task):
        if task.task_id == "t1":
            return {"status": "success", "result": "t1 done"}
        else:
            return {"status": "error", "details": "t2 failed"}
            
    res = tm.execute_graph(g, dummy_planner)
    
    assert res["status"] == "PARTIAL_SUCCESS"
    assert res["task_results"]["t1"]["status"] == TaskStatus.COMPLETED.value
    assert res["task_results"]["t2"]["status"] == TaskStatus.FAILED.value
