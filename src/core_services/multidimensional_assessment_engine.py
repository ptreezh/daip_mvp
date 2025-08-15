"""@Time: 2025-08-03
@Author: DAIP-LIVE
@File: multidimensional_assessment_engine.py
@Description: V0.3.5 多维度评估引擎 - 基于多维度指标的智能质量评估系统
"""

import asyncio
import json
import logging
import re
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
    from ..core_services.knowledge_retrieval_service import KnowledgeRetrievalService
    from ..core_services.memory_agent import MemAgent

# Heavy dependencies - lazy loaded
# numpy - lazy loaded
# sklearn modules - lazy loaded
# networkx - lazy loaded
# spacy - lazy loaded
# textstat - basic text statistics, keep for now
import threading
import time
from collections import Counter

from textstat import flesch_kincaid_grade, flesch_reading_ease

# Core services - lazy loaded to avoid circular dependencies and improve startup performance


class AssessmentDimension(Enum):
    """评估维度"""
    ACADEMIC_QUALITY = "academic_quality"      # 学术质量
    TECHNICAL_IMPLEMENTATION = "technical_implementation"  # 技术实现
    PRACTICALITY = "practicality"             # 实用性
    DOCUMENTATION_QUALITY = "documentation_quality"  # 文档质量
    ETHICS_COMPLIANCE = "ethics_compliance"    # 伦理合规
    INNOVATION = "innovation"                 # 创新性
    REPRODUCIBILITY = "reproducibility"       # 可复现性
    IMPACT = "impact"                         # 影响力


class QualityLevel(Enum):
    """质量等级"""
    EXCELLENT = "excellent"     # 优秀 (90-100)
    GOOD = "good"              # 良好 (80-89)
    SATISFACTORY = "satisfactory"  # 合格 (70-79)
    NEEDS_IMPROVEMENT = "needs_improvement"  # 需要改进 (60-69)
    POOR = "poor"              # 不足 (0-59)


class ContentType(Enum):
    """内容类型"""
    RESEARCH_PAPER = "research_paper"      # 研究论文
    TECHNICAL_REPORT = "technical_report"  # 技术报告
    CODE_REPOSITORY = "code_repository"     # 代码仓库
    DOCUMENTATION = "documentation"         # 文档
    PROPOSAL = "proposal"                   # 提案
    PRESENTATION = "presentation"           # 演示文稿


@dataclass
class AssessmentCriteria:
    """评估标准"""
    dimension: AssessmentDimension
    weight: float                           # 权重 (0-1)
    metrics: list[str]                      # 评估指标
    threshold: float                        # 阈值
    description: str                        # 描述
    importance: str                         # 重要性


@dataclass
class MetricResult:
    """指标结果"""
    name: str
    value: float
    score: float                           # 标准化分数 (0-1)
    confidence: float                      # 置信度 (0-1)
    evidence: list[str]                    # 证据
    details: dict[str, Any] = None


@dataclass
class DimensionResult:
    """维度结果"""
    dimension: AssessmentDimension
    score: float                           # 维度分数 (0-1)
    level: QualityLevel                    # 质量等级
    metrics: list[MetricResult]            # 指标结果
    summary: str                           # 总结
    strengths: list[str]                   # 优势
    weaknesses: list[str]                  # 不足
    suggestions: list[str]                 # 建议


@dataclass
class AssessmentResult:
    """评估结果"""
    id: str
    content_id: str
    content_type: ContentType
    overall_score: float                    # 总分 (0-1)
    overall_level: QualityLevel             # 总体等级
    dimensions: dict[str, DimensionResult]  # 维度结果
    confidence: float                       # 总体置信度
    assessment_time: datetime
    assessor: str
    criteria: dict[str, AssessmentCriteria]  # 使用的标准
    metadata: dict[str, Any] = None


@dataclass
class ContentToAssess:
    """待评估内容"""
    id: str
    title: str
    content: str
    content_type: ContentType
    author: str
    submission_date: datetime
    keywords: list[str]
    metadata: dict[str, Any] = None


