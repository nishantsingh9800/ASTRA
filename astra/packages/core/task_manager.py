import time
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, Any, List

from packages.core.models import TaskGraph, Task, TaskStatus, TaskPriority
from packages.core.resource_manager import ResourceManager
from packages.core import logger

class TaskManager:
    """
    Executes a TaskGraph, managing concurrency, dependencies, and resources.
    """
    def __init__(self, max_parallel_tasks: int = 4):
        self.max_parallel_tasks = max_parallel_tasks
        self.resource_manager = ResourceManager()
        self.executor = ThreadPoolExecutor(max_workers=max_parallel_tasks)
        self.active_futures: Dict[str, Future] = {}
        self._lock = threading.Lock()
        
    def execute_graph(self, task_graph: TaskGraph, planner_callback) -> Dict[str, Any]:
        """
        Executes the entire TaskGraph. Blocks until all tasks are completed, failed, or cancelled.
        planner_callback(task) should be a function that executes the task and returns a result dict.
        """
        logger.info(f"Starting execution of TaskGraph with {len(task_graph.tasks)} tasks.")
        
        while not task_graph.all_completed():
            with self._lock:
                ready_tasks = task_graph.get_ready_tasks()
                
                # Sort by priority (assuming enum ordering or explicit logic. CRITICAL > HIGH > NORMAL > LOW)
                priority_order = {TaskPriority.CRITICAL: 0, TaskPriority.HIGH: 1, TaskPriority.NORMAL: 2, TaskPriority.LOW: 3, TaskPriority.BACKGROUND: 4}
                ready_tasks.sort(key=lambda t: priority_order.get(t.priority, 2))
                
                for task in ready_tasks:
                    if len(self.active_futures) >= self.max_parallel_tasks:
                        break # Concurrency limit reached
                        
                    if self.resource_manager.acquire(task.task_id, task.resources):
                        task.status = TaskStatus.RUNNING
                        task.start_time = time.time()
                        logger.info(f"Task {task.task_id} acquired resources and is starting.")
                        
                        future = self.executor.submit(self._run_task_wrapper, task, planner_callback)
                        self.active_futures[task.task_id] = future
                    else:
                        logger.debug(f"Task {task.task_id} waiting on resources: {task.resources}")
            
            # Wait a bit before checking for completed tasks
            time.sleep(0.1)
            
            # Clean up completed futures and handle failed dependencies
            with self._lock:
                completed_ids = []
                for t_id, future in self.active_futures.items():
                    if future.done():
                        completed_ids.append(t_id)
                        
                for t_id in completed_ids:
                    del self.active_futures[t_id]
                    self.resource_manager.release(t_id)
                    
                # Cascade failures: cancel tasks whose dependencies have failed
                for task in task_graph.tasks.values():
                    if task.status == TaskStatus.PENDING:
                        for dep_id in task.dependencies:
                            dep_task = task_graph.get_task(dep_id)
                            if dep_task and dep_task.status in [TaskStatus.FAILED, TaskStatus.CANCELLED]:
                                logger.info(f"Task {task.task_id} cancelled because dependency {dep_id} failed.")
                                task.status = TaskStatus.CANCELLED
                                break

        # Aggregate results
        results = {}
        success_count = 0
        failure_count = 0
        
        for t_id, task in task_graph.tasks.items():
            results[t_id] = {
                "goal": task.goal,
                "status": task.status.value,
                "result": task.result,
                "error": task.error
            }
            if task.status == TaskStatus.COMPLETED:
                success_count += 1
            elif task.status == TaskStatus.FAILED:
                failure_count += 1
                
        logger.info(f"TaskGraph execution finished. Success: {success_count}, Failed: {failure_count}")
        return {
            "status": "COMPLETED" if failure_count == 0 else "PARTIAL_SUCCESS" if success_count > 0 else "FAILED",
            "task_results": results
        }

    def _run_task_wrapper(self, task: Task, planner_callback) -> None:
        try:
            logger.info(f"Executing Task {task.task_id}: {task.goal}")
            
            # Fast fail if cancelled
            if task.cancellation_token or task.status == TaskStatus.CANCELLED:
                task.status = TaskStatus.CANCELLED
                return
                
            # Execute
            result = planner_callback(task)
            
            # Set results
            if result.get("status") in ["success", "COMPLETED"]:
                task.status = TaskStatus.COMPLETED
                task.result = result.get("final_response", result.get("result", "Done."))
            else:
                task.status = TaskStatus.FAILED
                task.error = result.get("details", result.get("final_response", "Failed during execution."))
                task.result = task.error
                
            logger.info(f"Task {task.task_id} finished with status {task.status.value}")
        except Exception as e:
            logger.error(f"Task {task.task_id} threw an exception: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.result = str(e)
            
    def cancel_task(self, task_graph: TaskGraph, task_id: str):
        with self._lock:
            task = task_graph.get_task(task_id)
            if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task.cancellation_token = True
                task.status = TaskStatus.CANCELLED
                logger.info(f"Cancelled task {task_id}")
                
    def cancel_all(self, task_graph: TaskGraph):
        with self._lock:
            for task in task_graph.tasks.values():
                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    task.cancellation_token = True
                    task.status = TaskStatus.CANCELLED
            logger.info("Cancelled all active and pending tasks.")
