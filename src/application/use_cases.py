"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : use_cases.py
@Description:
    Application use cases for the Personal Intelligence Hub.
    These use cases orchestrate domain services and implement business workflows.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from ..domain.aggregates import DebateAggregate, SessionAggregate, TaskAggregate
from ..domain.domain_services import (
    ConsensusTrackingService,
    EntranceSelectorService,
    UserInterventionService,
    WorkflowOrchestratorService,
)
from ..infrastructure.database import (
    UserRepository,
    SessionRepository,
    TaskRepository,
    MessageRepository,
    DebateRepository,
)
from ..domain.entities import User
from ..domain.value_objects import (
    EntranceType,
    IntentType,
    MessageIntent,
    SessionStatus,
    TaskPriority,
    TaskStatus,
    UserPreference,
)
from ..infrastructure.database import DatabaseManager
from ..infrastructure.redis_client import RedisManager


class UseCaseResult:
    """用例执行结果"""
    
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


class BaseUseCase(ABC):
    """基础用例类"""
    
    def __init__(self, db_manager: DatabaseManager, redis_client: RedisManager):
        self.db_manager = db_manager
        self.redis_client = redis_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def execute(self, **kwargs) -> UseCaseResult:
        """执行用例"""
        pass


class CreateUserUseCase(BaseUseCase):
    """创建用户用例"""
    
    async def execute(self, user_id: str, username: str, email: str, 
                     preferred_entrance: EntranceType, 
                     preferences: dict[str, Any] = None) -> UseCaseResult:
        """执行创建用户用例"""
        try:
            async with self.db_manager.get_session() as session:
                user_repo = UserRepository(session)
                
                # 检查用户是否已存在
                existing_user = await user_repo.get_by_user_id(user_id)
                if existing_user:
                    return UseCaseResult(False, error=f"User {user_id} already exists")
                
                # 检查邮箱是否已被使用
                existing_email = await user_repo.get_by_email(email)
                if existing_email:
                    return UseCaseResult(False, error=f"Email {email} already registered")
                
                # 创建用户偏好
                user_preferences = preferences or {
                    "preferred_entrance": preferred_entrance.value,
                    "language": "zh-CN",
                    "theme": "light",
                    "notification_enabled": True,
                    "auto_transparency": False,
                    "detail_level": "comprehensive"
                }
                
                # 创建用户
                user = await user_repo.create_user(
                    user_id=user_id,
                    username=username,
                    email=email,
                    preferred_entrance=preferred_entrance.value,
                    preferences=user_preferences
                )
                
                # 缓存用户信息
                await self.redis_client.set(f"user:{user_id}", {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "preferred_entrance": user.preferred_entrance,
                    "is_active": user.is_active,
                    "preferences": user.preferences
                }, ttl=3600)
                
                return UseCaseResult(True, {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "preferred_entrance": user.preferred_entrance,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat()
                })
                
        except Exception as e:
            self.logger.error(f"Error creating user {user_id}: {e}")
            return UseCaseResult(False, error=str(e))


