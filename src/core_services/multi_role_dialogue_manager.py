#!/usr/bin/env python3
"""多角色对话管理器

负责管理多个认知代理之间的对话流程，包括：
1. 角色选择和匹配
2. 对话轮次管理
3. 上下文传递
4. 讨论收敛机制
5. LLM调用优化
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List, Optional
=======
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from .integrated_llm_manager import IntegratedLLMManager
from .memory_agent import MemAgent
from .role_manager import RoleManager

logger = logging.getLogger(__name__)


@dataclass
class DialogueParticipant:
    """对话参与者"""
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    role_id: str
    role_name: str
    role_description: str
    system_prompt: str
<<<<<<< HEAD
    expertise_areas: List[str]
    cognitive_style: Dict[str, Any]
=======
    expertise_areas: list[str]
    cognitive_style: dict[str, Any]
>>>>>>> feature/core-services-refactor


@dataclass
class DialogueRound:
    """对话轮次"""
<<<<<<< HEAD

    round_number: int
    topic: str
    participants: List[DialogueParticipant]
    responses: List[Dict[str, Any]]
=======
    round_number: int
    topic: str
    participants: list[DialogueParticipant]
    responses: list[dict[str, Any]]
>>>>>>> feature/core-services-refactor
    timestamp: datetime
    round_summary: Optional[str] = None


@dataclass
class DialogueSession:
    """对话会话"""
<<<<<<< HEAD

    session_id: str
    topic: str
    participants: List[DialogueParticipant]
    rounds: List[DialogueRound]
    start_time: datetime
    status: str  # 'active', 'paused', 'completed'
    convergence_score: float = 0.0
    user_interventions: List[Dict[str, Any]] = None
=======
    session_id: str
    topic: str
    participants: list[DialogueParticipant]
    rounds: list[DialogueRound]
    start_time: datetime
    status: str  # 'active', 'paused', 'completed'
    convergence_score: float = 0.0
    user_interventions: list[dict[str, Any]] = None
>>>>>>> feature/core-services-refactor

    def __post_init__(self):
        if self.user_interventions is None:
            self.user_interventions = []


class MultiRoleDialogueManager:
    """多角色对话管理器"""
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    def __init__(self):
        """初始化对话管理器"""
        self.role_manager = RoleManager()
        self.llm_manager = IntegratedLLMManager()
        self.memory_agent = MemAgent()
<<<<<<< HEAD

        # 活跃的对话会话
        self.active_sessions: Dict[str, DialogueSession] = {}

=======
        
        # 活跃的对话会话
        self.active_sessions: dict[str, DialogueSession] = {}
        
>>>>>>> feature/core-services-refactor
        # 角色选择策略配置
        self.role_selection_config = {
            "max_participants": 4,
            "min_participants": 2,
            "diversity_threshold": 0.7,
            "expertise_matching_weight": 0.6,
            "cognitive_diversity_weight": 0.4
        }
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 对话流程配置
        self.dialogue_config = {
            "max_rounds": 5,
            "convergence_threshold": 0.8,
            "response_timeout": 30.0,
            "round_pause_duration": 1.0
        }
<<<<<<< HEAD

        logger.info("多角色对话管理器初始化完成")

=======
        
        logger.info("多角色对话管理器初始化完成")
    
>>>>>>> feature/core-services-refactor
    async def initialize(self):
        """初始化所有组件"""
        await self.llm_manager.initialize()
        await self.memory_agent.initialize()
        logger.info("多角色对话管理器组件初始化完成")
<<<<<<< HEAD

    async def start_dialogue_session(
        self,
        topic: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        specific_roles: Optional[List[str]] = None
=======
    
    async def start_dialogue_session(
        self,
        topic: str,
        user_preferences: Optional[dict[str, Any]] = None,
        specific_roles: Optional[list[str]] = None
>>>>>>> feature/core-services-refactor
    ) -> DialogueSession:
        """启动多角色对话会话
        
        Args:
            topic: 对话主题
            user_preferences: 用户偏好设置
            specific_roles: 指定的角色列表（可选）
            
        Returns:
            创建的对话会话
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        try:
            # 1. 生成会话ID
            session_id = f"dialogue_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            # 2. 选择参与角色
            if specific_roles:
                participants = await self._get_specific_roles(specific_roles)
            else:
                participants = await self._select_optimal_roles(topic, user_preferences)
