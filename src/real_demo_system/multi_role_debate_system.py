#!/usr/bin/env python3
"""多角色辩论系统

基于设计文档实现的真实多角色辩论系统，支持：
- 从真实角色库加载认知代理
- 真实LLM调用生成角色观点
- 多视角辩论和共识形成
- 透明度监控和真实性验证
"""

import asyncio
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

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
    value_system: list[str]
    expertise_areas: list[str]
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
    reasoning_chain: list[str]
    evidence_sources: list[str]
    timestamp: datetime
    
    def to_dict(self) -> dict[str, Any]:
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
    participating_roles: list[str]
    cognitive_profiles: dict[str, CognitiveProfile]
    phase: DebatePhase
    arguments: list[DebateArgument]
    consensus_points: list[str]
    conflicts: list[dict[str, Any]]
    metrics: dict[str, Any]
    start_time: datetime
    max_rounds: int
    end_time: Optional[datetime] = None

class MultiRoleDebateSystem:
    """多角色辩论系统"""
    
    def __init__(self, llm_integrator, role_manager):
        """初始化多角色辩论系统
        
        Args:
            llm_integrator: LLM集成器，用于真实LLM调用
            role_manager: 角色管理器，用于加载真实角色
        """
        self.llm_integrator = llm_integrator
        self.role_manager = role_manager
        
        # 辩论会话管理
        self.active_debates: dict[str, DebateSession] = {}
        self.debate_history: list[dict[str, Any]] = []
        
        logger.info("MultiRoleDebateSystem initialized")

    async def run_full_debate(self, debate_id: str) -> dict[str, Any]:
        """运行完整的辩论流程"""
        if debate_id not in self.active_debates:
            raise ValueError(f"Debate not found: {debate_id}")

        debate_session = self.active_debates[debate_id]
        
        for i in range(debate_session.max_rounds):
            round_topic = f"第 {i+1} 轮辩论"
            await self.conduct_debate_round(debate_id, round_topic)

        return await self.conclude_debate(debate_id)

    
    async def start_debate(
        self,
        debate_topic: str,
        participating_roles: list[str],
        debate_format: str = "structured",
        time_limit_minutes: int = 30,
        max_rounds: int = 5
    ) -> dict[str, Any]:
        """启动多角色辩论
        
        Args:
            debate_topic: 辩论主题
            participating_roles: 参与角色ID列表
            debate_format: 辩论格式
            time_limit_minutes: 时间限制（分钟）
            max_rounds: 最大辩论轮数
            
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
                    role = self.role_manager.get_role(role_id)
                    if not role:
                        logger.warning(f"Role not found: {role_id}")
                        continue
                    
                    # 转换Role对象为字典格式，确保所有值都是可序列化的
                    role_data = {
                        "role_id": str(role.id),
                        "name": str(role.name),
                        "description": str(role.description),
                        "capabilities": list(getattr(role, 'capabilities', [])),
                        "values": list(getattr(role, 'values', [])),
                        "reasoning_style": str(getattr(role, 'reasoning_style', 'analytical'))
                    }

                    
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
                start_time=datetime.now(),
                max_rounds=max_rounds
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
        role_data: dict[str, Any]
    ) -> CognitiveProfile:
        """分析角色认知档案 - 简化版本，避免LLM解析问题
        
        Args:
            role_id: 角色ID
            role_data: 角色数据
            
        Returns:
            认知档案
        """
        # 直接基于角色数据构建认知档案，避免LLM解析问题
        logger.info(f"Creating cognitive profile for {role_id} without LLM analysis")
        
        # 从角色数据中提取信息
        capabilities = role_data.get('capabilities', [])
        description = role_data.get('description', '')
        
        # 基于描述和能力推断认知特征
        thinking_style = "analytical"
        if "creative" in description.lower() or "innovation" in description.lower():
            thinking_style = "creative"
        elif "systematic" in description.lower() or "process" in description.lower():
            thinking_style = "systematic"
        elif "intuitive" in description.lower():
            thinking_style = "intuitive"
        
        communication_style = "direct"
        if "diplomatic" in description.lower() or "negotiation" in description.lower():
            communication_style = "diplomatic"
        elif "persuasive" in description.lower() or "influence" in description.lower():
            communication_style = "persuasive"
        elif "supportive" in description.lower() or "collaborative" in description.lower():
            communication_style = "supportive"
        
        return CognitiveProfile(
            thinking_style=thinking_style,
            value_system=capabilities[:3] if capabilities else ["expertise", "accuracy", "helpfulness"],
            expertise_areas=capabilities if capabilities else ["general"],
            reasoning_approach="deductive",
            decision_making_style="rational",
            communication_style=communication_style
        )
    
    def _calculate_cognitive_diversity(
        self, 
        cognitive_profiles: dict[str, CognitiveProfile]
    ) -> float:
        """计算认知多样性分数
        
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
    ) -> dict[str, Any]:
        """进行一轮辩论
        
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
        
        logger.info(f"--- Starting Debate Round for '{debate_id}' on topic: {round_topic} ---")

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
        
        logger.info(f"--- Debate Round Completed: {len(round_arguments)} arguments, "
                   f"{len(conflicts)} conflicts, {len(consensus_points)} consensus points ---")
        
        return round_result
    
    async def _generate_role_argument(
        self,
        debate_session: DebateSession,
        role_id: str,
        topic: str
    ) -> Optional[DebateArgument]:
        """为特定角色生成论证
        
        Args:
            debate_session: 辩论会话
            role_id: 角色ID
            topic: 论证主题
            
        Returns:
            生成的论证
        """
        try:
            # 获取角色数据和认知档案
            role = self.role_manager.get_role(role_id)
            if not role:
                raise ValueError(f"Role {role_id} not found")
            role_data = role.to_dict()
            cognitive_profile = debate_session.cognitive_profiles[role_id]
            
            logger.info(f"Generating argument for role: {role_data.get('name', role_id)}...")

            # 构建角色特定的辩论提示
            argument_prompt = f"""
            You are {role_data.get('name', 'Unknown')}, a professional AI agent. Your task is to provide a structured argument for a debate.
            Your response MUST be a single, valid JSON object. Do not include any text, conversation, or explanation before or after the JSON object.
            
            The debate topic is: "{debate_session.topic}"
            This round's focus is: "{topic}"
            
            Your cognitive profile:
            - Thinking Style: {cognitive_profile.thinking_style}
            - Value System: {', '.join(cognitive_profile.value_system)}
            - Expertise: {', '.join(cognitive_profile.expertise_areas)}

            Recent arguments for context:
            {self._format_existing_arguments(debate_session.arguments[-3:])}

            Please generate your argument in the following JSON structure:
            {{
                "content": "Your detailed argument, based on your profile.",
                "argument_type": "support | oppose | question | clarification | synthesis",
                "confidence_score": <a float between 0.0 and 1.0>,
                "reasoning_chain": ["Step-by-step reasoning for your argument."],
                "evidence_sources": ["List of sources, if any."]
            }}
            """
            
            # 调用真实LLM生成论证
            record = await self.llm_integrator.call_llm(
                prompt=argument_prompt,
                metadata={
                    "current_task": "debate_argument_generation",
                    "debate_context": {
                        "topic": debate_session.topic,
                        "phase": debate_session.phase.value,
                        "previous_arguments": [arg.to_dict() for arg in debate_session.arguments[-5:]],  # 最近5个论证
                        "cognitive_profile": asdict(debate_session.cognitive_profiles.get(role_id))
                    },
                    "debate_id": debate_session.debate_id,
                    "role_id": role_id,
                    "argument_generation": True
                }
            )
            
            # 适配原有的record格式
            if record.success:
                import json
                
                response_text = record.response
                
                # --- Enhanced Preprocessing Logic ---
                try:
                    # Find the start and end of the JSON object
                    start_index = response_text.find('{')
                    end_index = response_text.rfind('}') + 1
                    
                    if start_index != -1 and end_index != 0:
                        json_str = response_text[start_index:end_index]
                        argument_data = json.loads(json_str)
                        
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
                            content=argument_data.get("content", response_text),
                            argument_type=arg_type,
                            confidence_score=float(argument_data.get("confidence_score", 0.7)),
                            reasoning_chain=argument_data.get("reasoning_chain", []),
                            evidence_sources=argument_data.get("evidence_sources", []),
                            timestamp=datetime.now()
                        )
                        
                        logger.info(f"Successfully generated argument for {role_data.get('name', role_id)}. Type: {argument.argument_type.value}, Confidence: {argument.confidence_score}")
                        return argument
                    else:
                        # Raise an error to be caught by the outer handler
                        raise json.JSONDecodeError("Could not find JSON object in response", response_text, 0)

                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON for {role_id}. Error: {e}.\n--- LLM Raw Response ---\n{response_text}\n------------------------")
                    # 创建简单论证作为回退
                    return DebateArgument(
                        argument_id=f"arg_{role_id}_{int(datetime.now().timestamp())}",
                        role_id=role_id,
                        role_name=role_data.get('name', 'Unknown'),
                        content=response_text,
                        argument_type=ArgumentType.SUPPORT,
                        confidence_score=0.5,
                        reasoning_chain=["Fallback due to parsing error."],
                        evidence_sources=[],
                        timestamp=datetime.now()
                    )
                
        except Exception as e:
            logger.error(f"Failed to generate argument for role {role_id}: {e}")
        
        return None
    
    def _format_existing_arguments(self, arguments: list[DebateArgument]) -> str:
        """格式化已有论证"""
        if not arguments:
            return "暂无已有论证"
        
        formatted = []
        for arg in arguments:
            formatted.append(f"- {arg.role_name}: {arg.content[:100]}...")
        
        return "\n".join(formatted)
    
    def _analyze_argument_conflicts(self, arguments: list[DebateArgument]) -> list[dict[str, Any]]:
        """分析论证冲突"""
        conflicts = []
        
        for i, arg1 in enumerate(arguments):
            for j, arg2 in enumerate(arguments[i+1:], i+1):
                # 简单的冲突检测逻辑
                if (
                    arg1.argument_type == ArgumentType.SUPPORT and 
                    arg2.argument_type == ArgumentType.OPPOSE
                ):
                    conflicts.append({
                        "type": "direct_opposition",
                        "arguments": [arg1.argument_id, arg2.argument_id],
                        "roles": [arg1.role_id, arg2.role_id],
                        "description": f"{arg1.role_name} 支持观点与 {arg2.role_name} 反对观点存在直接冲突"
                    })
        
        return conflicts
    
    def _identify_consensus_points(self, arguments: list[DebateArgument]) -> list[str]:
        """识别共识点"""
        consensus_points = []
        
        # 简单的共识检测：查找多个角色都支持的观点
        support_arguments = [arg for arg in arguments if arg.argument_type == ArgumentType.SUPPORT]
        
        if len(support_arguments) >= 2:
            consensus_points.append("多个角色对主要观点表示支持")
        
        return consensus_points
    
    def _measure_displayed_diversity(self, arguments: list[DebateArgument]) -> float:
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
    
    async def conclude_debate(self, debate_id: str) -> dict[str, Any]:
        """结束辩论并生成总结
        
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
            "consensus_emergence_rate": debate_session.metrics["consensus_emergence_rate"],
            "transcript": [arg.to_dict() for arg in debate_session.arguments]
        }
        
        # 移动到历史记录
        self.debate_history.append(summary)
        del self.active_debates[debate_id]
        
        logger.info(f"Debate concluded: {debate_id}")
        
        return summary
    
    def get_debate_status(self, debate_id: str) -> dict[str, Any]:
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
    
    def list_active_debates(self) -> list[dict[str, Any]]:
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