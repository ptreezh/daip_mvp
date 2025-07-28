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
                    workflow_type=workflow_type,
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
                workflow_type=WorkflowType.CRITICAL_REVIEW,
                confidence=0.70,
                reasoning="基于关键词的本地分析：建议使用批判性审查工作流",
                topic=user_input
            )
        elif any(keyword in user_input.lower() for keyword in ["讨论", "观点", "角度", "看法"]):
            return IntentResult(
                workflow_type=WorkflowType.MULTI_PERSPECTIVE,
                confidence=0.65,
                reasoning="基于关键词的本地分析：建议使用多视角综合工作流",
                topic=user_input
            )
        else:
            return IntentResult(
                workflow_type=WorkflowType.CRITICAL_REVIEW,
                confidence=0.50,
                reasoning="默认使用批判性审查工作流",
                topic=user_input
            )
    
    async def assemble_team(self, topic: str, workflow_type: WorkflowType) -> TeamProposal:
        """组建专家团队"""
        try:
            await self._ensure_backend_service()
            
            # 从后端获取可用角色
            available_roles = await self.backend_service.get_available_roles()
            
            if available_roles:
                # 根据工作流类型和可用角色智能选择团队
                team_agents = await self._select_optimal_team(available_roles, workflow_type, topic)
                diversity_score = self._calculate_team_diversity(team_agents)
                
                return TeamProposal(
                    agents=[agent["name"] for agent in team_agents],
                    diversity_score=diversity_score,
                    rationale=f"基于{len(available_roles)}个可用角色为'{topic}'智能选择的团队",
                    confirmation_message=f"我将让{', '.join([agent['name'] for agent in team_agents])}使用{workflow_type.value}流程分析。继续吗？"
                )
            else:
                # 后端不可用时的降级处理
                return await self._fallback_team_assembly(topic, workflow_type)
                
        except Exception as e:
            logger.error(f"团队组建失败: {e}")
            return await self._fallback_team_assembly(topic, workflow_type)
    
    async def _select_optimal_team(self, available_roles: List[Dict], workflow_type: WorkflowType, topic: str) -> List[Dict]:
        """从可用角色中选择最优团队"""
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
        
        # 简单的多样性计算：基于角色描述的差异性
        unique_keywords = set()
        for agent in team_agents:
            description = agent.get("description", "").lower()
            words = description.split()
            unique_keywords.update(words[:5])  # 取前5个词作为特征
        
        # 多样性 = 独特关键词数量 / (团队大小 * 5)
        diversity_score = min(len(unique_keywords) / (len(team_agents) * 5), 1.0)
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

            # Analyze user intent
            intent_analysis = await self.analyze_intent(user_input, context)

            # Assemble team
            team = await self.assemble_team(intent_analysis.topic, intent_analysis.workflow_type)
            
            # Generate response content
            response_content = f"""我理解您想要{intent_analysis.reasoning}

{team.confirmation_message}

**团队组成：** {', '.join(team.agents)}
**多样性评分：** {team.diversity_score:.2f}
**置信度：** {intent_analysis.confidence:.2f}

如果您确认，我将启动工作流开始分析。您也可以输入 `/consensus now` 来查看当前讨论的共识状态。"""
            
            # Update conversation context
            context["last_intent"] = intent_analysis
            context["proposed_team"] = team
            context["active_agents"] = team.agents
            
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
                
                # 模拟收集当前讨论的输入数据
                inputs = []
                if "active_agents" in context:
                    for i, agent in enumerate(context["active_agents"]):
                        inputs.append({
                            "position": f"{agent}的观点：基于当前讨论的立场 {i+1}",
                            "confidence": 0.75 + (i * 0.05),  # 模拟不同的置信度
                            "agent_id": agent,
                            "reasoning": f"基于{agent}的认知框架得出的结论"
                        })
                
                if inputs:
                    # 调用后端共识计算
                    consensus_result = await self.backend_service.execute_consensus(inputs)
                    
                    if "error" not in consensus_result:
                        return f"""**共识计算完成** 🎯

**算法类型：** {consensus_result.get('algorithm_type', 'simple_majority_vote')}
**共识强度：** {consensus_result.get('consensus_strength', 0.0):.2f}
**参与代理：** {len(inputs)}个

**结果摘要：**
{consensus_result.get('summary', '共识计算已完成，详细结果请查看透明度监控面板。')}

**置信度：** {consensus_result.get('confidence', 0.0):.2f}"""
                    else:
                        return f"共识计算失败：{consensus_result['error']}"
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
