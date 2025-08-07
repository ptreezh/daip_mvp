# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : personal_assistant_service.py
@Description:
    Personal Assistant Service - Unified AI assistant service that coordinates
    between different entrance types and provides intelligent user support.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from uuid import uuid4

from ..domain.entities import User, Session, Task, Message, UserMessage, AgentMessage, SystemMessage
from ..domain.value_objects import (
    EntranceType, IntentType, TaskStatus, SessionStatus, 
    MessageIntent, ConsensusLevel, UserPreference, 
    TaskPriority, TimeInterval
)
from ..domain.aggregates import SessionAggregate, TaskAggregate, DebateAggregate
from ..domain.domain_services import (
    EntranceSelectorService, WorkflowOrchestratorService, 
    UserInterventionService, ConsensusTrackingService
)
from .use_cases import (
    CreateUserUseCase, CreateSessionUseCase, CreateTaskUseCase,
    ProcessMessageUseCase, StartDebateUseCase, ExecuteTaskUseCase
)


class PersonalAssistantService:
    """统一AI助手服务 - 协调不同入口类型并提供智能用户支持"""
    
    def __init__(self):
        # 核心服务
        self.entrance_selector = EntranceSelectorService()
        self.workflow_orchestrator = WorkflowOrchestratorService()
        self.user_intervention = UserInterventionService()
        self.consensus_tracker = ConsensusTrackingService()
        
        # 用例服务
        self.secretariat_use_case = SecretariatUseCase()
        self.forum_use_case = ForumUseCase()
        self.entrance_switching_use_case = EntranceSwitchingUseCase()
        
        # 用户和会话管理
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, SessionAggregate] = {}
        self.tasks: Dict[str, TaskAggregate] = {}
        self.debates: Dict[str, DebateAggregate] = {}
        
        # 服务状态
        self.is_initialized = False
        self.startup_time = None
        
    async def initialize(self):
        """初始化服务"""
        if self.is_initialized:
            return
            
        self.startup_time = datetime.now()
        
        # 初始化默认用户
        await self._initialize_default_users()
        
        # 初始化系统配置
        await self._initialize_system_config()
        
        self.is_initialized = True
        
        # 记录初始化完成事件
        await self._log_system_event("service_initialized", {
            "startup_time": self.startup_time.isoformat(),
            "users_count": len(self.users),
            "service_version": "1.0.0"
        })
    
    async def _initialize_default_users(self):
        """初始化默认用户"""
        default_users = [
            {
                "user_id": "default_user",
                "username": "默认用户",
                "email": "user@daip.live",
                "preferred_entrance": EntranceType.SECRETARIAT,
                "preferences": UserPreference(
                    preferred_entrance=EntranceType.SECRETARIAT,
                    language="zh-CN",
                    theme="light",
                    notification_enabled=True,
                    auto_transparency=False,
                    detail_level="comprehensive"
                )
            }
        ]
        
        for user_data in default_users:
            user = User(**user_data)
            self.users[user.user_id] = user
    
    async def _initialize_system_config(self):
        """初始化系统配置"""
        # 初始化工作流模板
        self.workflow_templates = {
            "quick_analysis": {
                "name": "快速分析",
                "description": "快速内容分析和总结",
                "estimated_time": 5.0,
                "complexity": 0.3
            },
            "deep_analysis": {
                "name": "深度分析", 
                "description": "深度多维度分析",
                "estimated_time": 15.0,
                "complexity": 0.8
            },
            "collaborative_discussion": {
                "name": "协作讨论",
                "description": "多角色协作讨论",
                "estimated_time": 20.0,
                "complexity": 0.9
            }
        }
        
        # 初始化Agent角色配置
        self.agent_roles = {
            "facilitator": {
                "name": "协调员",
                "description": "负责协调讨论进程",
                "expertise": ["讨论管理", "进程控制", "总结归纳"]
            },
            "domain_expert": {
                "name": "领域专家",
                "description": "提供专业领域知识",
                "expertise": ["专业知识", "深度分析", "权威判断"]
            },
            "critic": {
                "name": "评论家",
                "description": "提供批判性思考",
                "expertise": ["批判思维", "风险评估", "问题识别"]
            },
            "synthesizer": {
                "name": "综合者",
                "description": "综合不同观点和结论",
                "expertise": ["信息整合", "观点综合", "结论生成"]
            }
        }
    
    async def _log_system_event(self, event_type: str, data: Dict[str, Any]):
        """记录系统事件"""
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        # 这里可以集成到日志系统
        print(f"[SYSTEM EVENT] {json.dumps(event_data, ensure_ascii=False, indent=2)}")
    
    async def create_session(self, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建会话"""
        if not self.is_initialized:
            await self.initialize()
        
        # 获取用户
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # 智能选择入口类型
        context = context or {}
        selected_entrance = await self.entrance_selector.select_entrance(user, context)
        
        # 根据入口类型创建会话
        if selected_entrance == EntranceType.SECRETARIAT:
            session = await self.secretariat_use_case.create_session(user, selected_entrance)
            session_aggregate = self.secretariat_use_case.active_sessions[session.session_id]
        else:
            session_config = {
                "topic": context.get("topic", "通用讨论"),
                "participants": context.get("participants", ["expert_1", "expert_2"])
            }
            session = await self.forum_use_case.create_forum_session(user, session_config)
            session_aggregate = self.forum_use_case.active_sessions[session.session_id]
        
        # 保存会话
        self.sessions[session.session_id] = session_aggregate
        
        # 记录会话创建事件
        await self._log_system_event("session_created", {
            "session_id": session.session_id,
            "user_id": user_id,
            "entrance_type": selected_entrance.value,
            "context": context
        })
        
        return {
            "session_id": session.session_id,
            "user_id": user_id,
            "entrance_type": selected_entrance.value,
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "message": f"已创建{selected_entrance.value}会话"
        }
    
    async def process_user_input(self, session_id: str, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户输入"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.sessions[session_id]
        entrance_type = session_aggregate.entrance_type
        
        # 根据入口类型处理输入
        if entrance_type == EntranceType.SECRETARIAT:
            return await self._process_secretariat_input(session_aggregate, user_input)
        else:
            return await self._process_forum_input(session_aggregate, user_input)
    
    async def _process_secretariat_input(self, session_aggregate: SessionAggregate, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """处理Secretariat输入"""
        content = user_input.get("content", "").strip()
        if not content:
            raise ValueError("Input content cannot be empty")
        
        # 分析输入意图
        intent_type = self._analyze_input_intent(content)
        
        # 创建任务
        task_request = {
            "content": content,
            "intent_type": intent_type.value,
            "priority": user_input.get("priority", "normal"),
            "context": user_input.get("context", {})
        }
        
        # 提交任务
        result = await self.secretariat_use_case.submit_task(
            session_aggregate.session_id, 
            task_request
        )
        
        # 添加用户消息到会话
        user_message = UserMessage(
            session_id=session_aggregate.session_id,
            content=content,
            sender=f"user_{session_aggregate.user_id}",
            intent=MessageIntent.COMMENT
        )
        session_aggregate.add_message(user_message)
        
        return {
            "type": "task_created",
            "task_id": result["task_id"],
            "workflow_id": result["workflow_id"],
            "estimated_duration": result["estimated_duration"],
            "message": f"任务已创建，预计需要 {result['estimated_duration']:.1f} 秒完成"
        }
    
    async def _process_forum_input(self, session_aggregate: SessionAggregate, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """处理Forum输入"""
        # 处理用户干预
        intervention_data = {
            "message": {
                "content": user_input.get("content", ""),
                "intent": user_input.get("intent", "comment")
            },
            "context": user_input.get("context", {})
        }
        
        result = await self.forum_use_case.handle_user_intervention(
            session_aggregate.session_id,
            intervention_data
        )
        
        return {
            "type": "intervention_processed",
            "message_id": result["message_id"],
            "integration_result": result["integration_result"],
            "message": "用户干预已集成到讨论中"
        }
    
    def _analyze_input_intent(self, content: str) -> IntentType:
        """分析输入意图"""
        content_lower = content.lower()
        
        # 问题意图
        question_words = ["什么", "如何", "为什么", "怎么样", "是否", "能否", "what", "why", "how", "whether"]
        if any(word in content_lower for word in question_words):
            return IntentType.QUESTION
        
        # 分析意图
        analysis_words = ["分析", "评估", "研究", "调查", "analyze", "evaluate", "research", "investigate"]
        if any(word in content_lower for word in analysis_words):
            return IntentType.ANALYSIS
        
        # 讨论意图
        discussion_words = ["讨论", "探讨", "辩论", "discuss", "debate", "explore"]
        if any(word in content_lower for word in discussion_words):
            return IntentType.DISCUSSION
        
        # 默认为评论意图
        return IntentType.COMMENT
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """获取会话状态"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.sessions[session_id]
        entrance_type = session_aggregate.entrance_type
        
        # 基础会话信息
        status_data = {
            "session_id": session_id,
            "user_id": session_aggregate.user_id,
            "entrance_type": entrance_type.value,
            "status": session_aggregate.session.status.value,
            "created_at": session_aggregate.session.created_at.isoformat(),
            "updated_at": session_aggregate.session.updated_at.isoformat(),
            "duration": session_aggregate.get_duration(),
            "task_count": session_aggregate.get_task_count(),
            "message_count": len(session_aggregate.messages)
        }
        
        # 根据入口类型添加特定信息
        if entrance_type == EntranceType.SECRETARIAT:
            # 获取任务状态
            tasks = session_aggregate.tasks
            completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
            running_tasks = [t for t in tasks if t.status == TaskStatus.RUNNING]
            
            status_data.update({
                "completed_tasks": len(completed_tasks),
                "running_tasks": len(running_tasks),
                "pending_tasks": len(tasks) - len(completed_tasks) - len(running_tasks)
            })
        else:
            # 获取辩论状态
            debate = session_aggregate.debate
            if debate:
                consensus_level = asyncio.run(self.consensus_tracker.calculate_consensus(debate.debate_id))
                status_data.update({
                    "debate_id": debate.debate_id,
                    "debate_topic": debate.topic,
                    "debate_status": debate.status,
                    "consensus_level": consensus_level.value,
                    "participant_count": len(debate.participants),
                    "debate_message_count": len(debate.messages)
                })
        
        return status_data
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        # 尝试从Secretariat用例获取
        try:
            return await self.secretariat_use_case.get_task_progress(task_id)
        except ValueError:
            pass
        
        # 如果找不到，检查任务是否在本地存储中
        if task_id in self.tasks:
            task_aggregate = self.tasks[task_id]
            return {
                "task_id": task_id,
                "status": task_aggregate.task.status.value,
                "progress_percentage": 100 if task_aggregate.is_completed() else 0,
                "content": task_aggregate.task.content,
                "created_at": task_aggregate.task.created_at.isoformat()
            }
        
        raise ValueError(f"Task {task_id} not found")
    
    async def get_transparency_data(self, session_id: str) -> Dict[str, Any]:
        """获取透明度数据"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.sessions[session_id]
        entrance_type = session_aggregate.entrance_type
        
        transparency_data = {
            "session_id": session_id,
            "entrance_type": entrance_type.value,
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {
                "uptime": (datetime.now() - self.startup_time).total_seconds() if self.startup_time else 0,
                "active_sessions": len(self.sessions),
                "total_tasks": sum(len(s.tasks) for s in self.sessions.values())
            }
        }
        
        # 根据入口类型添加特定透明度数据
        if entrance_type == EntranceType.SECRETARIAT:
            # 获取任务透明度数据
            tasks = session_aggregate.tasks
            task_transparency = []
            
            for task in tasks:
                task_data = {
                    "task_id": task.task_id,
                    "content": task.content,
                    "status": task.status.value,
                    "intent_type": task.intent_type.value,
                    "created_at": task.created_at.isoformat(),
                    "execution_time": task.get_execution_time()
                }
                
                if task.status == TaskStatus.COMPLETED and task.result:
                    task_data["result_summary"] = task.result[:200] + "..." if len(task.result) > 200 else task.result
                
                task_transparency.append(task_data)
            
            transparency_data["tasks"] = task_transparency
        else:
            # 获取辩论透明度数据
            debate = session_aggregate.debate
            if debate:
                consensus_level = asyncio.run(self.consensus_tracker.calculate_consensus(debate.debate_id))
                key_arguments = asyncio.run(self.consensus_tracker.extract_key_arguments(debate.debate_id))
                
                transparency_data.update({
                    "debate_id": debate.debate_id,
                    "debate_topic": debate.topic,
                    "consensus_level": consensus_level.value,
                    "consensus_description": consensus_level.description(),
                    "participant_count": len(debate.participants),
                    "message_count": len(debate.messages),
                    "key_arguments": key_arguments[:5],  # 前5个关键论点
                    "participant_activities": await self.forum_use_case.get_participant_activities(session_id)
                })
        
        return transparency_data
    
    async def switch_entrance(self, session_id: str, target_entrance: str) -> Dict[str, Any]:
        """切换入口"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        try:
            target_entrance_type = EntranceType(target_entrance)
        except ValueError:
            raise ValueError(f"Invalid entrance type: {target_entrance}")
        
        # 执行入口切换
        new_session = await self.entrance_switching_use_case.switch_entrance(
            session_id, 
            target_entrance_type
        )
        
        # 记录切换事件
        await self._log_system_event("entrance_switched", {
            "old_session_id": session_id,
            "new_session_id": new_session.session_id,
            "target_entrance": target_entrance
        })
        
        return {
            "old_session_id": session_id,
            "new_session_id": new_session.session_id,
            "target_entrance": target_entrance,
            "status": "switched",
            "message": f"已切换到{target_entrance}入口"
        }
    
    async def get_entrance_suggestions(self, session_id: str) -> List[Dict[str, Any]]:
        """获取入口切换建议"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.sessions[session_id]
        user_id = session_aggregate.user_id
        current_entrance = session_aggregate.entrance_type
        
        # 获取切换建议
        suggestions = await self.entrance_switching_use_case.get_switching_suggestions(
            user_id, 
            current_entrance
        )
        
        return suggestions
    
    async def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        return {
            "service_status": "healthy" if self.is_initialized else "initializing",
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "uptime": (datetime.now() - self.startup_time).total_seconds() if self.startup_time else 0,
            "active_sessions": len(self.sessions),
            "total_users": len(self.users),
            "memory_usage": "45MB",  # 简化值
            "cpu_usage": "12%",      # 简化值
            "version": "1.0.0",
            "last_check": datetime.now().isoformat()
        }
    
    async def cleanup_expired_sessions(self, timeout_hours: int = 24):
        """清理过期会话"""
        expired_sessions = []
        
        for session_id, session_aggregate in self.sessions.items():
            if session_aggregate.session.is_expired(timeout_hours):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            # 完成会话
            session_aggregate = self.sessions[session_id]
            session_aggregate.complete()
            
            # 从活跃会话中移除
            if session_id in self.secretariat_use_case.active_sessions:
                del self.secretariat_use_case.active_sessions[session_id]
            
            if session_id in self.forum_use_case.active_sessions:
                del self.forum_use_case.active_sessions[session_id]
            
            del self.sessions[session_id]
        
        if expired_sessions:
            await self._log_system_event("sessions_cleaned", {
                "expired_sessions": expired_sessions,
                "timeout_hours": timeout_hours
            })
        
        return len(expired_sessions)
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计信息"""
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
        
        total_sessions = len(user_sessions)
        total_tasks = sum(len(s.tasks) for s in user_sessions)
        completed_tasks = sum(len(s.get_completed_tasks()) for s in user_sessions)
        
        # 计算平均会话持续时间
        if user_sessions:
            avg_duration = sum(s.get_duration() for s in user_sessions) / total_sessions
        else:
            avg_duration = 0
        
        # 入口类型分布
        entrance_distribution = {}
        for session in user_sessions:
            entrance = session.entrance_type.value
            entrance_distribution[entrance] = entrance_distribution.get(entrance, 0) + 1
        
        return {
            "user_id": user_id,
            "total_sessions": total_sessions,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "task_completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "average_session_duration": avg_duration,
            "entrance_distribution": entrance_distribution,
            "last_activity": max([s.session.updated_at for s in user_sessions]) if user_sessions else None
        }