<<<<<<< HEAD

            if len(participants) < self.role_selection_config["min_participants"]:
                raise ValueError(f"参与角色数量不足，至少需要{self.role_selection_config['min_participants']}个角色")

=======
            
            if len(participants) < self.role_selection_config["min_participants"]:
                raise ValueError(f"参与角色数量不足，至少需要{self.role_selection_config['min_participants']}个角色")
            
>>>>>>> feature/core-services-refactor
            # 3. 创建对话会话
            session = DialogueSession(
                session_id=session_id,
                topic=topic,
                participants=participants,
                rounds=[],
                start_time=datetime.now(),
                status='active'
            )
<<<<<<< HEAD

            self.active_sessions[session_id] = session

            logger.info(f"启动对话会话 {session_id}，主题: {topic}，参与者: {[p.role_name for p in participants]}")

            return session

        except Exception as e:
            logger.error(f"启动对话会话失败: {e}")
            raise

    async def conduct_dialogue_round(
        self,
        session_id: str,
        round_context: Optional[Dict[str, Any]] = None
=======
            
            self.active_sessions[session_id] = session
            
            logger.info(f"启动对话会话 {session_id}，主题: {topic}，参与者: {[p.role_name for p in participants]}")
            
            return session
            
        except Exception as e:
            logger.error(f"启动对话会话失败: {e}")
            raise
    
    async def conduct_dialogue_round(
        self,
        session_id: str,
        round_context: Optional[dict[str, Any]] = None
>>>>>>> feature/core-services-refactor
    ) -> DialogueRound:
        """进行一轮对话
        
        Args:
            session_id: 会话ID
            round_context: 轮次上下文信息
            
        Returns:
            完成的对话轮次
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"会话 {session_id} 不存在")
<<<<<<< HEAD

        if session.status != 'active':
            raise ValueError(f"会话 {session_id} 状态为 {session.status}，无法进行对话")

        try:
            round_number = len(session.rounds) + 1

            logger.info(f"开始第 {round_number} 轮对话，会话: {session_id}")

            # 1. 构建轮次上下文
            context = await self._build_round_context(session, round_context)

=======
        
        if session.status != 'active':
            raise ValueError(f"会话 {session_id} 状态为 {session.status}，无法进行对话")
        
        try:
            round_number = len(session.rounds) + 1
            
            logger.info(f"开始第 {round_number} 轮对话，会话: {session_id}")
            
            # 1. 构建轮次上下文
            context = await self._build_round_context(session, round_context)
            
>>>>>>> feature/core-services-refactor
            # 2. 并行获取所有角色的回应
            responses = await self._get_parallel_role_responses(
                session.participants,
                session.topic,
                round_number,
                context
            )
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            # 3. 创建对话轮次
            dialogue_round = DialogueRound(
                round_number=round_number,
                topic=session.topic,
                participants=session.participants,
                responses=responses,
                timestamp=datetime.now()
            )
<<<<<<< HEAD

            # 4. 生成轮次总结
            dialogue_round.round_summary = await self._generate_round_summary(dialogue_round)

            # 5. 更新会话
            session.rounds.append(dialogue_round)

            # 6. 计算收敛度
            session.convergence_score = await self._calculate_convergence_score(session)

=======
            
            # 4. 生成轮次总结
            dialogue_round.round_summary = await self._generate_round_summary(dialogue_round)
            
            # 5. 更新会话
            session.rounds.append(dialogue_round)
            
            # 6. 计算收敛度
            session.convergence_score = await self._calculate_convergence_score(session)
            
>>>>>>> feature/core-services-refactor
            # 7. 检查是否需要结束对话
            if await self._should_end_dialogue(session):
                session.status = 'completed'
                logger.info(f"对话会话 {session_id} 已收敛完成")
<<<<<<< HEAD

            logger.info(f"完成第 {round_number} 轮对话，收敛度: {session.convergence_score:.2f}")

            return dialogue_round

=======
            
            logger.info(f"完成第 {round_number} 轮对话，收敛度: {session.convergence_score:.2f}")
            
            return dialogue_round
            
>>>>>>> feature/core-services-refactor
        except Exception as e:
            logger.error(f"进行对话轮次失败: {e}")
            session.status = 'paused'
            raise
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    async def add_user_intervention(
        self,
        session_id: str,
        user_input: str,
        intervention_type: str = "comment"
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """添加用户干预
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            intervention_type: 干预类型 ('comment', 'question', 'redirect')
            
        Returns:
            干预结果
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"会话 {session_id} 不存在")
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        try:
            # 1. 记录用户干预
            intervention = {
                "type": intervention_type,
                "content": user_input,
                "timestamp": datetime.now().isoformat(),
                "round_context": len(session.rounds)
            }
