"""
Personal Intelligence Hub - Task Models

任务管理相关的数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskUpdateSource(Enum):
    """任务更新来源"""
    TASK_DECOMPOSITION = "task_decomposition"
    USER_INPUT = "user_input"
    AGENT_UPDATE = "agent_update"
    SYSTEM_UPDATE = "system_update"


@dataclass
class Task:
    """任务数据模型"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    parent_id: Optional[str]
    assigned_agent: Optional[str]
    dependencies: List[str]
    subtasks: List[str]
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        if self.due_date and isinstance(self.due_date, str):
            self.due_date = datetime.fromisoformat(self.due_date)


@dataclass
class TaskUpdate:
    """任务更新"""
    id: str
    task_id: str
    source: TaskUpdateSource
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


@dataclass
class TaskDecompositionNode:
    """任务分解节点"""
    id: str
    original_task: str
    subtasks: List[Task]
    decomposition_strategy: str
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


@dataclass
class TaskAssignment:
    """任务分配"""
    task_id: str
    agent_id: str
    assigned_at: datetime
    priority: TaskPriority
    estimated_completion: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if isinstance(self.assigned_at, str):
            self.assigned_at = datetime.fromisoformat(self.assigned_at)
        if self.estimated_completion and isinstance(self.estimated_completion, str):
            self.estimated_completion = datetime.fromisoformat(self.estimated_completion)


@dataclass
class TaskProgress:
    """任务进度"""
    task_id: str
    progress: float
    status: TaskStatus
    updated_at: datetime
    notes: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)


@dataclass
class TaskDependency:
    """任务依赖"""
    task_id: str
    depends_on: str
    dependency_type: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
