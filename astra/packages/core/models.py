from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

class TargetType(str, Enum):
    WEB = "WEB"
    YOUTUBE = "YOUTUBE"
    WEBSITE = "WEBSITE"
    APPLICATION = "APPLICATION"
    BROWSER = "BROWSER"
    FILES = "FILES"
    CONTACTS = "CONTACTS"
    CURRENT_PAGE = "CURRENT_PAGE"
    CURRENT_APPLICATION = "CURRENT_APPLICATION"
    UNKNOWN = "UNKNOWN"

class FailureCategory(str, Enum):
    TRANSCRIPTION_FAILURE = "TRANSCRIPTION_FAILURE"
    INTENT_FAILURE = "INTENT_FAILURE"
    PLANNING_FAILURE = "PLANNING_FAILURE"
    TOOL_SELECTION_FAILURE = "TOOL_SELECTION_FAILURE"
    ARGUMENT_FAILURE = "ARGUMENT_FAILURE"
    EXECUTOR_FAILURE = "EXECUTOR_FAILURE"
    PERMISSION_FAILURE = "PERMISSION_FAILURE"
    ENVIRONMENT_FAILURE = "ENVIRONMENT_FAILURE"
    VERIFICATION_FAILURE = "VERIFICATION_FAILURE"
    MODEL_FAILURE = "MODEL_FAILURE"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    DEVICE_FAILURE = "DEVICE_FAILURE"

class EntityType(str, Enum):
    PERSON = "PERSON"
    APPLICATION = "APPLICATION"
    BROWSER = "BROWSER"
    WEBSITE = "WEBSITE"
    FILE = "FILE"
    PROJECT = "PROJECT"
    PLACE = "PLACE"
    ORGANIZATION = "ORGANIZATION"
    DEVICE = "DEVICE"
    UNKNOWN = "UNKNOWN"

class UIAction(str, Enum):
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    RIGHT_CLICK = "RIGHT_CLICK"
    TYPE = "TYPE"
    PRESS = "PRESS"
    SCROLL = "SCROLL"
    SELECT = "SELECT"
    FOCUS = "FOCUS"
    SEARCH = "SEARCH"

@dataclass
class UITarget:
    target_type: str
    name: str
    control_type: str
    bounds: Optional[Dict[str, int]] = None
    application: Optional[str] = None
    confidence: str = "LOW"
    element_ref: Optional[Any] = None
    timestamp: float = 0.0

@dataclass
class Entity:
    entity_type: EntityType
    text: str
    resolved_name: Optional[str] = None
    confidence: str = "LOW"
    source: str = "UNKNOWN"

@dataclass
class ContextSnapshot:
    active_device: str = "local"
    active_application: Optional[str] = None
    active_window_title: Optional[str] = None
    active_browser: Optional[str] = None
    active_page_url: Optional[str] = None
    active_document: Optional[str] = None
    current_task: Optional[str] = None
    previous_action: Optional[str] = None
    recent_observations: List[str] = field(default_factory=list)
    available_capabilities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_device": self.active_device,
            "active_application": self.active_application,
            "active_window_title": self.active_window_title,
            "active_browser": self.active_browser,
            "active_page_url": self.active_page_url,
            "active_document": self.active_document,
            "current_task": self.current_task,
            "previous_action": self.previous_action,
            "recent_observations": self.recent_observations,
            "available_capabilities": self.available_capabilities
        }

@dataclass
class Intent:
    action: str
    target_type: TargetType
    target: Optional[str] = None
    query: Optional[str] = None
    context_requirements: List[str] = field(default_factory=list)
    raw_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "target_type": self.target_type.value,
            "target": self.target,
            "query": self.query,
            "context_requirements": self.context_requirements,
            "raw_text": self.raw_text
        }

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"

class TaskPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    BACKGROUND = "BACKGROUND"

@dataclass
class Task:
    task_id: str
    goal: str
    action: str
    target_type: TargetType
    target: Optional[str] = None
    query: Optional[str] = None
    command: Optional[str] = None
    message: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    start_time: Optional[float] = None
    progress: int = 0
    result: Any = None
    error: Optional[str] = None
    cancellation_token: bool = False
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "action": self.action,
            "status": self.status.value,
            "priority": self.priority.value,
            "dependencies": self.dependencies,
            "resources": self.resources,
            "result": self.result,
            "error": self.error
        }

@dataclass
class TaskGraph:
    tasks: Dict[str, Task] = field(default_factory=dict)
    
    def add_task(self, task: Task):
        self.tasks[task.task_id] = task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_ready_tasks(self) -> List[Task]:
        ready = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are COMPLETED
                deps_met = True
                for dep_id in task.dependencies:
                    dep_task = self.tasks.get(dep_id)
                    if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                        deps_met = False
                        break
                if deps_met:
                    ready.append(task)
        return ready

    def all_completed(self) -> bool:
        return all(t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] for t in self.tasks.values())

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class CognitiveResult:
    raw_transcript: str
    normalized_transcript: str
    confidence: ConfidenceLevel
    clarification_question: Optional[str] = None
    reasoning: Optional[str] = None
    intent: Optional[str] = None
    target: Optional[str] = None
