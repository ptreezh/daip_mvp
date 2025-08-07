#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 20:00:00
@Author  : DAIP-LIVE Team
@File    : autonomous_role_creation_system.py
@Description:
    专业角色自主创建系统设计
    
    核心功能：
    - 基于需求自动生成专业角色
    - 角色能力智能推理
    - 动态角色模板生成
    - 角色持久化和版本管理
"""

import asyncio
import logging
import json
import time
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple, Set
from pathlib import Path
import yaml
import sqlite3
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)

# ============= 数据模型定义 =============

class RoleType(Enum):
    """角色类型"""
    EXPERT = "expert"  # 专家角色
    ADVISOR = "advisor"  # 顾问角色
    ANALYST = "analyst"  # 分析师角色
    CREATOR = "creator"  # 创作者角色
    FACILITATOR = "facilitator"  # 协调者角色
    CRITIC = "critic"  # 批评者角色
    SYNTHESIZER = "synthesizer"  # 综合者角色

class ExpertiseLevel(Enum):
    """专业水平"""
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"

class InteractionStyle(Enum):
    """交互风格"""
    FORMAL = "formal"
    CASUAL = "casual"
    ACADEMIC = "academic"
    PRACTICAL = "practical"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"

class RoleStatus(Enum):
    """角色状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    TESTING = "testing"

@dataclass
class RoleRequirement:
    """角色需求规范"""
    domain: str  # 专业领域
    task_description: str  # 任务描述
    expertise_level: ExpertiseLevel
    interaction_style: InteractionStyle
    required_capabilities: List[str] = field(default_factory=list)
    context_info: Dict[str, Any] = field(default_factory=dict)
    quality_requirements: Dict[str, float] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoleCapability:
    """角色能力定义"""
    capability_id: str
    name: str
    description: str
    skill_level: float  # 0.0-1.0
    keywords: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    related_domains: List[str] = field(default_factory=list)

@dataclass
class RolePersonality:
    """角色性格特征"""
    communication_style: str
    decision_making_approach: str
    problem_solving_method: str
    creativity_level: float  # 0.0-1.0
    analytical_depth: float  # 0.0-1.0
    risk_tolerance: float  # 0.0-1.0
    collaboration_preference: float  # 0.0-1.0

@dataclass
class GeneratedRole:
    """生成的角色定义"""
    role_id: str
    name: str
    role_type: RoleType
    domain: str
    description: str
    system_prompt: str
    capabilities: List[RoleCapability]
    personality: RolePersonality
    expertise_level: ExpertiseLevel
    interaction_style: InteractionStyle
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: RoleStatus = RoleStatus.DRAFT
    usage_count: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class RoleTemplate:
    """角色模板"""
    template_id: str
    name: str
    role_type: RoleType
    template_content: str
    variables: List[str]
    applicability_rules: Dict[str, Any]
    quality_score: float
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class RoleGenerationRequest:
    """角色生成请求"""
    request_id: str
    requirements: RoleRequirement
    preferences: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    reference_roles: List[str] = field(default_factory=list)  # 参考角色ID列表

@dataclass
class RoleGenerationResult:
    """角色生成结果"""
    request_id: str
    generated_role: GeneratedRole
    generation_process: Dict[str, Any]
    quality_assessment: Dict[str, Any]
    alternatives: List[GeneratedRole] = field(default_factory=list)
    generation_time_ms: float = 0.0
    confidence_score: float = 0.0

# ============= 核心接口定义 =============

class IRoleIntelligenceEngine(ABC):
    """角色智能推理引擎接口"""
    
    @abstractmethod
    async def analyze_domain_requirements(
        self, 
        domain: str, 
        task_description: str
    ) -> Dict[str, Any]:
        """分析领域需求"""
        pass
    
    @abstractmethod
    async def infer_capabilities(
        self, 
        requirements: RoleRequirement
    ) -> List[RoleCapability]:
        """推理所需能力"""
        pass
    
    @abstractmethod
    async def generate_personality(
        self, 
        requirements: RoleRequirement,
        capabilities: List[RoleCapability]
    ) -> RolePersonality:
        """生成角色性格"""
        pass
    
    @abstractmethod
    async def optimize_role_definition(
        self, 
        role: GeneratedRole,
        feedback: Dict[str, Any]
    ) -> GeneratedRole:
        """优化角色定义"""
        pass

class IRoleTemplateGenerator(ABC):
    """角色模板生成器接口"""
    
    @abstractmethod
    async def generate_system_prompt(
        self, 
        role: GeneratedRole,
        context: Dict[str, Any]
    ) -> str:
        """生成系统提示词"""
        pass
    
    @abstractmethod
    async def create_role_template(
        self, 
        role_type: RoleType,
        domain: str,
        requirements: RoleRequirement
    ) -> RoleTemplate:
        """创建角色模板"""
        pass
    
    @abstractmethod
    async def adapt_template(
        self, 
        template: RoleTemplate,
        specific_requirements: Dict[str, Any]
    ) -> RoleTemplate:
        """适配模板"""
        pass