class MultiDimensionalAssessmentEngine:
    """多维度评估引擎"""
    
    def __init__(self, knowledge_retrieval: Optional[Any] = None, 
                 sskg_manager: Optional[Any] = None, 
                 memory_agent: Optional[Any] = None):
        # Core services - optional and lazy-loaded
        self.knowledge_retrieval = knowledge_retrieval
        self.sskg_manager = sskg_manager
        self.memory_agent = memory_agent
        self.logger = logging.getLogger(__name__)
        
        # 初始化numpy (lazy-loaded)
        self.np = None
        try:
            import numpy as np
            self.np = np
        except Exception as e:
            self.logger.warning(f"Failed to load numpy: {e}")
            self.np = None
        
        # 初始化NLP模型 (lazy-loaded)
        self.nlp = None
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            self.logger.warning(f"Failed to load spacy model: {e}")
            self.nlp = None
        
        # 初始化sklearn模块 (lazy-loaded)
        self.tfidf_vectorizer = None
        self.minmax_scaler = None
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.preprocessing import MinMaxScaler
            self.tfidf_vectorizer = TfidfVectorizer
            self.minmax_scaler = MinMaxScaler
        except Exception as e:
            self.logger.warning(f"Failed to load sklearn modules: {e}")
            self.tfidf_vectorizer = None
            self.minmax_scaler = None
        
        # 初始化networkx (lazy-loaded)
        self.nx = None
        try:
            import networkx as nx
            self.nx = nx
        except Exception as e:
            self.logger.warning(f"Failed to load networkx: {e}")
            self.nx = None
        
        # 评估标准配置
        self.assessment_criteria = self._initialize_assessment_criteria()
        
        # 历史评估数据
        self.assessment_history = []
        
        # 启动后台任务
        self._start_background_tasks()
    
    def _initialize_assessment_criteria(self) -> dict[str, AssessmentCriteria]:
        """初始化评估标准"""
        return {
            "academic_quality": AssessmentCriteria(
                dimension=AssessmentDimension.ACADEMIC_QUALITY,
                weight=0.25,
                metrics=["theoretical_foundation", "methodology_rigor", "logical_coherence", "citation_quality"],
                threshold=0.7,
                description="学术理论基础、方法论严谨性、逻辑连贯性、引用质量",
                importance="high"
            ),
            "technical_implementation": AssessmentCriteria(
                dimension=AssessmentDimension.TECHNICAL_IMPLEMENTATION,
                weight=0.20,
                metrics=["code_quality", "performance", "scalability", "maintainability"],
                threshold=0.65,
                description="代码质量、性能表现、可扩展性、可维护性",
                importance="high"
            ),
            "practicality": AssessmentCriteria(
                dimension=AssessmentDimension.PRACTICALITY,
                weight=0.15,
                metrics=["applicability", "usability", "cost_effectiveness", "real_world_value"],
                threshold=0.6,
                description="应用价值、用户体验、成本效益、实际价值",
                importance="medium"
            ),
            "documentation_quality": AssessmentCriteria(
                dimension=AssessmentDimension.DOCUMENTATION_QUALITY,
                weight=0.10,
                metrics=["completeness", "clarity", "structure", "readability"],
                threshold=0.7,
                description="完整性、清晰度、结构化、可读性",
                importance="medium"
            ),
            "ethics_compliance": AssessmentCriteria(
                dimension=AssessmentDimension.ETHICS_COMPLIANCE,
                weight=0.10,
                metrics=["privacy_protection", "security_measures", "regulatory_compliance", "ethical_considerations"],
                threshold=0.8,
                description="隐私保护、安全措施、合规性、伦理考量",
                importance="high"
            ),
            "innovation": AssessmentCriteria(
                dimension=AssessmentDimension.INNOVATION,
                weight=0.10,
                metrics=["novelty", "creativity", "originality", "advancement"],
                threshold=0.6,
                description="新颖性、创造性、原创性、进步性",
                importance="medium"
            ),
            "reproducibility": AssessmentCriteria(
                dimension=AssessmentDimension.REPRODUCIBILITY,
                weight=0.05,
                metrics=["data_availability", "method_transparency", "experiment_repeatability", "code_accessibility"],
                threshold=0.7,
                description="数据可用性、方法透明度、实验可重复性、代码可访问性",
                importance="low"
            ),
            "impact": AssessmentCriteria(
                dimension=AssessmentDimension.IMPACT,
                weight=0.05,
                metrics=["reach", "influence", "citation_potential", "practical_implications"],
                threshold=0.6,
                description="影响范围、影响力、引用潜力、实际意义",
                importance="low"
            )
        }
    
    async def assess_content(self, 
                          content: ContentToAssess,
                          custom_criteria: dict[str, AssessmentCriteria] = None) -> AssessmentResult:
        """多维度评估内容"""
        try:
            self.logger.info(f"开始多维度评估: {content.id}")
            
            # 使用自定义标准或默认标准
            criteria = custom_criteria or self.assessment_criteria
            
            # 1. 内容预处理
            processed_content = await self._preprocess_content(content)
            
            # 2. 并行评估各维度
            dimension_tasks = []
            for dim_name, dim_criteria in criteria.items():
                task = self._assess_dimension(content, processed_content, dim_criteria)
                dimension_tasks.append(task)
            
            dimension_results = await asyncio.gather(*dimension_tasks)
            
            # 3. 汇总维度结果
            dimensions_dict = {result.dimension.value: result for result in dimension_results}
            
            # 4. 计算总体分数
            overall_score = self._calculate_overall_score(dimension_results, criteria)
            overall_level = self._determine_quality_level(overall_score)
            
            # 5. 计算置信度
            confidence = self._calculate_assessment_confidence(dimension_results)
            
            # 6. 生成评估结果
            assessment_result = AssessmentResult(
                id=f"assessment_{content.id}_{int(datetime.now().timestamp())}",
                content_id=content.id,
                content_type=content.content_type,
                overall_score=overall_score,
                overall_level=overall_level,
                dimensions=dimensions_dict,
                confidence=confidence,
                assessment_time=datetime.now(),
                assessor="multidimensional_assessment_engine",
                criteria=criteria,
                metadata={
                    "processing_time": datetime.now().isoformat(),
                    "content_length": len(content.content),
                    "word_count": len(content.content.split()),
                    "assessment_dimensions": list(criteria.keys())
                }
            )
            
            # 7. 记录评估历史
            self._record_assessment(assessment_result)
            
            self.logger.info(f"多维度评估完成: {content.id} -> 总分: {overall_score:.3f}")
            
            return assessment_result
            
        except Exception as e:
            self.logger.error(f"多维度评估失败: {e}")
            # 返回默认结果
            return AssessmentResult(
                id=f"assessment_{content.id}_error",
                content_id=content.id,
                content_type=content.content_type,
                overall_score=0.0,
                overall_level=QualityLevel.POOR,
                dimensions={},
                confidence=0.0,
                assessment_time=datetime.now(),
                assessor="multidimensional_assessment_engine",
                criteria=criteria or self.assessment_criteria,
                metadata={"error": str(e)}
            )
    
    async def _preprocess_content(self, content: ContentToAssess) -> dict[str, Any]:
        """预处理内容"""
        try:
            processed = {
                "text": content.content,
                "tokens": [],
                "sentences": [],
                "paragraphs": [],
                "keywords": content.keywords,
                "statistics": {},
                "semantic_features": {},
                "structure_features": {}
            }
            
            # 使用spaCy进行NLP处理
            doc = self.nlp(content.content)
            
            # 提取基本信息
            processed["tokens"] = [token.text for token in doc]
            processed["sentences"] = [sent.text for sent in doc.sents]
            processed["paragraphs"] = [p.strip() for p in content.content.split('\n\n') if p.strip()]
            
            # 计算统计信息
            processed["statistics"] = {
                "word_count": len(processed["tokens"]),
                "sentence_count": len(processed["sentences"]),
                "paragraph_count": len(processed["paragraphs"]),
                "avg_sentence_length": statistics.mean(len(sent.split()) for sent in processed["sentences"]),
                "vocabulary_richness": len(set(processed["tokens"])) / len(processed["tokens"]) if processed["tokens"] else 0,
                "readability_score": flesch_reading_ease(content.content),
                "grade_level": flesch_kincaid_grade(content.content)
            }
            
            # 提取语义特征
            processed["semantic_features"] = {
                "named_entities": [(ent.text, ent.label_) for ent in doc.ents],
                "pos_tags": [(token.text, token.pos_) for token in doc],
                "dependency_parse": [(token.text, token.dep_, token.head.text) for token in doc],
                "key_phrases": [chunk.text for chunk in doc.noun_chunks]
            }
            
            # 分析结构特征
            processed["structure_features"] = {
                "has_abstract": any("abstract" in p.lower() for p in processed["paragraphs"]),
                "has_introduction": any("introduction" in p.lower() for p in processed["paragraphs"]),
                "has_methodology": any("method" in p.lower() for p in processed["paragraphs"]),
                "has_results": any("result" in p.lower() for p in processed["paragraphs"]),
                "has_conclusion": any("conclusion" in p.lower() for p in processed["paragraphs"]),
                "has_references": any("reference" in p.lower() for p in processed["paragraphs"]),
                "section_count": len([p for p in processed["paragraphs"] if len(p) > 100])
            }
            
            return processed
            
        except Exception as e:
            self.logger.error(f"内容预处理失败: {e}")
            return {"text": content.content, "error": str(e)}
    
    async def _assess_dimension(self, 
                              content: ContentToAssess,
                              processed_content: dict[str, Any],
                              criteria: AssessmentCriteria) -> DimensionResult:
        """评估单个维度"""
        try:
            # 根据维度选择评估方法
            if criteria.dimension == AssessmentDimension.ACADEMIC_QUALITY:
                return await self._assess_academic_quality(content, processed_content, criteria)
            elif criteria.dimension == AssessmentDimension.TECHNICAL_IMPLEMENTATION:
                return await self._assess_technical_implementation(content, processed_content, criteria)
            elif criteria.dimension == AssessmentDimension.PRACTICALITY:
                return await self._assess_practicality(content, processed_content, criteria)
            elif criteria.dimension == AssessmentDimension.DOCUMENTATION_QUALITY:
                return await self._assess_documentation_quality(content, processed_content, criteria)
            elif criteria.dimension == AssessmentDimension.ETHICS_COMPLIANCE:
                return await self._assess_ethics_compliance(content, processed_content, criteria)
            elif criteria.dimension == AssessmentDimension.INNOVATION:
                return await self._assess_innovation(content, processed_content, criteria)
            elif criteria.dimension == AssessmentDimension.REPRODUCIBILITY:
                return await self._assess_reproducibility(content, processed_content, criteria)
            elif criteria.dimension == AssessmentDimension.IMPACT:
                return await self._assess_impact(content, processed_content, criteria)
            else:
                raise ValueError(f"未知的评估维度: {criteria.dimension}")
                
        except Exception as e:
            self.logger.error(f"维度评估失败: {criteria.dimension} - {e}")
            # 返回默认结果
            return DimensionResult(
                dimension=criteria.dimension,
                score=0.0,
                level=QualityLevel.POOR,
                metrics=[],
                summary=f"评估失败: {str(e)}",
                strengths=[],
                weaknesses=[],
                suggestions=[]
            )
    
    async def _assess_academic_quality(self, 
                                      content: ContentToAssess,
                                      processed_content: dict[str, Any],
                                      criteria: AssessmentCriteria) -> DimensionResult:
        """评估学术质量"""
        try:
            metrics = []
            
            # 1. 理论基础评估
            theoretical_score = await self._assess_theoretical_foundation(content, processed_content)
            metrics.append(MetricResult(
                name="theoretical_foundation",
                value=theoretical_score,
                score=theoretical_score,
                confidence=0.8,
                evidence=["理论基础分析", "概念框架评估"],
                details={"framework_detected": bool(re.search(r'framework|theory|model', content.content, re.I))}
            ))
            
            # 2. 方法论严谨性
            methodology_score = await self._assess_methodology_rigor(content, processed_content)
            metrics.append(MetricResult(
                name="methodology_rigor",
                value=methodology_score,
                score=methodology_score,
                confidence=0.85,
                evidence=["方法论描述", "实验设计评估"],
                details={"methods_mentioned": bool(re.search(r'method|experiment|study', content.content, re.I))}
            ))
            
            # 3. 逻辑连贯性
            coherence_score = self._assess_logical_coherence(content, processed_content)
            metrics.append(MetricResult(
                name="logical_coherence",
                value=coherence_score,
                score=coherence_score,
                confidence=0.7,
                evidence=["逻辑结构分析", "论证连贯性"],
                details={"structure_score": coherence_score}
            ))
            
            # 4. 引用质量
            citation_score = await self._assess_citation_quality(content, processed_content)
            metrics.append(MetricResult(
                name="citation_quality",
                value=citation_score,
                score=citation_score,
                confidence=0.75,
                evidence=["引用分析", "文献综述评估"],
                details={"citation_count": len(re.findall(r'\[\d+\]|\([A-Za-z]+, \d{4}\)', content.content))}
            ))
            
            # 计算维度分数
            dimension_score = statistics.mean([m.score for m in metrics])
            level = self._determine_quality_level(dimension_score)
            
            # 生成总结和建议
            summary, strengths, weaknesses, suggestions = self._generate_dimension_summary(
                "学术质量", metrics, dimension_score, level
            )
            
            return DimensionResult(
                dimension=criteria.dimension,
                score=dimension_score,
                level=level,
                metrics=metrics,
                summary=summary,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"学术质量评估失败: {e}")
            raise
    
    async def _assess_theoretical_foundation(self, 
                                           content: ContentToAssess,
                                           processed_content: dict[str, Any]) -> float:
        """评估理论基础"""
        try:
            score = 0.0
            
            # 检查理论框架
            theory_keywords = [
                "framework", "theory", "model", "concept", "paradigm", 
                "hypothesis", "assumption", "principle", "foundation"
            ]
            
            theory_matches = sum(1 for keyword in theory_keywords 
                               if keyword in content.content.lower())
            score += min(0.3, theory_matches * 0.05)
            
            # 检查概念定义
            definition_patterns = [
                r'defined as', r'refers to', r'is a', r'can be defined',
                r'concept of', r'notion of', r'idea of'
            ]
            
            definition_matches = sum(1 for pattern in definition_patterns 
                                   if re.search(pattern, content.content, re.I))
            score += min(0.3, definition_matches * 0.06)
            
            # 检查文献综述
            literature_indicators = [
                "literature review", "previous work", "prior research", 
                "existing studies", "related work", "background"
            ]
            
            literature_matches = sum(1 for indicator in literature_indicators 
                                    if indicator in content.content.lower())
            score += min(0.4, literature_matches * 0.1)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"理论基础评估失败: {e}")
            return 0.0
    
    async def _assess_methodology_rigor(self, 
                                      content: ContentToAssess,
                                      processed_content: dict[str, Any]) -> float:
        """评估方法论严谨性"""
        try:
            score = 0.0
            
            # 检查方法论描述
            methodology_keywords = [
                "method", "methodology", "approach", "procedure", 
                "algorithm", "technique", "process", "protocol"
            ]
            
            method_matches = sum(1 for keyword in methodology_keywords 
                               if keyword in content.content.lower())
            score += min(0.3, method_matches * 0.05)
            
            # 检查实验设计
            experiment_indicators = [
                "experiment", "test", "evaluation", "validation", 
                "measurement", "analysis", "data collection", "sample"
            ]
            
            experiment_matches = sum(1 for indicator in experiment_indicators 
                                   if indicator in content.content.lower())
            score += min(0.3, experiment_matches * 0.05)
            
            # 检查统计方法
            statistical_keywords = [
                "statistical", "significant", "p-value", "correlation",
                "regression", "analysis", "hypothesis testing", "confidence interval"
            ]
            
            statistical_matches = sum(1 for keyword in statistical_keywords 
                                    if keyword in content.content.lower())
            score += min(0.4, statistical_matches * 0.08)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"方法论严谨性评估失败: {e}")
            return 0.0
    
    def _assess_logical_coherence(self, 
                                content: ContentToAssess,
                                processed_content: dict[str, Any]) -> float:
        """评估逻辑连贯性"""
        try:
            score = 0.0
            
            # 检查段落结构
            if processed_content.get("structure_features"):
                structure = processed_content["structure_features"]
                
                # 标准结构加分
                standard_sections = [
                    "has_introduction", "has_methodology", 
                    "has_results", "has_conclusion"
                ]
                
                standard_count = sum(1 for section in standard_sections 
                                   if structure.get(section, False))
                score += min(0.4, standard_count * 0.1)
            
            # 检查逻辑连接词
            transition_words = [
                "therefore", "however", "furthermore", "moreover",
                "consequently", "additionally", "nevertheless", "thus"
            ]
            
            transition_count = sum(1 for word in transition_words 
                                if word in content.content.lower())
            score += min(0.3, transition_count * 0.05)
            
            # 检查论证结构
            argument_indicators = [
                "because", "since", "due to", "as a result",
                "for example", "for instance", "specifically", "in particular"
            ]
            
            argument_count = sum(1 for indicator in argument_indicators 
                               if indicator in content.content.lower())
            score += min(0.3, argument_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"逻辑连贯性评估失败: {e}")
            return 0.0
    
    async def _assess_citation_quality(self, 
                                      content: ContentToAssess,
                                      processed_content: dict[str, Any]) -> float:
        """评估引用质量"""
        try:
            score = 0.0
            
            # 检查引用格式
            citation_patterns = [
                r'\[\d+\]',  # [1], [2], [3]
                r'\([A-Za-z]+, \d{4}\)',  # (Smith, 2020)
                r'\([A-Za-z]+ et al\., \d{4}\)',  # (Smith et al., 2020)
                r'\d{4}'  # 年份引用
            ]
            
            total_citations = 0
            for pattern in citation_patterns:
                matches = len(re.findall(pattern, content.content))
                total_citations += matches
            
            # 引用数量评分
            if total_citations >= 20:
                score += 0.4
            elif total_citations >= 10:
                score += 0.3
            elif total_citations >= 5:
                score += 0.2
            else:
                score += 0.1
            
            # 检查参考文献部分
            if "reference" in content.content.lower() or "bibliography" in content.content.lower():
                score += 0.3
            
            # 检查引用多样性
            if "et al" in content.content.lower():
                score += 0.2  # 多作者引用
            
            # 检查近期引用
            recent_years = re.findall(r'\b20(1[8-9]|2[0-4])\b', content.content)
            if recent_years:
                score += min(0.1, len(recent_years) * 0.02)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"引用质量评估失败: {e}")
            return 0.0
    
    async def _assess_technical_implementation(self, 
                                            content: ContentToAssess,
                                            processed_content: dict[str, Any],
                                            criteria: AssessmentCriteria) -> DimensionResult:
        """评估技术实现"""
        try:
            metrics = []
            
            # 1. 代码质量评估
            code_score = await self._assess_code_quality(content, processed_content)
            metrics.append(MetricResult(
                name="code_quality",
                value=code_score,
                score=code_score,
                confidence=0.8,
                evidence=["代码结构分析", "代码规范检查"],
                details={"code_blocks_found": len(re.findall(r'```[\s\S]*?```', content.content))}
            ))
            
            # 2. 性能表现
            performance_score = await self._assess_performance(content, processed_content)
            metrics.append(MetricResult(
                name="performance",
                value=performance_score,
                score=performance_score,
                confidence=0.7,
                evidence=["性能指标分析", "效率评估"],
                details={"performance_mentioned": bool(re.search(r'performance|efficiency|speed', content.content, re.I))}
            ))
            
            # 3. 可扩展性
            scalability_score = await self._assess_scalability(content, processed_content)
            metrics.append(MetricResult(
                name="scalability",
                value=scalability_score,
                score=scalability_score,
                confidence=0.6,
                evidence=["扩展性分析", "架构评估"],
                details={"scalability_concepts": re.findall(r'scalable|scale|distributed', content.content, re.I)}
            ))
            
            # 4. 可维护性
            maintainability_score = await self._assess_maintainability(content, processed_content)
            metrics.append(MetricResult(
                name="maintainability",
                value=maintainability_score,
                score=maintainability_score,
                confidence=0.7,
                evidence=["可维护性分析", "代码结构评估"],
                details={"maintainability_indicators": re.findall(r'maintain|modular|clean', content.content, re.I)}
            ))
            
            # 计算维度分数
            dimension_score = statistics.mean([m.score for m in metrics])
            level = self._determine_quality_level(dimension_score)
            
            # 生成总结和建议
            summary, strengths, weaknesses, suggestions = self._generate_dimension_summary(
                "技术实现", metrics, dimension_score, level
            )
            
            return DimensionResult(
                dimension=criteria.dimension,
                score=dimension_score,
                level=level,
                metrics=metrics,
                summary=summary,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"技术实现评估失败: {e}")
            raise
    
    async def _assess_code_quality(self, 
                                 content: ContentToAssess,
                                 processed_content: dict[str, Any]) -> float:
        """评估代码质量"""
        try:
            score = 0.0
            
            # 检查代码块
            code_blocks = re.findall(r'```[\s\S]*?```', content.content)
            if code_blocks:
                score += 0.3
                
                # 分析代码质量
                for code_block in code_blocks:
                    # 检查注释
                    if '#' in code_block or '//' in code_block or '/*' in code_block:
                        score += 0.1
                    
                    # 检查函数定义
                    if re.search(r'def |function |class ', code_block):
                        score += 0.1
                    
                    # 检查错误处理
                    if re.search(r'try|catch|except|error', code_block):
                        score += 0.1
            
            # 检查代码相关术语
            code_terms = [
                "algorithm", "implementation", "code", "programming",
                "software", "development", "debug", "test"
            ]
            
            code_term_count = sum(1 for term in code_terms 
                                if term in content.content.lower())
            score += min(0.3, code_term_count * 0.05)
            
            # 检查版本控制
            if re.search(r'git|version|repository', content.content, re.I):
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"代码质量评估失败: {e}")
            return 0.0
    
    async def _assess_performance(self, 
                                content: ContentToAssess,
                                processed_content: dict[str, Any]) -> float:
        """评估性能表现"""
        try:
            score = 0.0
            
            # 检查性能指标
            performance_metrics = [
                "speed", "efficiency", "throughput", "latency",
                "response time", "cpu", "memory", "optimization"
            ]
            
            metric_count = sum(1 for metric in performance_metrics 
                             if metric in content.content.lower())
            score += min(0.4, metric_count * 0.08)
            
            # 检查性能测试
            if re.search(r'benchmark|test|measurement|evaluation', content.content, re.I):
                score += 0.3
            
            # 检查优化技术
            optimization_terms = [
                "optimize", "improve", "enhance", "accelerate",
                "reduce", "minimize", "streamline"
            ]
            
            optimization_count = sum(1 for term in optimization_terms 
                                   if term in content.content.lower())
            score += min(0.3, optimization_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"性能表现评估失败: {e}")
            return 0.0
    
    async def _assess_scalability(self, 
                                content: ContentToAssess,
                                processed_content: dict[str, Any]) -> float:
        """评估可扩展性"""
        try:
            score = 0.0
            
            # 检查扩展性概念
            scalability_concepts = [
                "scalable", "scale", "distributed", "parallel",
                "horizontal", "vertical", "elastic", "flexible"
            ]
            
            concept_count = sum(1 for concept in scalability_concepts 
                              if concept in content.content.lower())
            score += min(0.4, concept_count * 0.08)
            
            # 检查架构设计
            architecture_terms = [
                "architecture", "design", "framework", "pattern",
                "microservices", "cloud", "container"
            ]
            
            architecture_count = sum(1 for term in architecture_terms 
                                   if term in content.content.lower())
            score += min(0.3, architecture_count * 0.06)
            
            # 检查负载处理
            load_terms = [
                "load", "traffic", "concurrent", "users",
                "requests", "capacity", "bottleneck"
            ]
            
            load_count = sum(1 for term in load_terms 
                           if term in content.content.lower())
            score += min(0.3, load_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"可扩展性评估失败: {e}")
            return 0.0
    
    async def _assess_maintainability(self, 
                                    content: ContentToAssess,
                                    processed_content: dict[str, Any]) -> float:
        """评估可维护性"""
        try:
            score = 0.0
            
            # 检查可维护性指标
            maintainability_terms = [
                "maintainable", "maintain", "clean", "readable",
                "modular", "documentation", "comments", "structure"
            ]
            
            term_count = sum(1 for term in maintainability_terms 
                           if term in content.content.lower())
            score += min(0.4, term_count * 0.08)
            
            # 检查设计模式
            if re.search(r'pattern|design|architecture|framework', content.content, re.I):
                score += 0.3
            
            # 检查代码质量
            if re.search(r'refactoring|code review|quality', content.content, re.I):
                score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"可维护性评估失败: {e}")
            return 0.0
    
    async def _assess_practicality(self, 
                                  content: ContentToAssess,
                                  processed_content: dict[str, Any],
                                  criteria: AssessmentCriteria) -> DimensionResult:
        """评估实用性"""
        try:
            metrics = []
            
            # 1. 应用价值
            applicability_score = await self._assess_applicability(content, processed_content)
            metrics.append(MetricResult(
                name="applicability",
                value=applicability_score,
                score=applicability_score,
                confidence=0.8,
                evidence=["应用场景分析", "实际价值评估"],
                details={"application_scenarios": re.findall(r'application|use case|scenario', content.content, re.I)}
            ))
            
            # 2. 可用性
            usability_score = await self._assess_usability(content, processed_content)
            metrics.append(MetricResult(
                name="usability",
                value=usability_score,
                score=usability_score,
                confidence=0.7,
                evidence=["用户体验分析", "易用性评估"],
                details={"usability_features": re.findall(r'user|interface|experience', content.content, re.I)}
            ))
            
            # 3. 成本效益
            cost_effectiveness_score = await self._assess_cost_effectiveness(content, processed_content)
            metrics.append(MetricResult(
                name="cost_effectiveness",
                value=cost_effectiveness_score,
                score=cost_effectiveness_score,
                confidence=0.6,
                evidence=["成本分析", "效益评估"],
                details={"cost_mentioned": bool(re.search(r'cost|budget|resource', content.content, re.I))}
            ))
            
            # 4. 实际价值
            real_world_score = await self._assess_real_world_value(content, processed_content)
            metrics.append(MetricResult(
                name="real_world_value",
                value=real_world_score,
                score=real_world_score,
                confidence=0.7,
                evidence=["实际应用分析", "价值评估"],
                details={"real_world_applications": re.findall(r'industry|practice|implementation', content.content, re.I)}
            ))
            
            # 计算维度分数
            dimension_score = statistics.mean([m.score for m in metrics])
            level = self._determine_quality_level(dimension_score)
            
            # 生成总结和建议
            summary, strengths, weaknesses, suggestions = self._generate_dimension_summary(
                "实用性", metrics, dimension_score, level
            )
            
            return DimensionResult(
                dimension=criteria.dimension,
                score=dimension_score,
                level=level,
                metrics=metrics,
                summary=summary,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"实用性评估失败: {e}")
            raise
    
    async def _assess_applicability(self, 
                                 content: ContentToAssess,
                                 processed_content: dict[str, Any]) -> float:
        """评估应用价值"""
        try:
            score = 0.0
            
            # 检查应用场景
            application_scenarios = [
                "application", "use case", "scenario", "implementation",
                "deployment", "integration", "adoption", "utilization"
            ]
            
            scenario_count = sum(1 for scenario in application_scenarios 
                                if scenario in content.content.lower())
            score += min(0.4, scenario_count * 0.08)
            
            # 检查行业应用
            industry_terms = [
                "industry", "sector", "domain", "field",
                "business", "commercial", "enterprise", "organization"
            ]
            
            industry_count = sum(1 for term in industry_terms 
                               if term in content.content.lower())
            score += min(0.3, industry_count * 0.06)
            
            # 检查问题解决
            problem_solving_terms = [
                "solve", "solution", "problem", "challenge",
                "address", "overcome", "resolve", "tackle"
            ]
            
            problem_count = sum(1 for term in problem_solving_terms 
                              if term in content.content.lower())
            score += min(0.3, problem_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"应用价值评估失败: {e}")
            return 0.0
    
    async def _assess_usability(self, 
                             content: ContentToAssess,
                             processed_content: dict[str, Any]) -> float:
        """评估可用性"""
        try:
            score = 0.0
            
            # 检查用户体验
            ux_terms = [
                "user", "interface", "experience", "interaction",
                "usability", "accessibility", "intuitive", "friendly"
            ]
            
            ux_count = sum(1 for term in ux_terms 
                         if term in content.content.lower())
            score += min(0.4, ux_count * 0.08)
            
            # 检查易用性特征
            ease_terms = [
                "easy", "simple", "straightforward", "convenient",
                "user-friendly", "accessible", "intuitive", "clear"
            ]
            
            ease_count = sum(1 for term in ease_terms 
                           if term in content.content.lower())
            score += min(0.3, ease_count * 0.06)
            
            # 检查学习成本
            learning_terms = [
                "learning", "training", "tutorial", "documentation",
                "guide", "manual", "help", "support"
            ]
            
            learning_count = sum(1 for term in learning_terms 
                               if term in content.content.lower())
            score += min(0.3, learning_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"可用性评估失败: {e}")
            return 0.0
    
    async def _assess_cost_effectiveness(self, 
                                      content: ContentToAssess,
                                      processed_content: dict[str, Any]) -> float:
        """评估成本效益"""
        try:
            score = 0.0
            
            # 检查成本相关术语
            cost_terms = [
                "cost", "budget", "expense", "investment",
                "resource", "funding", "financial", "economic"
            ]
            
            cost_count = sum(1 for term in cost_terms 
                           if term in content.content.lower())
            score += min(0.4, cost_count * 0.08)
            
            # 检查效益相关术语
            benefit_terms = [
                "benefit", "value", "return", "gain",
                "advantage", "profit", "saving", "efficiency"
            ]
            
            benefit_count = sum(1 for term in benefit_terms 
                              if term in content.content.lower())
            score += min(0.3, benefit_count * 0.06)
            
            # 检查投资回报
            roi_terms = [
                "roi", "return on investment", "payback", "break-even",
                "cost-benefit", "value proposition", "business case"
            ]
            
            roi_count = sum(1 for term in roi_terms 
                         if term in content.content.lower())
            score += min(0.3, roi_count * 0.1)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"成本效益评估失败: {e}")
            return 0.0
    
    async def _assess_real_world_value(self, 
                                      content: ContentToAssess,
                                      processed_content: dict[str, Any]) -> float:
        """评估实际价值"""
        try:
            score = 0.0
            
            # 检查实际应用
            practical_terms = [
                "practice", "practical", "real-world", "real life",
                "implementation", "deployment", "production", "operational"
            ]
            
            practical_count = sum(1 for term in practical_terms 
                               if term in content.content.lower())
            score += min(0.4, practical_count * 0.08)
            
            # 检查案例研究
            case_study_terms = [
                "case study", "example", "instance", "demonstration",
                "proof of concept", "pilot", "prototype", "testing"
            ]
            
            case_count = sum(1 for term in case_study_terms 
                           if term in content.content.lower())
            score += min(0.3, case_count * 0.06)
            
            # 检查影响力
            impact_terms = [
                "impact", "effect", "outcome", "result",
                "consequence", "change", "improvement", "enhancement"
            ]
            
            impact_count = sum(1 for term in impact_terms 
                             if term in content.content.lower())
            score += min(0.3, impact_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"实际价值评估失败: {e}")
            return 0.0
    
    async def _assess_documentation_quality(self, 
                                          content: ContentToAssess,
                                          processed_content: dict[str, Any],
                                          criteria: AssessmentCriteria) -> DimensionResult:
        """评估文档质量"""
        try:
            metrics = []
            
            # 1. 完整性
            completeness_score = await self._assess_completeness(content, processed_content)
            metrics.append(MetricResult(
                name="completeness",
                value=completeness_score,
                score=completeness_score,
                confidence=0.9,
                evidence=["完整性检查", "文档结构评估"],
                details={"document_sections": len(processed_content.get("paragraphs", []))}
            ))
            
            # 2. 清晰度
            clarity_score = await self._assess_clarity(content, processed_content)
            metrics.append(MetricResult(
                name="clarity",
                value=clarity_score,
                score=clarity_score,
                confidence=0.8,
                evidence=["清晰度分析", "语言表达评估"],
                details={"readability_score": processed_content.get("statistics", {}).get("readability_score", 0)}
            ))
            
            # 3. 结构
            structure_score = await self._assess_structure(content, processed_content)
            metrics.append(MetricResult(
                name="structure",
                value=structure_score,
                score=structure_score,
                confidence=0.8,
                evidence=["结构分析", "组织评估"],
                details={"structure_features": processed_content.get("structure_features", {})}
            ))
            
            # 4. 可读性
            readability_score = await self._assess_readability(content, processed_content)
            metrics.append(MetricResult(
                name="readability",
                value=readability_score,
                score=readability_score,
                confidence=0.7,
                evidence=["可读性分析", "阅读体验评估"],
                details={"grade_level": processed_content.get("statistics", {}).get("grade_level", 0)}
            ))
            
            # 计算维度分数
            dimension_score = statistics.mean([m.score for m in metrics])
            level = self._determine_quality_level(dimension_score)
            
            # 生成总结和建议
            summary, strengths, weaknesses, suggestions = self._generate_dimension_summary(
                "文档质量", metrics, dimension_score, level
            )
            
            return DimensionResult(
                dimension=criteria.dimension,
                score=dimension_score,
                level=level,
                metrics=metrics,
                summary=summary,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"文档质量评估失败: {e}")
            raise
    
    async def _assess_completeness(self, 
                                 content: ContentToAssess,
                                 processed_content: dict[str, Any]) -> float:
        """评估完整性"""
        try:
            score = 0.0
            
            # 检查文档结构
            structure = processed_content.get("structure_features", {})
            
            # 标准章节检查
            standard_sections = [
                "has_abstract", "has_introduction", "has_methodology",
                "has_results", "has_conclusion", "has_references"
            ]
            
            section_count = sum(1 for section in standard_sections 
                             if structure.get(section, False))
            score += min(0.6, section_count * 0.1)
            
            # 检查内容长度
            word_count = processed_content.get("statistics", {}).get("word_count", 0)
            if word_count >= 5000:
                score += 0.2
            elif word_count >= 2000:
                score += 0.15
            elif word_count >= 1000:
                score += 0.1
            else:
                score += 0.05
            
            # 检查图表
            figure_count = len(re.findall(r'figure|table|diagram|chart', content.content, re.I))
            score += min(0.2, figure_count * 0.05)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"完整性评估失败: {e}")
            return 0.0
    
    async def _assess_clarity(self, 
                            content: ContentToAssess,
                            processed_content: dict[str, Any]) -> float:
        """评估清晰度"""
        try:
            score = 0.0
            
            # 检查可读性分数
            readability_score = processed_content.get("statistics", {}).get("readability_score", 0)
            if readability_score >= 60:
                score += 0.3
            elif readability_score >= 40:
                score += 0.2
            else:
                score += 0.1
            
            # 检查句子长度
            avg_sentence_length = processed_content.get("statistics", {}).get("avg_sentence_length", 0)
            if avg_sentence_length <= 20:
                score += 0.3
            elif avg_sentence_length <= 30:
                score += 0.2
            else:
                score += 0.1
            
            # 检查词汇丰富度
            vocabulary_richness = processed_content.get("statistics", {}).get("vocabulary_richness", 0)
            if vocabulary_richness >= 0.7:
                score += 0.2
            elif vocabulary_richness >= 0.5:
                score += 0.15
            else:
                score += 0.1
            
            # 检查术语解释
            definition_count = len(re.findall(r'defined as|means|refers to', content.content, re.I))
            score += min(0.2, definition_count * 0.05)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"清晰度评估失败: {e}")
            return 0.0
    
    async def _assess_structure(self, 
                             content: ContentToAssess,
                             processed_content: dict[str, Any]) -> float:
        """评估结构"""
        try:
            score = 0.0
            
            # 检查段落结构
            paragraphs = processed_content.get("paragraphs", [])
            if len(paragraphs) >= 10:
                score += 0.3
            elif len(paragraphs) >= 5:
                score += 0.2
            else:
                score += 0.1
            
            # 检查标题结构
            heading_count = len(re.findall(r'^#+\s+', content.content, re.MULTILINE))
            score += min(0.3, heading_count * 0.05)
            
            # 检查列表结构
            list_count = len(re.findall(r'^\s*[-*+]\s+|^\s*\d+\.\s+', content.content, re.MULTILINE))
            score += min(0.2, list_count * 0.04)
            
            # 检查逻辑流程
            if "introduction" in content.content.lower() and "conclusion" in content.content.lower():
                score += 0.2
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"结构评估失败: {e}")
            return 0.0
    
    async def _assess_readability(self, 
                                content: ContentToAssess,
                                processed_content: dict[str, Any]) -> float:
        """评估可读性"""
        try:
            score = 0.0
            
            # 检查年级水平
            grade_level = processed_content.get("statistics", {}).get("grade_level", 0)
            if grade_level <= 10:
                score += 0.3
            elif grade_level <= 12:
                score += 0.2
            elif grade_level <= 16:
                score += 0.1
            else:
                score += 0.05
            
            # 检查句子复杂度
            complex_sentences = len([s for s in processed_content.get("sentences", []) 
                                   if len(s.split()) > 25])
            total_sentences = len(processed_content.get("sentences", []))
            
            if total_sentences > 0:
                complex_ratio = complex_sentences / total_sentences
                if complex_ratio <= 0.2:
                    score += 0.3
                elif complex_ratio <= 0.4:
                    score += 0.2
                else:
                    score += 0.1
            
            # 检查被动语态
            passive_count = len(re.findall(r'\b(was|were|is|are|been|being)\s+\w+ed\b', content.content))
            total_words = len(processed_content.get("tokens", []))
            
            if total_words > 0:
                passive_ratio = passive_count / total_words
                if passive_ratio <= 0.05:
                    score += 0.2
                elif passive_ratio <= 0.1:
                    score += 0.15
                else:
                    score += 0.1
            
            # 检查技术术语密度
            technical_terms = [
                "algorithm", "framework", "methodology", "implementation",
                "architecture", "system", "process", "analysis"
            ]
            
            technical_count = sum(1 for term in technical_terms 
                                if term in content.content.lower())
            term_density = technical_count / total_words if total_words > 0 else 0
            
            if term_density <= 0.05:
                score += 0.2
            elif term_density <= 0.1:
                score += 0.15
            else:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"可读性评估失败: {e}")
            return 0.0
    
    async def _assess_ethics_compliance(self, 
                                       content: ContentToAssess,
                                       processed_content: dict[str, Any],
                                       criteria: AssessmentCriteria) -> DimensionResult:
        """评估伦理合规"""
        try:
            metrics = []
            
            # 1. 隐私保护
            privacy_score = await self._assess_privacy_protection(content, processed_content)
            metrics.append(MetricResult(
                name="privacy_protection",
                value=privacy_score,
                score=privacy_score,
                confidence=0.8,
                evidence=["隐私保护分析", "数据安全评估"],
                details={"privacy_measures": re.findall(r'privacy|confidential|anonym', content.content, re.I)}
            ))
            
            # 2. 安全措施
            security_score = await self._assess_security_measures(content, processed_content)
            metrics.append(MetricResult(
                name="security_measures",
                value=security_score,
                score=security_score,
                confidence=0.8,
                evidence=["安全措施分析", "风险评估"],
                details={"security_features": re.findall(r'security|encryption|authentication', content.content, re.I)}
            ))
            
            # 3. 合规性
            compliance_score = await self._assess_regulatory_compliance(content, processed_content)
            metrics.append(MetricResult(
                name="regulatory_compliance",
                value=compliance_score,
                score=compliance_score,
                confidence=0.7,
                evidence=["合规性检查", "法规遵循评估"],
                details={"compliance_mentions": re.findall(r'compliance|regulation|standard', content.content, re.I)}
            ))
            
            # 4. 伦理考量
            ethics_score = await self._assess_ethical_considerations(content, processed_content)
            metrics.append(MetricResult(
                name="ethical_considerations",
                value=ethics_score,
                score=ethics_score,
                confidence=0.7,
                evidence=["伦理分析", "道德评估"],
                details={"ethics_discussion": re.findall(r'ethical|moral|responsibility', content.content, re.I)}
            ))
            
            # 计算维度分数
            dimension_score = statistics.mean([m.score for m in metrics])
            level = self._determine_quality_level(dimension_score)
            
            # 生成总结和建议
            summary, strengths, weaknesses, suggestions = self._generate_dimension_summary(
                "伦理合规", metrics, dimension_score, level
            )
            
            return DimensionResult(
                dimension=criteria.dimension,
                score=dimension_score,
                level=level,
                metrics=metrics,
                summary=summary,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"伦理合规评估失败: {e}")
            raise
    
    async def _assess_privacy_protection(self, 
                                       content: ContentToAssess,
                                       processed_content: dict[str, Any]) -> float:
        """评估隐私保护"""
        try:
            score = 0.0
            
            # 检查隐私相关术语
            privacy_terms = [
                "privacy", "confidential", "anonymous", "pseudonymous",
                "personal data", "sensitive information", "data protection"
            ]
            
            privacy_count = sum(1 for term in privacy_terms 
                               if term in content.content.lower())
            score += min(0.4, privacy_count * 0.08)
            
            # 检查隐私保护措施
            protection_measures = [
                "encryption", "anonymization", "pseudonymization",
                "access control", "data minimization", "consent"
            ]
            
            measure_count = sum(1 for measure in protection_measures 
                              if measure in content.content.lower())
            score += min(0.3, measure_count * 0.06)
            
            # 检查隐私政策
            if re.search(r'privacy policy|data policy|gdpr|ccpa', content.content, re.I):
                score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"隐私保护评估失败: {e}")
            return 0.0
    
    async def _assess_security_measures(self, 
                                       content: ContentToAssess,
                                       processed_content: dict[str, Any]) -> float:
        """评估安全措施"""
        try:
            score = 0.0
            
            # 检查安全相关术语
            security_terms = [
                "security", "secure", "safe", "protect",
                "authentication", "authorization", "access control"
            ]
            
            security_count = sum(1 for term in security_terms 
                               if term in content.content.lower())
            score += min(0.4, security_count * 0.08)
            
            # 检查安全技术
            security_technologies = [
                "encryption", "decryption", "firewall", "vpn",
                "ssl", "tls", "hash", "digital signature"
            ]
            
            tech_count = sum(1 for tech in security_technologies 
                           if tech in content.content.lower())
            score += min(0.3, tech_count * 0.06)
            
            # 检查安全测试
            if re.search(r'security test|penetration test|vulnerability', content.content, re.I):
                score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"安全措施评估失败: {e}")
            return 0.0
    
    async def _assess_regulatory_compliance(self, 
                                          content: ContentToAssess,
                                          processed_content: dict[str, Any]) -> float:
        """评估合规性"""
        try:
            score = 0.0
            
            # 检查合规性术语
            compliance_terms = [
                "compliance", "regulation", "standard", "guideline",
                "policy", "procedure", "requirement", "mandate"
            ]
            
            compliance_count = sum(1 for term in compliance_terms 
                                  if term in content.content.lower())
            score += min(0.4, compliance_count * 0.08)
            
            # 检查具体法规
            regulations = [
                "gdpr", "hipaa", "sox", "pci dss", "iso",
                "fcc", "fda", "sec", "eu regulation"
            ]
            
            regulation_count = sum(1 for reg in regulations 
                                if reg in content.content.lower())
            score += min(0.3, regulation_count * 0.06)
            
            # 检查合规流程
            if re.search(r'compliance process|audit|assessment|certification', content.content, re.I):
                score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"合规性评估失败: {e}")
            return 0.0
    
    async def _assess_ethical_considerations(self, 
                                           content: ContentToAssess,
                                           processed_content: dict[str, Any]) -> float:
        """评估伦理考量"""
        try:
            score = 0.0
            
            # 检查伦理相关术语
            ethics_terms = [
                "ethical", "moral", "responsibility", "accountability",
                "transparency", "fairness", "justice", "integrity"
            ]
            
            ethics_count = sum(1 for term in ethics_terms 
                             if term in content.content.lower())
            score += min(0.4, ethics_count * 0.08)
            
            # 检查伦理框架
            ethical_frameworks = [
                "utilitarian", "deontological", "virtue ethics",
                "care ethics", "rights-based", "consequentialist"
            ]
            
            framework_count = sum(1 for framework in ethical_frameworks 
                                if framework in content.content.lower())
            score += min(0.3, framework_count * 0.06)
            
            # 检查伦理讨论
            if re.search(r'ethical consideration|moral implication|social impact', content.content, re.I):
                score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"伦理考量评估失败: {e}")
            return 0.0
    
    async def _assess_innovation(self, 
                                content: ContentToAssess,
                                processed_content: dict[str, Any],
                                criteria: AssessmentCriteria) -> DimensionResult:
        """评估创新性"""
        try:
            metrics = []
            
            # 1. 新颖性
            novelty_score = await self._assess_novelty(content, processed_content)
            metrics.append(MetricResult(
                name="novelty",
                value=novelty_score,
                score=novelty_score,
                confidence=0.7,
                evidence=["新颖性分析", "创新性评估"],
                details={"novel_concepts": re.findall(r'novel|new|innovative|original', content.content, re.I)}
            ))
            
            # 2. 创造性
            creativity_score = await self._assess_creativity(content, processed_content)
            metrics.append(MetricResult(
                name="creativity",
                value=creativity_score,
                score=creativity_score,
                confidence=0.6,
                evidence=["创造性分析", "创意评估"],
                details={"creative_approaches": re.findall(r'creative|unique|different|alternative', content.content, re.I)}
            ))
            
            # 3. 原创性
            originality_score = await self._assess_originality(content, processed_content)
            metrics.append(MetricResult(
                name="originality",
                value=originality_score,
                score=originality_score,
                confidence=0.7,
                evidence=["原创性分析", "独特性评估"],
                details={"original_contributions": re.findall(r'original|unique contribution|first', content.content, re.I)}
            ))
            
            # 4. 进步性
            advancement_score = await self._assess_advancement(content, processed_content)
            metrics.append(MetricResult(
                name="advancement",
                value=advancement_score,
                score=advancement_score,
                confidence=0.6,
                evidence=["进步性分析", "发展评估"],
                details={"advancement_mentions": re.findall(r'advance|progress|improvement|breakthrough', content.content, re.I)}
            ))
            
            # 计算维度分数
            dimension_score = statistics.mean([m.score for m in metrics])
            level = self._determine_quality_level(dimension_score)
            
            # 生成总结和建议
            summary, strengths, weaknesses, suggestions = self._generate_dimension_summary(
                "创新性", metrics, dimension_score, level
            )
            
            return DimensionResult(
                dimension=criteria.dimension,
                score=dimension_score,
                level=level,
                metrics=metrics,
                summary=summary,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"创新性评估失败: {e}")
            raise
    
    async def _assess_novelty(self, 
                           content: ContentToAssess,
                           processed_content: dict[str, Any]) -> float:
        """评估新颖性"""
        try:
            score = 0.0
            
            # 检查新颖性术语
            novelty_terms = [
                "novel", "new", "innovative", "breakthrough",
                "pioneering", "groundbreaking", "unprecedented", "first"
            ]
            
            novelty_count = sum(1 for term in novelty_terms 
                              if term in content.content.lower())
            score += min(0.4, novelty_count * 0.08)
            
            # 检查新概念
            new_concept_indicators = [
                "new approach", "new method", "new technique",
                "new framework", "new model", "new theory"
            ]
            
            concept_count = sum(1 for indicator in new_concept_indicators 
                               if indicator in content.content.lower())
            score += min(0.3, concept_count * 0.06)
            
            # 检查与传统方法的对比
            if re.search(r'traditional|conventional|existing|previous', content.content, re.I):
                score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"新颖性评估失败: {e}")
            return 0.0
    
    async def _assess_creativity(self, 
                              content: ContentToAssess,
                              processed_content: dict[str, Any]) -> float:
        """评估创造性"""
        try:
            score = 0.0
            
            # 检查创造性术语
            creative_terms = [
                "creative", "innovative", "unique", "original",
                "imaginative", "inventive", "resourceful", "clever"
            ]
            
            creative_count = sum(1 for term in creative_terms 
                               if term in content.content.lower())
            score += min(0.4, creative_count * 0.08)
            
            # 检查创造性方法
            creative_methods = [
                "alternative approach", "different perspective", "unconventional",
                "out-of-the-box", "lateral thinking", "divergent"
            ]
            
            method_count = sum(1 for method in creative_methods 
                             if method in content.content.lower())
            score += min(0.3, method_count * 0.06)
            
            # 检查跨学科元素
            interdisciplinary_terms = [
                "interdisciplinary", "multidisciplinary", "cross-disciplinary",
                "hybrid", "fusion", "integration", "synthesis"
            ]
            
            inter_count = sum(1 for term in interdisciplinary_terms 
                            if term in content.content.lower())
            score += min(0.3, inter_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"创造性评估失败: {e}")
            return 0.0
    
    async def _assess_originality(self, 
                                content: ContentToAssess,
                                processed_content: dict[str, Any]) -> float:
        """评估原创性"""
        try:
            score = 0.0
            
            # 检查原创性术语
            originality_terms = [
                "original", "unique", "distinctive", "proprietary",
                "exclusive", "patented", "copyrighted", "authentic"
            ]
            
            originality_count = sum(1 for term in originality_terms 
                                  if term in content.content.lower())
            score += min(0.4, originality_count * 0.08)
            
            # 检查原创贡献
            contribution_terms = [
                "original contribution", "unique contribution", "first to",
                "pioneering work", "seminal work", "foundational"
            ]
            
            contribution_count = sum(1 for term in contribution_terms 
                                   if term in content.content.lower())
            score += min(0.3, contribution_count * 0.06)
            
            # 检查知识产权
            ip_terms = [
                "patent", "copyright", "trademark", "intellectual property",
                "ip", "proprietary", "exclusive rights"
            ]
            
            ip_count = sum(1 for term in ip_terms 
                         if term in content.content.lower())
            score += min(0.3, ip_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"原创性评估失败: {e}")
            return 0.0
    
    async def _assess_advancement(self, 
                                content: ContentToAssess,
                                processed_content: dict[str, Any]) -> float:
        """评估进步性"""
        try:
            score = 0.0
            
            # 检查进步性术语
            advancement_terms = [
                "advance", "progress", "improvement", "enhancement",
                "development", "evolution", "growth", "breakthrough"
            ]
            
            advancement_count = sum(1 for term in advancement_terms 
                                  if term in content.content.lower())
            score += min(0.4, advancement_count * 0.08)
            
            # 检查进步贡献
            progress_terms = [
                "state of the art", "cutting edge", "leading edge",
                "frontier", "breakthrough", "milestone", "landmark"
            ]
            
            progress_count = sum(1 for term in progress_terms 
                               if term in content.content.lower())
            score += min(0.3, progress_count * 0.06)
            
            # 检查影响力
            impact_terms = [
                "impact", "influence", "significance", "importance",
                "contribution", "legacy", "lasting effect"
            ]
            
            impact_count = sum(1 for term in impact_terms 
                             if term in content.content.lower())
            score += min(0.3, impact_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"进步性评估失败: {e}")
            return 0.0
    
    async def _assess_reproducibility(self, 
                                     content: ContentToAssess,
                                     processed_content: dict[str, Any],
                                     criteria: AssessmentCriteria) -> DimensionResult:
        """评估可复现性"""
        try:
            metrics = []
            
            # 1. 数据可用性
            data_availability_score = await self._assess_data_availability(content, processed_content)
            metrics.append(MetricResult(
                name="data_availability",
                value=data_availability_score,
                score=data_availability_score,
                confidence=0.8,
                evidence=["数据可用性分析", "数据共享评估"],
                details={"data_mentions": re.findall(r'data|dataset|database', content.content, re.I)}
            ))
            
            # 2. 方法透明度
            transparency_score = await self._assess_method_transparency(content, processed_content)
            metrics.append(MetricResult(
                name="method_transparency",
                value=transparency_score,
                score=transparency_score,
                confidence=0.7,
                evidence=["方法透明度分析", "过程可追溯性评估"],
                details={"method_details": re.findall(r'method|procedure|protocol', content.content, re.I)}
            ))
            
            # 3. 实验可重复性
            repeatability_score = await self._assess_experiment_repeatability(content, processed_content)
            metrics.append(MetricResult(
                name="experiment_repeatability",
                value=repeatability_score,
                score=repeatability_score,
                confidence=0.7,
                evidence=["实验可重复性分析", "可复制性评估"],
                details={"experiment_details": re.findall(r'experiment|test|trial', content.content, re.I)}
            ))
            
            # 4. 代码可访问性
            code_accessibility_score = await self._assess_code_accessibility(content, processed_content)
            metrics.append(MetricResult(
                name="code_accessibility",
                value=code_accessibility_score,
                score=code_accessibility_score,
                confidence=0.8,
                evidence=["代码可访问性分析", "代码可用性评估"],
                details={"code_access_info": re.findall(r'code|software|program', content.content, re.I)}
            ))
            
            # 计算维度分数
            dimension_score = statistics.mean([m.score for m in metrics])
            level = self._determine_quality_level(dimension_score)
            
            # 生成总结和建议
            summary, strengths, weaknesses, suggestions = self._generate_dimension_summary(
                "可复现性", metrics, dimension_score, level
            )
            
            return DimensionResult(
                dimension=criteria.dimension,
                score=dimension_score,
                level=level,
                metrics=metrics,
                summary=summary,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"可复现性评估失败: {e}")
            raise
    
    async def _assess_data_availability(self, 
                                      content: ContentToAssess,
                                      processed_content: dict[str, Any]) -> float:
        """评估数据可用性"""
        try:
            score = 0.0
            
            # 检查数据相关术语
            data_terms = [
                "data", "dataset", "database", "repository",
                "archive", "collection", "sample", "corpus"
            ]
            
            data_count = sum(1 for term in data_terms 
                           if term in content.content.lower())
            score += min(0.4, data_count * 0.08)
            
            # 检查数据共享
            sharing_terms = [
                "share", "available", "accessible", "open",
                "public", "download", "repository", "archive"
            ]
            
            sharing_count = sum(1 for term in sharing_terms 
                              if term in content.content.lower())
            score += min(0.3, sharing_count * 0.06)
            
            # 检查数据格式
            format_terms = [
                "format", "structure", "schema", "metadata",
                "documentation", "description", "specification"
            ]
            
            format_count = sum(1 for term in format_terms 
                             if term in content.content.lower())
            score += min(0.3, format_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"数据可用性评估失败: {e}")
            return 0.0
    
    async def _assess_method_transparency(self, 
                                        content: ContentToAssess,
                                        processed_content: dict[str, Any]) -> float:
        """评估方法透明度"""
        try:
            score = 0.0
            
            # 检查方法详细程度
            method_detail_terms = [
                "detailed", "comprehensive", "thorough", "complete",
                "step-by-step", "systematic", "structured", "organized"
            ]
            
            detail_count = sum(1 for term in method_detail_terms 
                             if term in content.content.lower())
            score += min(0.4, detail_count * 0.08)
            
            # 检查可追溯性
            traceability_terms = [
                "traceable", "transparent", "clear", "explicit",
                "documented", "recorded", "logged", "tracked"
            ]
            
            traceability_count = sum(1 for term in traceability_terms 
                                   if term in content.content.lower())
            score += min(0.3, traceability_count * 0.06)
            
            # 检查验证过程
            validation_terms = [
                "validation", "verification", "confirmation", "testing",
                "checking", "auditing", "review", "inspection"
            ]
            
            validation_count = sum(1 for term in validation_terms 
                                 if term in content.content.lower())
            score += min(0.3, validation_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"方法透明度评估失败: {e}")
            return 0.0
    
    async def _assess_experiment_repeatability(self, 
                                             content: ContentToAssess,
                                             processed_content: dict[str, Any]) -> float:
        """评估实验可重复性"""
        try:
            score = 0.0
            
            # 检查实验设置
            setup_terms = [
                "setup", "configuration", "environment", "conditions",
                "parameters", "settings", "variables", "controls"
            ]
            
            setup_count = sum(1 for term in setup_terms 
                           if term in content.content.lower())
            score += min(0.4, setup_count * 0.08)
            
            # 检查实验步骤
            step_terms = [
                "step", "procedure", "protocol", "process",
                "sequence", "order", "flow", "pipeline"
            ]
            
            step_count = sum(1 for term in step_terms 
                           if term in content.content.lower())
            score += min(0.3, step_count * 0.06)
            
            # 检查结果记录
            result_terms = [
                "result", "outcome", "output", "finding",
                "measurement", "observation", "data", "evidence"
            ]
            
            result_count = sum(1 for term in result_terms 
                              if term in content.content.lower())
            score += min(0.3, result_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"实验可重复性评估失败: {e}")
            return 0.0
    
    async def _assess_code_accessibility(self, 
                                        content: ContentToAssess,
                                        processed_content: dict[str, Any]) -> float:
        """评估代码可访问性"""
        try:
            score = 0.0
            
            # 检查代码可用性
            availability_terms = [
                "available", "accessible", "open source", "public",
                "shared", "distributed", "published", "released"
            ]
            
            availability_count = sum(1 for term in availability_terms 
                                   if term in content.content.lower())
            score += min(0.4, availability_count * 0.08)
            
            # 检查代码库
            repository_terms = [
                "repository", "github", "gitlab", "bitbucket",
                "codebase", "source code", "archive", "library"
            ]
            
            repository_count = sum(1 for term in repository_terms 
                                 if term in content.content.lower())
            score += min(0.3, repository_count * 0.06)
            
            # 检查代码文档
            documentation_terms = [
                "documentation", "readme", "guide", "manual",
                "instructions", "comments", "annotations", "explanation"
            ]
            
            documentation_count = sum(1 for term in documentation_terms 
                                    if term in content.content.lower())
            score += min(0.3, documentation_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"代码可访问性评估失败: {e}")
            return 0.0
    
    async def _assess_impact(self, 
                           content: ContentToAssess,
                           processed_content: dict[str, Any],
                           criteria: AssessmentCriteria) -> DimensionResult:
        """评估影响力"""
        try:
            metrics = []
            
            # 1. 影响范围
            reach_score = await self._assess_reach(content, processed_content)
            metrics.append(MetricResult(
                name="reach",
                value=reach_score,
                score=reach_score,
                confidence=0.6,
                evidence=["影响范围分析", "受众评估"],
                details={"audience_mentions": re.findall(r'audience|user|community', content.content, re.I)}
            ))
            
            # 2. 影响力
            influence_score = await self._assess_influence(content, processed_content)
            metrics.append(MetricResult(
                name="influence",
                value=influence_score,
                score=influence_score,
                confidence=0.5,
                evidence=["影响力分析", "权威性评估"],
                details={"influence_indicators": re.findall(r'influence|authority|expert', content.content, re.I)}
            ))
            
            # 3. 引用潜力
            citation_potential_score = await self._assess_citation_potential(content, processed_content)
            metrics.append(MetricResult(
                name="citation_potential",
                value=citation_potential_score,
                score=citation_potential_score,
                confidence=0.5,
                evidence=["引用潜力分析", "学术价值评估"],
                details={"citation_value": re.findall(r'citation|reference|academic', content.content, re.I)}
            ))
            
            # 4. 实际意义
            practical_implications_score = await self._assess_practical_implications(content, processed_content)
            metrics.append(MetricResult(
                name="practical_implications",
                value=practical_implications_score,
                score=practical_implications_score,
                confidence=0.6,
                evidence=["实际意义分析", "应用价值评估"],
                details={"practical_value": re.findall(r'practical|application|implementation', content.content, re.I)}
            ))
            
            # 计算维度分数
            dimension_score = statistics.mean([m.score for m in metrics])
            level = self._determine_quality_level(dimension_score)
            
            # 生成总结和建议
            summary, strengths, weaknesses, suggestions = self._generate_dimension_summary(
                "影响力", metrics, dimension_score, level
            )
            
            return DimensionResult(
                dimension=criteria.dimension,
                score=dimension_score,
                level=level,
                metrics=metrics,
                summary=summary,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"影响力评估失败: {e}")
            raise
    
    async def _assess_reach(self, 
                          content: ContentToAssess,
                          processed_content: dict[str, Any]) -> float:
        """评估影响范围"""
        try:
            score = 0.0
            
            # 检查受众范围
            audience_terms = [
                "audience", "users", "community", "public",
                "stakeholders", "customers", "clients", "readers"
            ]
            
            audience_count = sum(1 for term in audience_terms 
                               if term in content.content.lower())
            score += min(0.4, audience_count * 0.08)
            
            # 检查规模术语
            scale_terms = [
                "scale", "scope", "range", "extent",
                "breadth", "width", "coverage", "span"
            ]
            
            scale_count = sum(1 for term in scale_terms 
                           if term in content.content.lower())
            score += min(0.3, scale_count * 0.06)
            
            # 检查分布术语
            distribution_terms = [
                "distribution", "dissemination", "spread", "circulation",
                "publication", "release", "launch", "deployment"
            ]
            
            distribution_count = sum(1 for term in distribution_terms 
                                   if term in content.content.lower())
            score += min(0.3, distribution_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"影响范围评估失败: {e}")
            return 0.0
    
    async def _assess_influence(self, 
                              content: ContentToAssess,
                              processed_content: dict[str, Any]) -> float:
        """评估影响力"""
        try:
            score = 0.0
            
            # 检查影响力术语
            influence_terms = [
                "influence", "impact", "effect", "change",
                "transformation", "revolution", "shift", "paradigm"
            ]
            
            influence_count = sum(1 for term in influence_terms 
                                if term in content.content.lower())
            score += min(0.4, influence_count * 0.08)
            
            # 检查权威性
            authority_terms = [
                "authority", "expert", "specialist", "leader",
                "pioneer", "innovator", "visionary", "thought leader"
            ]
            
            authority_count = sum(1 for term in authority_terms 
                                if term in content.content.lower())
            score += min(0.3, authority_count * 0.06)
            
            # 检查认可度
            recognition_terms = [
                "recognition", "award", "prize", "honor",
                "acclaim", "praise", "endorsement", "approval"
            ]
            
            recognition_count = sum(1 for term in recognition_terms 
                                   if term in content.content.lower())
            score += min(0.3, recognition_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"影响力评估失败: {e}")
            return 0.0
    
    async def _assess_citation_potential(self, 
                                        content: ContentToAssess,
                                        processed_content: dict[str, Any]) -> float:
        """评估引用潜力"""
        try:
            score = 0.0
            
            # 检查引用价值术语
            citation_terms = [
                "citation", "reference", "academic", "scholarly",
                "research", "study", "paper", "publication"
            ]
            
            citation_count = sum(1 for term in citation_terms 
                               if term in content.content.lower())
            score += min(0.4, citation_count * 0.08)
            
            # 检查贡献度
            contribution_terms = [
                "contribution", "addition", "advancement", "improvement",
                "enhancement", "development", "progress", "innovation"
            ]
            
            contribution_count = sum(1 for term in contribution_terms 
                                   if term in content.content.lower())
            score += min(0.3, contribution_count * 0.06)
            
            # 检查基础性
            fundamental_terms = [
                "fundamental", "basic", "essential", "core",
                "foundational", "groundbreaking", "seminal", "pioneering"
            ]
            
            fundamental_count = sum(1 for term in fundamental_terms 
                                  if term in content.content.lower())
            score += min(0.3, fundamental_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"引用潜力评估失败: {e}")
            return 0.0
    
    async def _assess_practical_implications(self, 
                                           content: ContentToAssess,
                                           processed_content: dict[str, Any]) -> float:
        """评估实际意义"""
        try:
            score = 0.0
            
            # 检查实际应用
            practical_terms = [
                "practical", "applied", "real-world", "tangible",
                "concrete", "actual", "implementation", "deployment"
            ]
            
            practical_count = sum(1 for term in practical_terms 
                                if term in content.content.lower())
            score += min(0.4, practical_count * 0.08)
            
            # 检查问题解决
            solution_terms = [
                "solution", "solve", "address", "resolve",
                "fix", "remedy", "overcome", "tackle"
            ]
            
            solution_count = sum(1 for term in solution_terms 
                               if term in content.content.lower())
            score += min(0.3, solution_count * 0.06)
            
            # 检查价值创造
            value_terms = [
                "value", "benefit", "advantage", "gain",
                "improvement", "enhancement", "optimization", "efficiency"
            ]
            
            value_count = sum(1 for term in value_terms 
                            if term in content.content.lower())
            score += min(0.3, value_count * 0.06)
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"实际意义评估失败: {e}")
            return 0.0
    
    def _calculate_overall_score(self, 
                                dimension_results: list[DimensionResult],
                                criteria: dict[str, AssessmentCriteria]) -> float:
        """计算总体分数"""
        try:
            weighted_sum = 0.0
            total_weight = 0.0
            
            for result in dimension_results:
                if result.dimension.value in criteria:
                    weight = criteria[result.dimension.value].weight
                    weighted_sum += result.score * weight
                    total_weight += weight
            
            if total_weight == 0:
                return 0.0
            
            return weighted_sum / total_weight
            
        except Exception as e:
            self.logger.error(f"计算总体分数失败: {e}")
            return 0.0
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """确定质量等级"""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.8:
            return QualityLevel.GOOD
        elif score >= 0.7:
            return QualityLevel.SATISFACTORY
        elif score >= 0.6:
            return QualityLevel.NEEDS_IMPROVEMENT
        else:
            return QualityLevel.POOR
    
    def _calculate_assessment_confidence(self, dimension_results: list[DimensionResult]) -> float:
        """计算评估置信度"""
        try:
            if not dimension_results:
                return 0.0
            
            # 基于指标置信度计算
            metric_confidences = []
            for result in dimension_results:
                if result.metrics:
                    metric_confidences.extend([m.confidence for m in result.metrics])
            
            if not metric_confidences:
                return 0.0
            
            avg_confidence = statistics.mean(metric_confidences)
            
            # 考虑维度覆盖率
            dimension_coverage = len(dimension_results) / 8.0  # 8个维度
            
            # 综合置信度
            final_confidence = avg_confidence * 0.8 + dimension_coverage * 0.2
            
            return min(1.0, max(0.0, final_confidence))
            
        except Exception as e:
            self.logger.error(f"计算评估置信度失败: {e}")
            return 0.0
    
    def _generate_dimension_summary(self, 
                                   dimension_name: str,
                                   metrics: list[MetricResult],
                                   score: float,
                                   level: QualityLevel) -> tuple[str, list[str], list[str], list[str]]:
        """生成维度总结"""
        try:
            # 基本总结
            summary = f"{dimension_name}评估结果: {level.value} (分数: {score:.3f})"
            
            # 分析优势
            strengths = []
            weaknesses = []
            suggestions = []
            
            for metric in metrics:
                if metric.score >= 0.8:
                    strengths.append(f"{metric.name}: 表现优秀 ({metric.score:.3f})")
                elif metric.score >= 0.6:
                    strengths.append(f"{metric.name}: 表现良好 ({metric.score:.3f})")
                else:
                    weaknesses.append(f"{metric.name}: 需要改进 ({metric.score:.3f})")
                    suggestions.append(f"改进{metric.name}: {self._generate_suggestion(metric.name, metric.score)}")
            
            # 确保至少有一个建议
            if not suggestions:
                suggestions.append("继续保持当前的高质量标准")
            
            return summary, strengths, weaknesses, suggestions
            
        except Exception as e:
            self.logger.error(f"生成维度总结失败: {e}")
            return f"{dimension_name}评估失败", [], [], ["无法生成具体建议"]
    
    def _generate_suggestion(self, metric_name: str, score: float) -> str:
        """生成改进建议"""
        try:
            suggestions = {
                "theoretical_foundation": "加强理论基础，完善概念框架",
                "methodology_rigor": "提高方法论严谨性，详细描述实验设计",
                "logical_coherence": "改善逻辑结构，增强论证连贯性",
                "citation_quality": "增加相关引用，提高文献综述质量",
                "code_quality": "提高代码质量，增加注释和文档",
                "performance": "优化性能指标，进行详细的性能测试",
                "scalability": "增强可扩展性设计，考虑分布式架构",
                "maintainability": "提高代码可维护性，采用模块化设计",
                "applicability": "增强实际应用价值，提供具体应用场景",
                "usability": "改善用户体验，提高系统易用性",
                "cost_effectiveness": "优化成本效益分析，提供详细的ROI计算",
                "real_world_value": "增强实际价值，提供案例研究",
                "completeness": "完善文档结构，确保内容完整性",
                "clarity": "提高内容清晰度，改善语言表达",
                "structure": "优化文档结构，增强逻辑组织",
                "readability": "提高可读性，简化复杂概念",
                "privacy_protection": "加强隐私保护措施，确保数据安全",
                "security_measures": "增强安全措施，进行全面的安全测试",
                "regulatory_compliance": "确保合规性，遵循相关法规标准",
                "ethical_considerations": "加强伦理考量，进行全面的影响评估",
                "novelty": "增强创新性，提出新的观点或方法",
                "creativity": "提高创造性，采用跨学科方法",
                "originality": "增强原创性，提供独特的贡献",
                "advancement": "加强进步性，推动领域发展",
                "data_availability": "提高数据可用性，共享数据资源",
                "method_transparency": "增强方法透明度，提供详细的过程描述",
                "experiment_repeatability": "确保实验可重复性，提供完整的实验设置",
                "code_accessibility": "提高代码可访问性，开源相关代码",
                "reach": "扩大影响范围，增加受众覆盖",
                "influence": "增强影响力，提高权威性",
                "citation_potential": "提高引用潜力，增强学术贡献",
                "practical_implications": "增强实际意义，提供具体应用价值"
            }
            
            return suggestions.get(metric_name, "需要进一步改进和完善")
            
        except Exception as e:
            self.logger.error(f"生成改进建议失败: {e}")
            return "需要进一步改进和完善"
    
    def _record_assessment(self, assessment_result: AssessmentResult):
        """记录评估历史"""
        try:
            self.assessment_history.append({
                "timestamp": assessment_result.assessment_time.isoformat(),
                "assessment_id": assessment_result.id,
                "content_id": assessment_result.content_id,
                "overall_score": assessment_result.overall_score,
                "overall_level": assessment_result.overall_level.value,
                "confidence": assessment_result.confidence,
                "dimension_scores": {dim: result.score for dim, result in assessment_result.dimensions.items()}
            })
            
            # 限制历史记录数量
            if len(self.assessment_history) > 1000:
                self.assessment_history = self.assessment_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"记录评估历史失败: {e}")
    
    def _start_background_tasks(self):
        """启动后台任务"""
        def model_optimization_task():
            while True:
                time.sleep(3600)  # 每小时执行一次
                try:
                    self._optimize_assessment_models()
                except Exception as e:
                    self.logger.error(f"评估模型优化失败: {e}")
        
        # 启动后台线程
        optimization_thread = threading.Thread(target=model_optimization_task, daemon=True)
        optimization_thread.start()
    
    def _optimize_assessment_models(self):
        """优化评估模型"""
        try:
            # 分析历史评估数据
            if len(self.assessment_history) >= 10:
                recent_assessments = self.assessment_history[-50:]
                
                # 计算平均分数
                avg_scores = {}
                for assessment in recent_assessments:
                    for dim, score in assessment.get("dimension_scores", {}).items():
                        if dim not in avg_scores:
                            avg_scores[dim] = []
                        avg_scores[dim].append(score)
                
                # 分析趋势
                for dim, scores in avg_scores.items():
                    if scores:
                        avg_score = statistics.mean(scores)
                        self.logger.info(f"维度 {dim} 平均分数: {avg_score:.3f}")
                
                self.logger.info(f"评估模型优化完成，分析了 {len(recent_assessments)} 条记录")
            
        except Exception as e:
            self.logger.error(f"评估模型优化失败: {e}")
    
    async def get_assessment_statistics(self) -> dict[str, Any]:
        """获取评估统计信息"""
        try:
            stats = {
                "total_assessments": len(self.assessment_history),
                "average_score": 0.0,
                "dimension_distribution": {},
                "quality_level_distribution": {},
                "recent_assessments": [],
                "assessment_trends": {}
            }
            
            if self.assessment_history:
                # 计算平均分数
                recent_scores = [assess["overall_score"] for assess in self.assessment_history[-50:]]
                stats["average_score"] = statistics.mean(recent_scores) if recent_scores else 0.0
                
                # 维度分布
                dimension_scores = {}
                for assessment in self.assessment_history:
                    for dim, score in assessment.get("dimension_scores", {}).items():
                        if dim not in dimension_scores:
                            dimension_scores[dim] = []
                        dimension_scores[dim].append(score)
                
                for dim, scores in dimension_scores.items():
                    stats["dimension_distribution"][dim] = {
                        "average": statistics.mean(scores),
                        "count": len(scores)
                    }
                
                # 质量等级分布
                level_counts = Counter(assess["overall_level"] for assess in self.assessment_history)
                stats["quality_level_distribution"] = dict(level_counts)
                
                # 最近评估
                stats["recent_assessments"] = self.assessment_history[-10:] if len(self.assessment_history) >= 10 else self.assessment_history
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取评估统计失败: {e}")
            return {}
    
    async def create_custom_criteria(self, 
                                   dimension_weights: dict[str, float],
                                   custom_thresholds: dict[str, float] = None) -> dict[str, AssessmentCriteria]:
        """创建自定义评估标准"""
        try:
            custom_criteria = {}
            
            for dim_name, weight in dimension_weights.items():
                if dim_name in self.assessment_criteria:
                    base_criteria = self.assessment_criteria[dim_name]
                    
                    custom_criteria[dim_name] = AssessmentCriteria(
                        dimension=base_criteria.dimension,
                        weight=weight,
                        metrics=base_criteria.metrics,
                        threshold=custom_thresholds.get(dim_name, base_criteria.threshold),
                        description=base_criteria.description,
                        importance=base_criteria.importance
                    )
            
            return custom_criteria
            
        except Exception as e:
            self.logger.error(f"创建自定义标准失败: {e}")
            return {}
    
    def export_assessment_report(self, assessment_result: AssessmentResult, format: str = "json") -> str:
        """导出评估报告"""
        try:
            if format.lower() == "json":
                return json.dumps(asdict(assessment_result), ensure_ascii=False, indent=2)
            elif format.lower() == "text":
                return self._generate_text_report(assessment_result)
            elif format.lower() == "html":
                return self._generate_html_report(assessment_result)
            else:
                raise ValueError(f"不支持的导出格式: {format}")
                
        except Exception as e:
            self.logger.error(f"导出评估报告失败: {e}")
            return f"报告导出失败: {str(e)}"
    
    def _generate_text_report(self, assessment_result: AssessmentResult) -> str:
        """生成文本报告"""
        try:
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("多维度评估报告")
            report_lines.append("=" * 60)
            report_lines.append(f"评估ID: {assessment_result.id}")
            report_lines.append(f"内容ID: {assessment_result.content_id}")
            report_lines.append(f"内容类型: {assessment_result.content_type.value}")
            report_lines.append(f"评估时间: {assessment_result.assessment_time}")
            report_lines.append(f"评估者: {assessment_result.assessor}")
            report_lines.append("")
            
            # 总体结果
            report_lines.append("总体评估结果:")
            report_lines.append(f"  总分: {assessment_result.overall_score:.3f}")
            report_lines.append(f"  等级: {assessment_result.overall_level.value}")
            report_lines.append(f"  置信度: {assessment_result.confidence:.3f}")
            report_lines.append("")
            
            # 各维度结果
            report_lines.append("各维度评估结果:")
            for dim_name, dim_result in assessment_result.dimensions.items():
                report_lines.append(f"  {dim_name}: {dim_result.level.value} ({dim_result.score:.3f})")
            
            report_lines.append("")
            
            # 详细分析
            report_lines.append("详细分析:")
            for dim_name, dim_result in assessment_result.dimensions.items():
                report_lines.append(f"\n{dim_name}维度:")
                report_lines.append(f"  总结: {dim_result.summary}")
                report_lines.append(f"  优势: {', '.join(dim_result.strengths)}")
                report_lines.append(f"  不足: {', '.join(dim_result.weaknesses)}")
                report_lines.append(f"  建议: {', '.join(dim_result.suggestions)}")
                
                # 指标详情
                report_lines.append("  指标详情:")
                for metric in dim_result.metrics:
                    report_lines.append(f"    {metric.name}: {metric.score:.3f} (置信度: {metric.confidence:.3f})")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            self.logger.error(f"生成文本报告失败: {e}")
            return f"报告生成失败: {str(e)}"
    
    def _generate_html_report(self, assessment_result: AssessmentResult) -> str:
        """生成HTML报告"""
        try:
            html_lines = []
            html_lines.append("<!DOCTYPE html>")
            html_lines.append("<html lang='zh-CN'>")
            html_lines.append("<head>")
            html_lines.append("    <meta charset='UTF-8'>")
            html_lines.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
            html_lines.append("    <title>多维度评估报告</title>")
            html_lines.append("    <style>")
            html_lines.append("        body { font-family: Arial, sans-serif; margin: 20px; }")
            html_lines.append("        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }")
            html_lines.append("        .section { margin: 20px 0; }")
            html_lines.append("        .metric { margin: 10px 0; padding: 10px; border-left: 3px solid #007bff; }")
            html_lines.append("        .strength { color: #28a745; }")
            html_lines.append("        .weakness { color: #dc3545; }")
            html_lines.append("        .suggestion { color: #ffc107; }")
            html_lines.append("        .score-excellent { color: #28a745; font-weight: bold; }")
            html_lines.append("        .score-good { color: #17a2b8; font-weight: bold; }")
            html_lines.append("        .score-satisfactory { color: #ffc107; font-weight: bold; }")
            html_lines.append("        .score-needs-improvement { color: #fd7e14; font-weight: bold; }")
            html_lines.append("        .score-poor { color: #dc3545; font-weight: bold; }")
            html_lines.append("    </style>")
            html_lines.append("</head>")
            html_lines.append("<body>")
            html_lines.append("    <div class='header'>")
            html_lines.append("        <h1>多维度评估报告</h1>")
            html_lines.append(f"        <p>评估ID: {assessment_result.id}</p>")
            html_lines.append(f"        <p>内容ID: {assessment_result.content_id}</p>")
            html_lines.append(f"        <p>内容类型: {assessment_result.content_type.value}</p>")
            html_lines.append(f"        <p>评估时间: {assessment_result.assessment_time}</p>")
            html_lines.append(f"        <p>评估者: {assessment_result.assessor}</p>")
            html_lines.append("    </div>")
            
            # 总体结果
            overall_class = f"score-{assessment_result.overall_level.value}"
            html_lines.append("    <div class='section'>")
            html_lines.append("        <h2>总体评估结果</h2>")
            html_lines.append(f"        <p>总分: <span class='{overall_class}'>{assessment_result.overall_score:.3f}</span></p>")
            html_lines.append(f"        <p>等级: <span class='{overall_class}'>{assessment_result.overall_level.value}</span></p>")
            html_lines.append(f"        <p>置信度: {assessment_result.confidence:.3f}</p>")
            html_lines.append("    </div>")
            
            # 各维度结果
            html_lines.append("    <div class='section'>")
            html_lines.append("        <h2>各维度评估结果</h2>")
            html_lines.append("        <ul>")
            for dim_name, dim_result in assessment_result.dimensions.items():
                dim_class = f"score-{dim_result.level.value}"
                html_lines.append(f"            <li>{dim_name}: <span class='{dim_class}'>{dim_result.level.value} ({dim_result.score:.3f})</span></li>")
            html_lines.append("        </ul>")
            html_lines.append("    </div>")
            
            # 详细分析
            html_lines.append("    <div class='section'>")
            html_lines.append("        <h2>详细分析</h2>")
            for dim_name, dim_result in assessment_result.dimensions.items():
                html_lines.append("        <div class='metric'>")
                html_lines.append(f"            <h3>{dim_name}维度</h3>")
                html_lines.append(f"            <p><strong>总结:</strong> {dim_result.summary}</p>")
                html_lines.append(f"            <p><strong>优势:</strong> <span class='strength'>{', '.join(dim_result.strengths)}</span></p>")
                html_lines.append(f"            <p><strong>不足:</strong> <span class='weakness'>{', '.join(dim_result.weaknesses)}</span></p>")
                html_lines.append(f"            <p><strong>建议:</strong> <span class='suggestion'>{', '.join(dim_result.suggestions)}</span></p>")
                html_lines.append("            <h4>指标详情</h4>")
                html_lines.append("            <ul>")
                for metric in dim_result.metrics:
                    html_lines.append(f"                <li>{metric.name}: {metric.score:.3f} (置信度: {metric.confidence:.3f})</li>")
                html_lines.append("            </ul>")
                html_lines.append("        </div>")
            html_lines.append("    </div>")
            
            html_lines.append("</body>")
            html_lines.append("</html>")
            
            return "\n".join(html_lines)
            
        except Exception as e:
            self.logger.error(f"生成HTML报告失败: {e}")
            return f"<html><body><h1>报告生成失败</h1><p>{str(e)}</p></body></html>"