<<<<<<< HEAD

            session.user_interventions.append(intervention)

            # 2. 获取角色对用户干预的回应
            intervention_responses = []

=======
            
            session.user_interventions.append(intervention)
            
            # 2. 获取角色对用户干预的回应
            intervention_responses = []
            
>>>>>>> feature/core-services-refactor
            for participant in session.participants:
                try:
                    response = await self.llm_manager.call_llm_for_role(
                        role_id=participant.role_id,
                        user_input=user_input,
                        task_context=f"用户在对话中的{intervention_type}",
                        additional_context={
                            "dialogue_topic": session.topic,
                            "current_round": len(session.rounds),
                            "intervention_type": intervention_type,
                            "dialogue_history": [r.round_summary for r in session.rounds[-2:]]
                        }
                    )
<<<<<<< HEAD

=======
                    
>>>>>>> feature/core-services-refactor
                    intervention_responses.append({
                        "role_id": participant.role_id,
                        "role_name": participant.role_name,
                        "response": response.get("response", ""),
                        "optimization_metrics": response.get("optimization_metrics", {})
                    })
<<<<<<< HEAD

=======
                    
>>>>>>> feature/core-services-refactor
                except Exception as e:
                    logger.warning(f"角色 {participant.role_name} 回应用户干预失败: {e}")
                    intervention_responses.append({
                        "role_id": participant.role_id,
                        "role_name": participant.role_name,
                        "response": f"抱歉，我暂时无法回应您的{intervention_type}",
                        "error": str(e)
                    })
<<<<<<< HEAD

            logger.info(f"用户干预已添加到会话 {session_id}，获得 {len(intervention_responses)} 个角色回应")

=======
            
            logger.info(f"用户干预已添加到会话 {session_id}，获得 {len(intervention_responses)} 个角色回应")
            
>>>>>>> feature/core-services-refactor
            return {
                "intervention_recorded": True,
                "intervention_id": len(session.user_interventions),
                "role_responses": intervention_responses,
                "session_status": session.status
            }
