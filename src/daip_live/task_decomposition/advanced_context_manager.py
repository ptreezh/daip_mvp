"""
增强的任务上下文管理器
实现类似优秀开源项目的设计模式和最佳实践
"""
import asyncio
import uuid
import json
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class SubTaskContext:
    """子任务上下文数据类"""
    id: str
    parent_task_id: str
    title: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1-5, 5 highest
    progress: float = 0.0  # 0.0-1.0


@dataclass
class TaskContext:
    """任务上下文数据类"""
    id: str
    original_request: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING
    subtasks: List[SubTaskContext] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    progress: float = 0.0
    completed_subtasks: int = 0
    total_subtasks: int = 0

    def update_progress(self):
        """更新任务进度"""
        if self.total_subtasks > 0:
            self.progress = self.completed_subtasks / self.total_subtasks
        else:
            self.progress = 0.0


class ContextStorage:
    """上下文存储管理器 - 实现线程安全的持久化存储"""
    
    def __init__(self):
        self._storage: Dict[str, TaskContext] = {}
        self._lock = threading.RLock()
        self._event_callbacks: Dict[str, List[Callable]] = {
            'task_created': [],
            'task_updated': [],
            'task_completed': [],
            'subtask_status_changed': []
        }
    
    def store(self, context: TaskContext) -> bool:
        """存储任务上下文"""
        with self._lock:
            try:
                self._storage[context.id] = context
                self._trigger_event('task_created', context)
                return True
            except Exception as e:
                logger.error(f"Failed to store task context {context.id}: {e}")
                return False
    
    def retrieve(self, task_id: str) -> Optional[TaskContext]:
        """检索任务上下文"""
        with self._lock:
            return self._storage.get(task_id)
    
    def update(self, context: TaskContext) -> bool:
        """更新任务上下文"""
        with self._lock:
            try:
                self._storage[context.id] = context
                self._trigger_event('task_updated', context)
                return True
            except Exception as e:
                logger.error(f"Failed to update task context {context.id}: {e}")
                return False
    
    def delete(self, task_id: str) -> bool:
        """删除任务上下文"""
        with self._lock:
            if task_id in self._storage:
                del self._storage[task_id]
                return True
            return False
    
    def get_all_tasks(self) -> List[TaskContext]:
        """获取所有任务"""
        with self._lock:
            return list(self._storage.values())
    
    def subscribe(self, event: str, callback: Callable):
        """订阅事件"""
        if event in self._event_callbacks:
            self._event_callbacks[event].append(callback)
    
    def _trigger_event(self, event: str, context: TaskContext):
        """触发事件"""
        if event in self._event_callbacks:
            for callback in self._event_callbacks[event]:
                try:
                    callback(event, context)
                except Exception as e:
                    logger.error(f"Event callback failed: {e}")