class CreateSessionUseCase(BaseUseCase):
    """创建会话用例"""
    
    def __init__(self, db_manager: DatabaseManager, redis_client: RedisManager,
                 entrance_selector: EntranceSelectorService):
        super().__init__(db_manager, redis_client)
        self.entrance_selector = entrance_selector
    
    async def execute(self, user_id: str, context: dict[str, Any] = None) -> UseCaseResult:
        """执行创建会话用例"""
        try:
            async with self.db_manager.get_session() as session:
                user_repo = UserRepository(session)
                session_repo = SessionRepository(session)
                
                # 获取用户信息
                user_data = await user_repo.get_by_user_id(user_id)
                if not user_data:
                    return UseCaseResult(False, error=f"User {user_id} not found")
                
                # 创建用户实体
                user = User(
                    user_id=user_data.user_id,
                    username=user_data.username,
                    email=user_data.email,
                    preferred_entrance=EntranceType(user_data.preferred_entrance),
                    preferences=UserPreference(**user_data.preferences),
                    created_at=user_data.created_at,
                    updated_at=user_data.updated_at,
                    is_active=user_data.is_active
                )
                
                # 智能选择入口类型
                selected_entrance = await self.entrance_selector.select_entrance(user, context or {})
                
                # 创建会话聚合
                session_aggregate = SessionAggregate(
                    user_id=user_id,
                    entrance_type=selected_entrance
                )
                
                # 保存会话到数据库
                await session_repo.create_session(
                    session_id=session_aggregate.session_id,
                    user_id=user_id,
                    entrance_type=selected_entrance.value,
                    status=session_aggregate.session.status.value,
                    metadata=session_aggregate.session.metadata
                )
                
                # 缓存会话信息
                await self.redis_client.set(f"session:{session_aggregate.session_id}", {
                    "session_id": session_aggregate.session_id,
                    "user_id": user_id,
                    "entrance_type": selected_entrance.value,
                    "status": session_aggregate.session.status.value,
                    "created_at": session_aggregate.session.created_at.isoformat(),
                    "metadata": session_aggregate.session.metadata
                }, ttl=7200)
                
                # 更新用户会话列表
                user_sessions_key = f"user_sessions:{user_id}"
                user_sessions = await self.redis_client.get(user_sessions_key) or []
                user_sessions.append(session_aggregate.session_id)
                await self.redis_client.set(user_sessions_key, user_sessions, ttl=7200)
                
                return UseCaseResult(True, {
                    "session_id": session_aggregate.session_id,
                    "user_id": user_id,
                    "entrance_type": selected_entrance.value,
                    "status": session_aggregate.session.status.value,
                    "created_at": session_aggregate.session.created_at.isoformat(),
                    "selected_entrance": selected_entrance.value,
                    "selection_reasoning": "智能选择基于用户偏好和上下文分析"
                })
                
        except Exception as e:
            self.logger.error(f"Error creating session for user {user_id}: {e}")
            return UseCaseResult(False, error=str(e))


class CreateTaskUseCase(BaseUseCase):
    """创建任务用例"""
    
    def __init__(self, db_manager: DatabaseManager, redis_client: RedisManager,
                 workflow_orchestrator: WorkflowOrchestratorService):
        super().__init__(db_manager, redis_client)
        self.workflow_orchestrator = workflow_orchestrator
    
    async def execute(self, session_id: str, content: str, intent_type: IntentType,
                     priority: TaskPriority = None, context: dict[str, Any] = None) -> UseCaseResult:
        """执行创建任务用例"""
        try:
            async with self.db_manager.get_session() as session:
                session_repo = SessionRepository(session)
                task_repo = TaskRepository(session)
                
                # 验证会话存在且活跃
                session_data = await session_repo.get_by_session_id(session_id)
                if not session_data:
                    return UseCaseResult(False, error=f"Session {session_id} not found")
                
                if session_data.status != SessionStatus.ACTIVE.value:
                    return UseCaseResult(False, error=f"Session {session_id} is not active")
                
                # 创建任务聚合
                task_aggregate = TaskAggregate()
                task_aggregate.set_session(session_id)
                task_aggregate.set_content(content, intent_type)
                
                if priority:
                    task_aggregate.set_priority(priority)
                
                # 保存任务到数据库
                await task_repo.create_task(
                    task_id=task_aggregate.task_id,
                    session_id=session_id,
                    content=content,
                    intent_type=intent_type.value,
                    status=task_aggregate.task.status.value,
                    priority=priority.value if priority else "normal",
                    metadata=task_aggregate.task.metadata
                )
                
                # 生成工作流计划
                workflow_plan = await self.workflow_orchestrator.plan_workflow({
                    "type": intent_type.value,
                    "content": content,
                    "context": context or {}
                })
                
                # 缓存任务信息
                await self.redis_client.set(f"task:{task_aggregate.task_id}", {
                    "task_id": task_aggregate.task_id,
                    "session_id": session_id,
                    "content": content,
                    "intent_type": intent_type.value,
                    "status": task_aggregate.task.status.value,
                    "priority": priority.value if priority else "normal",
                    "created_at": task_aggregate.task.created_at.isoformat(),
                    "workflow_plan": workflow_plan
                }, ttl=3600)
                
                return UseCaseResult(True, {
                    "task_id": task_aggregate.task_id,
                    "session_id": session_id,
                    "content": content,
                    "intent_type": intent_type.value,
                    "status": task_aggregate.task.status.value,
                    "priority": priority.value if priority else "normal",
                    "created_at": task_aggregate.task.created_at.isoformat(),
                    "workflow_plan": workflow_plan,
                    "estimated_duration": workflow_plan.get("estimated_duration", 0)
                })
                
        except Exception as e:
            self.logger.error(f"Error creating task for session {session_id}: {e}")
            return UseCaseResult(False, error=str(e))


