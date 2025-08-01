#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于LLM的智能工作流选择器

使用真实的LLM调用进行语义理解，支持：
1. 基于语义的智能工作流选择
2. 自然语言描述新增工作流
3. 动态学习和优化工作流匹配
"""

import logging
import json
import asyncio
import requests
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class ScenarioType(Enum):
    """场景类型枚举"""
    ACADEMIC_RESEARCH = "academic_research"      # 学术研究
    EXPERT_CONSULTATION = "expert_consultation"  # 专家咨询
    CASUAL_DISCUSSION = "casual_discussion"      # 轻松讨论


class WorkflowType(Enum):
    """工作流类型枚举"""
    CRITICAL_REVIEW = "critical_review"
    MULTI_PERSPECTIVE = "multi_perspective"
    CUSTOM = "custom"


@dataclass
class WorkflowDefinition:
    """工作流定义"""
    name: str
    type: WorkflowType
    description: str
    scenario_types: List[ScenarioType]
    keywords: List[str]
    examples: List[str]
    created_at: datetime
    usage_count: int = 0
    success_rate: float = 1.0


@dataclass
class LLMIntentResult:
    """基于LLM的意图分析结果"""
    workflow_type: WorkflowType
    scenario_type: ScenarioType
    confidence: float
    reasoning: str
    topic: str
    semantic_analysis: Dict[str, Any]
    suggested_improvements: List[str] = None


class LLMBasedWorkflowSelector:
    """基于LLM的工作流选择器"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """初始化LLM工作流选择器"""
        self.ollama_url = ollama_url
        self.model_name = "qwen3:8b"  # 使用可用的模型
        self.workflows_db_path = "workflows_database.json"
        self.workflows = self._load_workflows()
        logger.info(f"LLM-based Workflow Selector initialized with model: {self.model_name}")
    
    def _load_workflows(self) -> Dict[str, WorkflowDefinition]:
        """加载工作流定义数据库"""
        if os.path.exists(self.workflows_db_path):
            try:
                with open(self.workflows_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    workflows = {}
                    for key, value in data.items():
                        # 转换回WorkflowDefinition对象
                        value['type'] = WorkflowType(value['type'])
                        value['scenario_types'] = [ScenarioType(st) for st in value['scenario_types']]
                        value['created_at'] = datetime.fromisoformat(value['created_at'])
                        workflows[key] = WorkflowDefinition(**value)
                    return workflows
            except Exception as e:
                logger.warning(f"Failed to load workflows database: {e}")
        
        # 返回默认工作流
        return self._create_default_workflows()
    
    def _save_workflows(self):
        """保存工作流定义数据库"""
        try:
            data = {}
            for key, workflow in self.workflows.items():
                workflow_dict = asdict(workflow)
                workflow_dict['type'] = workflow.type.value
                workflow_dict['scenario_types'] = [st.value for st in workflow.scenario_types]
                workflow_dict['created_at'] = workflow.created_at.isoformat()
                data[key] = workflow_dict
            
            with open(self.workflows_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save workflows database: {e}")
    
    def _create_default_workflows(self) -> Dict[str, WorkflowDefinition]:
        """创建默认工作流定义"""
        now = datetime.now()
        
        return {
            "critical_review": WorkflowDefinition(
                name="批判性审查工作流",
                type=WorkflowType.CRITICAL_REVIEW,
                description="用于深入分析、评估和验证信息的准确性、可行性和逻辑性",
                scenario_types=[ScenarioType.EXPERT_CONSULTATION, ScenarioType.ACADEMIC_RESEARCH],
                keywords=["分析", "审查", "评估", "检查", "验证", "风险", "可行性", "逻辑"],
                examples=[
                    "请分析这个技术方案的可行性",
                    "审查这份商业计划书的逻辑漏洞",
                    "评估这个投资项目的风险"
                ],
                created_at=now
            ),
            
            "multi_perspective": WorkflowDefinition(
                name="多视角综合工作流",
                type=WorkflowType.MULTI_PERSPECTIVE,
                description="从多个角度收集观点，进行综合分析和讨论",
                scenario_types=[ScenarioType.ACADEMIC_RESEARCH, ScenarioType.CASUAL_DISCUSSION],
                keywords=["讨论", "观点", "角度", "看法", "多方面", "综合", "全面"],
                examples=[
                    "从不同角度讨论AI的影响",
                    "听听大家对教育改革的看法",
                    "综合分析城市发展策略"
                ],
                created_at=now
            )
        }
    
    async def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """调用LLM进行推理"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # 较低温度确保一致性
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"LLM API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return ""
    
    async def analyze_intent_with_llm(self, user_input: str, context: Optional[Dict] = None) -> LLMIntentResult:
        """使用LLM分析用户意图"""
        
        # 构建工作流描述
        workflow_descriptions = []
        for key, workflow in self.workflows.items():
            workflow_descriptions.append(
                f"- {workflow.name} ({workflow.type.value}): {workflow.description}"
            )
        
        # 构建场景描述
        scenario_descriptions = [
            "- academic_research: 学术研究场景，涉及深入分析、理论探讨、数据研究",
            "- expert_consultation: 专家咨询场景，需要专业建议、决策支持、问题解决",
            "- casual_discussion: 轻松讨论场景，日常交流、观点分享、兴趣话题"
        ]
        
        system_prompt = f"""你是一个智能工作流选择专家。你的任务是分析用户输入，选择最合适的工作流和场景类型。

可用工作流：
{chr(10).join(workflow_descriptions)}

可用场景类型：
{chr(10).join(scenario_descriptions)}

请分析用户输入的语义、意图和上下文，选择最合适的工作流和场景。

返回格式必须是有效的JSON：
{{
    "workflow_type": "工作流类型",
    "scenario_type": "场景类型", 
    "confidence": 0.95,
    "reasoning": "详细的推理过程",
    "topic": "提取的主题",
    "semantic_analysis": {{
        "intent": "用户意图",
        "complexity": "复杂度评估",
        "domain": "领域识别",
        "tone": "语调分析"
    }}
}}"""

        user_prompt = f"""请分析以下用户输入：

用户输入："{user_input}"

上下文信息：{json.dumps(context or {}, ensure_ascii=False)}

请根据语义理解选择最合适的工作流和场景类型。"""

        try:
            llm_response = await self._call_llm(user_prompt, system_prompt)
            
            if not llm_response:
                return self._fallback_analysis(user_input)
            
            # 解析LLM响应
            try:
                # 尝试提取JSON
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = llm_response[json_start:json_end]
                    result_data = json.loads(json_str)
                    
                    return LLMIntentResult(
                        workflow_type=WorkflowType(result_data.get("workflow_type", "multi_perspective")),
                        scenario_type=ScenarioType(result_data.get("scenario_type", "casual_discussion")),
                        confidence=float(result_data.get("confidence", 0.8)),
                        reasoning=result_data.get("reasoning", "基于LLM语义分析"),
                        topic=result_data.get("topic", user_input[:50]),
                        semantic_analysis=result_data.get("semantic_analysis", {}),
                        suggested_improvements=result_data.get("suggested_improvements", [])
                    )
                else:
                    logger.warning("No valid JSON found in LLM response")
                    return self._fallback_analysis(user_input)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM JSON response: {e}")
                logger.debug(f"LLM response: {llm_response}")
                return self._fallback_analysis(user_input)
                
        except Exception as e:
            logger.error(f"LLM intent analysis failed: {e}")
            return self._fallback_analysis(user_input)
    
    def _fallback_analysis(self, user_input: str) -> LLMIntentResult:
        """降级分析策略"""
        input_lower = user_input.lower()
        
        # 简单的关键词匹配作为降级
        if any(keyword in input_lower for keyword in ["分析", "审查", "评估", "检查", "验证"]):
            workflow_type = WorkflowType.CRITICAL_REVIEW
            scenario_type = ScenarioType.EXPERT_CONSULTATION
            confidence = 0.6
        elif any(keyword in input_lower for keyword in ["讨论", "观点", "角度", "看法"]):
            workflow_type = WorkflowType.MULTI_PERSPECTIVE
            scenario_type = ScenarioType.CASUAL_DISCUSSION
            confidence = 0.6
        else:
            workflow_type = WorkflowType.MULTI_PERSPECTIVE
            scenario_type = ScenarioType.CASUAL_DISCUSSION
            confidence = 0.5
        
        return LLMIntentResult(
            workflow_type=workflow_type,
            scenario_type=scenario_type,
            confidence=confidence,
            reasoning="降级策略：基于关键词匹配（LLM不可用）",
            topic=user_input[:50],
            semantic_analysis={"fallback": True}
        )
    
    async def add_workflow_from_description(self, description: str, examples: List[str] = None) -> bool:
        """基于自然语言描述添加新工作流"""
        
        system_prompt = """你是一个工作流设计专家。用户会用自然语言描述一个新的工作流需求，你需要分析并创建工作流定义。

返回格式必须是有效的JSON：
{
    "name": "工作流名称",
    "type": "custom",
    "description": "详细描述",
    "scenario_types": ["适用的场景类型列表"],
    "keywords": ["关键词列表"],
    "examples": ["使用示例列表"]
}

场景类型只能是：academic_research, expert_consultation, casual_discussion
"""

        user_prompt = f"""请基于以下描述创建新的工作流定义：

描述：{description}

示例（如果有）：{examples or []}

请分析这个工作流的特点、适用场景和关键词。"""

        try:
            llm_response = await self._call_llm(user_prompt, system_prompt)
            
            if not llm_response:
                return False
            
            # 解析LLM响应
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                result_data = json.loads(json_str)
                
                # 创建新工作流
                workflow_id = f"custom_{len(self.workflows)}"
                
                new_workflow = WorkflowDefinition(
                    name=result_data.get("name", "自定义工作流"),
                    type=WorkflowType.CUSTOM,
                    description=result_data.get("description", description),
                    scenario_types=[ScenarioType(st) for st in result_data.get("scenario_types", ["casual_discussion"])],
                    keywords=result_data.get("keywords", []),
                    examples=result_data.get("examples", examples or []),
                    created_at=datetime.now()
                )
                
                self.workflows[workflow_id] = new_workflow
                self._save_workflows()
                
                logger.info(f"Added new workflow: {new_workflow.name}")
                return True
            else:
                logger.error("No valid JSON in workflow creation response")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add workflow from description: {e}")
            return False
    
    async def optimize_workflow_matching(self, user_input: str, selected_workflow: str, user_feedback: str) -> bool:
        """基于用户反馈优化工作流匹配"""
        
        system_prompt = """你是一个工作流优化专家。基于用户反馈，分析如何改进工作流选择。

返回格式必须是有效的JSON：
{
    "optimization_suggestions": [
        {
            "workflow_id": "工作流ID",
            "action": "add_keyword|remove_keyword|adjust_weight",
            "value": "具体值",
            "reason": "原因"
        }
    ],
    "confidence_adjustment": 0.1,
    "reasoning": "优化推理"
}"""

        user_prompt = f"""用户输入：{user_input}
系统选择的工作流：{selected_workflow}
用户反馈：{user_feedback}

请分析如何优化工作流选择机制。"""

        try:
            llm_response = await self._call_llm(user_prompt, system_prompt)
            
            if llm_response:
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = llm_response[json_start:json_end]
                    optimization_data = json.loads(json_str)
                    
                    # 应用优化建议
                    for suggestion in optimization_data.get("optimization_suggestions", []):
                        workflow_id = suggestion.get("workflow_id")
                        if workflow_id in self.workflows:
                            workflow = self.workflows[workflow_id]
                            action = suggestion.get("action")
                            value = suggestion.get("value")
                            
                            if action == "add_keyword" and value:
                                if value not in workflow.keywords:
                                    workflow.keywords.append(value)
                            elif action == "remove_keyword" and value:
                                if value in workflow.keywords:
                                    workflow.keywords.remove(value)
                    
                    self._save_workflows()
                    logger.info("Applied workflow optimization suggestions")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to optimize workflow matching: {e}")
            return False
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """获取工作流使用统计"""
        stats = {
            "total_workflows": len(self.workflows),
            "workflow_types": {},
            "scenario_coverage": {},
            "usage_stats": {}
        }
        
        for workflow_id, workflow in self.workflows.items():
            # 工作流类型统计
            wf_type = workflow.type.value
            if wf_type not in stats["workflow_types"]:
                stats["workflow_types"][wf_type] = 0
            stats["workflow_types"][wf_type] += 1
            
            # 场景覆盖统计
            for scenario in workflow.scenario_types:
                scenario_name = scenario.value
                if scenario_name not in stats["scenario_coverage"]:
                    stats["scenario_coverage"][scenario_name] = 0
                stats["scenario_coverage"][scenario_name] += 1
            
            # 使用统计
            stats["usage_stats"][workflow_id] = {
                "name": workflow.name,
                "usage_count": workflow.usage_count,
                "success_rate": workflow.success_rate
            }
        
        return stats


# 全局实例
_llm_selector = None

def get_llm_workflow_selector() -> LLMBasedWorkflowSelector:
    """获取LLM工作流选择器的全局实例"""
    global _llm_selector
    if _llm_selector is None:
        _llm_selector = LLMBasedWorkflowSelector()
    return _llm_selector