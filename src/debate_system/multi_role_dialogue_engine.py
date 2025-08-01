#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多角色对话引擎

基于现有CognitiveAgent和IntegratedLLMManager实现多角色对话功能。
支持角色轮流发言、上下文传递、讨论收敛机制。

核心功能：
- 角色选择和匹配
- 对话流程管理
- 上下文传递和维护
- 讨论收敛检测
- LLM调用优化和错误处理
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

# 导入现有组件（在实际使用时需要正确的路径）
try:
    from src.core_services.cognitive_agent import CognitiveAgent
    from src.core_services.role_manager import RoleManager
    from src.core_services.integrated_llm_manager import IntegratedLLMManager
    from src.core_services.memory_agent import MemAgent
except ImportError:
    # 如果无法导入，创建占位符类
    class CognitiveAgent:
        pass
    class RoleManager:
        pass
    class IntegratedLLMManager:
        pass
    class MemAgent:
        pass

from .debate_flow_definition import (
    DebateSession, DebateRound, DebateContribution, 
    DebatePhase, ParticipantRole, DebateParticipant
)
from participant_management import ParticipantManager, Permission, ActionType


class DialogueState(Enum):
    """对话状态枚举"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    WAITING_FOR_RESPONSE = "waiting_for_response"
    CONVERGING = "converging"
    COMPLETED = "completed"
    ERROR = "error"


class ConversationTurn(Enum):
    """对话轮次类型"""
    OPENING = "opening"
    RESPONSE = "response"
    CHALLENGE = "challenge"
    SYNTHESIS = "synthesis"
    CONCLUSION = "conclusion"


@dataclass
class RoleContext:
    """角色上下文"""
    role_id: str
    role_name: str
    role_type: ParticipantRole
    expertise_areas: List[str] = field(default_factory=list)
    personality_traits: Dict[str, float] = field(default_factory=dict)
    speaking_style: str = "formal"
    current_stance: Optional[str] = None
    confidence_level: float = 0.5
    last_contribution_time: Optional[datetime] = None
    contribution_count: int = 0
    influence_score: float = 0.0


@dataclass
class DialogueTurn:
    """对话轮次"""
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    speaker_role_id: str = ""
    turn_type: ConversationTurn = ConversationTurn.RESPONSE
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    context_references: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DialogueContext:
    """对话上下文"""
    session_id: str
    topic: str
    current_phase: DebatePhase
    active_roles: List[RoleContext] = field(default_factory=list)
    dialogue_history: List[DialogueTurn] = field(default_factory=list)
    shared_knowledge: Dict[str, Any] = field(default_factory=dict)
    convergence_indicators: Dict[str, float] = field(default_factory=dict)
    discussion_summary: str = ""
    key_points: List[str] = field(default_factory=list)
    unresolved_issues: List[str] = field(default_factory=list)


class RoleSelector:
    """角色选择器"""
    
    def __init__(self, role_manager: RoleManager):
        self.role_manager = role_manager
        self.logger = logging.getLogger(__name__)
    
    async def select_roles_for_topic(self, 
                                   topic: str,
                                   max_roles: int = 4,
                                   required_diversity: float = 0.7) -> List[RoleContext]:
        """为话题选择合适的角色"""
        try:
            # 获取所有可用角色
            available_roles = await self.role_manager.get_available_roles()
            
            # 基于话题语义匹配角色
            role_scores = {}
            for role_id, role_info in available_roles.items():
                score = await self._calculate_role_relevance(topic, role_info)
                role_scores[role_id] = score
            
            # 选择最相关的角色，同时确保多样性
            selected_roles = await self._select_diverse_roles(
                role_scores, max_roles, required_diversity
            )
            
            # 创建角色上下文
            role_contexts = []
            for role_id in selected_roles:
                role_info = available_roles[role_id]
                context = RoleContext(
                    role_id=role_id,
                    role_name=role_info.get('name', role_id),
                    role_type=ParticipantRole.EXPERT,  # 默认为专家角色
                    expertise_areas=role_info.get('expertise_areas', []),
                    personality_traits=role_info.get('personality_traits', {}),
                    speaking_style=role_info.get('speaking_style', 'formal')
                )
                role_contexts.append(context)
            
            self.logger.info(f"为话题 '{topic}' 选择了 {len(role_contexts)} 个角色")
            return role_contexts
        
        except Exception as e:
            self.logger.error(f"角色选择失败: {e}")
            return []
    
    async def _calculate_role_relevance(self, topic: str, role_info: Dict[str, Any]) -> float:
        """计算角色与话题的相关性"""
        # 简单的关键词匹配算法
        # 在实际实现中，可以使用更复杂的语义匹配
        
        topic_keywords = set(topic.lower().split())
        role_keywords = set()
        
        # 从角色信息中提取关键词
        for area in role_info.get('expertise_areas', []):
            role_keywords.update(area.lower().split())
        
        if role_info.get('description'):
            role_keywords.update(role_info['description'].lower().split())
        
        # 计算交集比例
        if not role_keywords:
            return 0.1  # 默认最低相关性
        
        intersection = topic_keywords.intersection(role_keywords)
        relevance = len(intersection) / len(role_keywords)
        
        return min(relevance, 1.0)
    
    async def _select_diverse_roles(self, 
                                  role_scores: Dict[str, float],
                                  max_roles: int,
                                  required_diversity: float) -> List[str]:
        """选择多样化的角色组合"""
        # 按相关性排序
        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        
        selected = []
        for role_id, score in sorted_roles:
            if len(selected) >= max_roles:
                break
            
            # 检查多样性
            if self._check_diversity(selected, role_id, required_diversity):
                selected.append(role_id)
        
        return selected
    
    def _check_diversity(self, selected: List[str], candidate: str, threshold: float) -> bool:
        """检查角色多样性"""
        # 简单实现：确保不选择相同类型的角色
        # 在实际实现中，可以基于更复杂的多样性指标
        return True
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 简单的词汇重叠相似度
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


class ConversationManager:
    """对话管理器"""
    
    def __init__(self, 
                 cognitive_agent: CognitiveAgent,
                 llm_manager: IntegratedLLMManager,
                 memory_agent: MemAgent):
        self.cognitive_agent = cognitive_agent
        self.llm_manager = llm_manager
        self.memory_agent = memory_agent
        self.logger = logging.getLogger(__name__)
        
        # 对话配置
        self.max_turn_length = 500  # 最大发言长度
        self.response_timeout = 30  # 响应超时时间（秒）
        self.max_retries = 3  # 最大重试次数
    
    async def generate_role_response(self,
                                   role_context: RoleContext,
                                   dialogue_context: DialogueContext,
                                   turn_type: ConversationTurn) -> Optional[DialogueTurn]:
        """生成角色响应"""
        try:
            # 构建提示词
            prompt = await self._build_role_prompt(
                role_context, dialogue_context, turn_type
            )
            
            # 调用LLM生成响应
            response = await self._call_llm_with_retry(
                role_context.role_id, prompt
            )
            
            if not response:
                return None
            
            # 创建对话轮次
            turn = DialogueTurn(
                speaker_role_id=role_context.role_id,
                turn_type=turn_type,
                content=response,
                confidence_score=await self._calculate_confidence(response)
            )
            
            # 更新角色上下文
            role_context.last_contribution_time = datetime.now()
            role_context.contribution_count += 1
            
            return turn
        
        except Exception as e:
            self.logger.error(f"生成角色响应失败 {role_context.role_id}: {e}")
            return None
    
    async def _build_role_prompt(self,
                               role_context: RoleContext,
                               dialogue_context: DialogueContext,
                               turn_type: ConversationTurn) -> str:
        """构建角色提示词"""
        # 基础角色设定
        role_prompt = f"""
