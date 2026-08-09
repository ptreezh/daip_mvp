"""
Production-level Task Management System for Personal Assistant

This module provides comprehensive task management capabilities including:
- Task creation, scheduling, and execution tracking
- Dependency management and critical path analysis
- Priority queues and intelligent scheduling
- Task templates and batch operations
- Progress monitoring and notification systems
- Task analytics and performance metrics
- Integration with external task systems
"""

import asyncio
import heapq
import json
import logging
import os
import sqlite3
import threading
import uuid
from collections import defaultdict, deque

# import cron_parser  # Using custom implementation instead
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"


class TaskPriority(Enum):
    """Task priority levels"""

    CRITICAL = 0  # Highest priority
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4  # Lowest priority


class TaskType(Enum):
    """Task types for different handling strategies"""

    IMMEDIATE = "immediate"  # Execute immediately
    SCHEDULED = "scheduled"  # Scheduled for specific time
    RECURRING = "recurring"  # Recurring task
    DEPENDENT = "dependent"  # Depends on other tasks
    BATCH = "batch"  # Part of a batch
    WORKFLOW = "workflow"  # Part of a workflow


@dataclass
class TaskDependency:
    """Task dependency definition"""

    task_id: str
    dependency_type: str = "finish_to_start"  # finish_to_start, start_to_start, etc.
    lag_minutes: int = 0
    is_optional: bool = False


@dataclass
class TaskSchedule:
    """Task scheduling information"""

    scheduled_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    duration_estimate_minutes: Optional[int] = None
    cron_expression: Optional[str] = None
    timezone: str = "UTC"
    max_execution_time_minutes: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    backoff_factor: float = 2.0


@dataclass
class TaskMetrics:
    """Task execution metrics"""

    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None
    cpu_time_seconds: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    retry_count: int = 0
    failure_count: int = 0
    success_count: int = 0
    average_execution_time: Optional[float] = None
    last_failure_reason: Optional[str] = None
    performance_score: Optional[float] = None


@dataclass
class TaskNotification:
    """Task notification configuration"""

    notify_on_creation: bool = False
    notify_on_start: bool = True
    notify_on_completion: bool = True
    notify_on_failure: bool = True
    notify_on_timeout: bool = True
    notification_channels: list[str] = field(default_factory=list)
    custom_notification_message: Optional[str] = None