class IRoleValidator(ABC):
    """角色验证器接口"""
    
    @abstractmethod
    async def validate_role_definition(
        self, 
        role: GeneratedRole
    ) -> Dict[str, Any]:
        """验证角色定义"""
        pass
    
    @abstractmethod
    async def assess_role_quality(
        self, 
        role: GeneratedRole,
        test_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """评估角色质量"""
        pass
    
    @abstractmethod
    async def check_role_uniqueness(
        self, 
        new_role: GeneratedRole,
        existing_roles: List[GeneratedRole]
    ) -> Dict[str, Any]:
        """检查角色唯一性"""
        pass

class IRolePersistenceManager(ABC):
    """角色持久化管理器接口"""
    
    @abstractmethod
    async def save_role(
        self, 
        role: GeneratedRole
    ) -> bool:
        """保存角色"""
        pass
    
    @abstractmethod
    async def load_role(
        self, 
        role_id: str
    ) -> Optional[GeneratedRole]:
        """加载角色"""
        pass
    
    @abstractmethod
    async def list_roles(
        self, 
        filters: Dict[str, Any] = None
    ) -> List[GeneratedRole]:
        """列出角色"""
        pass
    
    @abstractmethod
    async def update_role(
        self, 
        role: GeneratedRole
    ) -> bool:
        """更新角色"""
        pass
    
    @abstractmethod
    async def archive_role(
        self, 
        role_id: str
    ) -> bool:
        """归档角色"""
        pass

class IAutonomousRoleCreationSystem(ABC):
    """自主角色创建系统主接口"""
    
    @abstractmethod
    async def create_role(
        self, 
        request: RoleGenerationRequest
    ) -> RoleGenerationResult:
        """创建角色"""
        pass
    
    @abstractmethod
    async def suggest_role_improvements(
        self, 
        role_id: str,
        usage_feedback: Dict[str, Any]
    ) -> List[str]:
        """建议角色改进"""
        pass
    
    @abstractmethod
    async def generate_role_variants(
        self, 
        base_role_id: str,
        variation_requirements: Dict[str, Any]
    ) -> List[GeneratedRole]:
        """生成角色变体"""
        pass
    
    @abstractmethod
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        pass

# ============= 实现类开始 =============

class RoleIntelligenceEngine(IRoleIntelligenceEngine):
    """角色智能推理引擎实现"""
    
    def __init__(self):
        self.domain_knowledge = self._load_domain_knowledge()
        self.capability_patterns = self._load_capability_patterns()
        self.personality_templates = self._load_personality_templates()
    
    def _load_domain_knowledge(self) -> Dict[str, Any]:
        """加载领域知识库"""
        return {
            "technology": {
                "core_capabilities": ["programming", "system_design", "problem_solving"],
                "sub_domains": ["ai", "web_development", "data_science", "cybersecurity"],
                "typical_roles": ["software_engineer", "data_scientist", "ai_researcher"]
            },
            "business": {
                "core_capabilities": ["strategic_thinking", "market_analysis", "leadership"],
                "sub_domains": ["finance", "marketing", "operations", "strategy"],
                "typical_roles": ["business_analyst", "consultant", "product_manager"]
            },
            "education": {
                "core_capabilities": ["teaching", "curriculum_design", "assessment"],
                "sub_domains": ["k12", "higher_education", "professional_training"],
                "typical_roles": ["teacher", "instructional_designer", "educational_researcher"]
            },
            "healthcare": {
                "core_capabilities": ["diagnosis", "treatment_planning", "patient_care"],
                "sub_domains": ["clinical", "research", "public_health", "medical_technology"],
                "typical_roles": ["physician", "nurse", "medical_researcher"]
            }
        }
    
    def _load_capability_patterns(self) -> Dict[str, List[str]]:
        """加载能力模式"""
        return {
            "analytical": ["data_analysis", "critical_thinking", "pattern_recognition"],
            "creative": ["innovation", "design_thinking", "brainstorming"],
            "leadership": ["team_management", "decision_making", "strategic_planning"],
            "technical": ["programming", "system_administration", "troubleshooting"],
            "communication": ["public_speaking", "writing", "negotiation"],
            "research": ["literature_review", "experimental_design", "data_collection"]
        }
    
    def _load_personality_templates(self) -> Dict[str, RolePersonality]:
        """加载性格模板"""
        return {
            "analytical_expert": RolePersonality(
                communication_style="precise and data-driven",
                decision_making_approach="evidence-based",
                problem_solving_method="systematic analysis",
                creativity_level=0.4,
                analytical_depth=0.9,
                risk_tolerance=0.3,
                collaboration_preference=0.6
            ),
            "creative_innovator": RolePersonality(
                communication_style="inspiring and visionary",
                decision_making_approach="intuitive with data support",
                problem_solving_method="creative exploration",
                creativity_level=0.9,
                analytical_depth=0.5,
                risk_tolerance=0.8,
                collaboration_preference=0.8
            ),
            "practical_advisor": RolePersonality(
                communication_style="clear and actionable",
                decision_making_approach="pragmatic",
                problem_solving_method="solution-focused",
                creativity_level=0.6,
                analytical_depth=0.7,
                risk_tolerance=0.5,
                collaboration_preference=0.7
            )
        }
    
    async def analyze_domain_requirements(
        self, 
        domain: str, 
        task_description: str
    ) -> Dict[str, Any]:
        """分析领域需求"""
        domain_info = self.domain_knowledge.get(domain.lower(), {})
        
        # 分析任务描述中的关键词
        task_keywords = self._extract_task_keywords(task_description)
        
        # 推断所需的核心能力
        required_capabilities = self._infer_core_capabilities(domain_info, task_keywords)
        
        # 确定专业水平需求
        complexity_level = self._assess_task_complexity(task_description)
        
        # 推荐角色类型
        recommended_role_type = self._recommend_role_type(task_keywords, domain_info)
        
        return {
            "domain_info": domain_info,
            "task_keywords": task_keywords,
            "required_capabilities": required_capabilities,
            "complexity_level": complexity_level,
            "recommended_role_type": recommended_role_type,
            "confidence_score": 0.8  # 简化实现
        }
    
    def _extract_task_keywords(self, task_description: str) -> List[str]:
        """提取任务关键词"""
        # 简化的关键词提取
        action_words = ["分析", "设计", "开发", "研究", "评估", "优化", "管理", "教学", "咨询"]
        object_words = ["系统", "产品", "策略", "方案", "技术", "数据", "流程", "团队"]
        
        keywords = []
        task_lower = task_description.lower()
        
        for word in action_words + object_words:
            if word in task_description:
                keywords.append(word)
        
        return keywords
    
    def _infer_core_capabilities(
        self, 
        domain_info: Dict[str, Any], 
        task_keywords: List[str]
    ) -> List[str]:
        """推断核心能力"""
        capabilities = set()
        
        # 添加领域核心能力
        capabilities.update(domain_info.get("core_capabilities", []))
        
        # 基于任务关键词推断能力
        keyword_capability_mapping = {
            "分析": ["analytical_thinking", "data_analysis"],
            "设计": ["design_thinking", "creativity"],
            "开发": ["programming", "system_development"],
            "研究": ["research_methods", "literature_review"],
            "管理": ["project_management", "leadership"],
            "教学": ["teaching", "communication"]
        }
        
        for keyword in task_keywords:
            if keyword in keyword_capability_mapping:
                capabilities.update(keyword_capability_mapping[keyword])
        
        return list(capabilities)
    
    def _assess_task_complexity(self, task_description: str) -> ExpertiseLevel:
        """评估任务复杂度"""
        complexity_indicators = {
            "高级": ExpertiseLevel.EXPERT,
            "复杂": ExpertiseLevel.ADVANCED,
            "专业": ExpertiseLevel.ADVANCED,
            "深入": ExpertiseLevel.ADVANCED,
            "基础": ExpertiseLevel.INTERMEDIATE,
            "简单": ExpertiseLevel.NOVICE
        }
        
        for indicator, level in complexity_indicators.items():
            if indicator in task_description:
                return level
        
        # 基于描述长度和复杂性判断
        if len(task_description) > 200:
            return ExpertiseLevel.EXPERT
        elif len(task_description) > 100:
            return ExpertiseLevel.ADVANCED
        else:
            return ExpertiseLevel.INTERMEDIATE
    
    def _recommend_role_type(
        self, 
        task_keywords: List[str], 
        domain_info: Dict[str, Any]
    ) -> RoleType:
        """推荐角色类型"""
        if any(word in task_keywords for word in ["分析", "评估", "研究"]):
            return RoleType.ANALYST
        elif any(word in task_keywords for word in ["设计", "创建", "开发"]):
            return RoleType.CREATOR
        elif any(word in task_keywords for word in ["咨询", "建议", "指导"]):
            return RoleType.ADVISOR
        elif any(word in task_keywords for word in ["专家", "技术", "专业"]):
            return RoleType.EXPERT
        else:
            return RoleType.EXPERT  # 默认为专家角色
    
    async def infer_capabilities(
        self, 
        requirements: RoleRequirement
    ) -> List[RoleCapability]:
        """推理所需能力"""
        domain_analysis = await self.analyze_domain_requirements(
            requirements.domain, 
            requirements.task_description
        )
        
        capabilities = []
        required_caps = domain_analysis["required_capabilities"]
        
        # 为每个能力创建详细定义
        for i, cap_name in enumerate(required_caps):
            capability = RoleCapability(
                capability_id=f"cap_{i+1}_{int(time.time())}",
                name=cap_name,
                description=f"能力：{cap_name}",
                skill_level=self._determine_skill_level(cap_name, requirements.expertise_level),
                keywords=[cap_name],
                related_domains=[requirements.domain]
            )
            capabilities.append(capability)
        
        # 添加用户指定的能力
        for user_cap in requirements.required_capabilities:
            if user_cap not in required_caps:
                capability = RoleCapability(
                    capability_id=f"user_cap_{len(capabilities)+1}_{int(time.time())}",
                    name=user_cap,
                    description=f"用户要求的能力：{user_cap}",
                    skill_level=self._determine_skill_level(user_cap, requirements.expertise_level),
                    keywords=[user_cap],
                    related_domains=[requirements.domain]
                )
                capabilities.append(capability)
        
        return capabilities
    
    def _determine_skill_level(self, capability_name: str, expertise_level: ExpertiseLevel) -> float:
        """确定技能水平"""
        base_levels = {
            ExpertiseLevel.NOVICE: 0.3,
            ExpertiseLevel.INTERMEDIATE: 0.5,
            ExpertiseLevel.ADVANCED: 0.7,
            ExpertiseLevel.EXPERT: 0.9,
            ExpertiseLevel.MASTER: 1.0
        }
        
        base_level = base_levels[expertise_level]
        
        # 根据能力类型调整
        if "leadership" in capability_name.lower():
            return min(base_level + 0.1, 1.0)
        elif "technical" in capability_name.lower():
            return max(base_level - 0.1, 0.1)
        
        return base_level
    
    async def generate_personality(
        self, 
        requirements: RoleRequirement,
        capabilities: List[RoleCapability]
    ) -> RolePersonality:
        """生成角色性格"""
        # 基于交互风格选择基础性格模板
        style_template_mapping = {
            InteractionStyle.ANALYTICAL: "analytical_expert",
            InteractionStyle.CREATIVE: "creative_innovator",
            InteractionStyle.PRACTICAL: "practical_advisor",
            InteractionStyle.ACADEMIC: "analytical_expert",
            InteractionStyle.FORMAL: "analytical_expert",
            InteractionStyle.CASUAL: "practical_advisor"
        }
        
        template_name = style_template_mapping.get(
            requirements.interaction_style, 
            "practical_advisor"
        )
        
        base_personality = self.personality_templates[template_name]
        
        # 基于能力调整性格特征
        capability_names = [cap.name.lower() for cap in capabilities]
        
        # 调整创造力水平
        if any("creative" in name or "design" in name for name in capability_names):
            base_personality.creativity_level = min(base_personality.creativity_level + 0.2, 1.0)
        
        # 调整分析深度
        if any("analytical" in name or "research" in name for name in capability_names):
            base_personality.analytical_depth = min(base_personality.analytical_depth + 0.1, 1.0)
        
        # 调整协作偏好
        if any("management" in name or "leadership" in name for name in capability_names):
            base_personality.collaboration_preference = min(base_personality.collaboration_preference + 0.2, 1.0)
        
        return base_personality
    
    async def optimize_role_definition(
        self, 
        role: GeneratedRole,
        feedback: Dict[str, Any]
    ) -> GeneratedRole:
        """优化角色定义"""
        optimized_role = role
        
        # 基于反馈调整角色定义
        if feedback.get("too_technical", False):
            # 降低技术能力，增加沟通能力
            for cap in optimized_role.capabilities:
                if "technical" in cap.name.lower():
                    cap.skill_level = max(cap.skill_level - 0.1, 0.1)
            
            # 调整性格
            optimized_role.personality.communication_style = "clear and accessible"
        
        if feedback.get("needs_more_expertise", False):
            # 提升专业水平
            optimized_role.expertise_level = ExpertiseLevel.EXPERT
            for cap in optimized_role.capabilities:
                cap.skill_level = min(cap.skill_level + 0.2, 1.0)
        
        # 更新时间戳和版本
        optimized_role.updated_at = datetime.now()
        version_parts = optimized_role.version.split('.')
        minor_version = int(version_parts[1]) + 1
        optimized_role.version = f"{version_parts[0]}.{minor_version}"
        
        return optimized_role

# ============= 角色模板生成器实现 =============

class RoleTemplateGenerator(IRoleTemplateGenerator):
    """角色模板生成器实现"""
    
    def __init__(self):
        self.system_prompt_templates = self._load_system_prompt_templates()
        self.role_templates = self._load_role_templates()
    
    def _load_system_prompt_templates(self) -> Dict[str, str]:
        """加载系统提示词模板"""
        return {
            "expert": """你是一位{domain}领域的{expertise_level}专家，名为{name}。

专业背景：
{description}

核心能力：
{capabilities_list}

工作风格：
- 沟通方式：{communication_style}
- 决策方法：{decision_making_approach}
- 问题解决：{problem_solving_method}

请以专业、{interaction_style}的方式回应用户的问题和需求。始终保持{expertise_level}的专业水准，提供准确、实用的建议。

特别注意：
- 基于你的专业知识和经验回答
- 保持适当的专业边界
- 在不确定时明确说明
- 提供可行的建议和解决方案""",
            
            "advisor": """作为{domain}领域的专业顾问{name}，你的角色是为用户提供战略性建议和指导。

你的专业特长：
{description}

核心服务能力：
{capabilities_list}

咨询风格：
- 沟通特点：{communication_style}
- 分析方法：{decision_making_approach}
- 解决问题的途径：{problem_solving_method}

作为{expertise_level}级别的顾问，请：
1. 深入理解用户的需求和背景
2. 提供全面、平衡的分析
3. 给出具体可行的建议
4. 考虑风险和机遇
5. 保持{interaction_style}的交流方式

始终以用户的最佳利益为出发点，提供有价值的专业见解。""",
            
            "analyst": """你是{domain}领域的{expertise_level}分析师{name}，专门从事深度分析和研究工作。

分析专长：
{description}

核心分析能力：
{capabilities_list}

分析方法：
- 研究方式：{communication_style}
- 决策逻辑：{decision_making_approach}
- 问题分析：{problem_solving_method}

作为专业分析师，你需要：
1. 进行客观、全面的分析
2. 基于数据和事实得出结论
3. 识别趋势和模式
4. 提供深入洞察
5. 以{interaction_style}的方式呈现分析结果

确保你的分析具有{expertise_level}的专业深度和准确性。""",
            
            "creator": """你是{domain}领域的{expertise_level}创作者/设计师{name}，专注于创新和创造性解决方案。

创作专长：
{description}

创意能力：
{capabilities_list}

创作理念：
- 表达方式：{communication_style}
- 创意过程：{decision_making_approach}
- 创新方法：{problem_solving_method}

作为创意专家，你要：
1. 提供原创性的想法和解决方案
2. 将创新思维与实践相结合
3. 激发用户的创造力
4. 设计美观且实用的方案
5. 保持{interaction_style}的创作风格

运用你{expertise_level}级别的专业技能，帮助用户实现创意目标。"""
        }
    
    def _load_role_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载角色模板"""
        return {
            "technology_expert": {
                "role_type": RoleType.EXPERT,
                "applicable_domains": ["technology", "ai", "software"],
                "default_capabilities": ["programming", "system_design", "technical_analysis"],
                "personality_traits": {
                    "analytical_depth": 0.9,
                    "creativity_level": 0.6,
                    "collaboration_preference": 0.7
                }
            },
            "business_advisor": {
                "role_type": RoleType.ADVISOR,
                "applicable_domains": ["business", "strategy", "management"],
                "default_capabilities": ["strategic_planning", "market_analysis", "leadership"],
                "personality_traits": {
                    "analytical_depth": 0.8,
                    "creativity_level": 0.7,
                    "collaboration_preference": 0.9
                }
            },
            "research_analyst": {
                "role_type": RoleType.ANALYST,
                "applicable_domains": ["research", "academia", "science"],
                "default_capabilities": ["research_methods", "data_analysis", "critical_thinking"],
                "personality_traits": {
                    "analytical_depth": 0.95,
                    "creativity_level": 0.5,
                    "collaboration_preference": 0.6
                }
            }
        }
    
    async def generate_system_prompt(
        self, 
        role: GeneratedRole,
        context: Dict[str, Any]
    ) -> str:
        """生成系统提示词"""
        # 选择合适的模板
        template_key = role.role_type.value
        if template_key not in self.system_prompt_templates:
            template_key = "expert"  # 默认模板
        
        template = self.system_prompt_templates[template_key]
        
        # 准备替换变量
        capabilities_list = "\n".join([
            f"- {cap.name}: {cap.description}" 
            for cap in role.capabilities[:5]  # 限制显示数量
        ])
        
        variables = {
            "name": role.name,
            "domain": role.domain,
            "description": role.description,
            "expertise_level": role.expertise_level.value,
            "interaction_style": role.interaction_style.value,
            "capabilities_list": capabilities_list,
            "communication_style": role.personality.communication_style,
            "decision_making_approach": role.personality.decision_making_approach,
            "problem_solving_method": role.personality.problem_solving_method
        }
        
        # 填充模板
        system_prompt = template
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            system_prompt = system_prompt.replace(placeholder, str(value))
        
        return system_prompt
    
    async def create_role_template(
        self, 
        role_type: RoleType,
        domain: str,
        requirements: RoleRequirement
    ) -> RoleTemplate:
        """创建角色模板"""
        template_id = f"template_{role_type.value}_{domain}_{int(time.time())}"
        
        # 选择基础模板
        base_template_key = f"{domain}_{role_type.value}"
        if base_template_key not in self.role_templates:
            # 使用通用模板
            base_template_key = list(self.role_templates.keys())[0]
        
        base_template = self.role_templates.get(base_template_key, {})
        
        # 生成模板内容
        template_content = self.system_prompt_templates.get(role_type.value, "")
        
        # 提取变量
        import re
        variables = re.findall(r'\{(\w+)\}', template_content)
        
        # 定义适用性规则
        applicability_rules = {
            "role_type": role_type.value,
            "domain": domain,
            "min_expertise_level": requirements.expertise_level.value,
            "interaction_style": requirements.interaction_style.value
        }
        
        template = RoleTemplate(
            template_id=template_id,
            name=f"{role_type.value}_{domain}_template",
            role_type=role_type,
            template_content=template_content,
            variables=list(set(variables)),
            applicability_rules=applicability_rules,
            quality_score=0.8  # 初始质量分数
        )
        
        return template
    
    async def adapt_template(
        self, 
        template: RoleTemplate,
        specific_requirements: Dict[str, Any]
    ) -> RoleTemplate:
        """适配模板"""
        adapted_template = template
        
        # 根据特定需求调整模板
        if "formality_level" in specific_requirements:
            formality = specific_requirements["formality_level"]
            if formality == "high":
                adapted_template.template_content = adapted_template.template_content.replace(
                    "的方式", "的专业方式"
                )
            elif formality == "low":
                adapted_template.template_content = adapted_template.template_content.replace(
                    "专业", "友好"
                )
        
        # 更新模板ID和时间戳
        adapted_template.template_id = f"adapted_{template.template_id}_{int(time.time())}"
        adapted_template.created_at = datetime.now()
        
        return adapted_template

# ============= 角色验证器实现 =============

class RoleValidator(IRoleValidator):
    """角色验证器实现"""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.quality_metrics = self._load_quality_metrics()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """加载验证规则"""
        return {
            "required_fields": ["name", "description", "system_prompt", "capabilities"],
            "name_constraints": {
                "min_length": 2,
                "max_length": 50,
                "forbidden_chars": ["<", ">", "&", "\"", "'"]
            },
            "description_constraints": {
                "min_length": 10,
                "max_length": 500
            },
            "capabilities_constraints": {
                "min_count": 1,
                "max_count": 20
            },
            "system_prompt_constraints": {
                "min_length": 50,
                "max_length": 2000
            }
        }
    
    def _load_quality_metrics(self) -> Dict[str, Dict[str, Any]]:
        """加载质量指标"""
        return {
            "clarity": {
                "weight": 0.3,
                "criteria": ["clear_description", "specific_capabilities", "coherent_prompt"]
            },
            "completeness": {
                "weight": 0.3,
                "criteria": ["all_required_fields", "sufficient_capabilities", "detailed_personality"]
            },
            "uniqueness": {
                "weight": 0.2,
                "criteria": ["distinct_capabilities", "unique_personality", "specific_domain"]
            },
            "usability": {
                "weight": 0.2,
                "criteria": ["actionable_capabilities", "practical_system_prompt", "appropriate_level"]
            }
        }
    
    async def validate_role_definition(
        self, 
        role: GeneratedRole
    ) -> Dict[str, Any]:
        """验证角色定义"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "score": 0.0
        }
        
        # 检查必需字段
        for field in self.validation_rules["required_fields"]:
            if not hasattr(role, field) or not getattr(role, field):
                validation_result["errors"].append(f"缺少必需字段: {field}")
                validation_result["is_valid"] = False
        
        # 验证角色名称
        name_errors = self._validate_name(role.name)
        validation_result["errors"].extend(name_errors)
        
        # 验证描述
        desc_errors = self._validate_description(role.description)
        validation_result["errors"].extend(desc_errors)
        
        # 验证能力
        cap_errors = self._validate_capabilities(role.capabilities)
        validation_result["errors"].extend(cap_errors)
        
        # 验证系统提示词
        prompt_errors = self._validate_system_prompt(role.system_prompt)
        validation_result["errors"].extend(prompt_errors)
        
        # 如果有错误，标记为无效
        if validation_result["errors"]:
            validation_result["is_valid"] = False
        
        # 计算质量分数
        validation_result["score"] = await self._calculate_quality_score(role)
        
        return validation_result
    
    def _validate_name(self, name: str) -> List[str]:
        """验证角色名称"""
        errors = []
        constraints = self.validation_rules["name_constraints"]
        
        if len(name) < constraints["min_length"]:
            errors.append(f"角色名称过短，最少{constraints['min_length']}个字符")
        
        if len(name) > constraints["max_length"]:
            errors.append(f"角色名称过长，最多{constraints['max_length']}个字符")
        
        for forbidden_char in constraints["forbidden_chars"]:
            if forbidden_char in name:
                errors.append(f"角色名称包含禁用字符: {forbidden_char}")
        
        return errors
    
    def _validate_description(self, description: str) -> List[str]:
        """验证角色描述"""
        errors = []
        constraints = self.validation_rules["description_constraints"]
        
        if len(description) < constraints["min_length"]:
            errors.append(f"角色描述过短，最少{constraints['min_length']}个字符")
        
        if len(description) > constraints["max_length"]:
            errors.append(f"角色描述过长，最多{constraints['max_length']}个字符")
        
        return errors
    
    def _validate_capabilities(self, capabilities: List[RoleCapability]) -> List[str]:
        """验证角色能力"""
        errors = []
        constraints = self.validation_rules["capabilities_constraints"]
        
        if len(capabilities) < constraints["min_count"]:
            errors.append(f"能力数量过少，最少{constraints['min_count']}个")
        
        if len(capabilities) > constraints["max_count"]:
            errors.append(f"能力数量过多，最多{constraints['max_count']}个")
        
        # 检查能力重复
        capability_names = [cap.name for cap in capabilities]
        if len(capability_names) != len(set(capability_names)):
            errors.append("存在重复的能力定义")
        
        # 检查技能水平
        for cap in capabilities:
            if not (0.0 <= cap.skill_level <= 1.0):
                errors.append(f"能力 {cap.name} 的技能水平无效: {cap.skill_level}")
        
        return errors
    
    def _validate_system_prompt(self, system_prompt: str) -> List[str]:
        """验证系统提示词"""
        errors = []
        constraints = self.validation_rules["system_prompt_constraints"]
        
        if len(system_prompt) < constraints["min_length"]:
            errors.append(f"系统提示词过短，最少{constraints['min_length']}个字符")
        
        if len(system_prompt) > constraints["max_length"]:
            errors.append(f"系统提示词过长，最多{constraints['max_length']}个字符")
        
        return errors
    
    async def _calculate_quality_score(self, role: GeneratedRole) -> float:
        """计算质量分数"""
        total_score = 0.0
        
        for metric_name, metric_config in self.quality_metrics.items():
            metric_score = await self._evaluate_metric(role, metric_name, metric_config)
            total_score += metric_score * metric_config["weight"]
        
        return min(total_score, 1.0)
    
    async def _evaluate_metric(
        self, 
        role: GeneratedRole, 
        metric_name: str, 
        metric_config: Dict[str, Any]
    ) -> float:
        """评估单个质量指标"""
        if metric_name == "clarity":
            return self._evaluate_clarity(role)
        elif metric_name == "completeness":
            return self._evaluate_completeness(role)
        elif metric_name == "uniqueness":
            return self._evaluate_uniqueness(role)
        elif metric_name == "usability":
            return self._evaluate_usability(role)
        else:
            return 0.5  # 默认分数
    
    def _evaluate_clarity(self, role: GeneratedRole) -> float:
        """评估清晰度"""
        score = 0.0
        
        # 描述清晰度
        if len(role.description) > 50 and "。" in role.description:
            score += 0.3
        
        # 能力具体性
        specific_caps = sum(1 for cap in role.capabilities if len(cap.description) > 10)
        score += min(specific_caps / len(role.capabilities), 1.0) * 0.4
        
        # 提示词连贯性
        if len(role.system_prompt.split("。")) > 3:
            score += 0.3
        
        return score
    
    def _evaluate_completeness(self, role: GeneratedRole) -> float:
        """评估完整性"""
        score = 0.0
        
        # 基本字段完整性
        required_fields = ["name", "description", "system_prompt"]
        complete_fields = sum(1 for field in required_fields if getattr(role, field))
        score += (complete_fields / len(required_fields)) * 0.4
        
        # 能力充分性
        if len(role.capabilities) >= 3:
            score += 0.3
        
        # 性格定义完整性
        if role.personality and role.personality.communication_style:
            score += 0.3
        
        return score
    
    def _evaluate_uniqueness(self, role: GeneratedRole) -> float:
        """评估独特性"""
        # 简化实现：基于角色特征的多样性
        score = 0.0
        
        # 能力多样性
        unique_capabilities = len(set(cap.name for cap in role.capabilities))
        score += min(unique_capabilities / 5, 1.0) * 0.4
        
        # 领域特异性
        if role.domain and len(role.domain) > 3:
            score += 0.3
        
        # 个性特征
        if role.personality:
            trait_diversity = (
                role.personality.creativity_level + 
                role.personality.analytical_depth + 
                role.personality.collaboration_preference
            ) / 3
            score += trait_diversity * 0.3
        
        return score
    
    def _evaluate_usability(self, role: GeneratedRole) -> float:
        """评估可用性"""
        score = 0.0
        
        # 能力可执行性
        actionable_caps = sum(
            1 for cap in role.capabilities 
            if any(word in cap.name.lower() for word in ["analysis", "design", "manage", "develop"])
        )
        score += min(actionable_caps / len(role.capabilities), 1.0) * 0.4
        
        # 提示词实用性
        if "请" in role.system_prompt or "你需要" in role.system_prompt:
            score += 0.3
        
        # 专业水平适当性
        if role.expertise_level in [ExpertiseLevel.INTERMEDIATE, ExpertiseLevel.ADVANCED]:
            score += 0.3
        
        return score
    
    async def assess_role_quality(
        self, 
        role: GeneratedRole,
        test_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """评估角色质量"""
        assessment = {
            "overall_score": 0.0,
            "metric_scores": {},
            "test_results": [],
            "recommendations": []
        }
        
        # 基础质量评估
        base_score = await self._calculate_quality_score(role)
        assessment["overall_score"] = base_score
        
        # 计算各项指标分数
        for metric_name, metric_config in self.quality_metrics.items():
            metric_score = await self._evaluate_metric(role, metric_name, metric_config)
            assessment["metric_scores"][metric_name] = metric_score
        
        # 运行测试场景
        for i, scenario in enumerate(test_scenarios[:3]):  # 限制测试数量
            test_result = await self._run_test_scenario(role, scenario)
            assessment["test_results"].append({
                "scenario_id": i,
                "scenario": scenario,
                "result": test_result
            })
        
        # 生成改进建议
        assessment["recommendations"] = self._generate_quality_recommendations(
            assessment["metric_scores"]
        )
        
        return assessment
    
    async def _run_test_scenario(
        self, 
        role: GeneratedRole, 
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行测试场景"""
        # 简化的测试场景执行
        test_query = scenario.get("query", "请介绍你的专业能力")
        expected_keywords = scenario.get("expected_keywords", [])
        
        # 模拟角色回应（实际应用中会调用LLM）
        simulated_response = f"作为{role.name}，我的专业领域是{role.domain}。" + \
                           f"我具备以下核心能力：{', '.join([cap.name for cap in role.capabilities[:3]])}。"
        
        # 检查是否包含期望的关键词
        keyword_matches = sum(1 for keyword in expected_keywords if keyword in simulated_response)
        keyword_score = keyword_matches / len(expected_keywords) if expected_keywords else 1.0
        
        return {
            "query": test_query,
            "response": simulated_response,
            "keyword_score": keyword_score,
            "passed": keyword_score >= 0.6
        }
    
    def _generate_quality_recommendations(self, metric_scores: Dict[str, float]) -> List[str]:
        """生成质量改进建议"""
        recommendations = []
        
        if metric_scores.get("clarity", 0) < 0.6:
            recommendations.append("改进角色描述的清晰度，使用更具体的表达")
        
        if metric_scores.get("completeness", 0) < 0.6:
            recommendations.append("补充角色定义的完整性，添加更多能力和特征")
        
        if metric_scores.get("uniqueness", 0) < 0.6:
            recommendations.append("增强角色的独特性，突出专业特色")
        
        if metric_scores.get("usability", 0) < 0.6:
            recommendations.append("提高角色的实用性，确保能力可执行")
        
        if not recommendations:
            recommendations.append("角色质量良好，可考虑针对特定场景进行微调")
        
        return recommendations
    
    async def check_role_uniqueness(
        self, 
        new_role: GeneratedRole,
        existing_roles: List[GeneratedRole]
    ) -> Dict[str, Any]:
        """检查角色唯一性"""
        uniqueness_result = {
            "is_unique": True,
            "similarity_scores": [],
            "conflicts": [],
            "suggestions": []
        }
        
        for existing_role in existing_roles:
            similarity_score = self._calculate_role_similarity(new_role, existing_role)
            
            uniqueness_result["similarity_scores"].append({
                "role_id": existing_role.role_id,
                "role_name": existing_role.name,
                "similarity": similarity_score
            })
            
            # 如果相似度太高，标记冲突
            if similarity_score > 0.8:
                uniqueness_result["is_unique"] = False
                uniqueness_result["conflicts"].append({
                    "role_id": existing_role.role_id,
                    "role_name": existing_role.name,
                    "similarity": similarity_score,
                    "conflict_reason": "角色定义过于相似"
                })
        
        # 生成建议
        if not uniqueness_result["is_unique"]:
            uniqueness_result["suggestions"] = [
                "调整角色的专业领域定位",
                "修改核心能力组合",
                "改变交互风格或专业水平",
                "增加独特的个性特征"
            ]
        
        return uniqueness_result
    
    def _calculate_role_similarity(
        self, 
        role1: GeneratedRole, 
        role2: GeneratedRole
    ) -> float:
        """计算角色相似度"""
        similarity_factors = []
        
        # 领域相似度
        domain_similarity = 1.0 if role1.domain == role2.domain else 0.0
        similarity_factors.append(domain_similarity * 0.3)
        
        # 角色类型相似度
        type_similarity = 1.0 if role1.role_type == role2.role_type else 0.0
        similarity_factors.append(type_similarity * 0.2)
        
        # 能力相似度
        caps1 = set(cap.name for cap in role1.capabilities)
        caps2 = set(cap.name for cap in role2.capabilities)
        if caps1 or caps2:
            cap_intersection = len(caps1.intersection(caps2))
            cap_union = len(caps1.union(caps2))
            cap_similarity = cap_intersection / cap_union if cap_union > 0 else 0.0
        else:
            cap_similarity = 0.0
        similarity_factors.append(cap_similarity * 0.3)
        
        # 专业水平相似度
        level_similarity = 1.0 if role1.expertise_level == role2.expertise_level else 0.0
        similarity_factors.append(level_similarity * 0.1)
        
        # 交互风格相似度
        style_similarity = 1.0 if role1.interaction_style == role2.interaction_style else 0.0
        similarity_factors.append(style_similarity * 0.1)
        
        return sum(similarity_factors)

# ============= 角色持久化管理器实现 =============

class RolePersistenceManager(IRolePersistenceManager):
    """角色持久化管理器实现"""
    
    def __init__(self, storage_dir: str = "data/roles"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_dir / "roles.db"
        self.json_storage_dir = self.storage_dir / "json"
        self.json_storage_dir.mkdir(exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        logger.info(f"角色持久化管理器初始化完成，存储路径: {self.storage_dir}")
    
    def _init_database(self):
        """初始化角色数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建角色表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                role_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role_type TEXT NOT NULL,
                domain TEXT NOT NULL,
                description TEXT,
                system_prompt TEXT,
                expertise_level TEXT,
                interaction_style TEXT,
                version TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT,
                usage_count INTEGER DEFAULT 0,
                json_file_path TEXT
            )
        ''')
        
        # 创建能力表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_capabilities (
                capability_id TEXT PRIMARY KEY,
                role_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                skill_level REAL,
                keywords TEXT,
                FOREIGN KEY (role_id) REFERENCES roles (role_id)
            )
        ''')
        
        # 创建性格特征表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_personalities (
                role_id TEXT PRIMARY KEY,
                communication_style TEXT,
                decision_making_approach TEXT,
                problem_solving_method TEXT,
                creativity_level REAL,
                analytical_depth REAL,
                risk_tolerance REAL,
                collaboration_preference REAL,
                FOREIGN KEY (role_id) REFERENCES roles (role_id)
            )
        ''')
        
        # 创建性能指标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_metrics (
                role_id TEXT,
                metric_name TEXT,
                metric_value REAL,
                recorded_at TEXT,
                PRIMARY KEY (role_id, metric_name, recorded_at),
                FOREIGN KEY (role_id) REFERENCES roles (role_id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_roles_domain ON roles(domain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_roles_type ON roles(role_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_roles_status ON roles(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_capabilities_role ON role_capabilities(role_id)')
        
        conn.commit()
        conn.close()
    
    async def save_role(self, role: GeneratedRole) -> bool:
        """保存角色"""
        try:
            # 保存到数据库
            await self._save_to_database(role)
            
            # 保存为JSON文件
            await self._save_to_json(role)
            
            logger.info(f"角色保存成功: {role.role_id} - {role.name}")
            return True
            
        except Exception as e:
            logger.error(f"保存角色失败: {e}")
            return False
    
    async def _save_to_database(self, role: GeneratedRole):
        """保存到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 保存主要角色信息
            cursor.execute('''
                INSERT OR REPLACE INTO roles 
                (role_id, name, role_type, domain, description, system_prompt,
                 expertise_level, interaction_style, version, status, 
                 created_at, updated_at, usage_count, json_file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                role.role_id,
                role.name,
                role.role_type.value,
                role.domain,
                role.description,
                role.system_prompt,
                role.expertise_level.value,
                role.interaction_style.value,
                role.version,
                role.status.value,
                role.created_at.isoformat(),
                role.updated_at.isoformat(),
                role.usage_count,
                f"json/{role.role_id}.json"
            ))
            
            # 删除旧的能力记录
            cursor.execute('DELETE FROM role_capabilities WHERE role_id = ?', (role.role_id,))
            
            # 保存能力信息
            for capability in role.capabilities:
                cursor.execute('''
                    INSERT INTO role_capabilities 
                    (capability_id, role_id, name, description, skill_level, keywords)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    capability.capability_id,
                    role.role_id,
                    capability.name,
                    capability.description,
                    capability.skill_level,
                    json.dumps(capability.keywords)
                ))
            
            # 保存性格特征
            if role.personality:
                cursor.execute('''
                    INSERT OR REPLACE INTO role_personalities 
                    (role_id, communication_style, decision_making_approach, 
                     problem_solving_method, creativity_level, analytical_depth,
                     risk_tolerance, collaboration_preference)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    role.role_id,
                    role.personality.communication_style,
                    role.personality.decision_making_approach,
                    role.personality.problem_solving_method,
                    role.personality.creativity_level,
                    role.personality.analytical_depth,
                    role.personality.risk_tolerance,
                    role.personality.collaboration_preference
                ))
            
            # 保存性能指标
            for metric_name, metric_value in role.performance_metrics.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO role_metrics 
                    (role_id, metric_name, metric_value, recorded_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    role.role_id,
                    metric_name,
                    metric_value,
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            
        finally:
            conn.close()
    
    async def _save_to_json(self, role: GeneratedRole):
        """保存为JSON文件"""
        json_file_path = self.json_storage_dir / f"{role.role_id}.json"
        
        # 转换为可序列化的字典
        role_dict = {
            "role_id": role.role_id,
            "name": role.name,
            "role_type": role.role_type.value,
            "domain": role.domain,
            "description": role.description,
            "system_prompt": role.system_prompt,
            "capabilities": [
                {
                    "capability_id": cap.capability_id,
                    "name": cap.name,
                    "description": cap.description,
                    "skill_level": cap.skill_level,
                    "keywords": cap.keywords,
                    "prerequisites": cap.prerequisites,
                    "related_domains": cap.related_domains
                }
                for cap in role.capabilities
            ],
            "personality": {
                "communication_style": role.personality.communication_style,
                "decision_making_approach": role.personality.decision_making_approach,
                "problem_solving_method": role.personality.problem_solving_method,
                "creativity_level": role.personality.creativity_level,
                "analytical_depth": role.personality.analytical_depth,
                "risk_tolerance": role.personality.risk_tolerance,
                "collaboration_preference": role.personality.collaboration_preference
            } if role.personality else None,
            "expertise_level": role.expertise_level.value,
            "interaction_style": role.interaction_style.value,
            "keywords": role.keywords,
            "metadata": role.metadata,
            "version": role.version,
            "created_at": role.created_at.isoformat(),
            "updated_at": role.updated_at.isoformat(),
            "status": role.status.value,
            "usage_count": role.usage_count,
            "performance_metrics": role.performance_metrics
        }
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(role_dict, f, ensure_ascii=False, indent=2)
    
    async def load_role(self, role_id: str) -> Optional[GeneratedRole]:
        """加载角色"""
        try:
            # 先尝试从数据库加载
            role = await self._load_from_database(role_id)
            if role:
                return role
            
            # 如果数据库中没有，尝试从JSON文件加载
            return await self._load_from_json(role_id)
            
        except Exception as e:
            logger.error(f"加载角色失败: {role_id}, 错误: {e}")
            return None
    
    async def _load_from_database(self, role_id: str) -> Optional[GeneratedRole]:
        """从数据库加载角色"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 加载基本信息
            cursor.execute('SELECT * FROM roles WHERE role_id = ?', (role_id,))
            role_row = cursor.fetchone()
            
            if not role_row:
                return None
            
            # 加载能力信息
            cursor.execute('SELECT * FROM role_capabilities WHERE role_id = ?', (role_id,))
            capability_rows = cursor.fetchall()
            
            capabilities = []
            for cap_row in capability_rows:
                capability = RoleCapability(
                    capability_id=cap_row[0],
                    name=cap_row[2],
                    description=cap_row[3],
                    skill_level=cap_row[4],
                    keywords=json.loads(cap_row[5]) if cap_row[5] else []
                )
                capabilities.append(capability)
            
            # 加载性格特征
            cursor.execute('SELECT * FROM role_personalities WHERE role_id = ?', (role_id,))
            personality_row = cursor.fetchone()
            
            personality = None
            if personality_row:
                personality = RolePersonality(
                    communication_style=personality_row[1],
                    decision_making_approach=personality_row[2],
                    problem_solving_method=personality_row[3],
                    creativity_level=personality_row[4],
                    analytical_depth=personality_row[5],
                    risk_tolerance=personality_row[6],
                    collaboration_preference=personality_row[7]
                )
            
            # 加载性能指标
            cursor.execute('SELECT metric_name, metric_value FROM role_metrics WHERE role_id = ?', (role_id,))
            metric_rows = cursor.fetchall()
            performance_metrics = {name: value for name, value in metric_rows}
            
            # 构建角色对象
            role = GeneratedRole(
                role_id=role_row[0],
                name=role_row[1],
                role_type=RoleType(role_row[2]),
                domain=role_row[3],
                description=role_row[4],
                system_prompt=role_row[5],
                capabilities=capabilities,
                personality=personality,
                expertise_level=ExpertiseLevel(role_row[6]),
                interaction_style=InteractionStyle(role_row[7]),
                version=role_row[8],
                status=RoleStatus(role_row[9]),
                created_at=datetime.fromisoformat(role_row[10]),
                updated_at=datetime.fromisoformat(role_row[11]),
                usage_count=role_row[12],
                performance_metrics=performance_metrics
            )
            
            return role
            
        finally:
            conn.close()
    
    async def _load_from_json(self, role_id: str) -> Optional[GeneratedRole]:
        """从JSON文件加载角色"""
        json_file_path = self.json_storage_dir / f"{role_id}.json"
        
        if not json_file_path.exists():
            return None
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            role_dict = json.load(f)
        
        # 重建能力对象
        capabilities = []
        for cap_dict in role_dict.get("capabilities", []):
            capability = RoleCapability(
                capability_id=cap_dict["capability_id"],
                name=cap_dict["name"],
                description=cap_dict["description"],
                skill_level=cap_dict["skill_level"],
                keywords=cap_dict.get("keywords", []),
                prerequisites=cap_dict.get("prerequisites", []),
                related_domains=cap_dict.get("related_domains", [])
            )
            capabilities.append(capability)
        
        # 重建性格对象
        personality = None
        if role_dict.get("personality"):
            p_dict = role_dict["personality"]
            personality = RolePersonality(
                communication_style=p_dict["communication_style"],
                decision_making_approach=p_dict["decision_making_approach"],
                problem_solving_method=p_dict["problem_solving_method"],
                creativity_level=p_dict["creativity_level"],
                analytical_depth=p_dict["analytical_depth"],
                risk_tolerance=p_dict["risk_tolerance"],
                collaboration_preference=p_dict["collaboration_preference"]
            )
        
        # 重建角色对象
        role = GeneratedRole(
            role_id=role_dict["role_id"],
            name=role_dict["name"],
            role_type=RoleType(role_dict["role_type"]),
            domain=role_dict["domain"],
            description=role_dict["description"],
            system_prompt=role_dict["system_prompt"],
            capabilities=capabilities,
            personality=personality,
            expertise_level=ExpertiseLevel(role_dict["expertise_level"]),
            interaction_style=InteractionStyle(role_dict["interaction_style"]),
            keywords=role_dict.get("keywords", []),
            metadata=role_dict.get("metadata", {}),
            version=role_dict["version"],
            created_at=datetime.fromisoformat(role_dict["created_at"]),
            updated_at=datetime.fromisoformat(role_dict["updated_at"]),
            status=RoleStatus(role_dict["status"]),
            usage_count=role_dict.get("usage_count", 0),
            performance_metrics=role_dict.get("performance_metrics", {})
        )
        
        return role
    
    async def list_roles(self, filters: Dict[str, Any] = None) -> List[GeneratedRole]:
        """列出角色"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 构建查询
            query = "SELECT role_id FROM roles"
            params = []
            conditions = []
            
            if filters:
                if "domain" in filters:
                    conditions.append("domain = ?")
                    params.append(filters["domain"])
                
                if "role_type" in filters:
                    conditions.append("role_type = ?")
                    params.append(filters["role_type"])
                
                if "status" in filters:
                    conditions.append("status = ?")
                    params.append(filters["status"])
                
                if "expertise_level" in filters:
                    conditions.append("expertise_level = ?")
                    params.append(filters["expertise_level"])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY updated_at DESC"
            
            cursor.execute(query, params)
            role_ids = [row[0] for row in cursor.fetchall()]
            
            # 加载每个角色
            roles = []
            for role_id in role_ids:
                role = await self.load_role(role_id)
                if role:
                    roles.append(role)
            
            return roles
            
        finally:
            conn.close()
    
    async def update_role(self, role: GeneratedRole) -> bool:
        """更新角色"""
        role.updated_at = datetime.now()
        return await self.save_role(role)
    
    async def archive_role(self, role_id: str) -> bool:
        """归档角色"""
        try:
            role = await self.load_role(role_id)
            if not role:
                return False
            
            role.status = RoleStatus.DEPRECATED
            role.updated_at = datetime.now()
            
            return await self.save_role(role)
            
        except Exception as e:
            logger.error(f"归档角色失败: {role_id}, 错误: {e}")
            return False
    
    async def get_role_statistics(self) -> Dict[str, Any]:
        """获取角色统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # 总数统计
            cursor.execute('SELECT COUNT(*) FROM roles')
            stats["total_roles"] = cursor.fetchone()[0]
            
            # 按状态统计
            cursor.execute('SELECT status, COUNT(*) FROM roles GROUP BY status')
            stats["by_status"] = dict(cursor.fetchall())
            
            # 按领域统计
            cursor.execute('SELECT domain, COUNT(*) FROM roles GROUP BY domain ORDER BY COUNT(*) DESC LIMIT 10')
            stats["by_domain"] = dict(cursor.fetchall())
            
            # 按类型统计
            cursor.execute('SELECT role_type, COUNT(*) FROM roles GROUP BY role_type')
            stats["by_type"] = dict(cursor.fetchall())
            
            # 使用频率统计
            cursor.execute('SELECT AVG(usage_count), MAX(usage_count) FROM roles')
            avg_usage, max_usage = cursor.fetchone()
            stats["usage_stats"] = {
                "average_usage": avg_usage or 0,
                "max_usage": max_usage or 0
            }
            
            return stats
            
        finally:
            conn.close()

# ============= 主服务实现 =============

class AutonomousRoleCreationSystem(IAutonomousRoleCreationSystem):
    """自主角色创建系统主实现类"""
    
    def __init__(self, storage_dir: str = "data/roles"):
        """初始化系统"""
        self.intelligence_engine = RoleIntelligenceEngine()
        self.template_generator = RoleTemplateGenerator()
        self.validator = RoleValidator()
        self.persistence_manager = RolePersistenceManager(storage_dir)
        
        # 性能监控
        self.metrics = {
            "roles_created": 0,
            "average_creation_time": 0.0,
            "success_rate": 0.0,
            "validation_pass_rate": 0.0
        }
        
        # 创建历史
        self.creation_history = []
        
        logger.info("自主角色创建系统初始化完成")
    
    async def create_role(self, request: RoleGenerationRequest) -> RoleGenerationResult:
        """创建角色"""
        start_time = time.time()
        
        try:
            # 1. 分析需求
            domain_analysis = await self.intelligence_engine.analyze_domain_requirements(
                request.requirements.domain,
                request.requirements.task_description
            )
            
            # 2. 推理能力
            capabilities = await self.intelligence_engine.infer_capabilities(request.requirements)
            
            # 3. 生成性格
            personality = await self.intelligence_engine.generate_personality(
                request.requirements, capabilities
            )
            
            # 4. 创建角色基础信息
            role_id = f"role_{uuid.uuid4().hex[:8]}"
            role_name = self._generate_role_name(request.requirements, domain_analysis)
            
            generated_role = GeneratedRole(
                role_id=role_id,
                name=role_name,
                role_type=domain_analysis["recommended_role_type"],
                domain=request.requirements.domain,
                description=self._generate_description(request.requirements, capabilities),
                system_prompt="",  # 稍后生成
                capabilities=capabilities,
                personality=personality,
                expertise_level=request.requirements.expertise_level,
                interaction_style=request.requirements.interaction_style,
                keywords=domain_analysis["task_keywords"],
                metadata={
                    "creation_request_id": request.request_id,
                    "domain_analysis": domain_analysis,
                    "auto_generated": True
                }
            )
            
            # 5. 生成系统提示词
            system_prompt = await self.template_generator.generate_system_prompt(
                generated_role, request.requirements.context_info
            )
            generated_role.system_prompt = system_prompt
            
            # 6. 验证角色定义
            validation_result = await self.validator.validate_role_definition(generated_role)
            
            # 7. 检查唯一性
            existing_roles = await self.persistence_manager.list_roles({
                "domain": request.requirements.domain,
                "status": "active"
            })
            uniqueness_result = await self.validator.check_role_uniqueness(
                generated_role, existing_roles
            )
            
            # 8. 如果验证通过，保存角色
            if validation_result["is_valid"] and uniqueness_result["is_unique"]:
                generated_role.status = RoleStatus.ACTIVE
                success = await self.persistence_manager.save_role(generated_role)
                
                if not success:
                    raise Exception("角色保存失败")
            else:
                generated_role.status = RoleStatus.DRAFT
            
            # 9. 生成结果
            generation_time = (time.time() - start_time) * 1000
            
            result = RoleGenerationResult(
                request_id=request.request_id,
                generated_role=generated_role,
                generation_process={
                    "domain_analysis": domain_analysis,
                    "capabilities_inferred": len(capabilities),
                    "personality_generated": bool(personality),
                    "validation_result": validation_result,
                    "uniqueness_check": uniqueness_result
                },
                quality_assessment=validation_result,
                generation_time_ms=generation_time,
                confidence_score=domain_analysis["confidence_score"]
            )
            
            # 10. 更新指标
            self._update_metrics(result, validation_result["is_valid"])
            
            # 11. 记录创建历史
            self.creation_history.append({
                "request_id": request.request_id,
                "role_id": role_id,
                "timestamp": datetime.now(),
                "success": validation_result["is_valid"]
            })
            
            logger.info(f"角色创建完成: {role_id} - {role_name}")
            return result
            
        except Exception as e:
            logger.error(f"角色创建失败: {e}")
            
            # 创建错误结果
            error_result = RoleGenerationResult(
                request_id=request.request_id,
                generated_role=GeneratedRole(
                    role_id="error",
                    name="Error Role",
                    role_type=RoleType.EXPERT,
                    domain="error",
                    description=f"创建失败: {str(e)}",
                    system_prompt="",
                    capabilities=[],
                    personality=RolePersonality(
                        communication_style="error",
                        decision_making_approach="error",
                        problem_solving_method="error",
                        creativity_level=0.0,
                        analytical_depth=0.0,
                        risk_tolerance=0.0,
                        collaboration_preference=0.0
                    ),
                    expertise_level=ExpertiseLevel.NOVICE,
                    interaction_style=InteractionStyle.FORMAL,
                    status=RoleStatus.DRAFT
                ),
                generation_process={"error": str(e)},
                quality_assessment={"is_valid": False, "errors": [str(e)]},
                generation_time_ms=(time.time() - start_time) * 1000,
                confidence_score=0.0
            )
            
            return error_result
    
    def _generate_role_name(
        self, 
        requirements: RoleRequirement, 
        domain_analysis: Dict[str, Any]
    ) -> str:
        """生成角色名称"""
        role_type = domain_analysis["recommended_role_type"]
        domain = requirements.domain
        
        # 角色类型的中文映射
        type_names = {
            RoleType.EXPERT: "专家",
            RoleType.ADVISOR: "顾问",
            RoleType.ANALYST: "分析师",
            RoleType.CREATOR: "创作者",
            RoleType.FACILITATOR: "协调者",
            RoleType.CRITIC: "评论家",
            RoleType.SYNTHESIZER: "综合专家"
        }
        
        type_name = type_names.get(role_type, "专家")
        
        # 生成名称
        if requirements.expertise_level == ExpertiseLevel.MASTER:
            level_prefix = "资深"
        elif requirements.expertise_level == ExpertiseLevel.EXPERT:
            level_prefix = "高级"
        elif requirements.expertise_level == ExpertiseLevel.ADVANCED:
            level_prefix = ""
        else:
            level_prefix = "初级"
        
        return f"{level_prefix}{domain}{type_name}"
    
    def _generate_description(
        self, 
        requirements: RoleRequirement, 
        capabilities: List[RoleCapability]
    ) -> str:
        """生成角色描述"""
        capability_names = [cap.name for cap in capabilities[:5]]
        
        description = f"专注于{requirements.domain}领域的{requirements.expertise_level.value}级专业人士。"
        
        if requirements.task_description:
            description += f"主要负责{requirements.task_description}。"
        
        if capability_names:
            description += f"核心能力包括：{', '.join(capability_names)}。"
        
        return description
    
    def _update_metrics(self, result: RoleGenerationResult, is_valid: bool):
        """更新性能指标"""
        self.metrics["roles_created"] += 1
        
        # 更新平均创建时间
        total_time = self.metrics["average_creation_time"] * (self.metrics["roles_created"] - 1)
        total_time += result.generation_time_ms
        self.metrics["average_creation_time"] = total_time / self.metrics["roles_created"]
        
        # 更新成功率
        if is_valid:
            success_count = self.metrics["success_rate"] * (self.metrics["roles_created"] - 1) + 1
        else:
            success_count = self.metrics["success_rate"] * (self.metrics["roles_created"] - 1)
        
        self.metrics["success_rate"] = success_count / self.metrics["roles_created"]
        
        # 更新验证通过率
        self.metrics["validation_pass_rate"] = self.metrics["success_rate"]  # 简化实现
    
    async def suggest_role_improvements(
        self, 
        role_id: str,
        usage_feedback: Dict[str, Any]
    ) -> List[str]:
        """建议角色改进"""
        try:
            # 加载角色
            role = await self.persistence_manager.load_role(role_id)
            if not role:
                return ["角色未找到"]
            
            # 分析反馈
            suggestions = []
            
            if usage_feedback.get("effectiveness_score", 0.5) < 0.6:
                suggestions.append("考虑提升专业能力的深度和广度")
            
            if usage_feedback.get("clarity_score", 0.5) < 0.6:
                suggestions.append("改进角色描述和系统提示词的清晰度")
            
            if usage_feedback.get("relevance_score", 0.5) < 0.6:
                suggestions.append("调整角色定位，使其更贴近实际需求")
            
            if usage_feedback.get("user_satisfaction", 0.5) < 0.6:
                suggestions.append("优化交互风格和沟通方式")
            
            # 基于使用数据的建议
            if role.usage_count > 10:
                if not suggestions:
                    suggestions.append("角色表现良好，可考虑创建专业化变体")
            else:
                suggestions.append("增加角色的实用性和适用场景")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"生成改进建议失败: {e}")
            return [f"生成建议时出错: {str(e)}"]
    
    async def generate_role_variants(
        self, 
        base_role_id: str,
        variation_requirements: Dict[str, Any]
    ) -> List[GeneratedRole]:
        """生成角色变体"""
        try:
            # 加载基础角色
            base_role = await self.persistence_manager.load_role(base_role_id)
            if not base_role:
                return []
            
            variants = []
            
            # 生成不同专业水平的变体
            if variation_requirements.get("expertise_levels"):
                for level in variation_requirements["expertise_levels"]:
                    variant = await self._create_expertise_variant(base_role, level)
                    if variant:
                        variants.append(variant)
            
            # 生成不同交互风格的变体
            if variation_requirements.get("interaction_styles"):
                for style in variation_requirements["interaction_styles"]:
                    variant = await self._create_style_variant(base_role, style)
                    if variant:
                        variants.append(variant)
            
            # 生成特定场景的变体
            if variation_requirements.get("scenarios"):
                for scenario in variation_requirements["scenarios"]:
                    variant = await self._create_scenario_variant(base_role, scenario)
                    if variant:
                        variants.append(variant)
            
            return variants
            
        except Exception as e:
            logger.error(f"生成角色变体失败: {e}")
            return []
    
    async def _create_expertise_variant(
        self, 
        base_role: GeneratedRole, 
        new_level: str
    ) -> Optional[GeneratedRole]:
        """创建不同专业水平的变体"""
        try:
            expertise_level = ExpertiseLevel(new_level)
            
            # 创建变体
            variant = GeneratedRole(
                role_id=f"{base_role.role_id}_expertise_{new_level}",
                name=f"{new_level}级{base_role.name}",
                role_type=base_role.role_type,
                domain=base_role.domain,
                description=f"基于{base_role.name}的{new_level}级专业变体。{base_role.description}",
                system_prompt="",  # 重新生成
                capabilities=[
                    RoleCapability(
                        capability_id=f"var_{cap.capability_id}",
                        name=cap.name,
                        description=cap.description,
                        skill_level=self._adjust_skill_level(cap.skill_level, expertise_level),
                        keywords=cap.keywords,
                        prerequisites=cap.prerequisites,
                        related_domains=cap.related_domains
                    )
                    for cap in base_role.capabilities
                ],
                personality=base_role.personality,
                expertise_level=expertise_level,
                interaction_style=base_role.interaction_style,
                keywords=base_role.keywords,
                metadata={
                    **base_role.metadata,
                    "variant_type": "expertise",
                    "base_role_id": base_role.role_id
                },
                status=RoleStatus.DRAFT
            )
            
            # 重新生成系统提示词
            variant.system_prompt = await self.template_generator.generate_system_prompt(
                variant, {}
            )
            
            return variant
            
        except Exception as e:
            logger.error(f"创建专业水平变体失败: {e}")
            return None
    
    def _adjust_skill_level(self, base_level: float, expertise_level: ExpertiseLevel) -> float:
        """调整技能水平"""
        level_multipliers = {
            ExpertiseLevel.NOVICE: 0.3,
            ExpertiseLevel.INTERMEDIATE: 0.5,
            ExpertiseLevel.ADVANCED: 0.7,
            ExpertiseLevel.EXPERT: 0.9,
            ExpertiseLevel.MASTER: 1.0
        }
        
        multiplier = level_multipliers.get(expertise_level, 0.5)
        return min(base_level * multiplier + 0.1, 1.0)
    
    async def _create_style_variant(
        self, 
        base_role: GeneratedRole, 
        new_style: str
    ) -> Optional[GeneratedRole]:
        """创建不同交互风格的变体"""
        # 实现交互风格变体创建逻辑
        # 简化实现，返回None
        return None
    
    async def _create_scenario_variant(
        self, 
        base_role: GeneratedRole, 
        scenario: str
    ) -> Optional[GeneratedRole]:
        """创建特定场景的变体"""
        # 实现场景变体创建逻辑
        # 简化实现，返回None
        return None
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            # 获取角色统计
            role_stats = await self.persistence_manager.get_role_statistics()
            
            # 系统健康状态
            health_status = {
                "intelligence_engine": "healthy",
                "template_generator": "healthy",
                "validator": "healthy",
                "persistence_manager": "healthy"
            }
            
            # 创建历史统计
            recent_history = self.creation_history[-10:] if self.creation_history else []
            
            status = {
                "system_name": "AutonomousRoleCreationSystem",
                "status": "healthy",
                "version": "1.0.0",
                "uptime": time.time(),  # 简化实现
                "metrics": self.metrics,
                "role_statistics": role_stats,
                "component_health": health_status,
                "recent_creations": len(recent_history),
                "total_creation_requests": len(self.creation_history)
            }
            
            return status
            
        except Exception as e:
            logger.error(f"获取系统状态失败: {e}")
            return {
                "system_name": "AutonomousRoleCreationSystem",
                "status": "error",
                "error": str(e)
            }

# ============= 工厂函数 =============

def create_autonomous_role_creation_system(
    storage_dir: str = "data/roles"
) -> AutonomousRoleCreationSystem:
    """创建自主角色创建系统实例"""
    return AutonomousRoleCreationSystem(storage_dir)

# ============= 便捷函数 =============

async def create_role_from_description(
    domain: str,
    task_description: str,
    expertise_level: str = "advanced",
    interaction_style: str = "professional",
    additional_capabilities: List[str] = None
) -> RoleGenerationResult:
    """从描述创建角色的便捷函数"""
    system = create_autonomous_role_creation_system()
    
    requirements = RoleRequirement(
        domain=domain,
        task_description=task_description,
        expertise_level=ExpertiseLevel(expertise_level),
        interaction_style=InteractionStyle(interaction_style),
        required_capabilities=additional_capabilities or []
    )
    
    request = RoleGenerationRequest(
        request_id=f"quick_create_{int(time.time())}",
        requirements=requirements
    )
    
    return await system.create_role(request)

# ============= 使用示例 =============

async def example_usage():
    """使用示例"""
    # 创建系统
    system = create_autonomous_role_creation_system()
    
    # 创建角色需求
    requirements = RoleRequirement(
        domain="人工智能",
        task_description="设计和实现机器学习算法，解决复杂的数据分析问题",
        expertise_level=ExpertiseLevel.EXPERT,
        interaction_style=InteractionStyle.ACADEMIC,
        required_capabilities=["机器学习", "深度学习", "数据分析", "算法优化"],
        context_info={"project_type": "research", "team_size": "small"}
    )
    
    # 创建生成请求
    request = RoleGenerationRequest(
        request_id="example_001",
        requirements=requirements,
        preferences={"emphasis": "technical_depth"},
        constraints={"max_capabilities": 10}
    )
    
    # 生成角色
    result = await system.create_role(request)
    
    print(f"角色创建结果:")
    print(f"- 角色ID: {result.generated_role.role_id}")
    print(f"- 角色名称: {result.generated_role.name}")
    print(f"- 专业领域: {result.generated_role.domain}")
    print(f"- 角色类型: {result.generated_role.role_type.value}")
    print(f"- 能力数量: {len(result.generated_role.capabilities)}")
    print(f"- 创建时间: {result.generation_time_ms:.2f}ms")
    print(f"- 置信度: {result.confidence_score:.2f}")
    print(f"- 验证通过: {result.quality_assessment.get('is_valid', False)}")
    
    # 获取系统状态
    status = await system.get_system_status()
    print(f"\n系统状态: {status['status']}")
    print(f"已创建角色数: {status['metrics']['roles_created']}")

if __name__ == "__main__":
    asyncio.run(example_usage())