class ProcessMessageUseCase(BaseUseCase):
    """处理消息用例"""
    
    def __init__(self, db_manager: DatabaseManager, redis_client: RedisManager,
                 user_intervention: UserInterventionService):
        super().__init__(db_manager, redis_client)
        self.user_intervention = user_intervention
    
    async def execute(self, session_id: str, content: str, sender: str,
                     message_intent: MessageIntent = None, context: dict[str, Any] = None) -> UseCaseResult:
        """执行处理消息用例"""
        try:
            async with self.db_manager.get_session() as session:
                session_repo = SessionRepository(session)
                message_repo = MessageRepository(session)
                
                # 验证会话存在且活跃
                session_data = await session_repo.get_by_session_id(session_id)
                if not session_data:
                    return UseCaseResult(False, error=f"Session {session_id} not found")
                
                if session_data.status != SessionStatus.ACTIVE.value:
                    return UseCaseResult(False, error=f"Session {session_id} is not active")
                
                # 优化用户输入
                optimized_content = content
                if sender.startswith("user_"):
                    optimized_content = await self.user_intervention.optimize_input(
                        content, message_intent.value if message_intent else "comment", context or {}
                    )
                
                # 创建消息实体
                from ..domain.entities import AgentMessage, SystemMessage, UserMessage
                
                if sender.startswith("user_"):
                    message = UserMessage(
                        message_id="",
                        session_id=session_id,
                        content=optimized_content,
                        sender=sender,
                        intent=message_intent or MessageIntent.COMMENT
                    )
                elif sender.startswith("agent_"):
                    message = AgentMessage(
                        message_id="",
                        session_id=session_id,
                        content=optimized_content,
                        sender=sender,
                        agent_role=sender.replace("agent_", "")
                    )
                else:
                    message = SystemMessage(
                        message_id="",
                        session_id=session_id,
                        content=optimized_content,
                        sender=sender,
                        system_event="user_message"
                    )
                
                # 保存消息到数据库
                await message_repo.create_message(
                    message_id=message.message_id,
                    session_id=session_id,
                    content=optimized_content,
                    sender=sender,
                    message_type=type(message).__name__,
                    intent=message_intent.value if message_intent else None,
                    metadata=message.metadata
                )
                
                # 缓存最近消息
                recent_messages_key = f"session_messages:{session_id}"
                recent_messages = await self.redis_client.get(recent_messages_key) or []
                recent_messages.append({
                    "message_id": message.message_id,
                    "content": optimized_content,
                    "sender": sender,
                    "timestamp": message.timestamp.isoformat(),
                    "type": type(message).__name__
                })
                
                # 只保留最近50条消息
                if len(recent_messages) > 50:
                    recent_messages = recent_messages[-50:]
                
                await self.redis_client.set(recent_messages_key, recent_messages, ttl=3600)
                
                return UseCaseResult(True, {
                    "message_id": message.message_id,
                    "session_id": session_id,
                    "content": optimized_content,
                    "sender": sender,
                    "timestamp": message.timestamp.isoformat(),
                    "type": type(message).__name__,
                    "was_optimized": optimized_content != content,
                    "optimization_diff": len(optimized_content) - len(content)
                })
                
        except Exception as e:
            self.logger.error(f"Error processing message for session {session_id}: {e}")
            return UseCaseResult(False, error=str(e))