class Task:
    """Production-level Task with comprehensive functionality"""

    def __init__(
        self,
        title: str,
        description: str = "",
        task_type: TaskType = TaskType.IMMEDIATE,
        priority: TaskPriority = TaskPriority.NORMAL,
        task_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
        assignee: Optional[str] = None,
        estimated_effort: Optional[float] = None,
        actual_effort: Optional[float] = None,
    ):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.task_type = task_type
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.context = context or {}
        self.tags = tags or []
        self.assignee = assignee
        self.estimated_effort = estimated_effort
        self.actual_effort = actual_effort

        # Dependencies and scheduling
        self.dependencies: list[TaskDependency] = []
        self.dependents: set[str] = set()
        self.schedule = TaskSchedule()
        self.notification = TaskNotification()

        # Execution details
        self.command: Optional[str] = None
        self.script_path: Optional[str] = None
        self.parameters: dict[str, Any] = {}
        self.result: Optional[dict[str, Any]] = None
        self.error_message: Optional[str] = None
        self.stack_trace: Optional[str] = None

        # Progress tracking
        self.progress_percentage: float = 0.0
        self.progress_message: str = ""
        self.subtasks: list[str] = []
        self.parent_task_id: Optional[str] = None

        # Metadata
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.created_by: Optional[str] = None
        self.modified_by: Optional[str] = None
        self.version: int = 1
        self.is_template: bool = False
        self.template_name: Optional[str] = None

        # Metrics and analytics
        self.metrics = TaskMetrics()
        self.custom_attributes: dict[str, Any] = {}

        # External integrations
        self.external_id: Optional[str] = None
        self.external_system: Optional[str] = None
        self.webhook_url: Optional[str] = None

        # Quality and validation
        self.validation_rules: list[dict[str, Any]] = []
        self.quality_checks: list[dict[str, Any]] = []
        self.approval_required: bool = False
        self.approved_by: Optional[str] = None
        self.approved_at: Optional[datetime] = None

    def add_dependency(
        self,
        task_id: str,
        dependency_type: str = "finish_to_start",
        lag_minutes: int = 0,
        is_optional: bool = False,
    ) -> None:
        """Add a dependency to this task"""
        dependency = TaskDependency(task_id, dependency_type, lag_minutes, is_optional)
        self.dependencies.append(dependency)
        self.updated_at = datetime.now()

    def remove_dependency(self, task_id: str) -> bool:
        """Remove a dependency from this task"""
        original_length = len(self.dependencies)
        self.dependencies = [dep for dep in self.dependencies if dep.task_id != task_id]
        if len(self.dependencies) < original_length:
            self.updated_at = datetime.now()
            return True
        return False

    def can_start(self, completed_tasks: set[str]) -> bool:
        """Check if task can start based on dependencies"""
        if self.status not in [TaskStatus.PENDING, TaskStatus.BLOCKED]:
            return False

        for dep in self.dependencies:
            if not dep.is_optional and dep.task_id not in completed_tasks:
                return False
        return True

    def calculate_critical_path(
        self, all_tasks: dict[str, "Task"]
    ) -> tuple[float, list[str]]:
        """Calculate critical path for this task"""
        if not self.dependencies:
            return 0.0, [self.id]

        max_duration = 0.0
        critical_path = [self.id]

        for dep in self.dependencies:
            if dep.task_id in all_tasks:
                dep_task = all_tasks[dep.task_id]
                dep_duration, dep_path = dep_task.calculate_critical_path(all_tasks)
                total_duration = dep_duration + (
                    dep_task.schedule.duration_estimate_minutes or 0
                )

                if total_duration > max_duration:
                    max_duration = total_duration
                    critical_path = dep_path + [self.id]

        return max_duration, critical_path

    def update_progress(self, percentage: float, message: str = "") -> None:
        """Update task progress"""
        self.progress_percentage = max(0.0, min(100.0, percentage))
        self.progress_message = message
        self.updated_at = datetime.now()

    def complete_task(self, result: Optional[dict[str, Any]] = None) -> None:
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        self.progress_percentage = 100.0
        self.metrics.completed_at = self.completed_at
        if self.metrics.started_at:
            self.metrics.execution_time_seconds = (
                self.completed_at - self.metrics.started_at
            ).total_seconds()
        self.updated_at = datetime.now()

    def fail_task(self, error_message: str, stack_trace: Optional[str] = None) -> None:
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.stack_trace = stack_trace
        self.metrics.failure_count += 1
        self.metrics.last_failure_reason = error_message
        self.updated_at = datetime.now()

    def start_task(self) -> None:
        """Mark task as started"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        self.metrics.started_at = self.started_at
        self.updated_at = datetime.now()

    def pause_task(self) -> None:
        """Pause task execution"""
        self.status = TaskStatus.PAUSED
        self.updated_at = datetime.now()

    def resume_task(self) -> None:
        """Resume task execution"""
        if self.status == TaskStatus.PAUSED:
            self.status = TaskStatus.RUNNING
            self.updated_at = datetime.now()

    def cancel_task(self, reason: str = "") -> None:
        """Cancel task execution"""
        self.status = TaskStatus.CANCELLED
        self.error_message = reason
        self.updated_at = datetime.now()

    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.schedule.deadline and self.status not in [
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        ]:
            return datetime.now() > self.schedule.deadline
        return False

    def get_priority_score(self) -> float:
        """Calculate priority score for sorting"""
        base_score = self.priority.value

        # Adjust for urgency (deadline proximity)
        if self.schedule.deadline:
            hours_until_deadline = (
                self.schedule.deadline - datetime.now()
            ).total_seconds() / 3600
            if hours_until_deadline < 1:
                base_score -= 0.5  # Very urgent
            elif hours_until_deadline < 24:
                base_score -= 0.3  # Urgent
            elif hours_until_deadline < 72:
                base_score -= 0.1  # Somewhat urgent

        # Adjust for age (older tasks get slightly higher priority)
        age_hours = (datetime.now() - self.created_at).total_seconds() / 3600
        age_factor = min(
            age_hours / 168, 0.2
        )  # Max 0.2 adjustment for 1-week-old tasks
        base_score -= age_factor

        return base_score

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "context": self.context,
            "tags": self.tags,
            "assignee": self.assignee,
            "estimated_effort": self.estimated_effort,
            "actual_effort": self.actual_effort,
            "dependencies": [
                {
                    "task_id": dep.task_id,
                    "dependency_type": dep.dependency_type,
                    "lag_minutes": dep.lag_minutes,
                    "is_optional": dep.is_optional,
                }
                for dep in self.dependencies
            ],
            "dependents": list(self.dependents),
            "schedule": {
                "scheduled_at": self.schedule.scheduled_at.isoformat()
                if self.schedule.scheduled_at
                else None,
                "deadline": self.schedule.deadline.isoformat()
                if self.schedule.deadline
                else None,
                "duration_estimate_minutes": self.schedule.duration_estimate_minutes,
                "cron_expression": self.schedule.cron_expression,
                "timezone": self.schedule.timezone,
                "max_execution_time_minutes": self.schedule.max_execution_time_minutes,
                "retry_count": self.schedule.retry_count,
                "max_retries": self.schedule.max_retries,
                "backoff_factor": self.schedule.backoff_factor,
            },
            "notification": {
                "notify_on_creation": self.notification.notify_on_creation,
                "notify_on_start": self.notification.notify_on_start,
                "notify_on_completion": self.notification.notify_on_completion,
                "notify_on_failure": self.notification.notify_on_failure,
                "notify_on_timeout": self.notification.notify_on_timeout,
                "notification_channels": self.notification.notification_channels,
                "custom_notification_message": self.notification.custom_notification_message,  # noqa: E501
            },
            "command": self.command,
            "script_path": self.script_path,
            "parameters": self.parameters,
            "result": self.result,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "progress_percentage": self.progress_percentage,
            "progress_message": self.progress_message,
            "subtasks": self.subtasks,
            "parent_task_id": self.parent_task_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "created_by": self.created_by,
            "modified_by": self.modified_by,
            "version": self.version,
            "is_template": self.is_template,
            "template_name": self.template_name,
            "metrics": {
                "created_at": self.metrics.created_at.isoformat(),
                "started_at": self.metrics.started_at.isoformat()
                if self.metrics.started_at
                else None,
                "completed_at": self.metrics.completed_at.isoformat()
                if self.metrics.completed_at
                else None,
                "execution_time_seconds": self.metrics.execution_time_seconds,
                "cpu_time_seconds": self.metrics.cpu_time_seconds,
                "memory_usage_mb": self.metrics.memory_usage_mb,
                "retry_count": self.metrics.retry_count,
                "failure_count": self.metrics.failure_count,
                "success_count": self.metrics.success_count,
                "average_execution_time": self.metrics.average_execution_time,
                "last_failure_reason": self.metrics.last_failure_reason,
                "performance_score": self.metrics.performance_score,
            },
            "custom_attributes": self.custom_attributes,
            "external_id": self.external_id,
            "external_system": self.external_system,
            "webhook_url": self.webhook_url,
            "validation_rules": self.validation_rules,
            "quality_checks": self.quality_checks,
            "approval_required": self.approval_required,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Create task from dictionary"""
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            task_type=TaskType(data.get("task_type", TaskType.IMMEDIATE.value)),
            priority=TaskPriority(data.get("priority", TaskPriority.NORMAL.value)),
            task_id=data.get("id"),
            context=data.get("context", {}),
            tags=data.get("tags", []),
            assignee=data.get("assignee"),
            estimated_effort=data.get("estimated_effort"),
            actual_effort=data.get("actual_effort"),
        )

        # Restore status
        task.status = TaskStatus(data.get("status", TaskStatus.PENDING.value))

        # Restore dependencies
        for dep_data in data.get("dependencies", []):
            task.add_dependency(
                dep_data["task_id"],
                dep_data.get("dependency_type", "finish_to_start"),
                dep_data.get("lag_minutes", 0),
                dep_data.get("is_optional", False),
            )

        task.dependents = set(data.get("dependents", []))

        # Restore schedule
        schedule_data = data.get("schedule", {})
        if schedule_data.get("scheduled_at"):
            task.schedule.scheduled_at = datetime.fromisoformat(
                schedule_data["scheduled_at"]
            )
        if schedule_data.get("deadline"):
            task.schedule.deadline = datetime.fromisoformat(schedule_data["deadline"])
        task.schedule.duration_estimate_minutes = schedule_data.get(
            "duration_estimate_minutes"
        )
        task.schedule.cron_expression = schedule_data.get("cron_expression")
        task.schedule.timezone = schedule_data.get("timezone", "UTC")
        task.schedule.max_execution_time_minutes = schedule_data.get(
            "max_execution_time_minutes"
        )
        task.schedule.retry_count = schedule_data.get("retry_count", 0)
        task.schedule.max_retries = schedule_data.get("max_retries", 3)
        task.schedule.backoff_factor = schedule_data.get("backoff_factor", 2.0)

        # Restore notification settings
        notification_data = data.get("notification", {})
        task.notification.notify_on_creation = notification_data.get(
            "notify_on_creation", False
        )
        task.notification.notify_on_start = notification_data.get(
            "notify_on_start", True
        )
        task.notification.notify_on_completion = notification_data.get(
            "notify_on_completion", True
        )
        task.notification.notify_on_failure = notification_data.get(
            "notify_on_failure", True
        )
        task.notification.notify_on_timeout = notification_data.get(
            "notify_on_timeout", True
        )
        task.notification.notification_channels = notification_data.get(
            "notification_channels", []
        )
        task.notification.custom_notification_message = notification_data.get(
            "custom_notification_message"
        )

        # Restore execution details
        task.command = data.get("command")
        task.script_path = data.get("script_path")
        task.parameters = data.get("parameters", {})
        task.result = data.get("result")
        task.error_message = data.get("error_message")
        task.stack_trace = data.get("stack_trace")

        # Restore progress
        task.progress_percentage = data.get("progress_percentage", 0.0)
        task.progress_message = data.get("progress_message", "")
        task.subtasks = data.get("subtasks", [])
        task.parent_task_id = data.get("parent_task_id")

        # Restore metadata
        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            task.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        task.created_by = data.get("created_by")
        task.modified_by = data.get("modified_by")
        task.version = data.get("version", 1)
        task.is_template = data.get("is_template", False)
        task.template_name = data.get("template_name")

        # Restore metrics
        metrics_data = data.get("metrics", {})
        if metrics_data.get("created_at"):
            task.metrics.created_at = datetime.fromisoformat(metrics_data["created_at"])
        if metrics_data.get("started_at"):
            task.metrics.started_at = datetime.fromisoformat(metrics_data["started_at"])
        if metrics_data.get("completed_at"):
            task.metrics.completed_at = datetime.fromisoformat(
                metrics_data["completed_at"]
            )
        task.metrics.execution_time_seconds = metrics_data.get("execution_time_seconds")
        task.metrics.cpu_time_seconds = metrics_data.get("cpu_time_seconds")
        task.metrics.memory_usage_mb = metrics_data.get("memory_usage_mb")
        task.metrics.retry_count = metrics_data.get("retry_count", 0)
        task.metrics.failure_count = metrics_data.get("failure_count", 0)
        task.metrics.success_count = metrics_data.get("success_count", 0)
        task.metrics.average_execution_time = metrics_data.get("average_execution_time")
        task.metrics.last_failure_reason = metrics_data.get("last_failure_reason")
        task.metrics.performance_score = metrics_data.get("performance_score")

        # Restore other attributes
        task.custom_attributes = data.get("custom_attributes", {})
        task.external_id = data.get("external_id")
        task.external_system = data.get("external_system")
        task.webhook_url = data.get("webhook_url")
        task.validation_rules = data.get("validation_rules", [])
        task.quality_checks = data.get("quality_checks", [])
        task.approval_required = data.get("approval_required", False)
        task.approved_by = data.get("approved_by")
        if data.get("approved_at"):
            task.approved_at = datetime.fromisoformat(data["approved_at"])

        return task

    def __str__(self) -> str:
        """String representation"""
        return f"Task({self.title}) - {self.status.value}"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"Task(id={self.id[:8]}..., title='{self.title}', "
            f"status='{self.status.value}', priority='{self.priority.name}')"
        )


