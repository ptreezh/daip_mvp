#!/usr/bin/env python3
"""@Time    : 2025-08-06 10:45:00
@Author  : DAIP-LIVE Team
@File    : forum_service.py
@Description:
    Forum模式后端服务 - 管理Forum会话、用户干预和多智能体协作
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ..api.dependencies import get_app_state
from ..core.exceptions import DebateOrchestrationError, ForumServiceError

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class ForumSession:
    """Forum会话数据类"""
    session_id: str
    topic: str
    start_time: datetime
    status: str = "active"  # active, paused, completed
    participants: list[str] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    active_agents: list[str] = field(default_factory=list)
    consensus_level: float = 0.0
    key_arguments: list[dict[str, Any]] = field(default_factory=list)
    user_interventions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ForumService:
    """Forum服务 - 管理Forum会话和多智能体协作"""
    
    def __init__(self):
        self.active_sessions: dict[str, ForumSession] = {}
        self.debate_orchestrator = DebateOrchestrator()
        self.user_intervention_manager = UserInterventionManager()
        self.consensus_tracker = ConsensusTracker()
        
        # 获取核心服务（延迟加载）
        self.multi_agent_service = None
        self.role_manager = None
        self.memory_service = None
        
        logger.info("Forum服务初始化完成")
    
    async def start_forum_session(self, topic: str, user_id: str = "default_user") -> ForumSession:
        """启动Forum会话"""
        try:
            session_id = f"forum_{uuid.uuid4().hex[:8]}"
            
            # 创建会话
            session = ForumSession(
                session_id=session_id,
                topic=topic,
                start_time=datetime.now(),
                metadata={
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat()
                }
            )
            
            self.active_sessions[session_id] = session
            
            # 智能选择Agent组合
            selected_agents = await self._select_agents_for_topic(topic)
            session.active_agents = selected_agents
            
            # 启动辩论
            await self.debate_orchestrator.start_debate(
                session_id, topic, selected_agents
            )
            
            logger.info(f"Forum会话已启动: {session_id}, 话题: {topic}")
            return session
            
        except Exception as e:
            logger.error(f"启动Forum会话失败: {e}")
            raise ForumServiceError(f"Failed to start forum session: {str(e)}")
    
    async def handle_user_intervention(self, session_id: str, user_message: dict[str, Any]) -> dict[str, Any]:
        """处理用户干预"""
        try:
            if session_id not in self.active_sessions:
                raise ForumServiceError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            
            # 优化用户输入
            optimized_input = await self.user_intervention_manager.optimize_input(
                user_message["content"],
                user_message["intent"],
                session.topic
            )
            
            # 记录用户干预
            intervention_record = {
                "original_input": user_message["content"],
                "optimized_input": optimized_input,
                "intent": user_message["intent"],
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id
            }
            session.user_interventions.append(intervention_record)
            
            # 集成到辩论中
            await self.debate_orchestrator.integrate_user_intervention(
                session_id, optimized_input
            )
            
            # 更新共识跟踪
            await self.consensus_tracker.update_with_intervention(
                session_id, intervention_record
            )
            
            logger.info(f"用户干预已处理: {session_id}")
            
            return {
                "status": "integrated",
                "optimized_input": optimized_input,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"处理用户干预失败: {e}")
            raise ForumServiceError(f"Failed to handle user intervention: {str(e)}")
    
    async def get_session_context(self, session_id: str) -> Optional[dict[str, Any]]:
        """获取会话上下文"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            
            # 获取实时共识度
            consensus_level = await self.consensus_tracker.get_consensus_level(session_id)
            
            # 获取关键论点
            key_arguments = await self.consensus_tracker.get_key_arguments(session_id)
            
            return {
                "session_id": session_id,
                "topic": session.topic,
                "status": session.status,
                "consensus_level": consensus_level,
                "active_agents": session.active_agents,
                "key_arguments": key_arguments,
                "message_count": len(session.messages),
                "user_intervention_count": len(session.user_interventions),
                "start_time": session.start_time.isoformat(),
                "duration": (datetime.now() - session.start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"获取会话上下文失败: {e}")
            return None
    
    async def pause_session(self, session_id: str) -> bool:
        """暂停会话"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            session.status = "paused"
            
            await self.debate_orchestrator.pause_debate(session_id)
            
            logger.info(f"Forum会话已暂停: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"暂停会话失败: {e}")
            return False
    
    async def resume_session(self, session_id: str) -> bool:
        """恢复会话"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            session.status = "active"
            
            await self.debate_orchestrator.resume_debate(session_id)
            
            logger.info(f"Forum会话已恢复: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"恢复会话失败: {e}")
            return False
    
    async def end_session(self, session_id: str) -> Optional[dict[str, Any]]:
        """结束会话"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            session.status = "completed"
            
            # 获取最终共识结果
            final_consensus = await self.consensus_tracker.get_final_consensus(session_id)
            
            # 结束辩论
            await self.debate_orchestrator.end_debate(session_id)
            
            # 保存到记忆服务
            await self._save_session_to_memory(session, final_consensus)
            
            # 从活跃会话中移除
            final_session = self.active_sessions.pop(session_id)
            
            logger.info(f"Forum会话已结束: {session_id}")
            return {
                "session_id": session_id,
                "topic": final_session.topic,
                "duration": (datetime.now() - final_session.start_time).total_seconds(),
                "total_messages": len(final_session.messages),
                "user_interventions": len(final_session.user_interventions),
                "final_consensus": final_consensus
            }
            
        except Exception as e:
            logger.error(f"结束会话失败: {e}")
            return None
    
    async def _select_agents_for_topic(self, topic: str) -> list[str]:
        """为话题选择合适的Agent组合"""
        try:
            # 延迟加载角色管理器
            if self.role_manager is None:
                app_state = get_app_state()
                # Check if role_manager exists as a property
                if hasattr(app_state, 'role_manager'):
                    self.role_manager = app_state.role_manager
                else:
                    # Fallback to simple role selection
                    return ["technical_expert", "business_analyst", "research_scientist"]
            
            # 使用角色管理器智能选择
            if hasattr(self.role_manager, 'select_roles_for_topic'):
                selected_roles = await self.role_manager.select_roles_for_topic(topic, max_roles=5)
                return [role["id"] for role in selected_roles]
            else:
                # Fallback to default roles
                return ["technical_expert", "business_analyst", "research_scientist"]
            
        except Exception as e:
            logger.error(f"选择Agent失败: {e}")
            # 回退到默认角色
            return ["technical_expert", "business_analyst", "research_scientist"]
    
    async def _save_session_to_memory(self, session: ForumSession, consensus_result: dict[str, Any]):
        """保存会话到记忆服务"""
        try:
            # 延迟加载记忆服务
            if self.memory_service is None:
                app_state = get_app_state()
                self.memory_service = app_state.memory_service
            
            memory_data = {
                "type": "forum_session",
                "session_id": session.session_id,
                "topic": session.topic,
                "duration": (datetime.now() - session.start_time).total_seconds(),
                "total_messages": len(session.messages),
                "user_interventions": len(session.user_interventions),
                "final_consensus": consensus_result,
                "created_at": session.start_time.isoformat(),
                "completed_at": datetime.now().isoformat()
            }
            
            await self.memory_service.store_memory(memory_data)
            
        except Exception as e:
            logger.error(f"保存会话到记忆失败: {e}")
    
    def get_active_sessions(self) -> list[dict[str, Any]]:
        """获取所有活跃会话"""
        return [
            {
                "session_id": session.session_id,
                "topic": session.topic,
                "status": session.status,
                "start_time": session.start_time.isoformat(),
                "active_agents": session.active_agents,
                "message_count": len(session.messages)
            }
            for session in self.active_sessions.values()
        ]
    
    def get_session_statistics(self) -> dict[str, Any]:
        """获取Forum服务统计信息"""
        total_sessions = len(self.active_sessions)
        active_sessions = len([s for s in self.active_sessions.values() if s.status == "active"])
        total_messages = sum(len(s.messages) for s in self.active_sessions.values())
        total_interventions = sum(len(s.user_interventions) for s in self.active_sessions.values())
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "total_interventions": total_interventions,
            "average_consensus": sum(s.consensus_level for s in self.active_sessions.values()) / max(total_sessions, 1)
        }


class DebateOrchestrator:
    """辩论编排器 - 管理多智能体辩论过程"""
    
    def __init__(self):
        self.active_debates: dict[str, dict[str, Any]] = {}
        self.multi_agent_service = None
        
        logger.info("辩论编排器初始化完成")
    
    async def start_debate(self, session_id: str, topic: str, agents: list[str]):
        """启动辩论"""
        try:
            debate_config = {
                "session_id": session_id,
                "topic": topic,
                "agents": agents,
                "start_time": datetime.now(),
                "status": "active",
                "messages": [],
                "current_round": 0
            }
            
            self.active_debates[session_id] = debate_config
            
            # 延迟加载多智能体协作系统
            if self.multi_agent_service is None:
                app_state = get_app_state()
                self.multi_agent_service = app_state.virtual_team_service
            
            # 启动多Agent协作
            # Check if the service has the required method
            if hasattr(self.multi_agent_service, 'start_collaboration'):
                await self.multi_agent_service.start_collaboration(
                    session_id=session_id,
                    agents=agents,
                    topic=topic,
                    collaboration_type="forum_debate"
                )
            else:
                # Mock the collaboration for testing
                logger.info(f"Mocking collaboration start for session {session_id}")
            
            logger.info(f"辩论已启动: {session_id}")
            
        except Exception as e:
            logger.error(f"启动辩论失败: {e}")
            raise DebateOrchestrationError(f"Failed to start debate: {str(e)}")
    
    async def integrate_user_intervention(self, session_id: str, user_input: str):
        """集成用户干预"""
        try:
            if session_id not in self.active_debates:
                return
            
            debate = self.active_debates[session_id]
            
            # 添加用户消息到辩论
            user_message = {
                "type": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat(),
                "sender": "user"
            }
            
            debate["messages"].append(user_message)
            
            # 调整协作方向
            if self.multi_agent_service and hasattr(self.multi_agent_service, 'adjust_collaboration'):
                await self.multi_agent_service.adjust_collaboration(
                    session_id=session_id,
                    adjustment={"type": "user_intervention", "content": user_input}
                )
            else:
                logger.info(f"Mocking collaboration adjustment for session {session_id}")
            
            logger.info(f"用户干预已集成到辩论: {session_id}")
            
        except Exception as e:
            logger.error(f"集成用户干预失败: {e}")
    
    async def pause_debate(self, session_id: str):
        """暂停辩论"""
        try:
            if session_id in self.active_debates:
                self.active_debates[session_id]["status"] = "paused"
                if self.multi_agent_service and hasattr(self.multi_agent_service, 'pause_collaboration'):
                    await self.multi_agent_service.pause_collaboration(session_id)
                else:
                    logger.info(f"Mocking collaboration pause for session {session_id}")
                
        except Exception as e:
            logger.error(f"暂停辩论失败: {e}")
    
    async def resume_debate(self, session_id: str):
        """恢复辩论"""
        try:
            if session_id in self.active_debates:
                self.active_debates[session_id]["status"] = "active"
                if self.multi_agent_service and hasattr(self.multi_agent_service, 'resume_collaboration'):
                    await self.multi_agent_service.resume_collaboration(session_id)
                else:
                    logger.info(f"Mocking collaboration resume for session {session_id}")
                
        except Exception as e:
            logger.error(f"恢复辩论失败: {e}")
    
    async def end_debate(self, session_id: str):
        """结束辩论"""
        try:
            if session_id in self.active_debates:
                debate = self.active_debates.pop(session_id)
                if self.multi_agent_service and hasattr(self.multi_agent_service, 'end_collaboration'):
                    await self.multi_agent_service.end_collaboration(session_id)
                else:
                    logger.info(f"Mocking collaboration end for session {session_id}")
                
        except Exception as e:
            logger.error(f"结束辩论失败: {e}")
    
    def get_debate_status(self, session_id: str) -> Optional[dict[str, Any]]:
        """获取辩论状态"""
        if session_id not in self.active_debates:
            return None
        
        debate = self.active_debates[session_id]
        return {
            "session_id": session_id,
            "status": debate["status"],
            "topic": debate["topic"],
            "active_agents": debate["agents"],
            "current_round": debate["current_round"],
            "message_count": len(debate["messages"])
        }


class UserInterventionManager:
    """用户干预管理器 - 优化和集成用户输入"""
    
    def __init__(self):
        self.input_optimizer = InputOptimizer()
        
        logger.info("用户干预管理器初始化完成")
    
    async def optimize_input(self, user_input: str, intent: str, topic: str) -> str:
        """优化用户输入"""
        try:
            optimization_config = {
                "intent": intent,
                "topic": topic,
                "context": "forum_debate",
                "style": "collaborative"
            }
            
            optimized_result = await self.input_optimizer.optimize(
                user_input, optimization_config
            )
            
            return optimized_result["optimized_text"]
            
        except Exception as e:
            logger.error(f"优化用户输入失败: {e}")
            return user_input  # 回退到原始输入


class InputOptimizer:
    """输入优化器 - 优化用户输入以提高协作效果"""
    
    async def optimize(self, user_input: str, config: dict[str, Any]) -> dict[str, Any]:
        """优化用户输入"""
        try:
            # 基于意图和上下文优化输入
            intent = config.get("intent", "comment")
            topic = config.get("topic", "")
            
            optimized_text = user_input
            
            # 根据意图类型应用不同的优化策略
            if intent == "question":
                optimized_text = self._optimize_question(user_input, topic)
            elif intent == "suggestion":
                optimized_text = self._optimize_suggestion(user_input, topic)
            elif intent == "correction":
                optimized_text = self._optimize_correction(user_input, topic)
            else:  # comment
                optimized_text = self._optimize_comment(user_input, topic)
            
            return {
                "optimized_text": optimized_text,
                "original_input": user_input,
                "optimization_type": intent,
                "confidence": 0.85  # 优化置信度
            }
            
        except Exception as e:
            logger.error(f"输入优化失败: {e}")
            return {"optimized_text": user_input, "original_input": user_input}
    
    def _optimize_question(self, question: str, topic: str) -> str:
        """优化问题"""
        # 确保问题清晰且与话题相关
        if not question.endswith("?"):
            question += "?"
        
        # 添加上下文引导
        if topic and topic.lower() not in question.lower():
            return f"关于{topic}，{question}"
        
        return question
    
    def _optimize_suggestion(self, suggestion: str, topic: str) -> str:
        """优化建议"""
        # 确保建议具有建设性
        constructive_phrases = [
            "我建议",
            "或许可以考虑",
            "另一个角度是",
            "补充一点"
        ]
        
        # 如果建议太简短，添加引导
        if len(suggestion) < 10:
            return f"我建议{suggestion}"
        
        return suggestion
    
    def _optimize_correction(self, correction: str, topic: str) -> str:
        """优化纠正"""
        # 确保纠正语气友好且准确
        friendly_phrases = [
            "需要纠正的是",
            "准确来说",
            "更准确的表达是"
        ]
        
        # 确保纠正不是以冲突方式表达
        if correction.startswith("不对") or correction.startswith("错误"):
            return f"需要纠正的是：{correction}"
        
        return correction
    
    def _optimize_comment(self, comment: str, topic: str) -> str:
        """优化评论"""
        # 确保评论有实质内容
        if len(comment) < 5:
            return comment
        
        return comment


class ConsensusTracker:
    """共识跟踪器 - 实时跟踪和计算共识"""
    
    def __init__(self):
        self.consensus_data: dict[str, dict[str, Any]] = {}
        
        logger.info("共识跟踪器初始化完成")
    
    async def update_with_message(self, session_id: str, message: dict[str, Any]):
        """根据消息更新共识"""
        try:
            if session_id not in self.consensus_data:
                self.consensus_data[session_id] = {
                    "messages": [],
                    "consensus_level": 0.0,
                    "key_arguments": [],
                    "agreement_points": [],
                    "disagreement_points": []
                }
            
            data = self.consensus_data[session_id]
            data["messages"].append(message)
            
            # 重新计算共识度
            await self._recalculate_consensus(session_id)
            
        except Exception as e:
            logger.error(f"更新共识失败: {e}")
    
    async def update_with_intervention(self, session_id: str, intervention: dict[str, Any]):
        """根据用户干预更新共识"""
        try:
            if session_id not in self.consensus_data:
                return
            
            # 用户干预可能影响共识，需要重新计算
            await self._recalculate_consensus(session_id)
            
        except Exception as e:
            logger.error(f"更新共识(用户干预)失败: {e}")
    
    async def get_consensus_level(self, session_id: str) -> float:
        """获取共识度"""
        if session_id not in self.consensus_data:
            return 0.0
        
        return self.consensus_data[session_id]["consensus_level"]
    
    async def get_key_arguments(self, session_id: str) -> list[dict[str, Any]]:
        """获取关键论点"""
        if session_id not in self.consensus_data:
            return []
        
        return self.consensus_data[session_id]["key_arguments"]
    
    async def get_final_consensus(self, session_id: str) -> dict[str, Any]:
        """获取最终共识结果"""
        if session_id not in self.consensus_data:
            return {"consensus_level": 0.0, "summary": "No consensus data"}
        
        data = self.consensus_data[session_id]
        
        return {
            "consensus_level": data["consensus_level"],
            "summary": await self._generate_consensus_summary(session_id),
            "key_arguments": data["key_arguments"],
            "agreement_points": data["agreement_points"],
            "disagreement_points": data["disagreement_points"]
        }
    
    async def _recalculate_consensus(self, session_id: str):
        """重新计算共识度"""
        try:
            if session_id not in self.consensus_data:
                return
            
            data = self.consensus_data[session_id]
            messages = data["messages"]
            
            if not messages:
                data["consensus_level"] = 0.0
                return
            
            # 简化的共识计算算法
            # 实际实现中可以使用更复杂的NLP和共识算法
            total_messages = len(messages)
            agreement_count = sum(1 for msg in messages if self._is_agreement_message(msg))
            
            # 基础共识度计算
            base_consensus = agreement_count / max(total_messages, 1)
            
            # 考虑用户干预的影响
            user_interventions = [msg for msg in messages if msg.get("type") == "user"]
            intervention_factor = min(len(user_interventions) * 0.1, 0.3)  # 最多增加30%
            
            final_consensus = min(base_consensus + intervention_factor, 1.0)
            data["consensus_level"] = final_consensus
            
            # 更新关键论点
            await self._update_key_arguments(session_id)
            
        except Exception as e:
            logger.error(f"重新计算共识失败: {e}")
    
    def _is_agreement_message(self, message: dict[str, Any]) -> bool:
        """判断是否为同意消息"""
        content = message.get("content", "").lower()
        
        agreement_keywords = ["同意", "认同", "支持", "正确", "是的", "对", "确实"]
        return any(keyword in content for keyword in agreement_keywords)
    
    async def _update_key_arguments(self, session_id: str):
        """更新关键论点"""
        try:
            if session_id not in self.consensus_data:
                return
            
            data = self.consensus_data[session_id]
            messages = data["messages"]
            
            # 简化的关键论点提取
            # 实际实现中可以使用更复杂的文本分析
            key_arguments = []
            
            for msg in messages[-10:]:  # 分析最近10条消息
                content = msg.get("content", "")
                if len(content) > 20:  # 只考虑较长的消息
                    key_arguments.append({
                        "content": content[:100] + "..." if len(content) > 100 else content,
                        "sender": msg.get("sender", "unknown"),
                        "timestamp": msg.get("timestamp", ""),
                        "importance": 0.8  # 简化的重要性评分
                    })
            
            data["key_arguments"] = key_arguments[-5:]  # 保留最近5个关键论点
            
        except Exception as e:
            logger.error(f"更新关键论点失败: {e}")
    
    async def _generate_consensus_summary(self, session_id: str) -> str:
        """生成共识总结"""
        try:
            if session_id not in self.consensus_data:
                return "No consensus data available"
            
            data = self.consensus_data[session_id]
            consensus_level = data["consensus_level"]
            
            if consensus_level >= 0.8:
                return "高度共识：参与者对该话题有很强的一致性"
            elif consensus_level >= 0.6:
                return "中等共识：参与者基本达成一致，存在一些不同意见"
            elif consensus_level >= 0.4:
                return "部分共识：存在明显分歧，但也有共同点"
            else:
                return "低共识：参与者之间存在显著分歧"
                
        except Exception as e:
            logger.error(f"生成共识总结失败: {e}")
            return "Consensus summary unavailable"


# 全局Forum服务实例
forum_service = ForumService()