class TaskContextManager:
    """任务上下文管理器 - 中央控制单元"""
    
    def __init__(self, storage: Optional[ContextStorage] = None):
        self.storage = storage or ContextStorage()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._event_handlers = {}
    
    @contextmanager
    def create_context(self, original_request: str, description: str = "") -> TaskContext:
        """创建任务上下文的上下文管理器"""
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        context = TaskContext(
            id=task_id,
            original_request=original_request,
            description=description or original_request
        )
        
        try:
            self.storage.store(context)
            yield context
        finally:
            # 清理资源
            pass
    
    async def create_task_context(self, original_request: str, description: str = "") -> TaskContext:
        """异步创建任务上下文"""
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        context = TaskContext(
            id=task_id,
            original_request=original_request,
            description=description or original_request
        )
        
        stored = self.storage.store(context)
        if not stored:
            raise RuntimeError(f"Failed to store task context {task_id}")
        
        return context
    
    async def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """更新任务状态"""
        context = self.storage.retrieve(task_id)
        if not context:
            return False
        
        old_status = context.status
        context.status = status
        context.updated_at = datetime.now()
        
        if status == TaskStatus.COMPLETED:
            self._trigger_completion_event(context)
        
        return self.storage.update(context)
    
    async def add_subtask(self, task_id: str, subtask: SubTaskContext) -> bool:
        """添加子任务"""
        context = self.storage.retrieve(task_id)
        if not context:
            return False
        
        context.subtasks.append(subtask)
        context.total_subtasks = len(context.subtasks)
        context.updated_at = datetime.now()
        
        return self.storage.update(context)
    
    async def update_subtask_status(self, task_id: str, subtask_id: str, 
                                   status: TaskStatus, result: Optional[str] = None, 
                                   error: Optional[str] = None) -> bool:
        """更新子任务状态"""
        context = self.storage.retrieve(task_id)
        if not context:
            return False
        
        subtask = next((st for st in context.subtasks if st.id == subtask_id), None)
        if not subtask:
            return False
        
        old_status = subtask.status
        subtask.status = status
        subtask.updated_at = datetime.now()
        
        if result:
            subtask.result = result
        if error:
            subtask.error = error
        
        if status == TaskStatus.IN_PROGRESS and not subtask.started_at:
            subtask.started_at = datetime.now()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            subtask.completed_at = datetime.now()
            if status == TaskStatus.COMPLETED:
                # 更新父任务的完成数量
                context.completed_subtasks += 1
        
        # 更新整体进度
        context.update_progress()
        context.updated_at = datetime.now()
        
        # 触发子任务状态变更事件
        self._trigger_subtask_event(context, subtask, old_status)
        
        return self.storage.update(context)
    
    async def get_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务进度"""
        context = self.storage.retrieve(task_id)
        if not context:
            return None
        
        completed = len([st for st in context.subtasks if st.status == TaskStatus.COMPLETED])
        in_progress = len([st for st in context.subtasks if st.status == TaskStatus.IN_PROGRESS])
        failed = len([st for st in context.subtasks if st.status == TaskStatus.FAILED])
        pending = len([st for st in context.subtasks if st.status == TaskStatus.PENDING])
        
        return {
            'task_id': task_id,
            'original_request': context.original_request,
            'status': context.status.value,
            'progress': context.progress,
            'completed_subtasks': completed,
            'in_progress_subtasks': in_progress,
            'failed_subtasks': failed,
            'pending_subtasks': pending,
            'total_subtasks': len(context.subtasks),
            'created_at': context.created_at.isoformat(),
            'updated_at': context.updated_at.isoformat()
        }
    
    def _trigger_completion_event(self, context: TaskContext):
        """触发任务完成事件"""
        logger.info(f"Task {context.id} completed")
    
    def _trigger_subtask_event(self, context: TaskContext, subtask: SubTaskContext, old_status: TaskStatus):
        """触发子任务事件"""
        logger.info(f"Subtask {subtask.id} in task {context.id} changed from {old_status.value} to {subtask.status.value}")


class AdvancedTaskOrchestrator:
    """高级任务编排器 - 负责编排复杂任务的执行"""
    
    def __init__(self, context_manager: TaskContextManager, model_provider=None):
        self.context_manager = context_manager
        self.model_provider = model_provider
    
    async def execute_task_with_context(self, original_request: str) -> Dict[str, Any]:
        """执行带有上下文管理的任务"""
        # 创建任务上下文
        context = await self.context_manager.create_task_context(original_request)
        
        # 使用模型分解任务
        subtasks = await self._decompose_task(context.original_request)
        
        # 添加子任务到上下文中
        for subtask in subtasks:
            await self.context_manager.add_subtask(context.id, subtask)
        
        # 更新任务状态为进行中
        await self.context_manager.update_task_status(context.id, TaskStatus.IN_PROGRESS)
        
        # 执行子任务 (按依赖顺序)
        execution_order = self._calculate_execution_order(subtasks)
        results = []
        
        for subtask_id in execution_order:
            subtask = next(st for st in subtasks if st.id == subtask_id)
            
            # 更新子任务为进行中
            await self.context_manager.update_subtask_status(
                context.id, 
                subtask_id, 
                TaskStatus.IN_PROGRESS
            )
            
            try:
                # 执行子任务
                result = await self._execute_subtask(subtask, context)
                
                # 更新子任务为完成
                await self.context_manager.update_subtask_status(
                    context.id, 
                    subtask_id, 
                    TaskStatus.COMPLETED, 
                    result=result
                )
                
                results.append(result)
            except Exception as e:
                # 更新子任务为失败
                await self.context_manager.update_subtask_status(
                    context.id, 
                    subtask_id, 
                    TaskStatus.FAILED, 
                    error=str(e)
                )
                results.append(f"Error: {str(e)}")
        
        # 计算最终结果
        final_result = await self._synthesize_results(original_request, results)
        
        # 更新任务为完成
        await self.context_manager.update_task_status(context.id, TaskStatus.COMPLETED)
        
        return {
            'task_id': context.id,
            'original_request': original_request,
            'final_result': final_result,
            'execution_results': results
        }
    
    async def _decompose_task(self, request: str) -> List[SubTaskContext]:
        """分解任务为子任务"""
        if self.model_provider:
            prompt = f"""请将以下复杂任务分解为3-8个具体的、可执行的子任务。