class TaskQueue:
    """Priority queue for tasks with efficient scheduling"""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._queue = []
        self._task_map = {}
        self._index_counter = 0
        self._lock = threading.Lock()

    def put(self, task: Task) -> bool:
        """Add task to queue"""
        with self._lock:
            if len(self._queue) >= self.max_size:
                return False

            # Use priority score and index for stable sorting
            priority_score = task.get_priority_score()
            entry = (priority_score, self._index_counter, task)
            heapq.heappush(self._queue, entry)
            self._task_map[task.id] = entry
            self._index_counter += 1
            return True

    def get(self) -> Optional[Task]:
        """Get highest priority task from queue"""
        with self._lock:
            if not self._queue:
                return None

            _, _, task = heapq.heappop(self._queue)
            if task.id in self._task_map:
                del self._task_map[task.id]
            return task

    def remove(self, task_id: str) -> bool:
        """Remove task from queue"""
        with self._lock:
            if task_id not in self._task_map:
                return False

            # Mark as removed (lazy deletion)
            self._task_map[task_id]
            self._task_map[task_id] = None
            return True

    def peek(self) -> Optional[Task]:
        """Peek at highest priority task without removing"""
        with self._lock:
            if not self._queue:
                return None

            _, _, task = self._queue[0]
            return task if task.id in self._task_map else None

    def size(self) -> int:
        """Get queue size"""
        with self._lock:
            return len([t for t in self._task_map.values() if t is not None])

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.size() == 0

    def clear(self) -> None:
        """Clear all tasks from queue"""
        with self._lock:
            self._queue.clear()
            self._task_map.clear()
            self._index_counter = 0


