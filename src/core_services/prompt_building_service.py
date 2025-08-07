#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 19:30:00
@Author  : DAIP-LIVE Team
@File    : prompt_building_service.py
@Description:
    项目级提示词构建服务
    
    核心功能：
    - 解耦复杂的上下文组装逻辑
    - 动态模板管理和生成
    - Token使用优化
    - 提示词质量保证
"""

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import yaml
import sqlite3
from collections import defaultdict
import weakref

logger = logging.getLogger(__name__)

# ============= 数据模型定义 =============

class ContextType(Enum):
    """上下文类型"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    ROLE = "role"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    TOOL = "tool"

class TemplateType(Enum):
    """模板类型"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    CONDITIONAL = "conditional"
    COMPOSITE = "composite"

class OptimizationGoal(Enum):
    """优化目标"""
    MIN_TOKENS = "minimize_tokens"
    MAX_RELEVANCE = "maximize_relevance"
    BALANCE = "balance"
    SPEED = "speed"

@dataclass
class ContextSource:
    """上下文源定义"""
    source_id: str
    source_type: ContextType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: float = 1.0
    relevance_score: float = 1.0
    token_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ContextConstraints:
    """上下文约束"""
    max_tokens: int = 4000
    min_relevance: float = 0.5
    required_sources: List[str] = field(default_factory=list)
    excluded_sources: List[str] = field(default_factory=list)
    preserve_order: bool = False
    allow_truncation: bool = True

@dataclass
class ContextSpec:
    """上下文规范"""
    context_id: str
    scenario: str
    user_query: str
    target_role: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    required_knowledge: List[str] = field(default_factory=list)
    constraints: Optional[ContextConstraints] = None

@dataclass
class AssembledContext:
    """组装后的上下文"""
    context_id: str
    sources: List[ContextSource]
    final_content: str
    total_tokens: int
    assembly_time_ms: float
    quality_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PromptTemplate:
    """提示词模板"""
    template_id: str
    name: str
    template_type: TemplateType
    content_template: str
    variables: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0

@dataclass
class TemplateRequirements:
    """模板需求"""
    scenario: str
    role_requirements: Dict[str, Any]
    context_requirements: Dict[str, Any]
    performance_requirements: Dict[str, Any]
    quality_requirements: Dict[str, Any]

@dataclass
class OptimizationGoals:
    """优化目标定义"""
    primary_goal: OptimizationGoal
    target_token_count: Optional[int] = None
    min_quality_score: float = 0.7
    max_processing_time_ms: float = 500.0
    custom_objectives: Dict[str, float] = field(default_factory=dict)

@dataclass
class OptimizedPrompt:
    """优化后的提示词"""
    original_prompt: str
    optimized_prompt: str
    optimization_report: Dict[str, Any]
    token_reduction: int
    quality_impact: float
    processing_time_ms: float

@dataclass
class PerformanceAnalysis:
    """性能分析结果"""
    prompt_id: str
    metrics: Dict[str, float]
    bottlenecks: List[str]
    recommendations: List[str]
    analysis_time: datetime = field(default_factory=datetime.now)

# ============= 核心接口定义 =============

class IContextAssemblyEngine(ABC):
    """上下文组装引擎接口"""
    
    @abstractmethod
    async def assemble_context(
        self, 
        context_spec: ContextSpec,
        sources: List[ContextSource],
        constraints: ContextConstraints
    ) -> AssembledContext:
        """组装上下文"""
        pass
    
    @abstractmethod
    async def optimize_context_size(
        self, 
        context: AssembledContext,
        target_tokens: int
    ) -> AssembledContext:
        """优化上下文大小"""
        pass
    
    @abstractmethod
    async def validate_context_quality(
        self,
        context: AssembledContext
    ) -> Dict[str, Any]:
        """验证上下文质量"""
        pass

class ITemplateManager(ABC):
    """模板管理器接口"""
    
    @abstractmethod
    async def get_template(
        self, 
        template_id: str,
        context: Dict[str, Any]
    ) -> PromptTemplate:
        """获取模板"""
        pass
    
    @abstractmethod
    async def generate_dynamic_template(
        self,
        scenario: str,
        requirements: TemplateRequirements
    ) -> PromptTemplate:
        """生成动态模板"""
        pass
    
    @abstractmethod
    async def save_template(
        self,
        template: PromptTemplate
    ) -> bool:
        """保存模板"""
        pass
    
    @abstractmethod
    async def list_templates(
        self,
        filters: Dict[str, Any] = None
    ) -> List[PromptTemplate]:
        """列出模板"""
        pass

class IOptimizationEngine(ABC):
    """优化引擎接口"""
    
    @abstractmethod
    async def optimize_prompt(
        self,
        prompt: str,
        optimization_goals: OptimizationGoals
    ) -> OptimizedPrompt:
        """优化提示词"""
        pass
    
    @abstractmethod
    async def analyze_performance(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> PerformanceAnalysis:
        """分析性能"""
        pass
    
    @abstractmethod
    async def suggest_improvements(
        self,
        prompt: str,
        performance_data: Dict[str, Any]
    ) -> List[str]:
        """建议改进"""
        pass

class IQualityAssurance(ABC):
    """质量保证接口"""
    
    @abstractmethod
    async def validate_prompt(
        self,
        prompt: str,
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证提示词"""
        pass
    
    @abstractmethod
    async def check_consistency(
        self,
        prompts: List[str]
    ) -> Dict[str, Any]:
        """检查一致性"""
        pass
    
    @abstractmethod
    async def run_ab_test(
        self,
        prompt_a: str,
        prompt_b: str,
        test_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行A/B测试"""
        pass

class IPromptBuildingService(ABC):
    """提示词构建服务主接口"""
    
    @abstractmethod
    async def build_prompt(
        self,
        context_spec: ContextSpec,
        template_id: Optional[str] = None,
        optimization_goals: Optional[OptimizationGoals] = None
    ) -> str:
        """构建提示词"""
        pass
    
    @abstractmethod
    async def build_prompt_with_analysis(
        self,
        context_spec: ContextSpec,
        template_id: Optional[str] = None,
        optimization_goals: Optional[OptimizationGoals] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """构建提示词并返回分析信息"""
        pass
    
    @abstractmethod
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        pass

# ============= 实现类开始 =============

class ContextAssemblyEngine(IContextAssemblyEngine):
    """上下文组装引擎实现"""
    
    def __init__(self):
        self.assembly_cache = {}
        self.performance_metrics = defaultdict(list)
    
    async def assemble_context(
        self, 
        context_spec: ContextSpec,
        sources: List[ContextSource],
        constraints: ContextConstraints
    ) -> AssembledContext:
        """组装上下文"""
        start_time = time.time()
        
        # 按优先级和相关性排序
        sorted_sources = sorted(
            sources, 
            key=lambda x: (x.priority * x.relevance_score, -x.token_count),
            reverse=True
        )
        
        # 过滤必需和排除的源
        filtered_sources = []
        for source in sorted_sources:
            if constraints.required_sources and source.source_id not in constraints.required_sources:
                continue
            if source.source_id in constraints.excluded_sources:
                continue
            if source.relevance_score < constraints.min_relevance:
                continue
            filtered_sources.append(source)
        
        # 组装内容，控制Token数量
        assembled_content = ""
        selected_sources = []
        total_tokens = 0
        
        for source in filtered_sources:
            if total_tokens + source.token_count > constraints.max_tokens:
                if constraints.allow_truncation and selected_sources:
                    # 尝试截断当前源
                    remaining_tokens = constraints.max_tokens - total_tokens
                    if remaining_tokens > 50:  # 最少保留50个token
                        truncated_content = self._truncate_content(
                            source.content, 
                            remaining_tokens
                        )
                        truncated_source = ContextSource(
                            source_id=source.source_id + "_truncated",
                            source_type=source.source_type,
                            content=truncated_content,
                            metadata={**source.metadata, "truncated": True},
                            priority=source.priority,
                            relevance_score=source.relevance_score * 0.8,  # 截断降低相关性
                            token_count=remaining_tokens
                        )
                        selected_sources.append(truncated_source)
                        assembled_content += truncated_content + "\n\n"
                        total_tokens += remaining_tokens
                break
            
            selected_sources.append(source)
            assembled_content += source.content + "\n\n"
            total_tokens += source.token_count
        
        # 计算质量分数
        quality_score = self._calculate_quality_score(
            selected_sources, 
            context_spec, 
            constraints
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        assembled_context = AssembledContext(
            context_id=context_spec.context_id,
            sources=selected_sources,
            final_content=assembled_content.strip(),
            total_tokens=total_tokens,
            assembly_time_ms=processing_time,
            quality_score=quality_score,
            metadata={
                "original_source_count": len(sources),
                "selected_source_count": len(selected_sources),
                "truncated": any(s.metadata.get("truncated", False) for s in selected_sources)
            }
        )
        
        # 记录性能指标
        self.performance_metrics["assembly_time"].append(processing_time)
        self.performance_metrics["token_efficiency"].append(
            total_tokens / constraints.max_tokens if constraints.max_tokens > 0 else 1.0
        )
        
        return assembled_context
    
    def _truncate_content(self, content: str, max_tokens: int) -> str:
        """智能截断内容"""
        # 简单的基于字符的截断，实际应用中可以使用更精确的Token计算
        target_chars = max_tokens * 4  # 假设平均1 token = 4 字符
        
        if len(content) <= target_chars:
            return content
        
        # 尝试在句子边界截断
        sentences = content.split('。')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '。') <= target_chars:
                truncated += sentence + '。'
            else:
                break
        
        if not truncated:
            # 如果没有完整的句子，则按字符截断
            truncated = content[:target_chars] + "..."
        
        return truncated
    
    def _calculate_quality_score(
        self, 
        sources: List[ContextSource], 
        context_spec: ContextSpec, 
        constraints: ContextConstraints
    ) -> float:
        """计算上下文质量分数"""
        if not sources:
            return 0.0
        
        # 相关性权重
        relevance_score = sum(s.relevance_score for s in sources) / len(sources)
        
        # 完整性权重 (是否包含必需的源)
        completeness_score = 1.0
        if constraints.required_sources:
            included_required = sum(
                1 for req in constraints.required_sources
                if any(s.source_id == req for s in sources)
            )
            completeness_score = included_required / len(constraints.required_sources)
        
        # 多样性权重 (不同类型的源)
        source_types = set(s.source_type for s in sources)
        diversity_score = min(len(source_types) / 3, 1.0)  # 最多3种类型为满分
        
        # Token效率权重
        total_tokens = sum(s.token_count for s in sources)
        efficiency_score = min(total_tokens / constraints.max_tokens, 1.0)
        
        # 综合评分
        quality_score = (
            relevance_score * 0.4 +
            completeness_score * 0.3 +
            diversity_score * 0.2 +
            efficiency_score * 0.1
        )
        
        return min(quality_score, 1.0)
    
    async def optimize_context_size(
        self, 
        context: AssembledContext,
        target_tokens: int
    ) -> AssembledContext:
        """优化上下文大小"""
        if context.total_tokens <= target_tokens:
            return context
        
        # 重新组装，使用更严格的约束
        new_constraints = ContextConstraints(
            max_tokens=target_tokens,
            min_relevance=0.6,  # 提高相关性要求
            allow_truncation=True
        )
        
        # 模拟重新组装（简化实现）
        sorted_sources = sorted(
            context.sources,
            key=lambda x: x.relevance_score * x.priority,
            reverse=True
        )
        
        selected_sources = []
        total_tokens = 0
        assembled_content = ""
        
        for source in sorted_sources:
            if total_tokens + source.token_count <= target_tokens:
                selected_sources.append(source)
                assembled_content += source.content + "\n\n"
                total_tokens += source.token_count
        
        optimized_context = AssembledContext(
            context_id=context.context_id + "_optimized",
            sources=selected_sources,
            final_content=assembled_content.strip(),
            total_tokens=total_tokens,
            assembly_time_ms=context.assembly_time_ms,
            quality_score=self._calculate_quality_score(
                selected_sources, 
                None,  # 简化实现
                new_constraints
            ),
            metadata={
                **context.metadata,
                "optimized": True,
                "original_tokens": context.total_tokens
            }
        )
        
        return optimized_context
    
    async def validate_context_quality(
        self,
        context: AssembledContext
    ) -> Dict[str, Any]:
        """验证上下文质量"""
        validation_result = {
            "is_valid": True,
            "quality_score": context.quality_score,
            "issues": [],
            "recommendations": []
        }
        
        # 检查质量分数
        if context.quality_score < 0.6:
            validation_result["issues"].append("质量分数过低")
            validation_result["recommendations"].append("增加更多相关源或提高相关性阈值")
        
        # 检查Token使用效率
        if context.total_tokens < 100:
            validation_result["issues"].append("上下文内容过少")
            validation_result["recommendations"].append("增加更多上下文源")
        
        # 检查源多样性
        source_types = set(s.source_type for s in context.sources)
        if len(source_types) < 2:
            validation_result["issues"].append("上下文源类型单一")
            validation_result["recommendations"].append("添加更多类型的上下文源")
        
        validation_result["is_valid"] = len(validation_result["issues"]) == 0
        
        return validation_result

# ============= 继续实现其他核心组件 =============

class TemplateManager(ITemplateManager):
    """模板管理器实现"""
    
    def __init__(self, templates_dir: str = "templates/prompts"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.templates_dir / "templates.db"
        self.template_cache = {}
        self._init_database()
    
    def _init_database(self):
        """初始化模板数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                template_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                template_type TEXT NOT NULL,
                content_template TEXT NOT NULL,
                variables TEXT,
                metadata TEXT,
                version TEXT,
                created_at TEXT,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def get_template(
        self, 
        template_id: str,
        context: Dict[str, Any]
    ) -> PromptTemplate:
        """获取模板"""
        # 先检查缓存
        if template_id in self.template_cache:
            template = self.template_cache[template_id]
        else:
            # 从数据库加载
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM templates WHERE template_id = ?",
                (template_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                raise ValueError(f"模板未找到: {template_id}")
            
            template = PromptTemplate(
                template_id=row[0],
                name=row[1],
                template_type=TemplateType(row[2]),
                content_template=row[3],
                variables=json.loads(row[4]) if row[4] else [],
                metadata=json.loads(row[5]) if row[5] else {},
                version=row[6],
                created_at=datetime.fromisoformat(row[7]),
                usage_count=row[8]
            )
            
            self.template_cache[template_id] = template
        
        # 更新使用计数
        await self._update_usage_count(template_id)
        
        return template
    
    async def generate_dynamic_template(
        self,
        scenario: str,
        requirements: TemplateRequirements
    ) -> PromptTemplate:
        """生成动态模板"""
        # 动态模板生成逻辑
        template_content = self._build_dynamic_template_content(scenario, requirements)
        
        template_id = f"dynamic_{scenario}_{int(time.time())}"
        
        template = PromptTemplate(
            template_id=template_id,
            name=f"Dynamic Template for {scenario}",
            template_type=TemplateType.DYNAMIC,
            content_template=template_content,
            variables=self._extract_variables(template_content),
            metadata={
                "scenario": scenario,
                "auto_generated": True,
                "requirements": requirements.__dict__
            }
        )
        
        return template
    
    def _build_dynamic_template_content(
        self, 
        scenario: str, 
        requirements: TemplateRequirements
    ) -> str:
        """构建动态模板内容"""
        base_templates = {
            "academic_research": """
你是一位专业的学术研究助手。根据以下要求进行研究分析：

研究主题：{research_topic}
研究角度：{research_perspective}
专业背景：{professional_background}

请提供：
1. 详细的分析报告
2. 相关研究发现
3. 结论和建议

上下文信息：
{context_information}
""",
            "expert_consultation": """
作为{expert_role}专家，请针对以下咨询提供专业建议：

咨询问题：{consultation_query}
专业领域：{expertise_domain}
相关背景：{background_context}

请从以下角度分析：
1. 专业观点和见解
2. 风险评估
3. 具体建议

相关信息：
{related_information}
""",
            "casual_discussion": """
让我们就以下话题进行深入讨论：

话题：{discussion_topic}
讨论角度：{discussion_perspective}
参与者背景：{participant_background}

讨论要点：
1. {point_1}
2. {point_2}
3. {point_3}

背景信息：
{background_information}
"""
        }
        
        return base_templates.get(scenario, base_templates["casual_discussion"])
    
    def _extract_variables(self, template_content: str) -> List[str]:
        """从模板内容中提取变量"""
        import re
        variables = re.findall(r'\{(\w+)\}', template_content)
        return list(set(variables))
    
    async def save_template(self, template: PromptTemplate) -> bool:
        """保存模板"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO templates 
                (template_id, name, template_type, content_template, variables, 
                 metadata, version, created_at, usage_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                template.template_id,
                template.name,
                template.template_type.value,
                template.content_template,
                json.dumps(template.variables),
                json.dumps(template.metadata),
                template.version,
                template.created_at.isoformat(),
                template.usage_count
            ))
            
            conn.commit()
            conn.close()
            
            # 更新缓存
            self.template_cache[template.template_id] = template
            
            return True
        except Exception as e:
            logger.error(f"保存模板失败: {e}")
            return False
    
    async def list_templates(
        self,
        filters: Dict[str, Any] = None
    ) -> List[PromptTemplate]:
        """列出模板"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM templates"
        params = []
        
        if filters:
            conditions = []
            if "template_type" in filters:
                conditions.append("template_type = ?")
                params.append(filters["template_type"])
            if "scenario" in filters:
                conditions.append("metadata LIKE ?")
                params.append(f'%"scenario": "{filters["scenario"]}"%')
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY usage_count DESC, created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        templates = []
        for row in rows:
            template = PromptTemplate(
                template_id=row[0],
                name=row[1],
                template_type=TemplateType(row[2]),
                content_template=row[3],
                variables=json.loads(row[4]) if row[4] else [],
                metadata=json.loads(row[5]) if row[5] else {},
                version=row[6],
                created_at=datetime.fromisoformat(row[7]),
                usage_count=row[8]
            )
            templates.append(template)
        
        return templates
    
    async def _update_usage_count(self, template_id: str):
        """更新使用计数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE templates SET usage_count = usage_count + 1 WHERE template_id = ?",
            (template_id,)
        )
        
        conn.commit()
        conn.close()

# ============= 优化引擎实现 =============

class OptimizationEngine(IOptimizationEngine):
    """优化引擎实现"""
    
    def __init__(self):
        self.optimization_cache = {}
        self.performance_history = defaultdict(list)
    
    async def optimize_prompt(
        self,
        prompt: str,
        optimization_goals: OptimizationGoals
    ) -> OptimizedPrompt:
        """优化提示词"""
        start_time = time.time()
        
        original_tokens = TokenCounter.count_tokens(prompt)
        optimized_content = prompt
        
        # 根据优化目标选择策略
        if optimization_goals.primary_goal == OptimizationGoal.MIN_TOKENS:
            optimized_content = await self._minimize_tokens(
                prompt, 
                optimization_goals.target_token_count
            )
        elif optimization_goals.primary_goal == OptimizationGoal.MAX_RELEVANCE:
            optimized_content = await self._maximize_relevance(prompt)
        elif optimization_goals.primary_goal == OptimizationGoal.BALANCE:
            optimized_content = await self._balance_optimization(prompt, optimization_goals)
        elif optimization_goals.primary_goal == OptimizationGoal.SPEED:
            optimized_content = await self._speed_optimization(prompt)
        
        optimized_tokens = TokenCounter.count_tokens(optimized_content)
        processing_time = (time.time() - start_time) * 1000
        
        # 计算质量影响
        quality_impact = await self._calculate_quality_impact(prompt, optimized_content)
        
        optimization_report = {
            "strategy": optimization_goals.primary_goal.value,
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "token_reduction": original_tokens - optimized_tokens,
            "reduction_percentage": (original_tokens - optimized_tokens) / original_tokens * 100,
            "quality_impact": quality_impact,
            "processing_time_ms": processing_time,
            "optimizations_applied": self._get_applied_optimizations(prompt, optimized_content)
        }
        
        return OptimizedPrompt(
            original_prompt=prompt,
            optimized_prompt=optimized_content,
            optimization_report=optimization_report,
            token_reduction=original_tokens - optimized_tokens,
            quality_impact=quality_impact,
            processing_time_ms=processing_time
        )
    
    async def _minimize_tokens(self, prompt: str, target_tokens: Optional[int]) -> str:
        """最小化Token数量"""
        optimized = prompt
        
        # 移除多余的空白
        optimized = ' '.join(optimized.split())
        
        # 简化表达
        simplifications = {
            "请您": "请",
            "能够": "能",
            "进行": "",
            "实现": "",
            "非常": "",
            "特别": "",
            "详细地": "详细",
            "仔细地": "仔细",
        }
        
        for old, new in simplifications.items():
            optimized = optimized.replace(old, new)
        
        # 如果指定了目标Token数，进行截断
        if target_tokens:
            current_tokens = TokenCounter.count_tokens(optimized)
            if current_tokens > target_tokens:
                # 智能截断保留重要信息
                optimized = self._intelligent_truncate(optimized, target_tokens)
        
        return optimized
    
    async def _maximize_relevance(self, prompt: str) -> str:
        """最大化相关性"""
        # 增加相关性指引
        relevance_enhancers = [
            "请确保回答直接相关：",
            "重点关注核心问题：",
            "避免偏离主题：",
        ]
        
        # 在适当位置插入相关性增强指令
        lines = prompt.split('\n')
        if len(lines) > 2:
            lines.insert(1, "请确保回答直接相关且准确。")
        
        return '\n'.join(lines)
    
    async def _balance_optimization(self, prompt: str, goals: OptimizationGoals) -> str:
        """平衡优化"""
        # 组合多种优化策略
        optimized = await self._minimize_tokens(prompt, goals.target_token_count)
        optimized = await self._maximize_relevance(optimized)
        
        return optimized
    
    async def _speed_optimization(self, prompt: str) -> str:
        """速度优化"""
        # 简化指令，减少复杂度
        optimized = prompt.replace("请详细说明", "请说明")
        optimized = optimized.replace("请提供全面的", "请提供")
        optimized = optimized.replace("请进行深入的", "请分析")
        
        return optimized
    
    def _intelligent_truncate(self, text: str, target_tokens: int) -> str:
        """智能截断文本"""
        current_tokens = TokenCounter.count_tokens(text)
        if current_tokens <= target_tokens:
            return text
        
        # 计算需要截断的比例
        ratio = target_tokens / current_tokens
        target_length = int(len(text) * ratio)
        
        # 在句子边界截断
        sentences = text.split('。')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '。') <= target_length:
                truncated += sentence + '。'
            else:
                break
        
        return truncated or text[:target_length]
    
    async def _calculate_quality_impact(self, original: str, optimized: str) -> float:
        """计算质量影响"""
        # 简化的质量影响计算
        original_length = len(original)
        optimized_length = len(optimized)
        
        if original_length == 0:
            return 0.0
        
        length_ratio = optimized_length / original_length
        
        # 基于长度变化估算质量影响
        if length_ratio > 0.8:
            return 0.1  # 轻微影响
        elif length_ratio > 0.6:
            return 0.3  # 中等影响
        else:
            return 0.5  # 较大影响
    
    def _get_applied_optimizations(self, original: str, optimized: str) -> List[str]:
        """获取应用的优化策略"""
        optimizations = []
        
        if len(optimized) < len(original):
            optimizations.append("内容压缩")
        
        if original.count(' ') > optimized.count(' '):
            optimizations.append("空白符优化")
        
        if '详细' in original and '详细' not in optimized:
            optimizations.append("表达简化")
        
        return optimizations
    
    async def analyze_performance(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> PerformanceAnalysis:
        """分析性能"""
        metrics = {}
        bottlenecks = []
        recommendations = []
        
        # Token分析
        token_count = TokenCounter.count_tokens(prompt)
        metrics["token_count"] = token_count
        metrics["estimated_cost"] = token_count * 0.0001  # 假设每Token成本
        
        if token_count > 3000:
            bottlenecks.append("Token数量过多")
            recommendations.append("考虑压缩提示词内容")
        
        # 复杂度分析
        complexity_score = self._calculate_complexity(prompt)
        metrics["complexity_score"] = complexity_score
        
        if complexity_score > 0.8:
            bottlenecks.append("提示词结构复杂")
            recommendations.append("简化指令结构")
        
        # 相关性分析
        relevance_score = self._calculate_relevance(prompt, context)
        metrics["relevance_score"] = relevance_score
        
        if relevance_score < 0.6:
            bottlenecks.append("相关性不足")
            recommendations.append("增加上下文相关信息")
        
        prompt_id = hashlib.md5(prompt.encode()).hexdigest()[:8]
        
        return PerformanceAnalysis(
            prompt_id=prompt_id,
            metrics=metrics,
            bottlenecks=bottlenecks,
            recommendations=recommendations
        )
    
    def _calculate_complexity(self, prompt: str) -> float:
        """计算复杂度"""
        # 基于多个指标计算复杂度
        lines = prompt.split('\n')
        avg_line_length = sum(len(line) for line in lines) / len(lines)
        
        complexity_factors = {
            "average_line_length": min(avg_line_length / 100, 1.0),
            "total_lines": min(len(lines) / 20, 1.0),
            "nested_structure": prompt.count('：') / 10,
            "question_complexity": prompt.count('？') / 5
        }
        
        return sum(complexity_factors.values()) / len(complexity_factors)
    
    def _calculate_relevance(self, prompt: str, context: Dict[str, Any]) -> float:
        """计算相关性"""
        if not context:
            return 0.5
        
        # 简化的相关性计算
        relevance_score = 0.5
        
        # 检查是否包含上下文关键词
        if "scenario" in context:
            scenario_keywords = context["scenario"].split()
            matching_keywords = sum(1 for kw in scenario_keywords if kw in prompt)
            relevance_score += (matching_keywords / len(scenario_keywords)) * 0.3
        
        # 检查是否包含用户查询相关内容
        if "user_query" in context:
            query_keywords = context["user_query"].split()
            matching_keywords = sum(1 for kw in query_keywords if kw in prompt)
            if query_keywords:
                relevance_score += (matching_keywords / len(query_keywords)) * 0.2
        
        return min(relevance_score, 1.0)
    
    async def suggest_improvements(
        self,
        prompt: str,
        performance_data: Dict[str, Any]
    ) -> List[str]:
        """建议改进"""
        suggestions = []
        
        token_count = performance_data.get("token_count", 0)
        complexity_score = performance_data.get("complexity_score", 0)
        relevance_score = performance_data.get("relevance_score", 0)
        
        if token_count > 2000:
            suggestions.append("建议压缩提示词长度，移除冗余信息")
        
        if complexity_score > 0.7:
            suggestions.append("简化指令结构，使用更直接的表达")
        
        if relevance_score < 0.6:
            suggestions.append("增加与任务更相关的上下文信息")
        
        if not suggestions:
            suggestions.append("当前提示词质量良好，可考虑微调以进一步优化")
        
        return suggestions

# ============= 质量保证实现 =============

class QualityAssurance(IQualityAssurance):
    """质量保证实现"""
    
    def __init__(self):
        self.validation_cache = {}
        self.ab_test_results = defaultdict(list)
    
    async def validate_prompt(
        self,
        prompt: str,
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证提示词"""
        validation_result = {
            "is_valid": True,
            "score": 0.0,
            "issues": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Token长度检查
        token_count = TokenCounter.count_tokens(prompt)
        max_tokens = criteria.get("max_tokens", 4000)
        
        if token_count > max_tokens:
            validation_result["issues"].append(f"Token数量超限: {token_count} > {max_tokens}")
            validation_result["is_valid"] = False
        elif token_count > max_tokens * 0.8:
            validation_result["warnings"].append(f"Token数量接近上限: {token_count}")
        
        # 内容质量检查
        quality_score = self._assess_content_quality(prompt)
        validation_result["score"] = quality_score
        
        if quality_score < criteria.get("min_quality", 0.6):
            validation_result["issues"].append(f"内容质量不足: {quality_score:.2f}")
            validation_result["is_valid"] = False
        
        # 结构检查
        structure_issues = self._check_structure(prompt)
        validation_result["issues"].extend(structure_issues)
        
        if structure_issues:
            validation_result["is_valid"] = False
        
        # 生成改进建议
        if not validation_result["is_valid"]:
            validation_result["suggestions"] = self._generate_improvement_suggestions(
                prompt, validation_result["issues"]
            )
        
        return validation_result
    
    def _assess_content_quality(self, prompt: str) -> float:
        """评估内容质量"""
        quality_factors = {
            "clarity": self._assess_clarity(prompt),
            "completeness": self._assess_completeness(prompt),
            "specificity": self._assess_specificity(prompt),
            "coherence": self._assess_coherence(prompt)
        }
        
        return sum(quality_factors.values()) / len(quality_factors)
    
    def _assess_clarity(self, prompt: str) -> float:
        """评估清晰度"""
        # 基于句子长度和复杂度
        sentences = prompt.split('。')
        if not sentences:
            return 0.0
        
        avg_sentence_length = sum(len(s.strip()) for s in sentences) / len(sentences)
        
        # 理想句子长度为30-60字符
        if 30 <= avg_sentence_length <= 60:
            return 1.0
        elif avg_sentence_length < 30:
            return 0.7  # 可能过于简短
        else:
            return max(0.3, 1.0 - (avg_sentence_length - 60) / 100)
    
    def _assess_completeness(self, prompt: str) -> float:
        """评估完整性"""
        required_elements = ["任务描述", "输出要求", "上下文"]
        found_elements = 0
        
        if any(keyword in prompt for keyword in ["请", "需要", "要求"]):
            found_elements += 1
        
        if any(keyword in prompt for keyword in ["输出", "返回", "提供", "生成"]):
            found_elements += 1
        
        if any(keyword in prompt for keyword in ["背景", "上下文", "信息", "基于"]):
            found_elements += 1
        
        return found_elements / len(required_elements)
    
    def _assess_specificity(self, prompt: str) -> float:
        """评估具体性"""
        # 基于具体指令和示例的存在
        specificity_indicators = [
            "例如", "比如", "具体", "详细", "步骤", "格式", "包括", "如下"
        ]
        
        found_indicators = sum(1 for indicator in specificity_indicators if indicator in prompt)
        return min(found_indicators / 3, 1.0)  # 最多3个指标为满分
    
    def _assess_coherence(self, prompt: str) -> float:
        """评估连贯性"""
        # 简化的连贯性检查
        lines = prompt.strip().split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        if len(non_empty_lines) < 2:
            return 0.5
        
        # 检查逻辑连接词
        connection_words = ["因此", "所以", "另外", "同时", "首先", "其次", "最后", "然后"]
        connections = sum(1 for word in connection_words if word in prompt)
        
        return min(connections / len(non_empty_lines), 1.0)
    
    def _check_structure(self, prompt: str) -> List[str]:
        """检查结构问题"""
        issues = []
        
        # 检查是否为空
        if not prompt.strip():
            issues.append("提示词内容为空")
            return issues
        
        # 检查是否过短
        if len(prompt.strip()) < 10:
            issues.append("提示词内容过短")
        
        # 检查是否有明确的指令
        instruction_keywords = ["请", "需要", "要求", "应该", "必须"]
        if not any(keyword in prompt for keyword in instruction_keywords):
            issues.append("缺少明确的指令词")
        
        return issues
    
    def _generate_improvement_suggestions(self, prompt: str, issues: List[str]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        for issue in issues:
            if "Token数量超限" in issue:
                suggestions.append("压缩内容长度，移除冗余信息")
            elif "内容质量不足" in issue:
                suggestions.append("增加具体指令和示例")
            elif "缺少明确的指令词" in issue:
                suggestions.append("添加明确的行动指令（如'请'、'需要'等）")
            elif "提示词内容过短" in issue:
                suggestions.append("增加更多上下文和具体要求")
        
        return suggestions
    
    async def check_consistency(
        self,
        prompts: List[str]
    ) -> Dict[str, Any]:
        """检查一致性"""
        if len(prompts) < 2:
            return {"consistent": True, "message": "需要至少2个提示词进行比较"}
        
        consistency_metrics = {
            "style_consistency": self._check_style_consistency(prompts),
            "length_consistency": self._check_length_consistency(prompts),
            "structure_consistency": self._check_structure_consistency(prompts),
            "tone_consistency": self._check_tone_consistency(prompts)
        }
        
        overall_consistency = sum(consistency_metrics.values()) / len(consistency_metrics)
        
        return {
            "consistent": overall_consistency > 0.7,
            "overall_score": overall_consistency,
            "metrics": consistency_metrics,
            "recommendations": self._get_consistency_recommendations(consistency_metrics)
        }
    
    def _check_style_consistency(self, prompts: List[str]) -> float:
        """检查风格一致性"""
        # 检查指令词使用的一致性
        instruction_patterns = []
        for prompt in prompts:
            pattern = {
                "uses_please": "请" in prompt,
                "uses_formal": any(word in prompt for word in ["您", "贵"]),
                "uses_questions": "？" in prompt or "?" in prompt
            }
            instruction_patterns.append(pattern)
        
        # 计算模式相似度
        if not instruction_patterns:
            return 1.0
        
        reference_pattern = instruction_patterns[0]
        matches = 0
        total_checks = len(reference_pattern) * len(instruction_patterns)
        
        for pattern in instruction_patterns:
            for key in reference_pattern:
                if pattern[key] == reference_pattern[key]:
                    matches += 1
        
        return matches / total_checks if total_checks > 0 else 1.0
    
    def _check_length_consistency(self, prompts: List[str]) -> float:
        """检查长度一致性"""
        lengths = [len(prompt) for prompt in prompts]
        if not lengths:
            return 1.0
        
        avg_length = sum(lengths) / len(lengths)
        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        coefficient_of_variation = (variance ** 0.5) / avg_length if avg_length > 0 else 0
        
        # CV < 0.3 认为是一致的
        return max(0, 1.0 - coefficient_of_variation / 0.3)
    
    def _check_structure_consistency(self, prompts: List[str]) -> float:
        """检查结构一致性"""
        structures = []
        for prompt in prompts:
            structure = {
                "has_sections": '\n\n' in prompt or '\n' in prompt,
                "has_numbering": any(str(i) in prompt for i in range(1, 6)),
                "has_bullets": '•' in prompt or '·' in prompt or '-' in prompt
            }
            structures.append(structure)
        
        if not structures:
            return 1.0
        
        reference_structure = structures[0]
        matches = 0
        total_checks = len(reference_structure) * len(structures)
        
        for structure in structures:
            for key in reference_structure:
                if structure[key] == reference_structure[key]:
                    matches += 1
        
        return matches / total_checks if total_checks > 0 else 1.0
    
    def _check_tone_consistency(self, prompts: List[str]) -> float:
        """检查语调一致性"""
        tones = []
        for prompt in prompts:
            tone = {
                "formal": any(word in prompt for word in ["请您", "烦请", "恳请"]),
                "casual": any(word in prompt for word in ["你", "咱们", "大家"]),
                "imperative": any(word in prompt for word in ["必须", "应该", "需要"])
            }
            tones.append(tone)
        
        if not tones:
            return 1.0
        
        reference_tone = tones[0]
        matches = 0
        total_checks = len(reference_tone) * len(tones)
        
        for tone in tones:
            for key in reference_tone:
                if tone[key] == reference_tone[key]:
                    matches += 1
        
        return matches / total_checks if total_checks > 0 else 1.0
    
    def _get_consistency_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """获取一致性建议"""
        recommendations = []
        
        if metrics["style_consistency"] < 0.7:
            recommendations.append("统一指令词和表达风格")
        
        if metrics["length_consistency"] < 0.7:
            recommendations.append("保持提示词长度相近")
        
        if metrics["structure_consistency"] < 0.7:
            recommendations.append("使用统一的结构格式")
        
        if metrics["tone_consistency"] < 0.7:
            recommendations.append("保持语调风格一致")
        
        return recommendations
    
    async def run_ab_test(
        self,
        prompt_a: str,
        prompt_b: str,
        test_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行A/B测试"""
        test_id = f"ab_test_{int(time.time())}"
        
        # 分析两个提示词
        analysis_a = await self._analyze_prompt_for_ab_test(prompt_a)
        analysis_b = await self._analyze_prompt_for_ab_test(prompt_b)
        
        # 比较结果
        comparison = {
            "token_efficiency": {
                "prompt_a": analysis_a["token_count"],
                "prompt_b": analysis_b["token_count"],
                "winner": "A" if analysis_a["token_count"] < analysis_b["token_count"] else "B"
            },
            "clarity_score": {
                "prompt_a": analysis_a["clarity"],
                "prompt_b": analysis_b["clarity"],
                "winner": "A" if analysis_a["clarity"] > analysis_b["clarity"] else "B"
            },
            "completeness_score": {
                "prompt_a": analysis_a["completeness"],
                "prompt_b": analysis_b["completeness"],
                "winner": "A" if analysis_a["completeness"] > analysis_b["completeness"] else "B"
            }
        }
        
        # 计算总分
        score_a = (analysis_a["clarity"] + analysis_a["completeness"]) / 2
        score_b = (analysis_b["clarity"] + analysis_b["completeness"]) / 2
        
        overall_winner = "A" if score_a > score_b else "B"
        confidence = abs(score_a - score_b)
        
        result = {
            "test_id": test_id,
            "timestamp": datetime.now().isoformat(),
            "prompts": {
                "prompt_a": prompt_a,
                "prompt_b": prompt_b
            },
            "analysis": {
                "prompt_a": analysis_a,
                "prompt_b": analysis_b
            },
            "comparison": comparison,
            "conclusion": {
                "winner": overall_winner,
                "confidence": confidence,
                "recommendation": self._get_ab_test_recommendation(overall_winner, confidence, comparison)
            }
        }
        
        # 保存测试结果
        self.ab_test_results[test_id] = result
        
        return result
    
    async def _analyze_prompt_for_ab_test(self, prompt: str) -> Dict[str, Any]:
        """为A/B测试分析提示词"""
        return {
            "token_count": TokenCounter.count_tokens(prompt),
            "clarity": self._assess_clarity(prompt),
            "completeness": self._assess_completeness(prompt),
            "specificity": self._assess_specificity(prompt),
            "coherence": self._assess_coherence(prompt)
        }
    
    def _get_ab_test_recommendation(
        self, 
        winner: str, 
        confidence: float, 
        comparison: Dict[str, Any]
    ) -> str:
        """获取A/B测试建议"""
        if confidence < 0.1:
            return f"两个提示词质量相近，可以选择任一个。建议选择提示词{winner}。"
        elif confidence < 0.3:
            return f"提示词{winner}略优，但差距不大。建议选择提示词{winner}并继续优化。"
        else:
            return f"提示词{winner}明显更优。强烈建议选择提示词{winner}。"

# ============= Token计算器类 =============

class TokenCounter:
    """Token计数器"""
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """计算Token数量（简化实现）"""
        if not text:
            return 0
        # 简化的Token计算：平均1个Token = 4个字符
        return len(text) // 4
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """估算Token数量"""
        if not text:
            return 0
        # 更精确的估算可以考虑：
        # - 中文字符通常1字符=1Token
        # - 英文单词平均1.3字符=1Token
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        other_chars = len(text) - chinese_chars
        
        return chinese_chars + (other_chars // 3)

# ============= 主服务实现 =============

class PromptBuildingService(IPromptBuildingService):
    """提示词构建服务主实现类"""
    
    def __init__(self, 
                 templates_dir: str = "templates/prompts",
                 enable_caching: bool = True,
                 context_optimization_engine = None):
        """
        初始化提示词构建服务
        
        Args:
            templates_dir: 模板存储目录
            enable_caching: 是否启用缓存
            context_optimization_engine: 现有的上下文优化引擎实例
        """
        self.context_assembly = ContextAssemblyEngine()
        self.template_manager = TemplateManager(templates_dir)
        self.optimization_engine = OptimizationEngine()
        self.quality_assurance = QualityAssurance()
        
        # 与现有系统集成
        self.context_optimization_engine = context_optimization_engine
        
        # 缓存设置
        self.enable_caching = enable_caching
        self.prompt_cache = {} if enable_caching else None
        self.source_extractors = {}
        
        # 性能监控
        self.metrics = {
            "prompts_built": 0,
            "cache_hits": 0,
            "avg_build_time": 0.0,
            "total_tokens_processed": 0
        }
        
        # 初始化源提取器
        self._init_source_extractors()
        
        logger.info("提示词构建服务初始化完成")
    
    def _init_source_extractors(self):
        """初始化上下文源提取器"""
        self.source_extractors = {
            "memory": self._extract_memory_sources,
            "conversation": self._extract_conversation_sources,
            "knowledge": self._extract_knowledge_sources,
            "role": self._extract_role_sources,
            "system": self._extract_system_sources
        }
    
    async def build_prompt(
        self,
        context_spec: ContextSpec,
        template_id: Optional[str] = None,
        optimization_goals: Optional[OptimizationGoals] = None
    ) -> str:
        """构建提示词"""
        result, _ = await self.build_prompt_with_analysis(
            context_spec, template_id, optimization_goals
        )
        return result
    
    async def build_prompt_with_analysis(
        self,
        context_spec: ContextSpec,
        template_id: Optional[str] = None,
        optimization_goals: Optional[OptimizationGoals] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """构建提示词并返回分析信息"""
        start_time = time.time()
        
        try:
            # 检查缓存
            cache_key = self._generate_cache_key(context_spec, template_id, optimization_goals)
            if self.enable_caching and cache_key in self.prompt_cache:
                self.metrics["cache_hits"] += 1
                cached_result = self.prompt_cache[cache_key]
                return cached_result["prompt"], cached_result["analysis"]
            
            # 1. 提取上下文源
            context_sources = await self._extract_context_sources(context_spec)
            
            # 2. 组装上下文
            constraints = context_spec.constraints or ContextConstraints()
            assembled_context = await self.context_assembly.assemble_context(
                context_spec, context_sources, constraints
            )
            
            # 3. 获取或生成模板
            if template_id:
                template = await self.template_manager.get_template(
                    template_id, context_spec.__dict__
                )
            else:
                # 生成动态模板
                requirements = self._create_template_requirements(context_spec)
                template = await self.template_manager.generate_dynamic_template(
                    context_spec.scenario, requirements
                )
            
            # 4. 填充模板
            filled_prompt = await self._fill_template(template, context_spec, assembled_context)
            
            # 5. 优化提示词
            if optimization_goals:
                optimized_result = await self.optimization_engine.optimize_prompt(
                    filled_prompt, optimization_goals
                )
                final_prompt = optimized_result.optimized_prompt
                optimization_info = optimized_result.optimization_report
            else:
                final_prompt = filled_prompt
                optimization_info = {}
            
            # 6. 质量验证
            validation_result = await self.quality_assurance.validate_prompt(
                final_prompt, {"max_tokens": constraints.max_tokens}
            )
            
            # 7. 生成分析报告
            analysis = {
                "context_analysis": {
                    "sources_count": len(context_sources),
                    "total_tokens": assembled_context.total_tokens,
                    "quality_score": assembled_context.quality_score,
                    "assembly_time_ms": assembled_context.assembly_time_ms
                },
                "template_info": {
                    "template_id": template.template_id,
                    "template_type": template.template_type.value,
                    "variables_filled": len(template.variables)
                },
                "optimization": optimization_info,
                "validation": validation_result,
                "performance": {
                    "total_build_time_ms": (time.time() - start_time) * 1000,
                    "final_token_count": TokenCounter.count_tokens(final_prompt)
                }
            }
            
            # 8. 缓存结果
            if self.enable_caching:
                self.prompt_cache[cache_key] = {
                    "prompt": final_prompt,
                    "analysis": analysis,
                    "timestamp": datetime.now()
                }
            
            # 9. 更新指标
            self.metrics["prompts_built"] += 1
            self.metrics["total_tokens_processed"] += assembled_context.total_tokens
            build_time = analysis["performance"]["total_build_time_ms"]
            self.metrics["avg_build_time"] = (
                (self.metrics["avg_build_time"] * (self.metrics["prompts_built"] - 1) + build_time) 
                / self.metrics["prompts_built"]
            )
            
            return final_prompt, analysis
            
        except Exception as e:
            logger.error(f"构建提示词失败: {e}")
            error_analysis = {
                "error": str(e),
                "context_spec": context_spec.__dict__,
                "template_id": template_id,
                "timestamp": datetime.now().isoformat()
            }
            raise Exception(f"提示词构建失败: {e}") from e
    
    async def _extract_context_sources(self, context_spec: ContextSpec) -> List[ContextSource]:
        """提取上下文源"""
        all_sources = []
        
        # 提取不同类型的上下文源
        for source_type, extractor in self.source_extractors.items():
            try:
                sources = await extractor(context_spec)
                all_sources.extend(sources)
            except Exception as e:
                logger.warning(f"提取{source_type}上下文源失败: {e}")
        
        return all_sources
    
    async def _extract_memory_sources(self, context_spec: ContextSpec) -> List[ContextSource]:
        """提取记忆上下文源"""
        sources = []
        
        # 如果有现有的上下文优化引擎，使用它
        if self.context_optimization_engine:
            try:
                # 构建上下文优化请求
                from .context_optimization_engine import ContextOptimizationRequest
                
                opt_request = ContextOptimizationRequest(
                    user_id=context_spec.context_id,
                    current_query=context_spec.user_query,
                    conversation_history=context_spec.conversation_history,
                    current_task=context_spec.scenario,
                    optimization_strategy="adaptive"
                )
                
                # 获取优化上下文
                optimized_context = await self.context_optimization_engine.optimize_context(opt_request)
                
                # 转换为ContextSource
                for element in optimized_context.context_elements:
                    source = ContextSource(
                        source_id=element.element_id,
                        source_type=ContextType.MEMORY,
                        content=element.content,
                        metadata=element.metadata or {},
                        priority=1.0,
                        relevance_score=element.relevance_score,
                        token_count=TokenCounter.count_tokens(element.content),
                        created_at=element.timestamp
                    )
                    sources.append(source)
                    
            except Exception as e:
                logger.warning(f"使用现有上下文优化引擎失败: {e}")
        
        # 基础记忆提取
        if context_spec.conversation_history:
            for i, turn in enumerate(context_spec.conversation_history[-5:]):  # 最近5轮对话
                content = turn.get("content", "")
                if content:
                    source = ContextSource(
                        source_id=f"conversation_turn_{i}",
                        source_type=ContextType.MEMORY,
                        content=f"历史对话: {content}",
                        priority=0.8 - i * 0.1,  # 越新的对话优先级越高
                        relevance_score=0.7,
                        token_count=TokenCounter.count_tokens(content)
                    )
                    sources.append(source)
        
        return sources
    
    async def _extract_conversation_sources(self, context_spec: ContextSpec) -> List[ContextSource]:
        """提取对话上下文源"""
        sources = []
        
        # 用户查询
        if context_spec.user_query:
            source = ContextSource(
                source_id="user_query",
                source_type=ContextType.USER,
                content=context_spec.user_query,
                priority=1.0,
                relevance_score=1.0,
                token_count=TokenCounter.count_tokens(context_spec.user_query)
            )
            sources.append(source)
        
        return sources
    
    async def _extract_knowledge_sources(self, context_spec: ContextSpec) -> List[ContextSource]:
        """提取知识上下文源"""
        sources = []
        
        # 处理必需的知识
        for i, knowledge_item in enumerate(context_spec.required_knowledge):
            source = ContextSource(
                source_id=f"required_knowledge_{i}",
                source_type=ContextType.KNOWLEDGE,
                content=f"相关知识: {knowledge_item}",
                priority=0.9,
                relevance_score=0.8,
                token_count=TokenCounter.count_tokens(knowledge_item)
            )
            sources.append(source)
        
        return sources
    
    async def _extract_role_sources(self, context_spec: ContextSpec) -> List[ContextSource]:
        """提取角色上下文源"""
        sources = []
        
        if context_spec.target_role:
            # 基础角色信息
            role_content = f"目标角色: {context_spec.target_role}"
            source = ContextSource(
                source_id="target_role",
                source_type=ContextType.ROLE,
                content=role_content,
                priority=0.9,
                relevance_score=0.9,
                token_count=TokenCounter.count_tokens(role_content)
            )
            sources.append(source)
        
        return sources
    
    async def _extract_system_sources(self, context_spec: ContextSpec) -> List[ContextSource]:
        """提取系统上下文源"""
        sources = []
        
        # 基础系统信息
        system_content = f"场景类型: {context_spec.scenario}"
        source = ContextSource(
            source_id="scenario_info",
            source_type=ContextType.SYSTEM,
            content=system_content,
            priority=0.6,
            relevance_score=0.7,
            token_count=TokenCounter.count_tokens(system_content)
        )
        sources.append(source)
        
        return sources
    
    def _create_template_requirements(self, context_spec: ContextSpec) -> TemplateRequirements:
        """创建模板需求"""
        return TemplateRequirements(
            scenario=context_spec.scenario,
            role_requirements={"target_role": context_spec.target_role} if context_spec.target_role else {},
            context_requirements={"max_tokens": context_spec.constraints.max_tokens if context_spec.constraints else 4000},
            performance_requirements={"response_time": "fast"},
            quality_requirements={"min_quality": 0.7}
        )
    
    async def _fill_template(
        self, 
        template: PromptTemplate, 
        context_spec: ContextSpec,
        assembled_context: AssembledContext
    ) -> str:
        """填充模板"""
        template_content = template.content_template
        
        # 准备变量映射
        variable_mapping = {
            "user_query": context_spec.user_query,
            "scenario": context_spec.scenario,
            "target_role": context_spec.target_role or "助手",
            "context_information": assembled_context.final_content,
            "research_topic": context_spec.user_query,  # 别名
            "consultation_query": context_spec.user_query,  # 别名
            "discussion_topic": context_spec.user_query,  # 别名
        }
        
        # 动态生成其他变量
        if context_spec.target_role:
            variable_mapping["expert_role"] = context_spec.target_role
            variable_mapping["expertise_domain"] = f"{context_spec.target_role}专业领域"
            variable_mapping["professional_background"] = f"{context_spec.target_role}专业背景"
        
        # 填充模板
        filled_content = template_content
        for variable, value in variable_mapping.items():
            placeholder = "{" + variable + "}"
            if placeholder in filled_content:
                filled_content = filled_content.replace(placeholder, str(value) if value else "")
        
        # 处理未填充的变量（用默认值替换）
        import re
        remaining_vars = re.findall(r'\{(\w+)\}', filled_content)
        for var in remaining_vars:
            placeholder = "{" + var + "}"
            default_value = f"[{var}]"  # 使用变量名作为默认值
            filled_content = filled_content.replace(placeholder, default_value)
        
        return filled_content
    
    def _generate_cache_key(
        self, 
        context_spec: ContextSpec, 
        template_id: Optional[str], 
        optimization_goals: Optional[OptimizationGoals]
    ) -> str:
        """生成缓存键"""
        key_components = [
            context_spec.scenario,
            context_spec.user_query,
            str(template_id),
            str(optimization_goals.primary_goal.value if optimization_goals else "none")
        ]
        
        # 使用对话历史的哈希作为键的一部分
        history_hash = hashlib.md5(
            json.dumps(context_spec.conversation_history, sort_keys=True).encode()
        ).hexdigest()[:8]
        
        key_components.append(history_hash)
        
        return hashlib.md5("|".join(key_components).encode()).hexdigest()
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        cache_size = len(self.prompt_cache) if self.prompt_cache else 0
        
        # 计算缓存命中率
        total_requests = self.metrics["prompts_built"] + self.metrics["cache_hits"]
        cache_hit_rate = (
            self.metrics["cache_hits"] / total_requests 
            if total_requests > 0 else 0.0
        )
        
        status = {
            "service_name": "PromptBuildingService",
            "status": "healthy",
            "version": "1.0.0",
            "uptime_seconds": time.time(),  # 简化实现
            "metrics": {
                **self.metrics,
                "cache_hit_rate": cache_hit_rate,
                "cache_size": cache_size
            },
            "components": {
                "context_assembly": "healthy",
                "template_manager": "healthy", 
                "optimization_engine": "healthy",
                "quality_assurance": "healthy"
            },
            "integrations": {
                "context_optimization_engine": "available" if self.context_optimization_engine else "not_available"
            }
        }
        
        return status

# ============= 工厂函数 =============

def create_prompt_building_service(
    templates_dir: str = "templates/prompts",
    enable_caching: bool = True,
    context_optimization_engine = None
) -> PromptBuildingService:
    """创建提示词构建服务实例"""
    return PromptBuildingService(
        templates_dir=templates_dir,
        enable_caching=enable_caching,
        context_optimization_engine=context_optimization_engine
    )