class StartDebateUseCase(BaseUseCase):
    """开始辩论用例"""
    
    def __init__(self, db_manager: DatabaseManager, redis_client: RedisManager,
                 consensus_tracker: ConsensusTrackingService):
        super().__init__(db_manager, redis_client)
        self.consensus_tracker = consensus_tracker
    
    async def execute(self, session_id: str, topic: str, participants: list[str]) -> UseCaseResult:
        """执行开始辩论用例"""
        try:
            async with self.db_manager.get_session() as session:
                session_repo = SessionRepository(session)
                debate_repo = DebateRepository(session)
                
                # 验证会话存在且活跃
                session_data = await session_repo.get_by_session_id(session_id)
                if not session_data:
                    return UseCaseResult(False, error=f"Session {session_id} not found")
                
                if session_data.entrance_type != EntranceType.FORUM.value:
                    return UseCaseResult(False, error="Debates can only be created in Forum sessions")
                
                if session_data.status != SessionStatus.ACTIVE.value:
                    return UseCaseResult(False, error=f"Session {session_id} is not active")
                
                # 检查是否已有活跃辩论
                existing_debate = await debate_repo.get_session_debate(session_id)
                if existing_debate and existing_debate.status == "active":
                    return UseCaseResult(False, error="Active debate already exists in this session")
                
                # 创建辩论聚合
                debate_aggregate = DebateAggregate()
                debate_aggregate.set_session(session_id)
                debate_aggregate.set_topic(topic)
                
                # 添加参与者
                for participant in participants:
                    debate_aggregate.add_participant(participant)
                
                # 保存辩论到数据库
                await debate_repo.create_debate(
                    debate_id=debate_aggregate.debate_id,
                    session_id=session_id,
                    topic=topic,
                    participants=participants,
                    status=debate_aggregate.status
                )
                
                # 初始化共识跟踪
                await self.consensus_tracker.add_agent_opinion(
                    debate_aggregate.debate_id,
                    "system",
                    f"辩论开始，主题：{topic}",
                    1.0
                )
                
                # 缓存辩论信息
                await self.redis_client.set(f"debate:{debate_aggregate.debate_id}", {
                    "debate_id": debate_aggregate.debate_id,
                    "session_id": session_id,
                    "topic": topic,
                    "participants": participants,
                    "status": debate_aggregate.status,
                    "created_at": debate_aggregate.created_at.isoformat(),
                    "consensus_level": 0.0
                }, ttl=7200)
                
                return UseCaseResult(True, {
                    "debate_id": debate_aggregate.debate_id,
                    "session_id": session_id,
                    "topic": topic,
                    "participants": participants,
                    "status": debate_aggregate.status,
                    "created_at": debate_aggregate.created_at.isoformat(),
                    "message": "辩论已成功开始"
                })
                
        except Exception as e:
            self.logger.error(f"Error starting debate for session {session_id}: {e}")
            return UseCaseResult(False, error=str(e))


class GetSessionStatusUseCase(BaseUseCase):
    """获取会话状态用例"""
    
    async def execute(self, session_id: str) -> UseCaseResult:
        """执行获取会话状态用例"""
        try:
            # 尝试从缓存获取
            cached_session = await self.redis_client.get(f"session:{session_id}")
            if cached_session:
                return UseCaseResult(True, cached_session)
            
            # 从数据库获取
            async with self.db_manager.get_session() as session:
                session_repo = SessionRepository(session)
                task_repo = TaskRepository(session)
                message_repo = MessageRepository(session)
                
                session_data = await session_repo.get_by_session_id(session_id)
                if not session_data:
                    return UseCaseResult(False, error=f"Session {session_id} not found")
                
                # 获取任务统计
                tasks = await task_repo.get_session_tasks(session_id)
                task_stats = {
                    "total": len(tasks),
                    "pending": len([t for t in tasks if t.status == TaskStatus.PENDING.value]),
                    "running": len([t for t in tasks if t.status == TaskStatus.RUNNING.value]),
                    "completed": len([t for t in tasks if t.status == TaskStatus.COMPLETED.value]),
                    "failed": len([t for t in tasks if t.status == TaskStatus.FAILED.value])
                }
                
                # 获取最近消息
                recent_messages = await message_repo.get_session_messages(session_id, limit=10)
                
                # 构建状态信息
                status_info = {
                    "session_id": session_id,
                    "user_id": session_data.user_id,
                    "entrance_type": session_data.entrance_type,
                    "status": session_data.status,
                    "created_at": session_data.created_at.isoformat(),
                    "updated_at": session_data.updated_at.isoformat(),
                    "metadata": session_data.metadata,
                    "task_stats": task_stats,
                    "recent_messages_count": len(recent_messages),
                    "last_activity": session_data.updated_at.isoformat()
                }
                
                # 缓存状态信息
                await self.redis_client.set(f"session:{session_id}", status_info, ttl=300)
                
                return UseCaseResult(True, status_info)
                
        except Exception as e:
            self.logger.error(f"Error getting status for session {session_id}: {e}")
            return UseCaseResult(False, error=str(e))