class TaskTemplate:
    """Task template for creating standardized tasks"""

    def __init__(
        self,
        name: str,
        title_template: str,
        description_template: str = "",
        default_task_type: TaskType = TaskType.IMMEDIATE,
        default_priority: TaskPriority = TaskPriority.NORMAL,
        default_parameters: Optional[dict[str, Any]] = None,
        validation_rules: Optional[list[dict[str, Any]]] = None,
        template_id: Optional[str] = None,
    ):
        self.id = template_id or str(uuid.uuid4())
        self.name = name
        self.title_template = title_template
        self.description_template = description_template
        self.default_task_type = default_task_type
        self.default_priority = default_priority
        self.default_parameters = default_parameters or {}
        self.validation_rules = validation_rules or []
        self.created_at = datetime.now()
        self.usage_count = 0

    def create_task(self, parameters: dict[str, Any], **kwargs) -> Task:
        """Create task from template"""
        # Merge template parameters with provided parameters
        merged_params = {**self.default_parameters, **parameters}

        # Format title and description
        title = self.title_template.format(**merged_params)
        description = (
            self.description_template.format(**merged_params)
            if self.description_template
            else ""
        )

        task = Task(
            title=title,
            description=description,
            task_type=kwargs.get("task_type", self.default_task_type),
            priority=kwargs.get("priority", self.default_priority),
            context=kwargs.get("context", {}),
            tags=kwargs.get("tags", []),
            assignee=kwargs.get("assignee"),
        )

        # Apply template-specific settings
        task.parameters = merged_params
        task.validation_rules = self.validation_rules
        task.is_template = True
        task.template_name = self.name

        self.usage_count += 1
        return task

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "title_template": self.title_template,
            "description_template": self.description_template,
            "default_task_type": self.default_task_type.value,
            "default_priority": self.default_priority.value,
            "default_parameters": self.default_parameters,
            "validation_rules": self.validation_rules,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
        }


