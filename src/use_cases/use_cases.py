"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : use_cases.py
@Description:
    Use cases for the Personal Intelligence Hub.
    These define the application's business rules and orchestrate the flow of data
    between entities, value objects, and domain services.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from ..domain.aggregates import SessionAggregate, TaskAggregate
from ..domain.domain_services import (
    ConsensusTrackingService,
    EntranceSelectorService,
    UserInterventionService,
    WorkflowOrchestratorService,
)
from ..domain.entities import AgentMessage, Session, Task, User, UserMessage, Debate # Added Debate
from ..domain.value_objects import EntranceType, IntentType, MessageIntent, TaskPriority


class BaseUseCase(ABC):
    """基础用例类"""
    
    def __init__(self):
        self.entrance_selector = EntranceSelectorService()
        self.workflow_orchestrator = WorkflowOrchestratorService()
        self.user_intervention = UserInterventionService()
        self.consensus_tracker = ConsensusTrackingService()
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> dict[str, Any]:
        """执行用例"""
        pass


class SecretariatUseCase(BaseUseCase):
    """Secretariat用例 - 处理效率型用户的快速任务执行"""
    
    def __init__(self):
        super().__init__()
        self.active_sessions = {}
        self.active_tasks = {}
    
    async def create_session(self, user: User, entrance_type: EntranceType) -> Session:
        """创建Secretariat会话"""
        if entrance_type != EntranceType.SECRETARIAT:
            raise ValueError("SecretariatUseCase only supports SECRETARIAT entrance type")
        
        session_aggregate = SessionAggregate(
            user_id=user.user_id,
            entrance_type=entrance_type
        )
        
        session = session_aggregate.session
        self.active_sessions[session.session_id] = session_aggregate
        
        return session
    
    async def submit_task(self, session_id: str, task_request: dict[str, Any]) -> dict[str, Any]:
        """提交任务"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.active_sessions[session_id]
        
        # 验证任务请求
        content = task_request.get("content", "").strip()
        if not content:
            raise ValueError("Task content cannot be empty")
        
        intent_type = IntentType(task_request.get("intent_type", "analysis"))
        priority = TaskPriority(task_request.get("priority", "normal"))
        
        # 创建任务聚合
        task_aggregate = TaskAggregate()
        task_aggregate.set_session(session_id)
        task_aggregate.set_content(content, intent_type)
        task_aggregate.set_priority(priority)
        
        # 添加任务到会话
        task = task_aggregate.task
        session_aggregate.add_task(task)
        
        # 保存任务聚合
        self.active_tasks[task.task_id] = task_aggregate
        
        # 规划工作流
        intent = {
            "type": intent_type.value,
            "content": content,
            "complexity": self._analyze_task_complexity(content),
            "context": task_request.get("context", {})
        }
        
        workflow_plan = await self.workflow_orchestrator.plan_workflow(intent)
        
        # 启动工作流
        await self.workflow_orchestrator.start_workflow(
            workflow_plan["workflow_id"], 
            workflow_plan
        )
        
        # 异步执行任务
        asyncio.create_task(self._execute_task_async(task_aggregate, workflow_plan))
        
        return {
            "status": "success",
            "task_id": task.task_id,
            "workflow_id": workflow_plan["workflow_id"],
            "estimated_duration": workflow_plan["estimated_duration"],
            "session_id": session_id
        }
    
    async def _execute_task_async(self, task_aggregate: TaskAggregate, workflow_plan: dict[str, Any]):
        """异步执行任务"""
        try:
            task = task_aggregate.task
            
            # 开始执行
            task_aggregate.start_execution()
            
            # 执行工作流步骤
            for step in workflow_plan["steps"]:
                step_result = await self.workflow_orchestrator.execute_step(
                    workflow_plan["workflow_id"], 
                    step["step_id"]
                )
                task_aggregate.record_step(step["step_id"], step_result)
            
            # 生成最终结果
            final_result = await self._generate_task_result(task, workflow_plan)
            
            # 完成任务
            task_aggregate.complete_execution(final_result)
            
        except Exception as e:
            task_aggregate.fail_execution(str(e))
    
    async def _generate_task_result(self, task: Task, workflow_plan: dict[str, Any]) -> str:
        """生成任务结果"""
        # 简化的结果生成逻辑
        intent_type = task.intent_type
        content = task.content
        
        if intent_type == IntentType.ANALYSIS:
            return f"关于'{content}'的分析报告已完成。通过{len(workflow_plan['steps'])}个步骤的深度分析，得出了全面的结论。"
        elif intent_type == IntentType.EVALUATION:
            return f"对'{content}'的评估已完成。基于多维度分析，提供了详细的评估结果和建议。"
        elif intent_type == IntentType.SUMMARIZATION:
            return f"'{content}'的总结报告已完成。提取了关键信息并进行了结构化整理。"
        else:
            return f"'{content}'的任务已完成。"
    
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
    
    async def get_task_progress(self, task_id: str) -> dict[str, Any]:
        """获取任务进度"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task_aggregate = self.active_tasks[task_id]
        
        # 查找相关工作流
        workflow_id = None
        for session_aggregate in self.active_sessions.values():
            if task_aggregate.task in session_aggregate.tasks:
                # 这里简化处理，实际应该从任务元数据中获取workflow_id
                workflow_id = f"workflow_{task_id}"
                break
        
        if workflow_id:
            try:
                progress = self.workflow_orchestrator.get_workflow_progress(workflow_id)
                return {
                    "task_id": task_id,
                    "status": task_aggregate.task.status.value,
                    "progress_percentage": progress["progress_percentage"],
                    "current_step": progress["current_step"],
                    "total_steps": progress["total_steps"],
                    "estimated_time_remaining": progress["estimated_time_remaining"],
                    "step_results": progress["step_results"]
                }
            except ValueError:
                pass
        
        # 如果没有工作流信息，返回基本状态
        return {
            "task_id": task_id,
            "status": task_aggregate.task.status.value,
            "progress_percentage": 100 if task_aggregate.is_completed() else 0,
            "current_step": 0,
            "total_steps": 1,
            "estimated_time_remaining": 0,
            "step_results": {}
        }
    
    async def get_task_result(self, task_id: str) -> dict[str, Any]:
        """获取任务结果"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task_aggregate = self.active_tasks[task_id]
        task = task_aggregate.task
        
        if not task_aggregate.is_completed():
            raise ValueError(f"Task {task_id} is not completed")
        
        return {
            "task_id": task_id,
            "status": task.status.value,
            "content": task.result,
            "execution_time": task_aggregate.get_execution_time(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "execution_history": task_aggregate.get_execution_history()
        }
    
    async def get_transparency_data(self, task_id: str) -> dict[str, Any]:
        """获取透明度数据"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task_aggregate = self.active_tasks[task_id]
        
        return {
            "task_id": task_id,
            "workflow_steps": task_aggregate.get_execution_steps(),
            "execution_time": task_aggregate.get_execution_time(),
            "agent_activities": self._extract_agent_activities(task_aggregate),
            "resource_usage": {
                "total_tokens": 12500,  # 简化值
                "execution_time": task_aggregate.get_execution_time() or 0,
                "memory_usage": "45MB"  # 简化值
            }
        }
    
    def _extract_agent_activities(self, task_aggregate: TaskAggregate) -> list[dict[str, Any]]:
        """提取Agent活动"""
        activities = []
        
        for step in task_aggregate.get_execution_steps():
            step_data = step.get("data", {})
            if "output" in step_data:
                activities.append({
                    "agent": "system",
                    "activity": step_data.get("output", ""),
                    "duration": step.get("execution_time", 0),
                    "contribution": "完成了工作流步骤"
                })
        
        return activities
    
    async def get_session_tasks(self, session_id: str) -> list[dict[str, Any]]:
        """获取会话的任务列表"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.active_sessions[session_id]
        tasks = session_aggregate.tasks
        
        return [
            {
                "task_id": task.task_id,
                "content": task.content,
                "intent_type": task.intent_type.value,
                "status": task.status.value,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in tasks
        ]
    
    async def get_system_status(self) -> dict[str, Any]:
        """获取系统状态"""
        return {
            "status": "operational",
            "active_sessions": len(self.active_sessions),
            "active_tasks": len(self.active_tasks),
            "total_sessions_created": len(self.active_sessions),
            "total_tasks_completed": len([t for t in self.active_tasks.values() if t.is_completed()]),
            "timestamp": datetime.now().isoformat()
        }


class ForumUseCase(BaseUseCase):
    """Forum用例 - 处理参与型用户的交互式讨论"""
    
    def __init__(self):
        super().__init__()
        self.active_sessions = {}
        self.active_debates = {}
    
    async def create_forum_session(self, user: User, session_config: dict[str, Any]) -> Session:
        """创建Forum会话"""
        topic = session_config.get("topic", "")
        if not topic:
            raise ValueError("Forum session topic cannot be empty")
        
        session_aggregate = SessionAggregate(
            user_id=user.user_id,
            entrance_type=EntranceType.FORUM
        )
        
        # 创建辩论
        participants = session_config.get("participants", ["expert_1", "expert_2"])
        debate = session_aggregate.create_debate(topic, participants)
        
        session = session_aggregate.session
        self.active_sessions[session.session_id] = session_aggregate
        self.active_debates[debate.debate_id] = debate
        
        # 启动辩论跟踪
        self.consensus_tracker.active_debates[debate.debate_id] = {
            "messages": [],
            "participants": participants,
            "topic": topic
        }
        
        return session
    
    async def start_debate(self, session_id: str) -> dict[str, Any]:
        """启动辩论"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.active_sessions[session_id]
        debate = session_aggregate.debate
        
        if not debate:
            raise ValueError(f"No debate found for session {session_id}")
        
        # 添加初始Agent消息
        initial_messages = [
            {
                "sender": "facilitator",
                "content": f"欢迎来到关于'{debate.topic}'的讨论。让我们从不同角度来探讨这个话题。",
                "timestamp": datetime.now()
            },
            {
                "sender": "expert_1",
                "content": f"从专业角度来看，'{debate.topic}'涉及多个重要方面需要考虑。",
                "timestamp": datetime.now()
            }
        ]
        
        for message_data in initial_messages:
            message = AgentMessage(
                session_id=session_id,
                content=message_data["content"],
                sender=message_data["sender"],
                agent_role="facilitator" if message_data["sender"] == "facilitator" else "expert",
                timestamp=message_data["timestamp"]
            )
            debate.add_message(message)
            await self.consensus_tracker.add_message(debate.debate_id, message_data)
        
        return {
            "status": "started",
            "debate_id": debate.debate_id,
            "topic": debate.topic,
            "participants": debate.participants,
            "initial_messages": len(initial_messages)
        }
    
    async def handle_user_intervention(self, session_id: str, intervention_data: dict[str, Any]) -> dict[str, Any]:
        """处理用户干预"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.active_sessions[session_id]
        debate = session_aggregate.debate
        
        if not debate:
            raise ValueError(f"No debate found for session {session_id}")
        
        # 获取用户输入
        message_data = intervention_data.get("message", {})
        raw_input = message_data.get("content", "")
        intent = message_data.get("intent", "comment")
        
        if not raw_input:
            raise ValueError("User intervention content cannot be empty")
        
        # 优化用户输入
        optimized_input = await self.user_intervention.optimize_input(
            raw_input, intent, {"debate_id": debate.debate_id}
        )
        
        # 创建用户消息
        user_message = UserMessage(
            session_id=session_id,
            content=optimized_input,
            sender=f"user_{session_aggregate.user_id}",
            intent=MessageIntent(intent)
        )
        
        # 添加到辩论
        debate.add_message(user_message)
        session_aggregate.add_message(user_message)
        
        # 添加到共识跟踪
        await self.consensus_tracker.add_message(debate.debate_id, {
            "sender": user_message.sender,
            "content": optimized_input,
            "timestamp": user_message.timestamp
        })
        
        # 集成干预
        integration_result = await self.user_intervention.integrate_intervention(
            debate.debate_id, intervention_data
        )
        
        # 触发Agent响应
        asyncio.create_task(self._generate_agent_responses(debate, user_message))
        
        return {
            "status": "integrated",
            "message_id": user_message.message_id,
            "optimized_input": optimized_input,
            "integration_result": integration_result,
            "timestamp": user_message.timestamp.isoformat()
        }
    
    async def _generate_agent_responses(self, debate: Debate, user_message: UserMessage):
        """生成Agent响应"""
        try:
            # 模拟Agent思考和响应
            await asyncio.sleep(1.0)  # 模拟思考时间
            
            # 生成相关Agent响应
            response_templates = [
                {
                    "sender": "expert_1",
                    "role": "domain_expert",
                    "content": f"感谢您的观点。从专业角度来看，{user_message.content}确实是一个重要的考虑因素。"
                },
                {
                    "sender": "expert_2", 
                    "role": "critic",
                    "content": f"我理解您的想法，不过我们也需要考虑{user_message.content}可能带来的挑战。"
                }
            ]
            
            for template in response_templates:
                agent_message = AgentMessage(
                    session_id=debate.session_id,
                    content=template["content"],
                    sender=template["sender"],
                    agent_role=template["role"],
                    confidence=0.85
                )
                
                debate.add_message(agent_message)
                
                # 添加到共识跟踪
                await self.consensus_tracker.add_agent_opinion(
                    debate.debate_id,
                    template["sender"],
                    template["content"],
                    0.85
                )
                
        except Exception as e:
            # 记录错误但不影响主流程
            error_message = SystemMessage(
                session_id=debate.session_id,
                content=f"生成Agent响应时出错: {str(e)}",
                system_event="agent_response_error",
                severity="warning"
            )
            debate.add_message(error_message)
    
    async def get_debate_context(self, session_id: str) -> dict[str, Any]:
        """获取辩论上下文"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.active_sessions[session_id]
        debate = session_aggregate.debate
        
        if not debate:
            raise ValueError(f"No debate found for session {session_id}")
        
        # 获取共识水平
        consensus_level = await self.consensus_tracker.calculate_consensus(debate.debate_id)
        
        # 获取关键论点
        key_arguments = await self.consensus_tracker.extract_key_arguments(debate.debate_id)
        
        return {
            "session_id": session_id,
            "debate_id": debate.debate_id,
            "topic": debate.topic,
            "status": debate.status,
            "consensus_level": consensus_level.value,
            "consensus_description": consensus_level.description(),
            "active_agents": debate.participants,
            "key_arguments": key_arguments,
            "message_count": debate.get_message_count(),
            "participant_count": debate.get_participant_count(),
            "duration": debate.get_duration(),
            "last_activity": debate.updated_at.isoformat()
        }
    
    async def get_debate_messages(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """获取辩论消息"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.active_sessions[session_id]
        debate = session_aggregate.debate
        
        if not debate:
            return []
        
        # 获取最近的N条消息
        recent_messages = sorted(debate.messages, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        return [
            {
                "message_id": msg.message_id,
                "sender": msg.sender,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "type": "user" if msg.is_user_message() else "agent" if msg.is_agent_message() else "system",
                "agent_role": getattr(msg, 'agent_role', None) if hasattr(msg, 'agent_role') else None,
                "confidence": getattr(msg, 'confidence', None) if hasattr(msg, 'confidence') else None
            }
            for msg in reversed(recent_messages)  # 按时间正序返回
        ]
    
    async def control_debate(self, session_id: str, action: str) -> dict[str, Any]:
        """控制辩论"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.active_sessions[session_id]
        debate = session_aggregate.debate
        
        if not debate:
            raise ValueError(f"No debate found for session {session_id}")
        
        if action == "pause":
            debate.pause()
            session_aggregate.pause()
            status = "paused"
        elif action == "resume":
            debate.resume()
            session_aggregate.resume()
            status = "resumed"
        elif action == "complete":
            debate.complete()
            session_aggregate.complete()
            status = "completed"
        else:
            raise ValueError(f"Unknown action: {action}")
        
        return {
            "status": "success",
            "action": action,
            "debate_status": debate.status,
            "session_status": session_aggregate.session.status.value,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_participant_activities(self, session_id: str) -> dict[str, Any]:
        """获取参与者活动"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_aggregate = self.active_sessions[session_id]
        debate = session_aggregate.debate
        
        if not debate:
            return {}
        
        activities = {}
        for participant in debate.participants:
            participant_messages = [msg for msg in debate.messages if msg.sender == participant]
            activities[participant] = {
                "message_count": len(participant_messages),
                "last_activity": max([msg.timestamp for msg in participant_messages]) if participant_messages else None,
                "role": getattr(next((msg for msg in participant_messages if hasattr(msg, 'agent_role')), None), 'agent_role', 'participant')
            }
        
        return activities


class EntranceSwitchingUseCase(BaseUseCase):
    """入口切换用例 - 处理用户在不同入口间的切换"""
    
    def __init__(self):
        super().__init__()
        self.session_context_store = {}
    
    async def switch_entrance(self, current_session_id: str, target_entrance: EntranceType) -> Session:
        """切换入口"""
        # 查找当前会话
        current_session = None
        current_aggregate = None
        
        # 这里简化处理，实际应该有一个会话管理器来查找会话
        # 暂时假设可以从某个地方获取当前会话
        
        if not current_session:
            raise ValueError(f"Current session {current_session_id} not found")
        
        # 保存当前会话的上下文
        context_data = await self._extract_session_context(current_session_id)
        self.session_context_store[current_session_id] = context_data
        
        # 创建新会话
        new_session_aggregate = SessionAggregate(
            user_id=current_session.user_id,
            entrance_type=target_entrance
        )
        
        # 恢复上下文
        await self._restore_session_context(new_session_aggregate, context_data)
        
        return new_session_aggregate.session
    
    async def _extract_session_context(self, session_id: str) -> dict[str, Any]:
        """提取会话上下文"""
        # 简化的上下文提取
        return {
            "user_preferences": {
                "language": "zh-CN",
                "theme": "light",
                "detail_level": "comprehensive"
            },
            "recent_topics": ["AI技术应用", "技术趋势分析"],
            "task_history": ["task_1", "task_2"],
            "interaction_patterns": {
                "preferred_response_length": "medium",
                "interaction_frequency": "high"
            }
        }
    
    async def _restore_session_context(self, session_aggregate: SessionAggregate, context_data: dict[str, Any]):
        """恢复会话上下文"""
        # 将上下文数据添加到会话元数据中
        for key, value in context_data.items():
            session_aggregate.update_metadata(f"context_{key}", value)
    
    async def get_session_context(self, session_id: str) -> dict[str, Any]:
        """获取会话上下文"""
        return self.session_context_store.get(session_id, {})
    
    async def get_switching_suggestions(self, user_id: str, current_entrance: EntranceType) -> list[dict[str, Any]]:
        """获取切换建议"""
        suggestions = []
        
        # 基于用户行为模式生成建议
        user_behavior = self.entrance_selector.get_user_preferences(user_id)
        
        # 分析当前会话的特征
        current_features = {
            "duration": 300,  # 简化值
            "interaction_count": 5,
            "task_complexity": 0.6
        }
        
        # 生成切换建议
        if current_entrance == EntranceType.SECRETARIAT:
            if current_features["task_complexity"] > 0.7:
                suggestions.append({
                    "target_entrance": EntranceType.FORUM,
                    "reason": "当前任务较为复杂，建议切换到Forum进行深入讨论",
                    "confidence": 0.8
                })
        else:
            if current_features["duration"] > 600 and current_features["interaction_count"] < 3:
                suggestions.append({
                    "target_entrance": EntranceType.SECRETARIAT,
                    "reason": "长时间低频交互，建议切换到Secretariat提高效率",
                    "confidence": 0.7
                })
        
        return suggestions