任务：{request}

请按照以下JSON格式返回结果，每项需要包含标题和描述：
{{
    "subtasks": [
        {{
            "title": "子任务标题",
            "description": "子任务详细描述",
            "priority": 1-5,  // 1-5, 5 highest
            "dependencies": ["dependency_task_id1", "dependency_task_id2"]  // 依赖的其他子任务ID
        }}
    ]
}}"""
            
            try:
                response = await self.model_provider.generate(prompt)
                response_text = str(response) if isinstance(response, dict) else response
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    subtasks_data = parsed.get("subtasks", [])
                    
                    subtasks = []
                    for task_data in subtasks_data:
                        subtask = SubTaskContext(
                            id=f"subtask_{uuid.uuid4().hex[:8]}",
                            parent_task_id="pending",  # 会在添加到任务中时更新
                            title=task_data.get("title", "未命名任务"),
                            description=task_data.get("description", ""),
                            dependencies=task_data.get("dependencies", []),
                            priority=task_data.get("priority", 3),
                        )
                        subtasks.append(subtask)
                    
                    return subtasks
            except Exception as e:
                logger.error(f"AI task decomposition failed: {e}")
        
        # 备选方案：基于规则的任务分解
        return self._rule_based_decomposition(request)
    
    def _rule_based_decomposition(self, request: str) -> List[SubTaskContext]:
        """基于规则的任务分解"""
        subtasks = []
        
        req_lower = request.lower()
        
        if any(keyword in req_lower for keyword in ["分析", "研究", "调研"]):
            steps = [
                ("需求分析", "分析任务的具体需求和目标"),
                ("文献调研", "收集相关领域的研究文献"),
                ("方法研究", "研究适用的分析方法"),
                ("数据收集", "收集必要的数据"),
                ("执行分析", "执行具体的分析工作"),
                ("结果总结", "总结分析结果")
            ]
        elif any(keyword in req_lower for keyword in ["设计", "开发", "构建"]):
            steps = [
                ("需求分析", "明确设计或开发的具体需求"),
                ("方案设计", "设计具体的实施方案"),
                ("原型开发", "开发原型或概念验证"),
                ("实施执行", "执行正式开发"),
                ("测试验证", "验证实现结果"),
                ("文档编写", "编写相关文档")
            ]
        elif any(keyword in req_lower for keyword in ["评估", "比较", "对比"]):
            steps = [
                ("标准制定", "确定比较或评估的标准"),
                ("信息收集", "收集各选项的相关信息"),
                ("对比分析", "进行详细的对比分析"),
                ("结果总结", "总结比较结果并提出建议")
            ]
        else:
            # 通用分解
            steps = [
                ("任务理解", "深入理解任务的具体要求"),
                ("准备阶段", "准备执行任务所需的资源"),
                ("执行过程", "执行任务的主要过程"),
                ("结果整理", "整理和总结执行结果"),
                ("报告编写", "编写相关报告或文档")
            ]
        
        for i, (title, description) in enumerate(steps, 1):
            subtask = SubTaskContext(
                id=f"subtask_{uuid.uuid4().hex[:8]}",
                parent_task_id="pending",
                title=title,
                description=description,
                dependencies=[steps[j][0] for j in range(i-1)],  # 每个任务依赖前面所有任务
                priority=min(5, max(1, 3))  # 默认优先级
            )
            subtasks.append(subtask)
        
        return subtasks
    
    def _calculate_execution_order(self, subtasks: List[SubTaskContext]) -> List[str]:
        """计算执行顺序（拓扑排序）"""
        # 创建依赖图
        graph = {}
        all_task_ids = {subtask.id for subtask in subtasks}

        for subtask in subtasks:
            # 只依赖不在当前任务列表中，则忽略
            valid_deps = [dep_id for dep_id in subtask.dependencies if dep_id in all_task_ids]
            graph[subtask.id] = valid_deps[:]

        # 拓扑排序
        result = []
        visited = set()
        temp = set()

        def visit(node_id: str):
            if node_id in visited:
                return
            if node_id in temp:
                raise ValueError(f"Circular dependency detected involving {node_id}")

            temp.add(node_id)
            for dep_id in graph[node_id]:
                visit(dep_id)
            temp.remove(node_id)
            visited.add(node_id)
            result.append(node_id)

        for subtask in subtasks:
            if subtask.id not in visited:
                visit(subtask.id)

        # 按优先级重新排序，确保依赖关系仍然满足
        # 优先级高的任务在满足依赖的前提下尽量靠前
        id_to_priority = {st.id: st.priority for st in subtasks}

        # 由于拓扑排序的结果已经满足依赖，我们可以直接按优先级分组
        priority_groups = {}
        for task_id in result:
            priority = id_to_priority[task_id]
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(task_id)

        # 按优先级降序排列
        sorted_priorities = sorted(priority_groups.keys(), reverse=True)
        sorted_result = []
        for priority in sorted_priorities:
            sorted_result.extend(priority_groups[priority])

        return sorted_result
    
    async def _execute_subtask(self, subtask: SubTaskContext, parent_context: TaskContext) -> str:
        """执行子任务"""
        if self.model_provider:
            context_prompt = f"""