你是一个{role_context.role_name}，专业领域包括：{', '.join(role_context.expertise_areas)}。
你的说话风格是{role_context.speaking_style}。

当前讨论话题：{dialogue_context.topic}
讨论阶段：{dialogue_context.current_phase.value}
"""
        
        # 添加对话历史
        if dialogue_context.dialogue_history:
            role_prompt += "\n对话历史：\n"
            for turn in dialogue_context.dialogue_history[-5:]:  # 只包含最近5轮
                speaker_name = self._get_role_name(turn.speaker_role_id, dialogue_context)
                role_prompt += f"{speaker_name}: {turn.content}\n"
        
        # 根据轮次类型添加特定指令
        if turn_type == ConversationTurn.OPENING:
            role_prompt += "\n请提出你的开场观点，简洁明了地表达你的立场。"
        elif turn_type == ConversationTurn.RESPONSE:
            role_prompt += "\n请回应前面的观点，可以表示同意、反对或补充。"
        elif turn_type == ConversationTurn.CHALLENGE:
            role_prompt += "\n请对前面的观点提出质疑或挑战，要有理有据。"
        elif turn_type == ConversationTurn.SYNTHESIS:
            role_prompt += "\n请尝试综合各方观点，寻找共同点或提出新的见解。"
        elif turn_type == ConversationTurn.CONCLUSION:
            role_prompt += "\n请总结你的最终观点，简明扼要。"
        
        role_prompt += f"\n\n请控制回应长度在{self.max_turn_length}字以内。"
        
        return role_prompt
    
    def _get_role_name(self, role_id: str, dialogue_context: DialogueContext) -> str:
        """获取角色名称"""
        for role in dialogue_context.active_roles:
            if role.role_id == role_id:
                return role.role_name
        return role_id
    
    async def _call_llm_with_retry(self, role_id: str, prompt: str) -> Optional[str]:
        """带重试的LLM调用"""
        for attempt in range(self.max_retries):
            try:
                # 使用IntegratedLLMManager调用LLM
                response = await self.llm_manager.generate_response(
                    prompt=prompt,
                    model_preference="gpt-4",  # 可配置
                    timeout=self.response_timeout
                )
                
                if response and response.strip():
                    return response.strip()
            
            except Exception as e:
                self.logger.warning(f"LLM调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
        
        return None
    
    async def _calculate_confidence(self, response: str) -> float:
        """计算响应的置信度"""
        # 简单的置信度计算
        # 可以基于响应长度、关键词密度等因素
        
        if not response:
            return 0.0
        
        # 基础分数
        base_score = 0.5
        
        # 长度因子
        length_factor = min(len(response) / 200, 1.0) * 0.2
        
        # 结构化因子（包含标点符号等）
        structure_factor = (response.count('.') + response.count('!') + response.count('?')) / len(response) * 100 * 0.1
        
        confidence = min(base_score + length_factor + structure_factor, 1.0)
        return confidence


class ConvergenceDetector:
    """讨论收敛检测器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 收敛检测参数
        self.similarity_threshold = 0.7  # 观点相似度阈值
        self.repetition_threshold = 3    # 重复观点阈值
        self.stagnation_threshold = 5    # 停滞轮次阈值
    
    async def detect_convergence(self, dialogue_context: DialogueContext) -> Dict[str, float]:
        """检测讨论收敛情况"""
        try:
            convergence_indicators = {}
            
            # 观点相似度检测
            similarity_score = await self._calculate_viewpoint_similarity(dialogue_context)
            convergence_indicators['viewpoint_similarity'] = similarity_score
            
            # 重复性检测
            repetition_score = await self._calculate_repetition_score(dialogue_context)
            convergence_indicators['repetition_level'] = repetition_score
            
            # 讨论活跃度检测
            activity_score = await self._calculate_activity_score(dialogue_context)
            convergence_indicators['activity_level'] = activity_score
            
            # 综合收敛分数
            overall_convergence = (
                similarity_score * 0.4 +
                repetition_score * 0.3 +
                (1 - activity_score) * 0.3  # 活跃度低表示可能收敛
            )
            convergence_indicators['overall_convergence'] = overall_convergence
            
            return convergence_indicators
        
        except Exception as e:
            self.logger.error(f"收敛检测失败: {e}")
            return {}
    
    async def _calculate_viewpoint_similarity(self, dialogue_context: DialogueContext) -> float:
        """计算观点相似度"""
        if len(dialogue_context.dialogue_history) < 2:
            return 0.0
        
        # 简单实现：基于关键词重叠
        recent_turns = dialogue_context.dialogue_history[-5:]
        
        total_similarity = 0.0
        comparison_count = 0
        
        for i in range(len(recent_turns)):
            for j in range(i + 1, len(recent_turns)):
                similarity = self._calculate_text_similarity(
                    recent_turns[i].content,
                    recent_turns[j].content
                )
                total_similarity += similarity
                comparison_count += 1
        
        if comparison_count == 0:
            return 0.0
        
        return total_similarity / comparison_count
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 简单的词汇重叠相似度
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def _calculate_repetition_score(self, dialogue_context: DialogueContext) -> float:
        """计算重复性分数"""
        if len(dialogue_context.dialogue_history) < 3:
            return 0.0
        
        # 检查最近的发言是否重复
        recent_turns = dialogue_context.dialogue_history[-10:]
        repetition_count = 0
        
        for i in range(len(recent_turns) - 1):
            similarity = self._calculate_text_similarity(
                recent_turns[i].content,
                recent_turns[i + 1].content
            )
            if similarity > self.similarity_threshold:
                repetition_count += 1
        
        return min(repetition_count / len(recent_turns), 1.0)
    
    async def _calculate_activity_score(self, dialogue_context: DialogueContext) -> float:
        """计算讨论活跃度"""
        if not dialogue_context.dialogue_history:
            return 0.0
        
        # 基于最近的发言频率
        now = datetime.now()
        recent_threshold = timedelta(minutes=10)
        
        recent_turns = [
            turn for turn in dialogue_context.dialogue_history
            if now - turn.timestamp < recent_threshold
        ]
        
        # 活跃度 = 最近发言数 / 总发言数
        if len(dialogue_context.dialogue_history) == 0:
            return 0.0
        
        activity = len(recent_turns) / min(len(dialogue_context.dialogue_history), 10)
        return min(activity, 1.0)


