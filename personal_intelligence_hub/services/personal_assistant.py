#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Intelligence Hub - Personal Assistant Service

个人助手服务，负责处理用户交互、意图分析、工作流编排等核心功能
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import uuid
from datetime import datetime
from enum import Enum

from personal_intelligence_hub.models.chat_models import ChatMessage, MessageType
from personal_intelligence_hub.services.backend_integration import get_backend_service

# 配置日志
logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """工作流类型枚举"""
    CRITICAL_REVIEW = "critical_review"
    MULTI_PERSPECTIVE = "multi_perspective"
    CUSTOM = "custom"


@dataclass
class IntentResult:
    """意图分析结果"""
    workflowType: WorkflowType
    confidence: float
    reasoning: str
    topic: str


@dataclass
class TeamProposal:
    """团队提议"""
    agents: List[str]
    diversity_score: float
    rationale: str
    confirmation_message: str


class PersonalAssistantService:
    """个人助手服务主类"""
    
    def __init__(self):
        self.conversation_contexts: Dict[str, Any] = {}
        self.backend_service = None
        logger.info("Personal Assistant Service 初始化完成")
    
    async def _ensure_backend_service(self):
        """确保后端服务已初始化"""
        if self.backend_service is None:
            self.backend_service = await get_backend_service()
    
    async def analyze_intent(self, user_input: str, context: Optional[Dict] = None) -> IntentResult:
        """分析用户意图"""
        try:
            await self._ensure_backend_service()
            
            # 调用后端意图分析服务
            user_id = context.get("user_id", "default_user") if context else "default_user"
            message_history = context.get("message_history", []) if context else []
            
            # 转换消息历史为后端期望的格式
            backend_context = []
            for msg in message_history[-5:]:  # 只取最近5条消息作为上下文
                if isinstance(msg, ChatMessage):
                    backend_context.append({
                        "sender": msg.sender,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    })
            
            result = await self.backend_service.analyze_intent(user_input, user_id, backend_context)
            
            if "error" not in result:
                # 解析后端返回的结果
                workflow_mapping = {
                    "critical_review": WorkflowType.CRITICAL_REVIEW,
                    "multi_perspective": WorkflowType.MULTI_PERSPECTIVE,
                    "custom": WorkflowType.CUSTOM
                }
                
                workflow_type = workflow_mapping.get(
                    result.get("workflow_type", "critical_review"), 
                    WorkflowType.CRITICAL_REVIEW
                )
                
                return IntentResult(
                    workflowType=workflow_type,
                    confidence=result.get("confidence", 0.75),
                    reasoning=result.get("reasoning", "基于后端分析的结果"),
                    topic=result.get("topic", user_input)
                )
            else:
                # 后端服务不可用时的降级处理
                return await self._fallback_intent_analysis(user_input)
                
        except Exception as e:
            logger.error(f"意图分析失败: {e}")
            return await self._fallback_intent_analysis(user_input)
    
    async def _fallback_intent_analysis(self, user_input: str) -> IntentResult:
        """降级意图分析（本地简单规则）"""
        if any(keyword in user_input.lower() for keyword in ["分析", "审查", "评估", "检查"]):
            return IntentResult(
                workflowType=WorkflowType.CRITICAL_REVIEW,
                confidence=0.70,
                reasoning="基于关键词的本地分析：建议使用批判性审查工作流",
                topic=user_input
            )
        elif any(keyword in user_input.lower() for keyword in ["讨论", "观点", "角度", "看法"]):
            return IntentResult(
                workflowType=WorkflowType.MULTI_PERSPECTIVE,
                confidence=0.65,
                reasoning="基于关键词的本地分析：建议使用多视角综合工作流",
                topic=user_input
            )
        else:
            return IntentResult(
                workflowType=WorkflowType.CRITICAL_REVIEW,
                confidence=0.50,
                reasoning="默认使用批判性审查工作流",
                topic=user_input
            )
    
    async def assemble_team(self, topic: str, workflow_type: WorkflowType) -> TeamProposal:
        """组建专家团队 - 混合模式：本地角色数据 + 智能选择算法"""
        try:
            # 策略：本地角色数据更可靠，用作主要数据源
            if not hasattr(self, 'role_manager'):
                from src.core_services.role_manager import RoleManager
                self.role_manager = RoleManager()
            
            # 获取本地角色数据
            local_roles = self.role_manager.list_roles()
            
            if local_roles:
                # 转换为统一格式，优化角色名称显示
                available_roles = []
                for role in local_roles:
                    # 优化角色名称：提取关键信息
                    display_name = self._optimize_role_name(role.name)
                    
                    available_roles.append({
                        "id": role.id,
                        "name": display_name,
                        "original_name": role.name,
                        "description": role.description,
                        "capabilities": role.capabilities
                    })
                
                # 使用本地智能选择算法
                team_agents = await self._select_optimal_team(available_roles, workflow_type, topic)
                diversity_score = self._calculate_team_diversity(team_agents)
                
                return TeamProposal(
                    agents=[agent["name"] for agent in team_agents],
                    diversity_score=diversity_score,
                    rationale=f"基于{len(available_roles)}个本地角色为'{topic}'智能选择的团队",
                    confirmation_message=f"我将让{', '.join([agent['name'] for agent in team_agents])}使用{workflow_type.value}流程分析。继续吗？"
                )
            else:
                # 本地角色不可用时的降级处理
                logger.warning("本地角色数据不可用，使用默认团队")
                return await self._fallback_team_assembly(topic, workflow_type)
                
        except Exception as e:
            logger.error(f"团队组建失败: {e}")
            return await self._fallback_team_assembly(topic, workflow_type)
    
    def _optimize_role_name(self, original_name: str) -> str:
        """优化角色名称显示"""
        # 如果名称太长，提取关键信息
        if len(original_name) > 50:
            # 尝试提取角色类型关键词
            keywords = ["Expert", "Specialist", "Analyst", "Manager", "Reviewer", "Architect", "Consultant"]
            for keyword in keywords:
                if keyword in original_name:
                    # 提取包含关键词的部分
                    parts = original_name.split()
                    relevant_parts = []
                    for i, part in enumerate(parts):
                        if keyword in part or (i > 0 and keyword in parts[i-1]) or (i < len(parts)-1 and keyword in parts[i+1]):
                            relevant_parts.append(part)
                    
                    if relevant_parts:
                        optimized = " ".join(relevant_parts[:3])  # 最多3个词
                        return optimized if len(optimized) < 50 else optimized[:47] + "..."
            
            # 如果没有找到关键词，截取前50个字符
            return original_name[:47] + "..."
        
        return original_name
    
    async def _local_consensus_calculation(self, inputs: List[Dict[str, Any]]) -> str:
        """本地共识计算实现 - 使用高级共识算法"""
        try:
            if not inputs:
                return "没有足够的输入数据进行共识计算"
            
            # 使用系统中的高级共识算法
            if not hasattr(self, 'consensus_algorithms'):
                from src.core_services.advanced_consensus_algorithms import AdvancedConsensusAlgorithms
                self.consensus_algorithms = AdvancedConsensusAlgorithms()
            
            # 转换输入格式为ConsensusInput
            from src.core_services.advanced_consensus_algorithms import ConsensusInput
            consensus_inputs = []
            
            for input_data in inputs:
                consensus_input = ConsensusInput(
                    agent_id=input_data.get("agent_id", "unknown"),
                    position=input_data.get("position", ""),
                    confidence=input_data.get("confidence", 0.5),
                    reasoning=input_data.get("reasoning", ""),
                    timestamp=datetime.now()
                )
                consensus_inputs.append(consensus_input)
            
            # 执行高级共识算法
            consensus_result = await self.consensus_algorithms.calculate_consensus(
                consensus_inputs,
                algorithm_type="weighted_voting"  # 使用加权投票算法
            )
            
            if consensus_result and hasattr(consensus_result, 'consensus_value'):
                return f"""**高级共识计算完成** 🎯

**算法类型：** {consensus_result.algorithm_used}
**共识强度：** {consensus_result.confidence:.2f}
**参与代理：** {len(inputs)}个

**结果摘要：**
{consensus_result.summary if hasattr(consensus_result, 'summary') else '基于高级算法的共识分析已完成'}

**共识值：** {consensus_result.consensus_value}
**置信度：** {consensus_result.confidence:.2f}

*使用本地高级共识算法计算*"""
            else:
                # 降级到简单算法
                return await self._simple_consensus_calculation(inputs)
            
        except Exception as e:
            logger.warning(f"高级共识计算失败: {e}，使用简单算法")
            return await self._simple_consensus_calculation(inputs)
    
    async def _simple_consensus_calculation(self, inputs: List[Dict[str, Any]]) -> str:
        """简单共识计算实现（降级版本）"""
        try:
            # 简化的共识算法：基于置信度加权平均
            total_confidence = 0.0
            position_count = {}
            
            for input_data in inputs:
                confidence = input_data.get("confidence", 0.5)
                position = input_data.get("position", "")
                
                total_confidence += confidence
                
                # 统计立场关键词
                position_words = position.lower().split()
                for word in position_words[:5]:  # 只取前5个词
                    if len(word) > 3:  # 过滤短词
                        position_count[word] = position_count.get(word, 0) + confidence
            
            # 计算共识强度
            avg_confidence = total_confidence / len(inputs)
            
            # 找出最高频的关键词作为共识点
            if position_count:
                consensus_keywords = sorted(position_count.items(), key=lambda x: x[1], reverse=True)[:3]
                consensus_points = [kw[0] for kw in consensus_keywords]
            else:
                consensus_points = ["协作", "分析", "讨论"]
            
            # 生成共识摘要
            summary = f"基于{len(inputs)}个专业观点的分析，在{', '.join(consensus_points)}等方面形成了共识。"
            
            return f"""**简单共识计算完成** 🎯

**算法类型：** 置信度加权分析
**共识强度：** {avg_confidence:.2f}
**参与代理：** {len(inputs)}个

**结果摘要：**
{summary}

**主要共识点：**
{chr(10).join([f"• {point}" for point in consensus_points])}

**置信度：** {avg_confidence:.2f}"""
            
        except Exception as e:
            logger.error(f"简单共识计算失败: {e}")
            return f"共识计算失败：{str(e)}"
    
    async def _select_optimal_team(self, available_roles: List[Dict], workflow_type: WorkflowType, topic: str) -> List[Dict]:
        """从可用角色中选择最优团队"""
        # 验证输入数据类型
        if not isinstance(available_roles, list):
            logger.warning(f"available_roles不是列表类型: {type(available_roles)}")
            return []
        
        # 根据工作流类型定义角色偏好
        role_preferences = {
            WorkflowType.CRITICAL_REVIEW: ["critic", "analyst", "validator", "expert"],
            WorkflowType.MULTI_PERSPECTIVE: ["advocate", "skeptic", "moderator", "philosopher"],
            WorkflowType.CUSTOM: ["generalist", "specialist", "coordinator"]
        }
        
        preferred_keywords = role_preferences.get(workflow_type, ["generalist"])
        selected_roles = []
        
        # 优先选择匹配的角色
        for role in available_roles:
            # 确保role是字典类型
            if not isinstance(role, dict):
                logger.warning(f"角色不是字典类型: {type(role)}")
                continue
                
            role_name_lower = role.get("name", "").lower()
            role_description_lower = role.get("description", "").lower()
            
            for keyword in preferred_keywords:
                if keyword in role_name_lower or keyword in role_description_lower:
                    selected_roles.append(role)
                    break
            
            if len(selected_roles) >= 3:  # 限制团队大小
                break
        
        # 如果选择的角色不足，添加通用角色
        if len(selected_roles) < 2:
            for role in available_roles:
                if role not in selected_roles:
                    selected_roles.append(role)
                    if len(selected_roles) >= 3:
                        break
        
        return selected_roles[:3]  # 最多3个角色
    
    def _calculate_team_diversity(self, team_agents: List[Dict]) -> float:
        """计算团队多样性评分"""
        if not team_agents:
            return 0.0
        
        # 验证输入数据类型
        if not isinstance(team_agents, list):
            logger.warning(f"team_agents不是列表类型: {type(team_agents)}")
            return 0.0
        
        # 简单的多样性计算：基于角色描述的差异性
        unique_keywords = set()
        for agent in team_agents:
            # 确保agent是字典类型
            if not isinstance(agent, dict):
                logger.warning(f"代理不是字典类型: {type(agent)}")
                continue
                
            description = agent.get("description", "").lower()
            words = description.split()
            unique_keywords.update(words[:5])  # 取前5个词作为特征
        
        # 多样性 = 独特关键词数量 / (团队大小 * 5)
        if len(team_agents) > 0:
            diversity_score = min(len(unique_keywords) / (len(team_agents) * 5), 1.0)
        else:
            diversity_score = 0.0
        return round(diversity_score, 2)
    
    async def _fallback_team_assembly(self, topic: str, workflow_type: WorkflowType) -> TeamProposal:
        """降级团队组建（本地默认配置）"""
        if workflow_type == WorkflowType.CRITICAL_REVIEW:
            agents = ["Critic-AI", "Analyst-AI", "Validator-AI"]
            rationale = f"为批判性审查'{topic}'选择的默认专业团队"
        elif workflow_type == WorkflowType.MULTI_PERSPECTIVE:
            agents = ["Advocate-AI", "Skeptic-AI", "Moderator-AI"]
            rationale = f"为多角度讨论'{topic}'选择的默认多元化团队"
        else:
            agents = ["General-AI"]
            rationale = f"为处理'{topic}'选择的默认通用团队"
        
        return TeamProposal(
            agents=agents,
            diversity_score=0.75,
            rationale=rationale,
            confirmation_message=f"我将让{', '.join(agents)}使用{workflow_type.value}流程分析。继续吗？"
        )
    
    async def process_message(self, user_input: str, session_id: str) -> str:
        """处理用户消息并返回响应字符串"""
        try:
            # Get conversation context
            context = self.get_conversation_context(session_id)
            context["user_id"] = context.get("user_id", "default_user")

            # 保存用户消息到历史
            user_message = {
                "sender": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            }
            context["message_history"].append(user_message)

            # Analyze user intent
            intent_analysis = await self.analyze_intent(user_input, context)

            # Assemble team
            team = await self.assemble_team(intent_analysis.topic, intent_analysis.workflowType)
            
            # Generate response content
            response_content = f"""我理解您想要{intent_analysis.reasoning}

{team.confirmation_message}

**团队组成：** {', '.join(team.agents)}
**多样性评分：** {team.diversity_score:.2f}
**置信度：** {intent_analysis.confidence:.2f}

如果您确认，我将启动工作流开始分析。您也可以输入 `/consensus now` 来查看当前讨论的共识状态。"""
            
            # 保存助手回复到历史
            assistant_message = {
                "sender": "assistant",
                "content": response_content,
                "timestamp": datetime.now().isoformat()
            }
            context["message_history"].append(assistant_message)
            
            # Update conversation context
            context["last_intent"] = intent_analysis
            context["proposed_team"] = team
            context["active_agents"] = team.agents
            
            # 保持历史记录在合理范围内
            if len(context["message_history"]) > 50:
                context["message_history"] = context["message_history"][-30:]
            
            return response_content
            
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return f"抱歉，处理您的请求时出错：{str(e)}"
    
    def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """获取对话上下文"""
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = {
                "session_id": session_id,
                "message_history": [],
                "current_workflow": None,
                "active_agents": []
            }
        return self.conversation_contexts[session_id]

    async def execute_command(self, command: str, session_id: str) -> str:
        """执行用户输入的命令"""
        try:
            if command == "/consensus now":
                await self._ensure_backend_service()
                logger.info(f"Executing command: /consensus now for session {session_id}")
                
                context = self.get_conversation_context(session_id)
                
                # 基于真实对话历史收集讨论数据
                inputs = []
                if "active_agents" in context and context.get("message_history"):
                    # 从消息历史中提取相关内容
                    recent_messages = context["message_history"][-10:]  # 最近10条消息
                    discussion_content = " ".join([msg["content"] for msg in recent_messages if msg["sender"] == "user"])
                    
                    for i, agent in enumerate(context["active_agents"]):
                        inputs.append({
                            "position": f"{agent}基于讨论内容'{discussion_content[:100]}...'的专业观点",
                            "confidence": 0.75 + (i * 0.05),  # 模拟不同的置信度
                            "agent_id": agent,
                            "reasoning": f"基于{agent}的认知框架和当前讨论内容得出的结论"
                        })
                
                if inputs:
                    # 正确策略：通过工具管理器调用SimpleMajorityVoteStrategy
                    try:
                        # 尝试通过后端工具管理器调用
                        consensus_result = await self.backend_service.execute_consensus(inputs, "simple_majority_vote")
                        
                        if "error" not in consensus_result:
                            return f"""**共识计算完成** 🎯

**算法类型：** {consensus_result.get('algorithm_type', 'simple_majority_vote')}
**共识强度：** {consensus_result.get('consensus_strength', 0.0):.2f}
**参与代理：** {len(inputs)}个

**结果摘要：**
{consensus_result.get('summary', '共识计算已完成')}

**置信度：** {consensus_result.get('confidence', 0.0):.2f}"""
                        else:
                            # 工具调用失败，使用本地高级算法
                            return await self._local_consensus_calculation(inputs)
                    except Exception as e:
                        logger.warning(f"工具管理器共识计算失败: {e}，使用本地算法")
                        return await self._local_consensus_calculation(inputs)
                else:
                    return "当前没有活跃的讨论可以计算共识。请先启动一个工作流。"
                    
            elif command == "/help":
                return """**可用命令：**

`/consensus now` - 计算当前讨论的共识状态
`/help` - 显示帮助信息
`/status` - 显示系统状态
`/clear` - 清除当前会话

您也可以直接输入自然语言来启动新的分析工作流。"""

            elif command == "/status":
                await self._ensure_backend_service()
                health_status = await self.backend_service.check_backend_health()
                
                status_info = []
                for service_name, status in health_status.items():
                    status_emoji = {
                        "healthy": "✅",
                        "degraded": "⚠️", 
                        "unhealthy": "❌",
                        "unavailable": "🔴"
                    }.get(status.status.value, "❓")
                    
                    status_info.append(f"{status_emoji} {status.service_name}: {status.status.value}")
                
                return f"""**系统状态：**

{chr(10).join(status_info)}

**响应时间：** {health_status.get('backend', type('obj', (object,), {'response_time': 0.0})).response_time:.2f}s
**最后检查：** {datetime.now().strftime('%H:%M:%S')}"""

            elif command == "/clear":
                if session_id in self.conversation_contexts:
                    del self.conversation_contexts[session_id]
                return "会话已清除。您可以开始新的对话。"
                
            else:
                logger.warning(f"Unknown command received: {command}")
                return f"未知命令: {command}。输入 `/help` 查看可用命令。"
                
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return f"执行命令 '{command}' 时出错: {str(e)}"
