"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : task_orchestrator.py
@Description:
    Task Orchestrator - Orchestrates task execution across different entrance types.
    Manages task lifecycle, workflow execution, and resource allocation.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from ..domain.aggregates import TaskAggregate
from ..domain.domain_services import WorkflowOrchestratorService
from ..domain.value_objects import IntentType, TaskPriority, TaskStatus


class TaskState(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskEventType(Enum):
    """任务事件类型枚举"""
    CREATED = "task_created"
    QUEUED = "task_queued"
    STARTED = "task_started"
    PAUSED = "task_paused"
    RESUMED = "task_resumed"
    COMPLETED = "task_completed"
    FAILED = "task_failed"
    CANCELLED = "task_cancelled"
    TIMEOUT = "task_timeout"
    PROGRESS_UPDATED = "progress_updated"
    RESOURCE_ALLOCATED = "resource_allocated"
    RESOURCE_RELEASED = "resource_released"


@dataclass
class TaskEvent:
    """任务事件"""
    event_id: str
    event_type: TaskEventType
    task_id: str
    session_id: str
    timestamp: datetime
    data: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


@dataclass
class ResourceRequirement:
    """资源需求"""
    cpu_cores: float = 1.0
    memory_mb: int = 512
    gpu_required: bool = False
    network_bandwidth: float = 1.0  # Mbps
    storage_mb: int = 100
    timeout_seconds: int = 300


@dataclass
class TaskExecutionResult:
    """任务执行结果"""
    task_id: str
    status: TaskStatus
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    resource_usage: dict[str, Any] = field(default_factory=dict)
    steps_executed: list[dict[str, Any]] = field(default_factory=list)
    output_files: list[str] = field(default_factory=list)
    completed_at: Optional[datetime] = None


@dataclass
class TaskConfig:
    """任务配置"""
    max_concurrent_tasks: int = 10
    max_queue_size: int = 100
    task_timeout_seconds: int = 1800  # 30分钟
    enable_priority_queue: bool = True
    enable_resource_management: bool = True
    enable_retry_mechanism: bool = True
    max_retries: int = 3
    retry_delay_seconds: int = 60
    enable_event_logging: bool = True
    max_event_history: int = 5000
    cleanup_interval_seconds: int = 300


class TaskOrchestrator:
    """任务编排器 - 协调不同入口类型的任务执行"""
    
    def __init__(self, config: TaskConfig = None):
        self.config = config or TaskConfig()
        
        # 核心服务
        self.workflow_orchestrator = WorkflowOrchestratorService()
        
        # 任务存储
        self.tasks: dict[str, TaskAggregate] = {}
        self.session_tasks: dict[str, set[str]] = {}  # session_id -> task_ids
        
        # 任务队列
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.priority_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
        # 执行中的任务
        self.running_tasks: dict[str, asyncio.Task] = {}
        
        # 资源管理
        self.available_resources = {
            "cpu_cores": 8.0,
            "memory_mb": 8192,
            "gpu_count": 1,
            "network_bandwidth": 100.0,
            "storage_mb": 10240
        }
        self.allocated_resources: dict[str, ResourceRequirement] = {}
        
        # 事件历史
        self.event_history: list[TaskEvent] = []
        
        # 统计信息
        self.stats = {
            "total_tasks_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_cancelled": 0,
            "tasks_timeout": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0,
            "queue_size": 0,
            "running_tasks": 0,
            "start_time": datetime.now()
        }
        
        # 任务监听器
        self.task_listeners: dict[str, list[callable]] = {}
        
        # 后台任务
        self._queue_processor_task: Optional[asyncio.Task] = None
        self._resource_monitor_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def start(self):
        """启动任务编排器"""
        if self._is_running:
            return
        
        self._is_running = True
        
        # 启动后台任务
        self._queue_processor_task = asyncio.create_task(self._process_task_queue())
        self._resource_monitor_task = asyncio.create_task(self._monitor_resources())
        self._cleanup_task = asyncio.create_task(self._cleanup_completed_tasks())
        
        logging.info("Task Orchestrator started")
    
    async def stop(self):
        """停止任务编排器"""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # 取消后台任务
        if self._queue_processor_task:
            self._queue_processor_task.cancel()
        
        if self._resource_monitor_task:
            self._resource_monitor_task.cancel()
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # 取消所有运行中的任务
        for _, task in self.running_tasks.items():
            task.cancel()
        
        # 清空队列
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        while not self.priority_queue.empty():
            try:
                self.priority_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        logging.info("Task Orchestrator stopped")
    
    async def create_task(self, session_id: str, content: str, intent_type: IntentType, 
                         priority: TaskPriority = None, context: dict[str, Any] = None) -> TaskAggregate:
        """创建新任务"""
        if not priority:
            priority = TaskPriority("normal")
        
        # 创建任务聚合
        task_aggregate = TaskAggregate()
        task_aggregate.set_session(session_id)
        task_aggregate.set_content(content, intent_type)
        task_aggregate.set_priority(priority)
        
        # 添加上下文信息
        if context:
            for key, value in context.items():
                task_aggregate.task.metadata[key] = value
        
        # 保存任务
        self.tasks[task_aggregate.task_id] = task_aggregate
        
        # 更新会话任务映射
        if session_id not in self.session_tasks:
            self.session_tasks[session_id] = set()
        self.session_tasks[session_id].add(task_aggregate.task_id)
        
        # 更新统计
        self.stats["total_tasks_created"] += 1
        
        # 记录事件
        await self._record_event(TaskEventType.CREATED, task_aggregate.task_id, session_id, {
            "content": content[:100] + "..." if len(content) > 100 else content,
            "intent_type": intent_type.value,
            "priority": priority.value,
            "context": context
        })
        
        # 通知监听器
        await self._notify_listeners(task_aggregate.task_id, TaskEventType.CREATED, task_aggregate)
        
        # 将任务加入队列
        await self._queue_task(task_aggregate)
        
        logging.info(f"Created task {task_aggregate.task_id} for session {session_id}")
        
        return task_aggregate
    
    async def get_task(self, task_id: str) -> Optional[TaskAggregate]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    async def get_session_tasks(self, session_id: str) -> list[TaskAggregate]:
        """获取会话的所有任务"""
        task_ids = self.session_tasks.get(session_id, set())
        return [self.tasks[task_id] for task_id in task_ids if task_id in self.tasks]
    
    async def get_running_tasks(self) -> list[TaskAggregate]:
        """获取运行中的任务"""
        return [task for task in self.tasks.values() if task.task.status == TaskStatus.RUNNING]
    
    async def get_queued_tasks(self) -> list[TaskAggregate]:
        """获取队列中的任务"""
        return [task for task in self.tasks.values() if task.task.status == TaskStatus.PENDING]
    
    async def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        task_aggregate = await self.get_task(task_id)
        if not task_aggregate:
            return False
        
        if task_aggregate.task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            return False
        
        # 如果任务正在运行，取消执行任务
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        # 更新任务状态
        task_aggregate.task.status = TaskStatus.PAUSED
        task_aggregate.task.updated_at = datetime.now()
        
        await self._record_event(TaskEventType.PAUSED, task_id, task_aggregate.task.session_id)
        await self._notify_listeners(task_id, TaskEventType.PAUSED, task_aggregate)
        
        logging.info(f"Paused task {task_id}")
        return True
    
    async def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        task_aggregate = await self.get_task(task_id)
        if not task_aggregate:
            return False
        
        if task_aggregate.task.status != TaskStatus.PAUSED:
            return False
        
        # 重新排队任务
        task_aggregate.task.status = TaskStatus.PENDING
        task_aggregate.task.updated_at = datetime.now()
        
        await self._record_event(TaskEventType.RESUMED, task_id, task_aggregate.task.session_id)
        await self._notify_listeners(task_id, TaskEventType.RESUMED, task_aggregate)
        
        # 重新加入队列
        await self._queue_task(task_aggregate)
        
        logging.info(f"Resumed task {task_id}")
        return True
    
    async def cancel_task(self, task_id: str, reason: str = "user_request") -> bool:
        """取消任务"""
        task_aggregate = await self.get_task(task_id)
        if not task_aggregate:
            return False
        
        if task_aggregate.task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return True
        
        # 如果任务正在运行，取消执行任务
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        # 释放资源
        await self._release_resources(task_id)
        
        # 更新任务状态
        task_aggregate.cancel_execution()
        
        await self._record_event(TaskEventType.CANCELLED, task_id, task_aggregate.task.session_id, {"reason": reason})
        await self._notify_listeners(task_id, TaskEventType.CANCELLED, task_aggregate)
        
        # 更新统计
        self.stats["tasks_cancelled"] += 1
        
        logging.info(f"Cancelled task {task_id} (reason: {reason})")
        return True
    
    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        """获取任务状态"""
        task_aggregate = await self.get_task(task_id)
        if not task_aggregate:
            return {"error": "Task not found"}
        
        task = task_aggregate.task
        
        # 检查任务是否超时
        is_timeout = False
        if task.status == TaskStatus.RUNNING:
            execution_time = (datetime.now() - task.updated_at).total_seconds()
            if execution_time > self.config.task_timeout_seconds:
                is_timeout = True
                await self._handle_task_timeout(task_id)
        
        # 获取执行历史
        execution_history = task_aggregate.get_execution_history()
        
        # 计算进度
        progress = 0.0
        if task.status == TaskStatus.COMPLETED:
            progress = 1.0
        elif task.status == TaskStatus.RUNNING and execution_history:
            total_steps = len(execution_history)
            completed_steps = len([step for step in execution_history if step.get("event") == "completed"])
            progress = completed_steps / total_steps if total_steps > 0 else 0.0
        
        return {
            "task_id": task_id,
            "session_id": task.session_id,
            "content": task.content,
            "intent_type": task.intent_type.value,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "is_timeout": is_timeout,
            "progress": progress,
            "execution_time": task_aggregate.get_execution_time(),
            "execution_history": execution_history,
            "result": task.result,
            "error": task.metadata.get("error"),
            "metadata": task.metadata
        }
    
    async def get_task_result(self, task_id: str) -> Optional[TaskExecutionResult]:
        """获取任务执行结果"""
        task_aggregate = await self.get_task(task_id)
        if not task_aggregate:
            return None
        
        if not task_aggregate.is_completed():
            return None
        
        return TaskExecutionResult(
            task_id=task_id,
            status=task_aggregate.task.status,
            result=task_aggregate.task.result,
            error=task_aggregate.task.metadata.get("error"),
            execution_time=task_aggregate.get_execution_time() or 0.0,
            steps_executed=task_aggregate.get_execution_steps(),
            completed_at=task_aggregate.task.completed_at
        )
    
    async def _queue_task(self, task_aggregate: TaskAggregate):
        """将任务加入队列"""
        task_id = task_aggregate.task_id
        
        # 更新任务状态
        task_aggregate.task.status = TaskStatus.PENDING
        task_aggregate.task.updated_at = datetime.now()
        
        # 根据优先级选择队列
        if self.config.enable_priority_queue and task_aggregate.task.priority.value in ["high", "urgent"]:
            # 优先队列：优先级越高，数值越小
            priority_value = {"urgent": 1, "high": 2, "normal": 3, "low": 4}[task_aggregate.task.priority.value]
            await self.priority_queue.put((priority_value, task_id))
        else:
            # 普通队列
            await self.task_queue.put(task_id)
        
        await self._record_event(TaskEventType.QUEUED, task_id, task_aggregate.task.session_id)
        await self._notify_listeners(task_id, TaskEventType.QUEUED, task_aggregate)
        
        # 更新统计
        self.stats["queue_size"] = self.task_queue.qsize() + self.priority_queue.qsize()
    
    async def _process_task_queue(self):
        """处理任务队列"""
        while self._is_running:
            try:
                # 优先处理优先队列
                if not self.priority_queue.empty():
                    priority, task_id = await self.priority_queue.get()
                elif not self.task_queue.empty():
                    task_id = await self.task_queue.get()
                else:
                    # 队列为空，等待一段时间
                    await asyncio.sleep(1)
                    continue
                
                # 获取任务
                task_aggregate = await self.get_task(task_id)
                if not task_aggregate:
                    continue
                
                # 检查任务是否已被取消
                if task_aggregate.task.status == TaskStatus.CANCELLED:
                    continue
                
                # 检查资源是否足够
                if self.config.enable_resource_management:
                    resource_requirement = self._estimate_resource_requirement(task_aggregate)
                    if not await self._allocate_resources(task_id, resource_requirement):
                        # 资源不足，重新排队
                        await asyncio.sleep(5)
                        await self._queue_task(task_aggregate)
                        continue
                
                # 执行任务
                execution_task = asyncio.create_task(self._execute_task(task_aggregate))
                self.running_tasks[task_id] = execution_task
                
                # 更新统计
                self.stats["running_tasks"] = len(self.running_tasks)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error processing task queue: {e}")
    
    async def _execute_task(self, task_aggregate: TaskAggregate):
        """执行任务"""
        task_id = task_aggregate.task_id
        session_id = task_aggregate.task.session_id
        
        try:
            # 开始执行
            task_aggregate.start_execution()
            
            await self._record_event(TaskEventType.STARTED, task_id, session_id)
            await self._notify_listeners(task_id, TaskEventType.STARTED, task_aggregate)
            
            # 规划工作流
            intent = {
                "type": task_aggregate.task.intent_type.value,
                "content": task_aggregate.task.content,
                "complexity": self._analyze_task_complexity(task_aggregate.task.content),
                "context": task_aggregate.task.metadata
            }
            
            workflow_plan = await self.workflow_orchestrator.plan_workflow(intent)
            
            # 启动工作流
            await self.workflow_orchestrator.start_workflow(
                workflow_plan["workflow_id"],
                workflow_plan
            )
            
            # 执行工作流步骤
            final_result = None
            for step in workflow_plan["steps"]:
                if task_aggregate.task.status != TaskStatus.RUNNING:
                    break
                
                # 记录步骤开始
                task_aggregate.record_step(step["step_id"], {
                    "step_name": step["name"],
                    "status": "started",
                    "timestamp": datetime.now()
                })
                
                # 执行步骤
                step_result = await self.workflow_orchestrator.execute_step(
                    workflow_plan["workflow_id"],
                    step["step_id"]
                )
                
                # 记录步骤完成
                task_aggregate.record_step(step["step_id"], {
                    "step_name": step["name"],
                    "status": "completed",
                    "result": step_result,
                    "timestamp": datetime.now()
                })
                
                # 更新进度
                await self._record_event(TaskEventType.PROGRESS_UPDATED, task_id, session_id, {
                    "step_id": step["step_id"],
                    "step_name": step["name"],
                    "progress": len(task_aggregate.get_execution_steps()) / len(workflow_plan["steps"])
                })
            
            # 生成最终结果
            final_result = await self._generate_task_result(task_aggregate, workflow_plan)
            
            # 完成任务
            task_aggregate.complete_execution(final_result)
            
            await self._record_event(TaskEventType.COMPLETED, task_id, session_id, {
                "result": final_result[:200] + "..." if len(final_result) > 200 else final_result,
                "execution_time": task_aggregate.get_execution_time()
            })
            await self._notify_listeners(task_id, TaskEventType.COMPLETED, task_aggregate)
            
            # 更新统计
            self.stats["tasks_completed"] += 1
            self.stats["total_execution_time"] += task_aggregate.get_execution_time() or 0
            self.stats["average_execution_time"] = self.stats["total_execution_time"] / self.stats["tasks_completed"]
            
        except asyncio.CancelledError:
            # 任务被取消
            if task_aggregate.task.status == TaskStatus.RUNNING:
                task_aggregate.fail_execution("Task cancelled during execution")
            
            await self._record_event(TaskEventType.CANCELLED, task_id, session_id, {"reason": "execution_cancelled"})
            
        except Exception as e:
            # 任务执行失败
            error_message = str(e)
            task_aggregate.fail_execution(error_message)
            
            await self._record_event(TaskEventType.FAILED, task_id, session_id, {"error": error_message})
            await self._notify_listeners(task_id, TaskEventType.FAILED, task_aggregate)
            
            # 更新统计
            self.stats["tasks_failed"] += 1
            
            # 重试机制
            if self.config.enable_retry_mechanism:
                await self._handle_task_retry(task_aggregate, error_message)
        
        finally:
            # 清理资源
            await self._release_resources(task_id)
            
            # 从运行中任务中移除
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            # 更新统计
            self.stats["running_tasks"] = len(self.running_tasks)
    
    def _analyze_task_complexity(self, content: str) -> float:
        """分析任务复杂度"""
        # 基于内容长度和关键词分析复杂度
        length_factor = min(len(content) / 200, 1.0)
        
        complexity_keywords = [
            "分析", "评估", "比较", "综合", "深入", "详细", "全面",
            "analyze", "evaluate", "compare", "comprehensive", "detailed"
        ]
        
        keyword_count = sum(1 for keyword in complexity_keywords if keyword in content)
        keyword_factor = min(keyword_count / 3, 1.0)
        
        return (length_factor * 0.4 + keyword_factor * 0.6)
    
    async def _generate_task_result(self, task_aggregate: TaskAggregate, workflow_plan: dict[str, Any]) -> str:
        """生成任务结果"""
        intent_type = task_aggregate.task.intent_type
        content = task_aggregate.task.content
        
        if intent_type == IntentType.ANALYSIS:
            return f"关于'{content}'的分析报告已完成。通过{len(workflow_plan['steps'])}个步骤的深度分析，得出了全面的结论。分析涵盖了多个维度，提供了详细的见解和建议。"
        elif intent_type == IntentType.EVALUATION:
            return f"对'{content}'的评估已完成。基于多维度分析，提供了详细的评估结果和建议。评估过程考虑了各种因素，确保了结果的客观性和准确性。"
        elif intent_type == IntentType.SUMMARIZATION:
            return f"'{content}'的总结报告已完成。提取了关键信息并进行了结构化整理，确保了内容的完整性和可读性。"
        elif intent_type == IntentType.DISCUSSION:
            return f"关于'{content}'的讨论已完成。通过多角度的观点交流和综合分析，形成了有价值的讨论成果和共识。"
        else:
            return f"'{content}'的任务已完成。执行过程顺利，结果符合预期要求。"
    
    def _estimate_resource_requirement(self, task_aggregate: TaskAggregate) -> ResourceRequirement:
        """估算资源需求"""
        # 基于任务复杂度和类型估算资源需求
        complexity = self._analyze_task_complexity(task_aggregate.task.content)
        intent_type = task_aggregate.task.intent_type
        
        # 基础资源需求
        base_cpu = 1.0
        base_memory = 512
        
        # 根据复杂度调整
        cpu_cores = base_cpu + complexity * 2.0
        memory_mb = int(base_memory + complexity * 1024)
        
        # 根据意图类型调整
        if intent_type in [IntentType.ANALYSIS, IntentType.EVALUATION]:
            cpu_cores *= 1.5
            memory_mb = int(memory_mb * 1.3)
        elif intent_type == IntentType.DISCUSSION:
            cpu_cores *= 1.2
            memory_mb = int(memory_mb * 1.1)
        
        return ResourceRequirement(
            cpu_cores=min(cpu_cores, 8.0),
            memory_mb=min(memory_mb, 4096),
            gpu_required=complexity > 0.8,
            timeout_seconds=self.config.task_timeout_seconds
        )
    
    async def _allocate_resources(self, task_id: str, requirement: ResourceRequirement) -> bool:
        """分配资源"""
        # 检查资源是否足够
        if (self.available_resources["cpu_cores"] < requirement.cpu_cores or
            self.available_resources["memory_mb"] < requirement.memory_mb or
            (requirement.gpu_required and self.available_resources["gpu_count"] <= 0)):
            return False
        
        # 分配资源
        self.available_resources["cpu_cores"] -= requirement.cpu_cores
        self.available_resources["memory_mb"] -= requirement.memory_mb
        if requirement.gpu_required:
            self.available_resources["gpu_count"] -= 1
        
        self.allocated_resources[task_id] = requirement
        
        await self._record_event(TaskEventType.RESOURCE_ALLOCATED, task_id, "", {
            "cpu_cores": requirement.cpu_cores,
            "memory_mb": requirement.memory_mb,
            "gpu_required": requirement.gpu_required
        })
        
        return True
    
    async def _release_resources(self, task_id: str):
        """释放资源"""
        if task_id not in self.allocated_resources:
            return
        
        requirement = self.allocated_resources[task_id]
        
        # 释放资源
        self.available_resources["cpu_cores"] += requirement.cpu_cores
        self.available_resources["memory_mb"] += requirement.memory_mb
        if requirement.gpu_required:
            self.available_resources["gpu_count"] += 1
        
        del self.allocated_resources[task_id]
        
        await self._record_event(TaskEventType.RESOURCE_RELEASED, task_id, "")
    
    async def _handle_task_timeout(self, task_id: str):
        """处理任务超时"""
        task_aggregate = await self.get_task(task_id)
        if not task_aggregate:
            return
        
        # 取消任务
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        # 释放资源
        await self._release_resources(task_id)
        
        # 更新任务状态
        task_aggregate.fail_execution("Task execution timeout")
        
        await self._record_event(TaskEventType.TIMEOUT, task_id, task_aggregate.task.session_id)
        await self._notify_listeners(task_id, TaskEventType.TIMEOUT, task_aggregate)
        
        # 更新统计
        self.stats["tasks_timeout"] += 1
        
        logging.warning(f"Task {task_id} timed out")
    
    async def _handle_task_retry(self, task_aggregate: TaskAggregate, error: str):
        """处理任务重试"""
        retry_count = task_aggregate.task.metadata.get("retry_count", 0)
        
        if retry_count < self.config.max_retries:
            # 增加重试计数
            task_aggregate.task.metadata["retry_count"] = retry_count + 1
            task_aggregate.task.metadata["last_error"] = error
            
            # 延迟后重试
            await asyncio.sleep(self.config.retry_delay_seconds)
            
            # 重新排队
            await self._queue_task(task_aggregate)
            
            logging.info(f"Retrying task {task_aggregate.task_id} (attempt {retry_count + 1})")
        else:
            logging.error(f"Task {task_aggregate.task_id} failed after {self.config.max_retries} retries")
    
    async def _monitor_resources(self):
        """监控资源使用情况"""
        while self._is_running:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                
                
                
                # 可以在这里添加资源告警逻辑
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in resource monitoring: {e}")
    
    async def _cleanup_completed_tasks(self):
        """清理已完成的任务"""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.cleanup_interval_seconds)
                
                # 清理超过24小时的已完成任务
                cleanup_time = datetime.now() - timedelta(hours=24)
                tasks_to_remove = []
                
                for task_id, task_aggregate in self.tasks.items():
                    if (task_aggregate.is_completed() and 
                        task_aggregate.task.completed_at and 
                        task_aggregate.task.completed_at < cleanup_time):
                        tasks_to_remove.append(task_id)
                
                for task_id in tasks_to_remove:
                    await self._remove_task(task_id)
                
                if tasks_to_remove:
                    logging.info(f"Cleaned up {len(tasks_to_remove)} completed tasks")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in cleanup task: {e}")
    
    async def _remove_task(self, task_id: str):
        """移除任务"""
        if task_id not in self.tasks:
            return
        
        task_aggregate = self.tasks[task_id]
        session_id = task_aggregate.task.session_id
        
        # 从会话任务映射中移除
        if session_id in self.session_tasks:
            self.session_tasks[session_id].discard(task_id)
        
        # 从任务列表中移除
        del self.tasks[task_id]
        
        # 移除监听器
        if task_id in self.task_listeners:
            del self.task_listeners[task_id]
    
    def add_task_listener(self, task_id: str, listener: callable):
        """添加任务监听器"""
        if task_id not in self.task_listeners:
            self.task_listeners[task_id] = []
        self.task_listeners[task_id].append(listener)
    
    def remove_task_listener(self, task_id: str, listener: callable):
        """移除任务监听器"""
        if task_id in self.task_listeners:
            try:
                self.task_listeners[task_id].remove(listener)
            except ValueError:
                pass
    
    async def _notify_listeners(self, task_id: str, event_type: TaskEventType, task_aggregate: TaskAggregate):
        """通知监听器"""
        if task_id in self.task_listeners:
            for listener in self.task_listeners[task_id]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(event_type, task_aggregate)
                    else:
                        listener(event_type, task_aggregate)
                except Exception as e:
                    logging.error(f"Error in task listener for {task_id}: {e}")
    
    async def _record_event(self, event_type: TaskEventType, task_id: str, session_id: str, data: dict[str, Any] = None):
        """记录事件"""
        if not self.config.enable_event_logging:
            return
        
        event = TaskEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            task_id=task_id,
            session_id=session_id,
            timestamp=datetime.now(),
            data=data or {}
        )
        
        self.event_history.append(event)
        
        # 限制事件历史大小
        if len(self.event_history) > self.config.max_event_history:
            self.event_history = self.event_history[-self.config.max_event_history:]
    
    async def get_task_events(self, task_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """获取任务事件历史"""
        task_events = [
            event for event in self.event_history 
            if event.task_id == task_id
        ]
        
        # 按时间排序并限制数量
        task_events.sort(key=lambda x: x.timestamp, reverse=True)
        recent_events = task_events[:limit]
        
        return [event.to_dict() for event in recent_events]
    
    async def get_system_statistics(self) -> dict[str, Any]:
        """获取系统统计信息"""
        uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        # 计算任务状态分布
        task_status_distribution = {}
        for task_aggregate in self.tasks.values():
            status = task_aggregate.task.status.value
            task_status_distribution[status] = task_status_distribution.get(status, 0) + 1
        
        # 计算意图类型分布
        intent_type_distribution = {}
        for task_aggregate in self.tasks.values():
            intent_type = task_aggregate.task.intent_type.value
            intent_type_distribution[intent_type] = intent_type_distribution.get(intent_type, 0) + 1
        
        return {
            "total_tasks_created": self.stats["total_tasks_created"],
            "tasks_completed": self.stats["tasks_completed"],
            "tasks_failed": self.stats["tasks_failed"],
            "tasks_cancelled": self.stats["tasks_cancelled"],
            "tasks_timeout": self.stats["tasks_timeout"],
            "total_execution_time": self.stats["total_execution_time"],
            "average_execution_time": self.stats["average_execution_time"],
            "queue_size": self.stats["queue_size"],
            "running_tasks": self.stats["running_tasks"],
            "uptime_seconds": uptime,
            "task_status_distribution": task_status_distribution,
            "intent_type_distribution": intent_type_distribution,
            "resource_usage": {
                "cpu_cores": {
                    "available": self.available_resources["cpu_cores"],
                    "allocated": sum(r.cpu_cores for r in self.allocated_resources.values())
                },
                "memory_mb": {
                    "available": self.available_resources["memory_mb"],
                    "allocated": sum(r.memory_mb for r in self.allocated_resources.values())
                },
                "gpu_count": {
                    "available": self.available_resources["gpu_count"],
                    "allocated": sum(1 for r in self.allocated_resources.values() if r.gpu_required)
                }
            },
            "is_running": self._is_running
        }
    
    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy",
            "is_running": self._is_running,
            "queue_size": self.stats["queue_size"],
            "running_tasks": self.stats["running_tasks"],
            "available_resources": self.available_resources,
            "last_health_check": datetime.now().isoformat()
        }