<<<<<<< HEAD

        except Exception as e:
            logger.error(f"添加用户干预失败: {e}")
            raise

    async def _select_optimal_roles(
        self,
        topic: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[DialogueParticipant]:
=======
            
        except Exception as e:
            logger.error(f"添加用户干预失败: {e}")
            raise
    
    async def _select_optimal_roles(
        self,
        topic: str,
        user_preferences: Optional[dict[str, Any]] = None
    ) -> list[DialogueParticipant]:
>>>>>>> feature/core-services-refactor
        """基于主题和用户偏好选择最优角色组合
        
        Args:
            topic: 对话主题
            user_preferences: 用户偏好
            
        Returns:
            选择的角色列表
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        try:
            # 1. 获取所有可用角色
            all_roles = self.role_manager.list_roles()
<<<<<<< HEAD

            if not all_roles:
                raise ValueError("没有可用的角色")

            # 2. 基于主题关键词进行初步筛选
            relevant_roles = await self._filter_roles_by_topic(all_roles, topic)

            # 3. 应用认知多样性评估
            diverse_roles = await self._ensure_cognitive_diversity(relevant_roles)

            # 4. 应用用户偏好
            if user_preferences:
                diverse_roles = await self._apply_user_preferences(diverse_roles, user_preferences)

            # 5. 限制参与者数量
            max_participants = self.role_selection_config["max_participants"]
            selected_roles = diverse_roles[:max_participants]

=======
            
            if not all_roles:
                raise ValueError("没有可用的角色")
            
            # 2. 基于主题关键词进行初步筛选
            relevant_roles = await self._filter_roles_by_topic(all_roles, topic)
            
            # 3. 应用认知多样性评估
            diverse_roles = await self._ensure_cognitive_diversity(relevant_roles)
            
            # 4. 应用用户偏好
            if user_preferences:
                diverse_roles = await self._apply_user_preferences(diverse_roles, user_preferences)
            
            # 5. 限制参与者数量
            max_participants = self.role_selection_config["max_participants"]
            selected_roles = diverse_roles[:max_participants]
            
>>>>>>> feature/core-services-refactor
            # 6. 转换为DialogueParticipant对象
            participants = []
            for role in selected_roles:
                participant = DialogueParticipant(
                    role_id=role.id,
                    role_name=role.name,
                    role_description=role.description,
                    system_prompt=role.system_prompt,
                    expertise_areas=role.capabilities,
                    cognitive_style={}  # 可以从角色定义中提取
                )
                participants.append(participant)
<<<<<<< HEAD

            logger.info(f"为主题 '{topic}' 选择了 {len(participants)} 个角色: {[p.role_name for p in participants]}")

            return participants

=======
            
            logger.info(f"为主题 '{topic}' 选择了 {len(participants)} 个角色: {[p.role_name for p in participants]}")
            
            return participants
            
>>>>>>> feature/core-services-refactor
        except Exception as e:
            logger.error(f"选择最优角色失败: {e}")
            # 返回默认角色组合
            return await self._get_default_roles()
<<<<<<< HEAD

    async def _filter_roles_by_topic(self, roles: List, topic: str) -> List:
=======
    
    async def _filter_roles_by_topic(self, roles: list, topic: str) -> list:
>>>>>>> feature/core-services-refactor
        """基于主题过滤角色"""
        # 定义主题关键词到角色的映射
        topic_role_mapping = {
            "AI": ["AI Ethics", "Technology Ethics Reviewer", "AI Governance"],
            "人工智能": ["AI Ethics", "Technology Ethics Reviewer", "AI Governance"],
            "管理": ["Critical Management", "Organizational Culture", "StrategicHR"],
            "数据": ["DataMining", "ComputationalSocialScientist", "Data Governance Expert"],
            "分析": ["system_synthesis_master", "socratic_dialogue_guide", "task_decomposition_master"],
            "技术": ["Technology Ethics Reviewer", "AI Governance", "system_synthesis_master"],
            "教育": ["socratic_dialogue_guide", "task_decomposition_master", "system_synthesis_master"],
            "商业": ["economist", "Critical Management", "StrategicHR"],
            "法律": ["legal_expert", "AI Governance", "Data Governance Expert"]
        }
<<<<<<< HEAD

        # 查找匹配的角色名称
        relevant_role_names = set()
        topic_lower = topic.lower()

        for keyword, role_names in topic_role_mapping.items():
            if keyword.lower() in topic_lower:
                relevant_role_names.update(role_names)

        # 如果没有找到特定匹配，使用默认的通用角色
        if not relevant_role_names:
            relevant_role_names = {"system_synthesis_master", "socratic_dialogue_guide", "task_decomposition_master"}

=======
        
        # 查找匹配的角色名称
        relevant_role_names = set()
        topic_lower = topic.lower()
        
        for keyword, role_names in topic_role_mapping.items():
            if keyword.lower() in topic_lower:
                relevant_role_names.update(role_names)
        
        # 如果没有找到特定匹配，使用默认的通用角色
        if not relevant_role_names:
            relevant_role_names = {"system_synthesis_master", "socratic_dialogue_guide", "task_decomposition_master"}
        
>>>>>>> feature/core-services-refactor
        # 过滤角色
        filtered_roles = []
        for role in roles:
            if role.id in relevant_role_names or role.name in relevant_role_names:
                filtered_roles.append(role)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 如果过滤后角色不足，添加一些通用角色
        if len(filtered_roles) < self.role_selection_config["min_participants"]:
            backup_role_names = {"economist", "legal_expert", "quality_assurance_001"}
            for role in roles:
                if len(filtered_roles) >= self.role_selection_config["max_participants"]:
                    break
                if role.id in backup_role_names and role not in filtered_roles:
                    filtered_roles.append(role)
<<<<<<< HEAD

        return filtered_roles

    async def _ensure_cognitive_diversity(self, roles: List) -> List:
        """确保认知多样性"""
        # 简化的认知多样性评估
        # 在实际实现中，这里应该基于角色的认知风格、专业背景等进行更复杂的评估

        if len(roles) <= self.role_selection_config["max_participants"]:
            return roles

        # 基于角色描述的多样性进行简单排序
        # 这里可以实现更复杂的多样性算法
        return roles[:self.role_selection_config["max_participants"]]

    async def _apply_user_preferences(self, roles: List, preferences: Dict[str, Any]) -> List:
        """应用用户偏好"""
        # 根据用户偏好调整角色选择
        # 例如：偏好某些专业领域、认知风格等

=======
        
        return filtered_roles
    
    async def _ensure_cognitive_diversity(self, roles: list) -> list:
        """确保认知多样性"""
        # 简化的认知多样性评估
        # 在实际实现中，这里应该基于角色的认知风格、专业背景等进行更复杂的评估
        
        if len(roles) <= self.role_selection_config["max_participants"]:
            return roles
        
        # 基于角色描述的多样性进行简单排序
        # 这里可以实现更复杂的多样性算法
        return roles[:self.role_selection_config["max_participants"]]
    
    async def _apply_user_preferences(self, roles: list, preferences: dict[str, Any]) -> list:
        """应用用户偏好"""
        # 根据用户偏好调整角色选择
        # 例如：偏好某些专业领域、认知风格等
        
>>>>>>> feature/core-services-refactor
        preferred_expertise = preferences.get("expertise", [])
        if preferred_expertise:
            # 优先选择用户偏好的专业领域角色
            preferred_roles = []
            other_roles = []
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            for role in roles:
                if any(exp in role.capabilities for exp in preferred_expertise):
                    preferred_roles.append(role)
                else:
                    other_roles.append(role)
<<<<<<< HEAD

            # 组合偏好角色和其他角色
            return preferred_roles + other_roles

        return roles

    async def _get_specific_roles(self, role_ids: List[str]) -> List[DialogueParticipant]:
        """获取指定的角色"""
        participants = []

=======
            
            # 组合偏好角色和其他角色
            return preferred_roles + other_roles
        
        return roles
    
    async def _get_specific_roles(self, role_ids: list[str]) -> list[DialogueParticipant]:
        """获取指定的角色"""
        participants = []
        
>>>>>>> feature/core-services-refactor
        for role_id in role_ids:
            role = self.role_manager.get_role_by_id(role_id)
            if role:
                participant = DialogueParticipant(
                    role_id=role.id,
                    role_name=role.name,
                    role_description=role.description,
                    system_prompt=role.system_prompt,
                    expertise_areas=role.capabilities,
                    cognitive_style={}
                )
                participants.append(participant)
            else:
                logger.warning(f"角色 {role_id} 不存在")
<<<<<<< HEAD

        return participants

    async def _get_default_roles(self) -> List[DialogueParticipant]:
        """获取默认角色组合"""
        default_role_ids = ["system_synthesis_master", "socratic_dialogue_guide", "task_decomposition_master"]
        return await self._get_specific_roles(default_role_ids)

    async def _build_round_context(
        self,
        session: DialogueSession,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
=======
        
        return participants
    
    async def _get_default_roles(self) -> list[DialogueParticipant]:
        """获取默认角色组合"""
        default_role_ids = ["system_synthesis_master", "socratic_dialogue_guide", "task_decomposition_master"]
        return await self._get_specific_roles(default_role_ids)
    
    async def _build_round_context(
        self,
        session: DialogueSession,
        additional_context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """构建轮次上下文"""
        context = {
            "session_id": session.session_id,
            "topic": session.topic,
            "round_number": len(session.rounds) + 1,
            "participants": [p.role_name for p in session.participants],
            "previous_rounds": len(session.rounds),
            "convergence_score": session.convergence_score,
            "user_interventions": len(session.user_interventions)
        }
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 添加最近几轮的总结
        if session.rounds:
            context["recent_summaries"] = [
                r.round_summary for r in session.rounds[-2:] if r.round_summary
            ]
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 添加用户干预
        if session.user_interventions:
            context["recent_user_inputs"] = [
                i["content"] for i in session.user_interventions[-2:]
            ]
<<<<<<< HEAD

        # 合并额外上下文
        if additional_context:
            context.update(additional_context)

        return context

    async def _get_parallel_role_responses(
        self,
        participants: List[DialogueParticipant],
        topic: str,
        round_number: int,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """并行获取所有角色的回应"""

        async def get_role_response(participant: DialogueParticipant) -> Dict[str, Any]:
            try:
                # 构建角色专用的提示
                role_prompt = f"请就以下议题发表你的专业观点（第{round_number}轮讨论）: {topic}"

=======
        
        # 合并额外上下文
        if additional_context:
            context.update(additional_context)
        
        return context
    
    async def _get_parallel_role_responses(
        self,
        participants: list[DialogueParticipant],
        topic: str,
        round_number: int,
        context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """并行获取所有角色的回应"""
        
        async def get_role_response(participant: DialogueParticipant) -> dict[str, Any]:
            try:
                # 构建角色专用的提示
                role_prompt = f"请就以下议题发表你的专业观点（第{round_number}轮讨论）: {topic}"
                
>>>>>>> feature/core-services-refactor
                # 调用LLM
                response = await self.llm_manager.call_llm_for_role(
                    role_id=participant.role_id,
                    user_input=role_prompt,
                    task_context=f"多角色对话第{round_number}轮",
                    additional_context=context
                )
<<<<<<< HEAD

=======
                
>>>>>>> feature/core-services-refactor
                return {
                    "role_id": participant.role_id,
                    "role_name": participant.role_name,
                    "response": response.get("response", ""),
                    "optimization_metrics": response.get("optimization_metrics", {}),
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
<<<<<<< HEAD

=======
                
>>>>>>> feature/core-services-refactor
            except Exception as e:
                logger.error(f"角色 {participant.role_name} 回应失败: {e}")
                return {
                    "role_id": participant.role_id,
                    "role_name": participant.role_name,
                    "response": f"抱歉，我在第{round_number}轮讨论中遇到了技术问题",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                }
<<<<<<< HEAD

        # 并行执行所有角色的回应
        tasks = [get_role_response(participant) for participant in participants]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

=======
        
        # 并行执行所有角色的回应
        tasks = [get_role_response(participant) for participant in participants]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
>>>>>>> feature/core-services-refactor
        # 处理异常结果
        valid_responses = []
        for response in responses:
            if isinstance(response, Exception):
                logger.error(f"角色回应任务异常: {response}")
                valid_responses.append({
                    "role_id": "unknown",
                    "role_name": "Unknown",
                    "response": "系统错误",
                    "error": str(response),
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                })
            else:
                valid_responses.append(response)
<<<<<<< HEAD

        return valid_responses

=======
        
        return valid_responses
    
>>>>>>> feature/core-services-refactor
    async def _generate_round_summary(self, dialogue_round: DialogueRound) -> str:
        """生成轮次总结"""
        try:
            # 收集所有回应
            all_responses = [r["response"] for r in dialogue_round.responses if r.get("success", True)]
<<<<<<< HEAD

            if not all_responses:
                return f"第{dialogue_round.round_number}轮讨论中所有角色都遇到了技术问题"

            # 简化的总结生成（在实际实现中可以使用更复杂的NLP技术）
            summary = f"第{dialogue_round.round_number}轮讨论中，{len(all_responses)}个角色就'{dialogue_round.topic}'发表了观点。"

=======
            
            if not all_responses:
                return f"第{dialogue_round.round_number}轮讨论中所有角色都遇到了技术问题"
            
            # 简化的总结生成（在实际实现中可以使用更复杂的NLP技术）
            summary = f"第{dialogue_round.round_number}轮讨论中，{len(all_responses)}个角色就'{dialogue_round.topic}'发表了观点。"
            
>>>>>>> feature/core-services-refactor
            # 统计优化效果
            successful_optimizations = sum(1 for r in dialogue_round.responses if r.get("optimization_metrics", {}).get("improvement_score", 0) > 0)
            if successful_optimizations > 0:
                summary += f" 其中{successful_optimizations}个角色的回应得到了优化。"
<<<<<<< HEAD

            return summary

        except Exception as e:
            logger.error(f"生成轮次总结失败: {e}")
            return f"第{dialogue_round.round_number}轮讨论总结生成失败"

=======
            
            return summary
            
        except Exception as e:
            logger.error(f"生成轮次总结失败: {e}")
            return f"第{dialogue_round.round_number}轮讨论总结生成失败"
    
>>>>>>> feature/core-services-refactor
    async def _calculate_convergence_score(self, session: DialogueSession) -> float:
        """计算对话收敛度"""
        try:
            if len(session.rounds) < 2:
                return 0.0
<<<<<<< HEAD

            # 简化的收敛度计算
            # 在实际实现中，可以使用更复杂的语义相似度算法

            # 基于轮次数量的基础收敛度
            base_convergence = min(len(session.rounds) * 0.2, 0.8)

            # 基于用户干预的调整
            user_engagement_bonus = min(len(session.user_interventions) * 0.1, 0.2)

=======
            
            # 简化的收敛度计算
            # 在实际实现中，可以使用更复杂的语义相似度算法
            
            # 基于轮次数量的基础收敛度
            base_convergence = min(len(session.rounds) * 0.2, 0.8)
            
            # 基于用户干预的调整
            user_engagement_bonus = min(len(session.user_interventions) * 0.1, 0.2)
            
>>>>>>> feature/core-services-refactor
            # 基于成功回应率的调整
            latest_round = session.rounds[-1]
            success_rate = sum(1 for r in latest_round.responses if r.get("success", True)) / len(latest_round.responses)
            success_bonus = success_rate * 0.1
<<<<<<< HEAD

            convergence_score = base_convergence + user_engagement_bonus + success_bonus
            return min(convergence_score, 1.0)

        except Exception as e:
            logger.error(f"计算收敛度失败: {e}")
            return 0.0

=======
            
            convergence_score = base_convergence + user_engagement_bonus + success_bonus
            return min(convergence_score, 1.0)
            
        except Exception as e:
            logger.error(f"计算收敛度失败: {e}")
            return 0.0
    
>>>>>>> feature/core-services-refactor
    async def _should_end_dialogue(self, session: DialogueSession) -> bool:
        """判断是否应该结束对话"""
        # 检查最大轮次限制
        if len(session.rounds) >= self.dialogue_config["max_rounds"]:
            return True
<<<<<<< HEAD

        # 检查收敛度阈值
        if session.convergence_score >= self.dialogue_config["convergence_threshold"]:
            return True

=======
        
        # 检查收敛度阈值
        if session.convergence_score >= self.dialogue_config["convergence_threshold"]:
            return True
        
>>>>>>> feature/core-services-refactor
        # 检查最近轮次的成功率
        if session.rounds:
            latest_round = session.rounds[-1]
            success_rate = sum(1 for r in latest_round.responses if r.get("success", True)) / len(latest_round.responses)
            if success_rate < 0.5:  # 如果成功率太低，考虑结束
                return True
<<<<<<< HEAD

        return False

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
=======
        
        return False
    
    def get_session_status(self, session_id: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取会话状态"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": f"会话 {session_id} 不存在"}
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "status": session.status,
            "participants": [p.role_name for p in session.participants],
            "rounds_completed": len(session.rounds),
            "convergence_score": session.convergence_score,
            "user_interventions": len(session.user_interventions),
            "start_time": session.start_time.isoformat(),
            "duration_seconds": (datetime.now() - session.start_time).total_seconds()
        }
<<<<<<< HEAD

    def list_active_sessions(self) -> List[Dict[str, Any]]:
=======
    
    def list_active_sessions(self) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """列出所有活跃会话"""
        return [
            {
                "session_id": session_id,
                "topic": session.topic,
                "status": session.status,
                "participants_count": len(session.participants),
                "rounds_count": len(session.rounds),
                "convergence_score": session.convergence_score
            }
            for session_id, session in self.active_sessions.items()
        ]
<<<<<<< HEAD

    async def close_session(self, session_id: str) -> Dict[str, Any]:
=======
    
    async def close_session(self, session_id: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """关闭会话"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": f"会话 {session_id} 不存在"}
