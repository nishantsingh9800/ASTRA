import threading
from typing import List, Dict, Set

class ResourceManager:
    """
    Manages locks on shared UI and device resources to prevent conflicts between parallel tasks.
    """
    def __init__(self):
        self._locks: Dict[str, str] = {} # resource_name -> task_id
        self._lock_mutex = threading.Lock()
        
    def acquire(self, task_id: str, resources: List[str]) -> bool:
        """
        Attempts to acquire all requested resources for the task.
        Returns True if successful, False if any resource is already locked by another task.
        """
        if not resources:
            return True
            
        with self._lock_mutex:
            # Check if all available
            for res in resources:
                if res in self._locks and self._locks[res] != task_id:
                    return False
            
            # Acquire all
            for res in resources:
                self._locks[res] = task_id
                
            return True
            
    def release(self, task_id: str):
        """
        Releases all resources held by the task.
        """
        with self._lock_mutex:
            resources_to_remove = [res for res, owner in self._locks.items() if owner == task_id]
            for res in resources_to_remove:
                del self._locks[res]
                
    def get_locked_resources(self) -> Dict[str, str]:
        """Returns a copy of the current locks."""
        with self._lock_mutex:
            return dict(self._locks)