原始任务: {parent_context.original_request}
当前子任务: {subtask.title}
子任务描述: {subtask.description}
子任务ID: {subtask.id}

请专注于完成当前子任务，并提供具体的结果或答案。
"""
            
            try:
                response = await self.model_provider.generate(context_prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception as e:
                logger.error(f"Subtask execution failed: {e}")
                raise
        
        # 备选执行方式
        return f"模拟执行结果: {subtask.title}"
    
    async def _synthesize_results(self, original_request: str, subtask_results: List[str]) -> str:
        """合成子任务结果"""
        if self.model_provider:
            results_summary = "\\n".join([
                f"- 子任务 {i+1}: {result[:200]}..."
                for i, result in enumerate(subtask_results)
                if result and not result.startswith("Error:")
            ])
            
            prompt = f"""
原始请求: {original_request}

子任务执行结果:
{results_summary}

请基于以上子任务结果，生成对原始请求的完整、连贯的回答。
"""
            
            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception as e:
                logger.error(f"Result synthesis failed: {e}")
        
        # 备选合成方式
        return f"任务执行完成。\\n\\n执行了 {len(subtask_results)} 个子任务，主要结果:\\n" + "\\n".join([
            f"- {result[:100]}..." for result in subtask_results[:3]
        ])


# 全局上下文管理器实例
_global_context_manager = None
_global_orchestrator = None


def get_context_manager(model_provider=None) -> TaskContextManager:
    """获取任务上下文管理器实例"""
    global _global_context_manager
    if _global_context_manager is None:
        _global_context_manager = TaskContextManager()
    return _global_context_manager


def get_task_orchestrator(model_provider=None) -> AdvancedTaskOrchestrator:
    """获取任务编排器实例"""
    global _global_orchestrator
    if _global_orchestrator is None:
        context_manager = get_context_manager()
        _global_orchestrator = AdvancedTaskOrchestrator(context_manager, model_provider)
    return _global_orchestrator