class TaskManager:
    """Production-level Task Manager with comprehensive functionality"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = (
            Path(storage_path) if storage_path else Path("data/tasks.db")
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # In-memory storage
        self.tasks: dict[str, Task] = {}
        self.templates: dict[str, TaskTemplate] = {}
        self.task_queue = TaskQueue()

        # Execution management
        self.running_tasks: dict[str, asyncio.Task] = {}
        self.completed_tasks: set[str] = set()
        self.failed_tasks: set[str] = set()

        # Scheduling
        self.scheduler_active = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.schedule_interval_seconds = 60  # Check every minute

        # Threading and execution
        self.executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="task_executor"
        )
        self.max_concurrent_tasks = 10

        # Analytics and monitoring
        self.task_metrics = defaultdict(list)
        self.performance_history = deque(maxlen=1000)

        # Database initialization
        self._init_database()

        # Load existing data
        self._load_tasks()
        self._load_templates()

    def _init_database(self) -> None:
        """Initialize database schema"""
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_templates (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_metrics (
                    task_id TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (
                    json_extract(data, '$.status')
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks (
                    json_extract(data, '$.priority')
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks (
                    json_extract(data, '$.created_at')
                )
            """)

            conn.commit()

    def _load_tasks(self) -> None:
        """Load tasks from database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute("SELECT id, data FROM tasks")
                for task_id, data in cursor.fetchall():
                    try:
                        task_data = json.loads(data)
                        task = Task.from_dict(task_data)
                        self.tasks[task_id] = task

                        # Update status tracking
                        if task.status == TaskStatus.COMPLETED:
                            self.completed_tasks.add(task_id)
                        elif task.status == TaskStatus.FAILED:
                            self.failed_tasks.add(task_id)

                    except Exception as e:
                        logger.error(f"Failed to load task {task_id}: {e}")

            logger.info(f"Loaded {len(self.tasks)} tasks from database")

        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")

    def _load_templates(self) -> None:
        """Load templates from database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute("SELECT id, data FROM task_templates")
                for template_id, data in cursor.fetchall():
                    try:
                        template_data = json.loads(data)
                        template = TaskTemplate(
                            name=template_data["name"],
                            title_template=template_data["title_template"],
                            description_template=template_data.get(
                                "description_template", ""
                            ),
                            default_task_type=TaskType(
                                template_data.get(
                                    "default_task_type", TaskType.IMMEDIATE.value
                                )
                            ),
                            default_priority=TaskPriority(
                                template_data.get(
                                    "default_priority", TaskPriority.NORMAL.value
                                )
                            ),
                            default_parameters=template_data.get(
                                "default_parameters", {}
                            ),
                            validation_rules=template_data.get("validation_rules", []),
                            template_id=template_data.get("id"),
                        )
                        template.created_at = datetime.fromisoformat(
                            template_data["created_at"]
                        )
                        template.usage_count = template_data.get("usage_count", 0)
                        self.templates[template_id] = template

                    except Exception as e:
                        logger.error(f"Failed to load template {template_id}: {e}")

            logger.info(f"Loaded {len(self.templates)} templates from database")

        except Exception as e:
            logger.error(f"Failed to load templates: {e}")

    def _save_task(self, task: Task) -> None:
        """Save task to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO tasks (id, data, updated_at) VALUES (?, ?, ?)",  # noqa: E501
                    (task.id, json.dumps(task.to_dict()), datetime.now().isoformat()),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save task {task.id}: {e}")

    def _save_template(self, template: TaskTemplate) -> None:
        """Save template to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO task_templates (id, data) VALUES (?, ?)",
                    (template.id, json.dumps(template.to_dict())),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save template {template.id}: {e}")

    async def create_task(
        self,
        title: str,
        description: str = "",
        task_type: TaskType = TaskType.IMMEDIATE,
        priority: TaskPriority = TaskPriority.NORMAL,
        context: Optional[dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
        assignee: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        deadline: Optional[datetime] = None,
        dependencies: Optional[list[TaskDependency]] = None,
        **kwargs,
    ) -> str:
        """Create a new task with comprehensive parameters"""
        task = Task(
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            context=context,
            tags=tags,
            assignee=assignee,
            estimated_effort=kwargs.get("estimated_effort"),
        )

        # Apply scheduling
        if scheduled_at:
            task.schedule.scheduled_at = scheduled_at
        if deadline:
            task.schedule.deadline = deadline
        if dependencies:
            task.dependencies = dependencies

        # Apply additional parameters
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        # Store task
        self.tasks[task.id] = task
        self._save_task(task)

        # Add to queue if ready
        if task.can_start(self.completed_tasks):
            self.task_queue.put(task)

        # Send notification if configured
        if task.notification.notify_on_creation:
            await self._send_notification(task, "created")

        logger.info(f"Created task: {task.title} ({task.id})")
        return task.id

    async def create_task_from_template(
        self, template_name: str, parameters: dict[str, Any], **kwargs
    ) -> str:
        """Create task from template"""
        template = None
        for tmpl in self.templates.values():
            if tmpl.name == template_name:
                template = tmpl
                break

        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        task = template.create_task(parameters, **kwargs)
        self.tasks[task.id] = task
        self._save_task(task)

        # Add to queue if ready
        if task.can_start(self.completed_tasks):
            self.task_queue.put(task)

        logger.info(
            f"Created task from template '{template_name}': {task.title} ({task.id})"
        )
        return task.id

    def create_template(
        self,
        name: str,
        title_template: str,
        description_template: str = "",
        default_task_type: TaskType = TaskType.IMMEDIATE,
        default_priority: TaskPriority = TaskPriority.NORMAL,
        default_parameters: Optional[dict[str, Any]] = None,
        validation_rules: Optional[list[dict[str, Any]]] = None,
    ) -> str:
        """Create a new task template"""
        template = TaskTemplate(
            name=name,
            title_template=title_template,
            description_template=description_template,
            default_task_type=default_task_type,
            default_priority=default_priority,
            default_parameters=default_parameters,
            validation_rules=validation_rules,
        )

        self.templates[template.id] = template
        self._save_template(template)

        logger.info(f"Created template: {template.name} ({template.id})")
        return template.id

    async def update_task(self, task_id: str, **kwargs) -> bool:
        """Update task with new values"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        # Update allowed fields
        updatable_fields = [
            "title",
            "description",
            "priority",
            "context",
            "tags",
            "assignee",
            "estimated_effort",
            "command",
            "script_path",
            "parameters",
        ]

        for field_name, value in kwargs.items():
            if field_name in updatable_fields:
                setattr(task, field_name, value)

        task.updated_at = datetime.now()
        self._save_task(task)

        logger.info(f"Updated task: {task.title} ({task.id})")
        return True

    async def delete_task(self, task_id: str, force: bool = False) -> bool:
        """Delete task (with safety checks)"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        # Safety checks
        if not force:
            if task.status == TaskStatus.RUNNING:
                raise ValueError(
                    "Cannot delete running task. Use force=True to override."
                )

            if task.dependents:
                raise ValueError(
                    f"Cannot delete task with dependents: {task.dependents}"
                )

        # Remove from queue
        self.task_queue.remove(task_id)

        # Cancel if running
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]

        # Delete from storage
        del self.tasks[task_id]
        self.completed_tasks.discard(task_id)
        self.failed_tasks.discard(task_id)

        # Remove from database
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.execute("DELETE FROM task_metrics WHERE task_id = ?", (task_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to delete task {task_id} from database: {e}")

        logger.info(f"Deleted task: {task.title} ({task_id})")
        return True

    async def execute_task(self, task_id: str) -> bool:
        """Execute a task immediately"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        if not task.can_start(self.completed_tasks):
            logger.warning(f"Task {task_id} cannot start due to unmet dependencies")
            return False

        if len(self.running_tasks) >= self.max_concurrent_tasks:
            logger.warning(
                f"Maximum concurrent tasks ({self.max_concurrent_tasks}) reached"
            )
            return False

        # Start task execution
        execution_task = asyncio.create_task(self._execute_task_wrapper(task))
        self.running_tasks[task_id] = execution_task

        logger.info(f"Started execution of task: {task.title} ({task_id})")
        return True

    async def _execute_task_wrapper(self, task: Task) -> None:
        """Wrapper for task execution with error handling"""
        try:
            task.start_task()
            await self._send_notification(task, "started")

            # Check for execution timeout
            if task.schedule.max_execution_time_minutes:
                timeout_seconds = task.schedule.max_execution_time_minutes * 60
                await asyncio.wait_for(
                    self._execute_task_core(task), timeout=timeout_seconds
                )
            else:
                await self._execute_task_core(task)

            # Task completed successfully
            task.complete_task(
                {"status": "success", "message": "Task completed successfully"}
            )
            self.completed_tasks.add(task.id)
            await self._send_notification(task, "completed")

            # Trigger dependent tasks
            await self._check_dependent_tasks(task.id)

        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error_message = f"Task timed out after {task.schedule.max_execution_time_minutes} minutes"  # noqa: E501
            await self._send_notification(task, "timeout")
            await self._handle_task_failure(task)

        except Exception as e:
            task.fail_task(str(e), None)
            await self._send_notification(task, "failed")
            await self._handle_task_failure(task)

        finally:
            # Clean up
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            self._save_task(task)

    async def _execute_task_core(self, task: Task) -> None:
        """Core task execution logic"""
        if task.command:
            # Execute shell command
            await self._execute_command(task)
        elif task.script_path:
            # Execute script
            await self._execute_script(task)
        elif task.parameters:
            # Execute based on parameters
            await self._execute_parameters(task)
        else:
            # Simple task - just mark as completed
            await asyncio.sleep(0.1)  # Small delay to simulate work
            task.result = {"message": "Task completed", "execution_type": "simple"}

    async def _execute_command(self, task: Task) -> None:
        """Execute shell command"""

        try:
            # Enhanced command execution with proper handling
            env = {**os.environ, **task.context.get("environment", {})}

            process = await asyncio.create_subprocess_shell(
                task.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=task.context.get("working_directory", "."),
            )

            stdout, stderr = await process.communicate()

            task.result = {
                "return_code": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "command": task.command,
            }

            if process.returncode != 0:
                raise RuntimeError(
                    f"Command failed with return code {process.returncode}: {task.result['stderr']}"  # noqa: E501
                )

        except Exception as e:
            raise RuntimeError(f"Failed to execute command '{task.command}': {e}")

    async def _execute_script(self, task: Task) -> None:
        """Execute Python script"""
        import importlib.util
        import sys

        try:
            script_path = Path(task.script_path)
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")

            # Load and execute script
            spec = importlib.util.spec_from_file_location("task_script", script_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["task_script"] = module

            # Prepare execution context
            execution_context = {
                "task": task,
                "parameters": task.parameters,
                "context": task.context,
                "logger": logger,
            }

            # Execute script
            spec.loader.exec_module(module)

            # Call main function if exists
            if hasattr(module, "main"):
                result = await module["main"](execution_context)
                task.result = {"result": result, "script": str(script_path)}
            else:
                task.result = {
                    "message": "Script executed successfully",
                    "script": str(script_path),
                }

        except Exception as e:
            raise RuntimeError(f"Failed to execute script '{task.script_path}': {e}")

    async def _execute_parameters(self, task: Task) -> None:
        """Execute task based on parameters"""
        # Simulate parameter-based execution
        await asyncio.sleep(0.1)

        task.result = {
            "message": "Parameter-based execution completed",
            "parameters": task.parameters,
            "execution_type": "parameters",
        }

    async def _handle_task_failure(self, task: Task) -> None:
        """Handle task failure with retry logic"""
        self.failed_tasks.add(task.id)

        # Check if retry is needed
        if task.schedule.retry_count < task.schedule.max_retries:
            task.schedule.retry_count += 1
            task.status = TaskStatus.PENDING

            # Calculate backoff delay
            delay_seconds = task.schedule.backoff_factor**task.schedule.retry_count
            delay_seconds = min(delay_seconds, 300)  # Cap at 5 minutes

            logger.info(
                f"Scheduling retry for task {task.id} in {delay_seconds} seconds"
            )

            # Schedule retry
            asyncio.create_task(self._retry_task(task, delay_seconds))
        else:
            logger.error(
                f"Task {task.id} failed after {task.schedule.max_retries} retries"
            )

    async def _retry_task(self, task: Task, delay_seconds: float) -> None:
        """Retry task after delay"""
        await asyncio.sleep(delay_seconds)

        if task.status == TaskStatus.PENDING:
            await self.execute_task(task.id)

    async def _check_dependent_tasks(self, completed_task_id: str) -> None:
        """Check and queue tasks that depend on completed task"""
        for task_id, task in self.tasks.items():
            if task.status in [
                TaskStatus.PENDING,
                TaskStatus.BLOCKED,
            ] and task.can_start(self.completed_tasks):
                self.task_queue.put(task)

    async def _send_notification(self, task: Task, event_type: str) -> None:
        """Send task notification"""
        # Implementation would depend on notification system
        logger.info(f"Task notification: {task.title} - {event_type}")

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    async def list_tasks(
        self,
        status_filter: Optional[TaskStatus] = None,
        priority_filter: Optional[TaskPriority] = None,
        assignee_filter: Optional[str] = None,
        tag_filter: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> list[Task]:
        """List tasks with filtering and pagination"""
        tasks = list(self.tasks.values())

        # Apply filters
        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]
        if priority_filter:
            tasks = [t for t in tasks if t.priority == priority_filter]
        if assignee_filter:
            tasks = [t for t in tasks if t.assignee == assignee_filter]
        if tag_filter:
            tasks = [t for t in tasks if tag_filter in t.tags]

        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        # Apply pagination
        if offset > 0:
            tasks = tasks[offset:]
        if limit:
            tasks = tasks[:limit]

        return tasks

    async def get_task_statistics(self) -> dict[str, Any]:
        """Get comprehensive task statistics"""
        total_tasks = len(self.tasks)
        status_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        type_counts = defaultdict(int)

        overdue_tasks = 0
        upcoming_deadlines = 0

        now = datetime.now()

        for task in self.tasks.values():
            status_counts[task.status.value] += 1
            priority_counts[task.priority.value] += 1
            type_counts[task.task_type.value] += 1

            if task.is_overdue():
                overdue_tasks += 1

            if (
                task.schedule.deadline
                and task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
                and 0 < (task.schedule.deadline - now).total_seconds() / 3600 <= 24
            ):
                upcoming_deadlines += 1

        return {
            "total_tasks": total_tasks,
            "status_distribution": dict(status_counts),
            "priority_distribution": dict(priority_counts),
            "type_distribution": dict(type_counts),
            "overdue_tasks": overdue_tasks,
            "upcoming_deadlines": upcoming_deadlines,
            "running_tasks": len(self.running_tasks),
            "queued_tasks": self.task_queue.size(),
            "completion_rate": len(self.completed_tasks) / total_tasks
            if total_tasks > 0
            else 0,
            "failure_rate": len(self.failed_tasks) / total_tasks
            if total_tasks > 0
            else 0,
        }

    async def start_scheduler(self) -> None:
        """Start task scheduler"""
        if self.scheduler_active:
            return

        self.scheduler_active = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Task scheduler started")

    async def stop_scheduler(self) -> None:
        """Stop task scheduler"""
        self.scheduler_active = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Task scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self.scheduler_active:
            try:
                await self._process_scheduled_tasks()
                await self._check_deadlines()
                await self._cleanup_completed_tasks()
                await asyncio.sleep(self.schedule_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry

    async def _process_scheduled_tasks(self) -> None:
        """Process tasks scheduled for execution"""
        now = datetime.now()
        ready_tasks = []

        for task in self.tasks.values():
            if (
                task.status == TaskStatus.PENDING
                and task.schedule.scheduled_at
                and task.schedule.scheduled_at <= now
                and task.can_start(self.completed_tasks)
            ):
                ready_tasks.append(task)

        # Queue ready tasks
        for task in ready_tasks:
            self.task_queue.put(task)

    async def _check_deadlines(self) -> None:
        """Check for upcoming deadlines and send notifications"""
        now = datetime.now()
        warning_hours = [1, 24, 72]  # Send warnings at these intervals

        for task in self.tasks.values():
            if task.schedule.deadline and task.status not in [
                TaskStatus.COMPLETED,
                TaskStatus.CANCELLED,
            ]:
                hours_until_deadline = (
                    task.schedule.deadline - now
                ).total_seconds() / 3600

                for warning_hour in warning_hours:
                    if (
                        hours_until_deadline <= warning_hour
                        and hours_until_deadline > warning_hour - 1
                    ):
                        await self._send_deadline_warning(task, hours_until_deadline)
                        break

    async def _send_deadline_warning(self, task: Task, hours_remaining: float) -> None:
        """Send deadline warning notification"""
        logger.warning(
            f"Deadline warning: Task '{task.title}' has {hours_remaining:.1f} hours remaining"  # noqa: E501
        )

    async def _cleanup_completed_tasks(self) -> None:
        """Clean up old completed tasks"""
        cutoff_date = datetime.now() - timedelta(days=30)  # Keep for 30 days

        old_completed_tasks = [
            task_id
            for task_id, task in self.tasks.items()
            if (task.status == TaskStatus.COMPLETED and task.updated_at < cutoff_date)
        ]

        for task_id in old_completed_tasks:
            await self.delete_task(task_id, force=True)
            logger.debug(f"Cleaned up old completed task: {task_id}")

    async def process_task_queue(self) -> None:
        """Process tasks from the queue"""
        while (
            not self.task_queue.is_empty()
            and len(self.running_tasks) < self.max_concurrent_tasks
        ):
            task = self.task_queue.get()
            if task and await self.execute_task(task.id):
                logger.debug(f"Queued task for execution: {task.title}")
            else:
                break

    async def shutdown(self) -> None:
        """Shutdown task manager gracefully"""
        logger.info("Shutting down task manager")

        # Stop scheduler
        await self.stop_scheduler()

        # Wait for running tasks to complete (with timeout)
        if self.running_tasks:
            logger.info(
                f"Waiting for {len(self.running_tasks)} running tasks to complete"
            )

            # Cancel remaining tasks after timeout
            await asyncio.sleep(10)  # Give tasks time to complete
            for task_id, task in self.running_tasks.items():
                if not task.done():
                    logger.warning(f"Cancelling task: {task_id}")
                    task.cancel()

            # Wait for cancellation
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)

        # Shutdown thread pool
        self.executor.shutdown(wait=True)

        logger.info("Task manager shutdown complete")

    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)