# 使用示例
async def example_usage():
    """使用示例"""
    # 初始化组件
    knowledge_retrieval = KnowledgeRetrievalService()
    sskg_manager = EnhancedSSKGManager()
    memory_agent = MemAgent()
    
    # 创建多维度评估引擎
    assessment_engine = MultiDimensionalAssessmentEngine(knowledge_retrieval, sskg_manager, memory_agent)
    
    # 创建待评估内容
    content = ContentToAssess(
        id="content_001",
        title="基于深度学习的图像识别系统研究",
        content="""本研究提出了一种新的深度学习架构用于图像识别任务。
我们设计了卷积神经网络(CNN)架构，通过多层特征提取实现高精度识别。
实验结果表明，我们的方法在多个数据集上都取得了优异的性能。

# 1. 引言
图像识别是计算机视觉领域的重要任务，具有广泛的应用前景。
传统的图像识别方法在复杂场景下表现不佳，而深度学习方法通过端到端学习
能够自动提取特征，显著提高了识别准确率。

# 2. 相关工作
近年来，深度学习在图像识别领域取得了显著进展。
LeCun等人提出的LeNet-5开创了卷积神经网络的先河。
Krizhevsky等人提出的AlexNet在ImageNet竞赛中取得了突破性成果。
VGG、ResNet等网络架构不断推动着该领域的发展。

# 3. 方法
我们设计的网络架构包含以下关键组件：
- 卷积层：使用3x3卷积核进行特征提取
- 池化层：采用最大池化降低维度
- 全连接层：实现最终分类
- 激活函数：使用ReLU提高非线性表达能力

# 4. 实验
我们在CIFAR-10、ImageNet等数据集上进行了实验。
实验设置如下：
- 学习率：0.001
- 批次大小：32
- 训练轮数：100
- 优化器：Adam

# 5. 结果
实验结果显示，我们的方法在CIFAR-10上达到了95.2%的准确率，
在ImageNet上达到了87.6%的Top-5准确率，均优于现有方法。

# 6. 结论
本研究提出的深度学习架构在图像识别任务中表现出色，
为该领域的发展提供了新的思路。未来工作将进一步优化网络结构，
提高计算效率，并探索更广泛的应用场景。

# 参考文献
[1] LeCun, Y., et al. (1998). Gradient-based learning applied to document recognition.
[2] Krizhevsky, A., et al. (2012). ImageNet classification with deep convolutional neural networks.
[3] He, K., et al. (2016). Deep residual learning for image recognition.""",
        content_type=ContentType.RESEARCH_PAPER,
        author="researcher_001",
        submission_date=datetime.now(),
        keywords=["深度学习", "图像识别", "CNN", "计算机视觉"],
        metadata={"institution": "清华大学", "department": "计算机科学"}
    )
    
    # 执行评估
    assessment_result = await assessment_engine.assess_content(content)
    
    # 输出结果
    print("评估结果:")
    print(f"  总分: {assessment_result.overall_score:.3f}")
    print(f"  等级: {assessment_result.overall_level.value}")
    print(f"  置信度: {assessment_result.confidence:.3f}")
    
    print("\n各维度分数:")
    for dim_name, dim_result in assessment_result.dimensions.items():
        print(f"  {dim_name}: {dim_result.score:.3f} ({dim_result.level.value})")
    
    # 生成报告
    report = assessment_engine.export_assessment_report(assessment_result, "text")
    print("\n详细报告已生成")
    
    # 获取统计信息
    stats = await assessment_engine.get_assessment_statistics()
    print("\n评估统计:")
    print(f"  总评估次数: {stats['total_assessments']}")
    print(f"  平均分数: {stats['average_score']:.3f}")


if __name__ == "__main__":
    asyncio.run(example_usage())