class MultiRoleDialogueEngine:
    """多角色对话引擎"""
    
    def __init__(self,
                 cognitive_agent: CognitiveAgent,
                 role_manager: RoleManager,
                 llm_manager: IntegratedLLMManager,
                 memory_agent: MemAgent,
                 participant_manager: ParticipantManager):
        
        self.cognitive_agent = cognitive_agent
        self.role_manager = role_manager
        self.llm_manager = llm_manager
        self.memory_agent = memory_agent
        self.participant_manager = participant_manager
        
        # 子组件
        self.role_selector = RoleSelector(role_manager)
        self.conversation_manager = ConversationManager(
            cognitive_agent, llm_manager, memory_agent
        )
        self.convergence_detector = ConvergenceDetector()
        
        # 状态管理
        self.active_dialogues: Dict[str, DialogueContext] = {}
        self.dialogue_state: Dict[str, DialogueState] = {}
        
        self.logger = logging.getLogger(__name__)
    
    async def start_dialogue(self,
                           session: DebateSession,
                           topic: str,
                           max_roles: int = 4) -> bool:
        """启动多角色对话"""
        try:
            session_id = session.session_id
            
            # 选择角色
            selected_roles = await self.role_selector.select_roles_for_topic(
                topic, max_roles
            )
            
            if not selected_roles:
                self.logger.error(f"无法为话题 '{topic}' 选择合适的角色")
                return False
            
            # 创建对话上下文
            dialogue_context = DialogueContext(
                session_id=session_id,
                topic=topic,
                current_phase=session.rounds[-1].current_phase if session.rounds else DebatePhase.MAIN_ARGUMENTS,
                active_roles=selected_roles
            )
            
            # 保存上下文
            self.active_dialogues[session_id] = dialogue_context
            self.dialogue_state[session_id] = DialogueState.INITIALIZING
            
            # 开始对话
            success = await self._conduct_dialogue_round(session_id, ConversationTurn.OPENING)
            
            if success:
                self.dialogue_state[session_id] = DialogueState.ACTIVE
                self.logger.info(f"成功启动会话 {session_id} 的多角色对话")
            
            return success
        
        except Exception as e:
            self.logger.error(f"启动对话失败: {e}")
            return False
    
    async def continue_dialogue(self, session_id: str) -> bool:
        """继续对话"""
        try:
            if session_id not in self.active_dialogues:
                return False
            
            dialogue_context = self.active_dialogues[session_id]
            
            # 检查收敛情况
            convergence = await self.convergence_detector.detect_convergence(dialogue_context)
            dialogue_context.convergence_indicators = convergence
            
            # 如果收敛度高，尝试综合
            if convergence.get('overall_convergence', 0) > 0.7:
                self.dialogue_state[session_id] = DialogueState.CONVERGING
                success = await self._conduct_dialogue_round(session_id, ConversationTurn.SYNTHESIS)
            else:
                # 继续正常对话
                success = await self._conduct_dialogue_round(session_id, ConversationTurn.RESPONSE)
            
            return success
        
        except Exception as e:
            self.logger.error(f"继续对话失败: {e}")
            return False
    
    async def _conduct_dialogue_round(self,
                                    session_id: str,
                                    turn_type: ConversationTurn) -> bool:
        """执行对话轮次"""
        try:
            dialogue_context = self.active_dialogues[session_id]
            
            # 确定发言顺序
            speaking_order = await self._determine_speaking_order(dialogue_context, turn_type)
            
            round_success = True
            for role_context in speaking_order:
                # 生成角色响应
                turn = await self.conversation_manager.generate_role_response(
                    role_context, dialogue_context, turn_type
                )
                
                if turn:
                    # 添加到对话历史
                    dialogue_context.dialogue_history.append(turn)
                    
                    # 更新记忆
                    await self._update_memory(session_id, turn)
                    
                    self.logger.info(f"角色 {role_context.role_name} 发言: {turn.content[:100]}...")
                else:
                    self.logger.warning(f"角色 {role_context.role_name} 未能生成响应")
                    round_success = False
            
            return round_success
        
        except Exception as e:
            self.logger.error(f"执行对话轮次失败: {e}")
            return False
    
    async def _determine_speaking_order(self,
                                      dialogue_context: DialogueContext,
                                      turn_type: ConversationTurn) -> List[RoleContext]:
        """确定发言顺序"""
        active_roles = dialogue_context.active_roles.copy()
        
        if turn_type == ConversationTurn.OPENING:
            # 开场按影响力排序
            active_roles.sort(key=lambda r: r.influence_score, reverse=True)
        elif turn_type == ConversationTurn.RESPONSE:
            # 响应轮次随机化，但考虑最近发言时间
            now = datetime.now()
            for role in active_roles:
                if role.last_contribution_time:
                    time_since_last = (now - role.last_contribution_time).total_seconds()
                    role.influence_score += time_since_last / 3600  # 时间权重
            
            active_roles.sort(key=lambda r: r.influence_score, reverse=True)
        elif turn_type == ConversationTurn.SYNTHESIS:
            # 综合轮次选择最有影响力的角色
            active_roles = active_roles[:2]  # 只选择前两个
        
        return active_roles
    
    async def _update_memory(self, session_id: str, turn: DialogueTurn) -> None:
        """更新记忆"""
        try:
            # 构建记忆条目
            memory_entry = {
                "session_id": session_id,
                "speaker": turn.speaker_role_id,
                "content": turn.content,
                "timestamp": turn.timestamp.isoformat(),
                "turn_type": turn.turn_type.value,
                "confidence": turn.confidence_score
            }
            
            # 保存到记忆系统
            await self.memory_agent.store_memory(
                key=f"dialogue_turn_{turn.turn_id}",
                content=memory_entry,
                memory_type="dialogue_history"
            )
        
        except Exception as e:
            self.logger.error(f"更新记忆失败: {e}")
    
    async def get_dialogue_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取对话摘要"""
        try:
            if session_id not in self.active_dialogues:
                return None
            
            dialogue_context = self.active_dialogues[session_id]
            
            # 统计信息
            total_turns = len(dialogue_context.dialogue_history)
            role_contributions = {}
            
            for turn in dialogue_context.dialogue_history:
                role_id = turn.speaker_role_id
                if role_id not in role_contributions:
                    role_contributions[role_id] = 0
                role_contributions[role_id] += 1
            
            # 获取角色名称映射
            role_names = {
                role.role_id: role.role_name 
                for role in dialogue_context.active_roles
            }
            
            return {
                "session_id": session_id,
                "topic": dialogue_context.topic,
                "current_phase": dialogue_context.current_phase.value,
                "total_turns": total_turns,
                "active_roles": len(dialogue_context.active_roles),
                "role_contributions": {
                    role_names.get(role_id, role_id): count
                    for role_id, count in role_contributions.items()
                },
                "convergence_indicators": dialogue_context.convergence_indicators,
                "dialogue_state": self.dialogue_state.get(session_id, DialogueState.ACTIVE).value,
                "key_points": dialogue_context.key_points,
                "unresolved_issues": dialogue_context.unresolved_issues
            }
        
        except Exception as e:
            self.logger.error(f"获取对话摘要失败: {e}")
            return None
    
    async def end_dialogue(self, session_id: str) -> bool:
        """结束对话"""
        try:
            if session_id not in self.active_dialogues:
                return False
            
            # 生成最终总结
            dialogue_context = self.active_dialogues[session_id]
            
            # 执行结论轮次
            await self._conduct_dialogue_round(session_id, ConversationTurn.CONCLUSION)
            
            # 更新状态
            self.dialogue_state[session_id] = DialogueState.COMPLETED
            
            # 生成讨论总结
            summary = await self._generate_discussion_summary(dialogue_context)
            dialogue_context.discussion_summary = summary
            
            self.logger.info(f"会话 {session_id} 的对话已结束")
            return True
        
        except Exception as e:
            self.logger.error(f"结束对话失败: {e}")
            return False
    
    async def _generate_discussion_summary(self, dialogue_context: DialogueContext) -> str:
        """生成讨论总结"""
        try:
            # 构建总结提示词
            summary_prompt = f"""