class ExecuteTaskUseCase(BaseUseCase):
    """执行任务用例"""
    
    def __init__(self, db_manager: DatabaseManager, redis_client: RedisManager,
                 workflow_orchestrator: WorkflowOrchestratorService):
        super().__init__(db_manager, redis_client)
        self.workflow_orchestrator = workflow_orchestrator
    
    async def execute(self, task_id: str) -> UseCaseResult:
        """执行任务"""
        try:
            async with self.db_manager.get_session() as session:
                task_repo = TaskRepository(session)
                
                # 获取任务
                task_data = await task_repo.get_by_task_id(task_id)
                if not task_data:
                    return UseCaseResult(False, error=f"Task {task_id} not found")
                
                if task_data.status != TaskStatus.PENDING.value:
                    return UseCaseResult(False, error=f"Task {task_id} is not in pending status")
                
                # 更新任务状态为运行中
                await task_repo.update_task_status(task_id, TaskStatus.RUNNING.value)
                
                # 获取工作流计划
                cached_task = await self.redis_client.get(f"task:{task_id}")
                workflow_plan = cached_task.get("workflow_plan") if cached_task else None
                
                if workflow_plan:
                    # 启动工作流
                    workflow_id = workflow_plan.get("workflow_id")
                    await self.workflow_orchestrator.start_workflow(workflow_id, workflow_plan)
                    
                    # 执行工作流步骤
                    steps = workflow_plan.get("steps", [])
                    results = []
                    
                    for step in steps:
                        step_result = await self.workflow_orchestrator.execute_step(workflow_id, step["step_id"])
                        results.append(step_result)
                    
                    # 完成任务
                    final_result = f"任务执行完成，共执行 {len(results)} 个步骤"
                    await task_repo.update_task_status(task_id, TaskStatus.COMPLETED.value, final_result)
                    
                    return UseCaseResult(True, {
                        "task_id": task_id,
                        "status": "completed",
                        "result": final_result,
                        "steps_executed": len(results),
                        "execution_time": sum(r.get("execution_time", 0) for r in results)
                    })
                else:
                    # 简化执行
                    await task_repo.update_task_status(task_id, TaskStatus.COMPLETED.value, "任务执行完成")
                    
                    return UseCaseResult(True, {
                        "task_id": task_id,
                        "status": "completed",
                        "result": "任务执行完成",
                        "steps_executed": 0,
                        "execution_time": 0
                    })
                
        except Exception as e:
            self.logger.error(f"Error executing task {task_id}: {e}")
            # 更新任务状态为失败
            try:
                async with self.db_manager.get_session() as session:
                    task_repo = TaskRepository(session)
                    await task_repo.update_task_status(task_id, TaskStatus.FAILED.value)
            except Exception as inner_e:
                self.logger.error(f"Error updating task status to failed: {inner_e}")
            
            return UseCaseResult(False, error=str(e))


class UseCaseFactory:
    """用例工厂"""
    
    def __init__(self, db_manager: DatabaseManager, redis_client: RedisManager,
                 entrance_selector: EntranceSelectorService,
                 workflow_orchestrator: WorkflowOrchestratorService,
                 user_intervention: UserInterventionService,
                 consensus_tracker: ConsensusTrackingService):
        self.db_manager = db_manager
        self.redis_client = redis_client
        self.entrance_selector = entrance_selector
        self.workflow_orchestrator = workflow_orchestrator
        self.user_intervention = user_intervention
        self.consensus_tracker = consensus_tracker
    
    def create_user_use_case(self) -> CreateUserUseCase:
        """创建用户用例"""
        return CreateUserUseCase(self.db_manager, self.redis_client)
    
    def create_session_use_case(self) -> CreateSessionUseCase:
        """创建会话用例"""
        return CreateSessionUseCase(self.db_manager, self.redis_client, self.entrance_selector)
    
    def create_task_use_case(self) -> CreateTaskUseCase:
        """创建任务用例"""
        return CreateTaskUseCase(self.db_manager, self.redis_client, self.workflow_orchestrator)
    
    def process_message_use_case(self) -> ProcessMessageUseCase:
        """处理消息用例"""
        return ProcessMessageUseCase(self.db_manager, self.redis_client, self.user_intervention)
    
    def start_debate_use_case(self) -> StartDebateUseCase:
        """开始辩论用例"""
        return StartDebateUseCase(self.db_manager, self.redis_client, self.consensus_tracker)
    
    def get_session_status_use_case(self) -> GetSessionStatusUseCase:
        """获取会话状态用例"""
        return GetSessionStatusUseCase(self.db_manager, self.redis_client)
    
    def execute_task_use_case(self) -> ExecuteTaskUseCase:
        """执行任务用例"""
        return ExecuteTaskUseCase(self.db_manager, self.redis_client, self.workflow_orchestrator)