<<<<<<< HEAD

        session.status = 'completed'

=======
        
        session.status = 'completed'
        
>>>>>>> feature/core-services-refactor
        # 生成会话总结
        session_summary = {
            "session_id": session_id,
            "topic": session.topic,
            "total_rounds": len(session.rounds),
            "final_convergence_score": session.convergence_score,
            "total_user_interventions": len(session.user_interventions),
            "duration_seconds": (datetime.now() - session.start_time).total_seconds(),
            "participants": [p.role_name for p in session.participants]
        }
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 保存到记忆系统
        try:
            await self.memory_agent.store_memory("dialogue_sessions", {
                "session_summary": session_summary,
                "full_session_data": session,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.warning(f"保存会话记忆失败: {e}")
<<<<<<< HEAD

        # 从活跃会话中移除
        del self.active_sessions[session_id]

        logger.info(f"会话 {session_id} 已关闭")

        return session_summary

=======
        
        # 从活跃会话中移除
        del self.active_sessions[session_id]
        
        logger.info(f"会话 {session_id} 已关闭")
        
        return session_summary
    
>>>>>>> feature/core-services-refactor
    async def close(self):
        """关闭对话管理器"""
        # 关闭所有活跃会话
        for session_id in list(self.active_sessions.keys()):
            await self.close_session(session_id)
<<<<<<< HEAD

        # 关闭组件
        await self.llm_manager.close()

        logger.info("多角色对话管理器已关闭")
=======
        
        # 关闭组件
        await self.llm_manager.close()
        
        logger.info("多角色对话管理器已关闭")
>>>>>>> feature/core-services-refactor
