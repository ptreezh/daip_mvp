#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多角色辩论系统

基于设计文档实现的真实多角色辩论系统，支持：
- 从真实角色库加载认知代理
- 真实LLM调用生成角色观点
- 多视角辩论和共识形成
- 透明度监控和真实性验证
"""

import logging
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DebatePhase(Enum):
    """辩论阶段枚举"""
    INITIALIZATION = "initialization"
    OPENING_STATEMENTS = "opening_statements"
    ARGUMENT_EXCHANGE = "argument_exchange"
    CROSS_EXAMINATION = "cross_examination"
    CONSENSUS_BUILDING = "consensus_building"
    CONCLUSION = "conclusion"


class ArgumentType(Enum):
    """论证类型枚举"""
    SUPPORT = "support"
    OPPOSE = "oppose"
    QUESTION = "question"
    CLARIFICATION = "clarification"
    SYNTHESIS = "synthesis"


@dataclass
class CognitiveProfile:
    """认知档案"""
    thinking_style: str
    value_system: List[str]
    expertise_areas: List[str]
    reasoning_approach: str
    decision_making_style: str
    communication_style: str


@dataclass
class DebateArgument:
    """辩论论证"""
    argument_id: str
    role_id: str
    role_name: str
    content: str
    argument_type: ArgumentType
    confidence_score: float
    reasoning_chain: List[str]
    evidence_sources: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "argument_id": self.argument_id,
            "role_id": self.role_id,
            "role_name": self.role_name,
            "content": self.content,
            "argument_type": self.argument_type.value,
            "confidence_score": self.confidence_score,
            "reasoning_chain": self.reasoning_chain,
            "evidence_sources": self.evidence_sources,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class DebateSession:
    """辩论会话"""
    debate_id: str
    topic: str
    participating_roles: List[str]
    cognitive_profiles: Dict[str, CognitiveProfile]
    phase: DebatePhase
    arguments: List[DebateArgument]
    consensus_points: List[str]
    conflicts: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime] = None


class MultiRoleDebateSystem:
    """多角色辩论系统"""
    
    def __init__(self, llm_integrator, role_manager):
        """
        初始化多角色辩论系统
        
        Args:
            llm_integrator: LLM集成器，用于真实LLM调用
            role_manager: 角色管理器，用于加载真实角色
        """
        self.llm_integrator = llm_integrator
        self.role_manager = role_manager
        
        # 辩论会话管理
        self.active_debates: Dict[str, DebateSession] = {}
        self.debate_history: List[Dict[str, Any]] = []
        
        logger.info("MultiRoleDebateSystem initialized")
    
    async def start_debate(
        self,
        debate_topic: str,
        participating_roles: List[str],
        debate_format: str = "structured",
        time_limit_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        启动多角色辩论
        
        Args:
            debate_topic: 辩论主题
            participating_roles: 参与角色ID列表
            debate_format: 辩论格式
            time_limit_minutes: 时间限制（分钟）
            
        Returns:
            辩论会话信息
        """
        try:
            debate_id = f"debate_{uuid.uuid4().hex[:8]}"
            
            # 验证和加载参与角色
            validated_roles = []
            cognitive_profiles = {}
            
            for role_id in participating_roles:
                try:
                    # 从角色管理器加载真实角色
                    role_data = await self.role_manager.get_role(role_id)
                    if not role_data:
                        logger.warning(f"Role not found: {role_id}")
                        continue
                    
                    # 分析角色认知档案
                    cognitive_profile = await self._analyze_cognitive_profile(role_id, role_data)
                    
                    validated_roles.append(role_id)
                    cognitive_profiles[role_id] = cognitive_profile
                    
                except Exception as e:
                    logger.error(f"Failed to load role {role_id}: {e}")
                    continue
            
            if len(validated_roles) < 2:
                raise ValueError("At least 2 valid roles are required for debate")
            
            # 创建辩论会话
            debate_session = DebateSession(
                debate_id=debate_id,
                topic=debate_topic,
                participating_roles=validated_roles,
                cognitive_profiles=cognitive_profiles,
                phase=DebatePhase.INITIALIZATION,
                arguments=[],
                consensus_points=[],
                conflicts=[],
                metrics={
                    "cognitive_diversity_score": 0.0,
                    "argument_quality_score": 0.0,
                    "consensus_emergence_rate": 0.0,
                    "total_arguments": 0,
                    "unique_perspectives": 0
                },
                start_time=datetime.now()
            )
            
            # 计算认知多样性分数
            diversity_score = self._calculate_cognitive_diversity(cognitive_profiles)
            debate_session.metrics["cognitive_diversity_score"] = diversity_score
            
            # 保存会话
            self.active_debates[debate_id] = debate_session
            
            logger.info(f"Started debate: {debate_id} with {len(validated_roles)} roles")
            logger.info(f"Cognitive diversity score: {diversity_score:.2f}")
            
            return {
                "debate_id": debate_id,
                "topic": debate_topic,
                "participating_roles": validated_roles,
                "cognitive_diversity_score": diversity_score,
                "phase": DebatePhase.INITIALIZATION.value,
                "status": "started"
            }
            
        except Exception as e:
            logger.error(f"Failed to start debate: {e}")
            return {"error": str(e)}
    
    async def _analyze_cognitive_profile(
        self, 
        role_id: str, 
        role_data: Dict[str, Any]
    ) -> CognitiveProfile:
        """
        分析角色认知档案
        
        Args:
            role_id: 角色ID
            role_data: 角色数据
            
        Returns:
            认知档案
        """
        try:
            # 构建认知分析提示
            analysis_prompt = f"""
            分析以下AI角色的认知特征，提取关键认知维度：
            
            角色名称: {role_data.get('name', 'Unknown')}
            角色描述: {role_data.get('description', '')}
            专业领域: {role_data.get('expertise', [])}
            价值观: {role_data.get('values', [])}
            推理风格: {role_data.get('reasoning_style', '')}
            
            请分析并返回以下认知维度：
            1. 思维风格 (analytical/intuitive/creative/systematic)
            2. 价值体系 (核心价值观列表)
            3. 专业领域 (专长领域列表)
            4. 推理方式 (deductive/inductive/abductive/analogical)
            5. 决策风格 (rational/emotional/collaborative/authoritative)
            6. 沟通风格 (direct/diplomatic/persuasive/supportive)
            
            以JSON格式返回分析结果。
            """
            
            # 调用真实LLM进行认知分析
            record = await self.llm_integrator.call_llm(
                role_id=role_id,
                user_input=analysis_prompt,
                context={
                    "analysis_type": "cognitive_profile",
                    "role_data": role_data
                }
            )
            
            if record.success:
                # 解析LLM响应
                try:
                    import json
                    analysis_result = json.loads(record.response)
                    
                    return CognitiveProfile(
                        thinking_style=analysis_result.get("thinking_style", "analytical"),
                        value_system=analysis_result.get("value_system", role_data.get('values', [])),
                        expertise_areas=analysis_result.get("expertise_areas", role_data.get('expertise', [])),
                        reasoning_approach=analysis_result.get("reasoning_approach", "deductive"),
                        decision_making_style=analysis_result.get("decision_making_style", "rational"),
                        communication_style=analysis_result.get("communication_style", "direct")
                    )
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse cognitive analysis for {role_id}")
                    
        except Exception as e:
            logger.error(f"Failed to analyze cognitive profile for {role_id}: {e}")
        
        # 回退到基于角色数据的简单分析
        return CognitiveProfile(
            thinking_style=role_data.get('reasoning_style', 'analytical'),
            value_system=role_data.get('values', []),
            expertise_areas=role_data.get('expertise', []),
            reasoning_approach="deductive",
            decision_making_style="rational",
            communication_style="direct"
        )
    
    def _calculate_cognitive_diversity(
        self, 
        cognitive_profiles: Dict[str, CognitiveProfile]
    ) -> float:
        """
        计算认知多样性分数
        
        Args:
            cognitive_profiles: 认知档案字典
            
        Returns:
            多样性分数 (0.0-1.0)
        """
        if len(cognitive_profiles) < 2:
            return 0.0
        
        # 收集所有认知维度的值
        thinking_styles = set()
        reasoning_approaches = set()
        decision_styles = set()
        communication_styles = set()
        
        for profile in cognitive_profiles.values():
            thinking_styles.add(profile.thinking_style)
            reasoning_approaches.add(profile.reasoning_approach)
            decision_styles.add(profile.decision_making_style)
            communication_styles.add(profile.communication_style)
        
        # 计算多样性分数
        max_diversity = len(cognitive_profiles)
        actual_diversity = (
            len(thinking_styles) + 
            len(reasoning_approaches) + 
            len(decision_styles) + 
            len(communication_styles)
        ) / 4.0
        
        return min(actual_diversity / max_diversity, 1.0)
    
    async def conduct_debate_round(
        self,
        debate_id: str,
        round_topic: str,
        max_arguments_per_role: int = 2
    ) -> Dict[str, Any]:
        """
        进行一轮辩论
        
        Args:
            debate_id: 辩论ID
            round_topic: 本轮主题
            max_arguments_per_role: 每个角色最大论证数
            
        Returns:
            本轮辩论结果
        """
        if debate_id not in self.active_debates:
            raise ValueError(f"Debate not found: {debate_id}")
        
        debate_session = self.active_debates[debate_id]
        round_arguments = []
        
        # 为每个角色生成论证
        for role_id in debate_session.participating_roles:
            try:
                argument = await self._generate_role_argument(
                    debate_session, role_id, round_topic
                )
                if argument:
                    round_arguments.append(argument)
                    debate_session.arguments.append(argument)
                
            except Exception as e:
                logger.error(f"Failed to generate argument for role {role_id}: {e}")
        
        # 分析论证间的冲突和共识
        conflicts = self._analyze_argument_conflicts(round_arguments)
        consensus_points = self._identify_consensus_points(round_arguments)
        
        # 更新会话状态
        debate_session.conflicts.extend(conflicts)
        debate_session.consensus_points.extend(consensus_points)
        debate_session.metrics["total_arguments"] = len(debate_session.arguments)
        debate_session.metrics["unique_perspectives"] = len(set(arg.role_id for arg in debate_session.arguments))
        
        # 计算共识涌现率
        consensus_rate = len(consensus_points) / max(len(round_arguments), 1)
        debate_session.metrics["consensus_emergence_rate"] = consensus_rate
        
        round_result = {
            "round_topic": round_topic,
            "arguments": [arg.to_dict() for arg in round_arguments],
            "conflicts": conflicts,
            "consensus_points": consensus_points,
            "consensus_emergence_rate": consensus_rate,
            "cognitive_diversity_displayed": self._measure_displayed_diversity(round_arguments)
        }
        
        logger.info(f"Debate round completed: {len(round_arguments)} arguments, "
                   f"{len(conflicts)} conflicts, {len(consensus_points)} consensus points")
        
        return round_result
    
    async def _generate_role_argument(
        self,
        debate_session: DebateSession,
        role_id: str,
        topic: str
    ) -> Optional[DebateArgument]:
        """
        为特定角色生成论证
        
        Args:
            debate_session: 辩论会话
            role_id: 角色ID
            topic: 论证主题
            
        Returns:
            生成的论证
        """
        try:
            # 获取角色数据和认知档案
            role_data = await self.role_manager.get_role(role_id)
            cognitive_profile = debate_session.cognitive_profiles[role_id]
            
            # 构建角色特定的辩论提示
            argument_prompt = f"""
            你是 {role_data.get('name', 'Unknown')}，具有以下认知特征：
            - 思维风格: {cognitive_profile.thinking_style}
            - 价值体系: {', '.join(cognitive_profile.value_system)}
            - 专业领域: {', '.join(cognitive_profile.expertise_areas)}
            - 推理方式: {cognitive_profile.reasoning_approach}
            
            当前辩论主题: {debate_session.topic}
            本轮讨论焦点: {topic}
            
            已有论证观点:
            {self._format_existing_arguments(debate_session.arguments[-3:])}
            
            请基于你的认知特征和专业背景，对本轮话题提出你的观点。
            要求：
            1. 体现你独特的思维风格和价值观
            2. 运用你的专业知识
            3. 可以支持、反对或质疑已有观点
            4. 提供清晰的推理链条
            5. 给出你的置信度评分 (0.0-1.0)
            
            请以JSON格式返回，包含：content, argument_type, confidence_score, reasoning_chain, evidence_sources
            """
            
            # 调用真实LLM生成论证
            record = await self.llm_integrator.call_llm(
                role_id=role_id,
                user_input=argument_prompt,
                context={
                    "current_task": "debate_argument_generation",
                    "debate_context": {
                        "topic": debate_session.topic,
                        "phase": debate_session.phase.value,
                        "previous_arguments": debate_session.arguments[-5:],  # 最近5个论证
                        "cognitive_profile": debate_session.cognitive_profiles.get(role_id, {})
                    },
                    "metadata": {
                        "debate_id": debate_session.debate_id,
                        "role_id": role_id,
                        "argument_generation": True
                    }
                }
            )
            
            # 适配原有的record格式
            if record.success:
                try:
                    import json
                    argument_data = json.loads(record.response)
                    
                    # 确定论证类型
                    arg_type_str = argument_data.get("argument_type", "support").lower()
                    if arg_type_str in ["support", "agree"]:
                        arg_type = ArgumentType.SUPPORT
                    elif arg_type_str in ["oppose", "disagree"]:
                        arg_type = ArgumentType.OPPOSE
                    elif arg_type_str in ["question", "query"]:
                        arg_type = ArgumentType.QUESTION
                    elif arg_type_str in ["clarification", "clarify"]:
                        arg_type = ArgumentType.CLARIFICATION
                    else:
                        arg_type = ArgumentType.SYNTHESIS
                    
                    argument = DebateArgument(
                        argument_id=f"arg_{role_id}_{int(datetime.now().timestamp())}",
                        role_id=role_id,
                        role_name=role_data.get('name', 'Unknown'),
                        content=argument_data.get("content", record.response),
                        argument_type=arg_type,
                        confidence_score=float(argument_data.get("confidence_score", 0.7)),
                        reasoning_chain=argument_data.get("reasoning_chain", []),
                        evidence_sources=argument_data.get("evidence_sources", []),
                        timestamp=datetime.now()
                    )
                    
                    return argument
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    logger.warning(f"Failed to parse argument JSON for {role_id}: {e}")
                    # 创建简单论证作为回退
                    return DebateArgument(
                        argument_id=f"arg_{role_id}_{int(datetime.now().timestamp())}",
                        role_id=role_id,
                        role_name=role_data.get('name', 'Unknown'),
                        content=record.response,
                        argument_type=ArgumentType.SUPPORT,
                        confidence_score=0.7,
                        reasoning_chain=[],
                        evidence_sources=[],
                        timestamp=datetime.now()
                    )
                
        except Exception as e:
            logger.error(f"Failed to generate argument for role {role_id}: {e}")
        
        return None
    
    def _format_existing_arguments(self, arguments: List[DebateArgument]) -> str:
        """格式化已有论证"""
        if not arguments:
            return "暂无已有论证"
        
        formatted = []
        for arg in arguments:
            formatted.append(f"- {arg.role_name}: {arg.content[:100]}...")
        
        return "\n".join(formatted)
    
    def _analyze_argument_conflicts(self, arguments: List[DebateArgument]) -> List[Dict[str, Any]]:
        """分析论证冲突"""
        conflicts = []
        
        for i, arg1 in enumerate(arguments):
            for j, arg2 in enumerate(arguments[i+1:], i+1):
                # 简单的冲突检测逻辑
                if (arg1.argument_type == ArgumentType.SUPPORT and 
                    arg2.argument_type == ArgumentType.OPPOSE):
                    conflicts.append({
                        "type": "direct_opposition",
                        "arguments": [arg1.argument_id, arg2.argument_id],
                        "roles": [arg1.role_id, arg2.role_id],
                        "description": f"{arg1.role_name} 支持观点与 {arg2.role_name} 反对观点存在直接冲突"
                    })
        
        return conflicts
    
    def _identify_consensus_points(self, arguments: List[DebateArgument]) -> List[str]:
        """识别共识点"""
        consensus_points = []
        
        # 简单的共识检测：查找多个角色都支持的观点
        support_arguments = [arg for arg in arguments if arg.argument_type == ArgumentType.SUPPORT]
        
        if len(support_arguments) >= 2:
            consensus_points.append("多个角色对主要观点表示支持")
        
        return consensus_points
    
    def _measure_displayed_diversity(self, arguments: List[DebateArgument]) -> float:
        """测量显示的认知多样性"""
        if not arguments:
            return 0.0
        
        # 基于论证类型的多样性
        arg_types = set(arg.argument_type for arg in arguments)
        type_diversity = len(arg_types) / len(ArgumentType)
        
        # 基于角色的多样性
        unique_roles = set(arg.role_id for arg in arguments)
        role_diversity = len(unique_roles) / max(len(arguments), 1)
        
        return (type_diversity + role_diversity) / 2.0
    
    async def conclude_debate(self, debate_id: str) -> Dict[str, Any]:
        """
        结束辩论并生成总结
        
        Args:
            debate_id: 辩论ID
            
        Returns:
            辩论总结
        """
        if debate_id not in self.active_debates:
            raise ValueError(f"Debate not found: {debate_id}")
        
        debate_session = self.active_debates[debate_id]
        debate_session.end_time = datetime.now()
        debate_session.phase = DebatePhase.CONCLUSION
        
        # 生成辩论总结
        summary = {
            "debate_id": debate_id,
            "topic": debate_session.topic,
            "duration_minutes": (debate_session.end_time - debate_session.start_time).total_seconds() / 60,
            "participating_roles": debate_session.participating_roles,
            "total_arguments": len(debate_session.arguments),
            "total_conflicts": len(debate_session.conflicts),
            "consensus_points": debate_session.consensus_points,
            "final_metrics": debate_session.metrics,
            "cognitive_diversity_score": debate_session.metrics["cognitive_diversity_score"],
            "consensus_emergence_rate": debate_session.metrics["consensus_emergence_rate"]
        }
        
        # 移动到历史记录
        self.debate_history.append(summary)
        del self.active_debates[debate_id]
        
        logger.info(f"Debate concluded: {debate_id}")
        
        return summary
    
    def get_debate_status(self, debate_id: str) -> Dict[str, Any]:
        """获取辩论状态"""
        if debate_id not in self.active_debates:
            return {"error": "Debate not found"}
        
        debate_session = self.active_debates[debate_id]
        
        return {
            "debate_id": debate_id,
            "topic": debate_session.topic,
            "phase": debate_session.phase.value,
            "participating_roles": debate_session.participating_roles,
            "arguments_count": len(debate_session.arguments),
            "conflicts_count": len(debate_session.conflicts),
            "consensus_points_count": len(debate_session.consensus_points),
            "metrics": debate_session.metrics,
            "start_time": debate_session.start_time.isoformat(),
            "duration_minutes": (datetime.now() - debate_session.start_time).total_seconds() / 60
        }
    
    def list_active_debates(self) -> List[Dict[str, Any]]:
        """列出活跃的辩论"""
        return [
            {
                "debate_id": debate_id,
                "topic": session.topic,
                "phase": session.phase.value,
                "participants": len(session.participating_roles),
                "arguments": len(session.arguments)
            }
            for debate_id, session in self.active_debates.items()
        ]


# 便捷函数
async def create_multi_role_debate_system(llm_integrator, role_manager) -> MultiRoleDebateSystem:
    """创建多角色辩论系统实例"""
    return MultiRoleDebateSystem(llm_integrator, role_manager)


# 测试函数
async def test_debate_system():
    """测试辩论系统"""
    # 这里可以添加测试代码
    pass


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_debate_system())