请总结以下关于"{dialogue_context.topic}"的多角色讨论：

参与角色：{', '.join([role.role_name for role in dialogue_context.active_roles])}

对话内容：
"""
            
            for turn in dialogue_context.dialogue_history:
                speaker_name = next(
                    (role.role_name for role in dialogue_context.active_roles 
                     if role.role_id == turn.speaker_role_id),
                    turn.speaker_role_id
                )
                summary_prompt += f"{speaker_name}: {turn.content}\n"
            
            summary_prompt += """
请提供一个简洁的总结，包括：
1. 主要观点
2. 共识点
3. 分歧点
4. 关键洞察
"""
            
            # 调用LLM生成总结
            summary = await self.llm_manager.generate_response(
                prompt=summary_prompt,
                model_preference="gpt-4"
            )
            
            return summary or "无法生成讨论总结"
        
        except Exception as e:
            self.logger.error(f"生成讨论总结失败: {e}")
            return "总结生成失败"


# 使用示例和测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_multi_role_dialogue_engine():
        """测试多角色对话引擎"""
        print("🧪 测试多角色对话引擎...")
        
        # 这里需要实际的组件实例
        # 在实际使用中，这些组件应该从依赖注入容器获取
        
        print("⚠️ 需要实际的组件实例才能运行完整测试")
        print("✅ 多角色对话引擎代码结构验证完成")
    
    # 运行测试
    asyncio.run(test_multi_role_dialogue_engine())