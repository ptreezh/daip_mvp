#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
研究方法论指导系统

V0.2.3 - 学术研究场景核心功能
提供全面的研究方法论指导和建议
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

from src.scenarios.enhanced_academic_research_scenario import (
    ResearchMethodology, ResearchQuestion, ResearchMethodologyGuide
)

logger = logging.getLogger(__name__)


class ResearchDomain(Enum):
    """研究领域"""
    COMPUTER_SCIENCE = "computer_science"
    PSYCHOLOGY = "psychology"
    EDUCATION = "education"
    MEDICINE = "medicine"
    ENGINEERING = "engineering"
    SOCIAL_SCIENCES = "social_sciences"
    NATURAL_SCIENCES = "natural_sciences"
    BUSINESS = "business"
    HUMANITIES = "humanities"
    INTERDISCIPLINARY = "interdisciplinary"


class ResearchComplexity(Enum):
    """研究复杂度"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class MethodologyRecommendation:
    """方法论推荐"""
    methodology: ResearchMethodology
    suitability_score: float
    reasoning: str
    prerequisites: List[str]
    estimated_duration: str
    resource_requirements: List[str]
    success_factors: List[str]
    potential_challenges: List[str]


@dataclass
class ResearchDesign:
    """研究设计"""
    research_question: ResearchQuestion
    methodology: ResearchMethodology
    study_design: str
    data_collection_methods: List[str]
    data_analysis_plan: str
    sample_size_recommendation: str
    timeline: Dict[str, str]
    ethical_considerations: List[str]
    validity_threats: List[str]
    mitigation_strategies: List[str]


class ResearchMethodologyGuideSystem:
    """研究方法论指导系统"""
    
    def __init__(self):
        self.methodology_database = self._initialize_methodology_database()
        self.domain_specific_guides = self._initialize_domain_guides()
        
        logger.info("Research Methodology Guide System initialized")
    
    def _initialize_methodology_database(self) -> Dict[ResearchMethodology, ResearchMethodologyGuide]:
        """初始化方法论数据库"""
        return {
            ResearchMethodology.QUANTITATIVE: ResearchMethodologyGuide(
                methodology=ResearchMethodology.QUANTITATIVE,
                description="Quantitative research involves the collection and analysis of numerical data to test hypotheses and examine relationships between variables.",
                steps=[
                    "Define research questions and hypotheses",
                    "Design study and select variables",
                    "Choose appropriate sampling method",
                    "Collect numerical data",
                    "Perform statistical analysis",
                    "Interpret results and draw conclusions",
                    "Report findings with statistical evidence"
                ],
                advantages=[
                    "Objective and replicable results",
                    "Large sample sizes possible",
                    "Statistical generalizability",
                    "Clear cause-and-effect relationships",
                    "Standardized data collection"
                ],
                limitations=[
                    "Limited depth of understanding",
                    "May miss contextual factors",
                    "Requires large sample sizes",
                    "Assumes measurable variables",
                    "Less flexible during data collection"
                ],
                suitable_for=[
                    "Testing hypotheses",
                    "Measuring relationships between variables",
                    "Large-scale surveys",
                    "Experimental studies",
                    "Comparative studies"
                ],
                required_resources=[
                    "Statistical software (SPSS, R, Python)",
                    "Large sample access",
                    "Survey tools or measurement instruments",
                    "Statistical expertise",
                    "Data collection infrastructure"
                ],
                timeline_estimate="6-18 months",
                quality_criteria=[
                    "Statistical significance",
                    "Effect size reporting",
                    "Sample representativeness",
                    "Measurement validity and reliability",
                    "Appropriate statistical tests"
                ],
                common_pitfalls=[
                    "Inadequate sample size",
                    "Violation of statistical assumptions",
                    "Multiple testing without correction",
                    "Confusing correlation with causation",
                    "Ignoring missing data patterns"
                ]
            ),
            
            ResearchMethodology.QUALITATIVE: ResearchMethodologyGuide(
                methodology=ResearchMethodology.QUALITATIVE,
                description="Qualitative research explores and understands the meaning individuals or groups ascribe to social or human problems through in-depth, contextual analysis.",
                steps=[
                    "Formulate research questions",
                    "Select appropriate qualitative approach",
                    "Choose participants and settings",
                    "Collect rich, detailed data",
                    "Analyze data thematically",
                    "Develop theoretical insights",
                    "Validate findings with participants"
                ],
                advantages=[
                    "Rich, detailed insights",
                    "Contextual understanding",
                    "Flexible data collection",
                    "Participant perspectives",
                    "Theory development potential"
                ],
                limitations=[
                    "Limited generalizability",
                    "Time-intensive analysis",
                    "Researcher bias potential",
                    "Subjective interpretation",
                    "Smaller sample sizes"
                ],
                suitable_for=[
                    "Exploring new phenomena",
                    "Understanding experiences",
                    "Theory development",
                    "Cultural studies",
                    "Process evaluation"
                ],
                required_resources=[
                    "Qualitative analysis software (NVivo, Atlas.ti)",
                    "Interview/observation skills",
                    "Transcription services",
                    "Extended fieldwork time",
                    "Coding and analysis expertise"
                ],
                timeline_estimate="8-24 months",
                quality_criteria=[
                    "Credibility and trustworthiness",
                    "Transferability",
                    "Dependability",
                    "Confirmability",
                    "Reflexivity"
                ],
                common_pitfalls=[
                    "Insufficient data saturation",
                    "Lack of reflexivity",
                    "Over-generalization",
                    "Inadequate member checking",
                    "Weak audit trail"
                ]
            )
        }
    
    def _initialize_domain_guides(self) -> Dict[ResearchDomain, Dict[str, Any]]:
        """初始化领域特定指导"""
        return {
            ResearchDomain.COMPUTER_SCIENCE: {
                "preferred_methodologies": [ResearchMethodology.EXPERIMENTAL, ResearchMethodology.QUANTITATIVE],
                "common_data_types": ["performance metrics", "user behavior", "system logs", "survey responses"],
                "typical_sample_sizes": "50-1000 participants for user studies, larger for system evaluations",
                "key_considerations": ["Reproducibility", "Scalability", "Real-world applicability", "Ethical AI considerations"],
                "recommended_tools": ["Python/R for analysis", "Git for version control", "Docker for reproducibility"]
            },
            
            ResearchDomain.PSYCHOLOGY: {
                "preferred_methodologies": [ResearchMethodology.EXPERIMENTAL, ResearchMethodology.QUALITATIVE, ResearchMethodology.MIXED_METHODS],
                "common_data_types": ["behavioral measures", "self-report scales", "physiological data", "interview transcripts"],
                "typical_sample_sizes": "30-200 for experiments, 10-30 for qualitative studies",
                "key_considerations": ["Ethical approval", "Informed consent", "Psychological safety", "Cultural sensitivity"],
                "recommended_tools": ["SPSS/R for statistics", "NVivo for qualitative analysis", "E-Prime for experiments"]
            }
        }
    
    async def recommend_methodology(self, research_question: ResearchQuestion, 
                                  domain: ResearchDomain, 
                                  complexity: ResearchComplexity,
                                  constraints: Dict[str, Any] = None) -> List[MethodologyRecommendation]:
        """推荐研究方法论"""
        try:
            logger.info(f"Recommending methodology for {domain.value} research")
            
            constraints = constraints or {}
            recommendations = []
            
            # 获取领域特定信息
            domain_info = self.domain_specific_guides.get(domain, {})
            preferred_methodologies = domain_info.get("preferred_methodologies", list(self.methodology_database.keys()))
            
            # 为每个可能的方法论计算适用性分数
            for methodology in self.methodology_database.keys():
                if methodology in preferred_methodologies or len(preferred_methodologies) == 0:
                    recommendation = await self._evaluate_methodology_suitability(
                        methodology, research_question, domain, complexity, constraints
                    )
                    recommendations.append(recommendation)
            
            # 按适用性分数排序
            recommendations.sort(key=lambda x: x.suitability_score, reverse=True)
            
            logger.info(f"Generated {len(recommendations)} methodology recommendations")
            return recommendations[:5]  # 返回前5个推荐
            
        except Exception as e:
            logger.error(f"Error recommending methodology: {e}")
            return []
    
    async def _evaluate_methodology_suitability(self, methodology: ResearchMethodology,
                                              research_question: ResearchQuestion,
                                              domain: ResearchDomain,
                                              complexity: ResearchComplexity,
                                              constraints: Dict[str, Any]) -> MethodologyRecommendation:
        """评估方法论适用性"""
        guide = self.methodology_database[methodology]
        domain_info = self.domain_specific_guides.get(domain, {})
        
        # 计算适用性分数
        score = 0.0
        
        # 领域偏好权重
        if methodology in domain_info.get("preferred_methodologies", []):
            score += 0.3
        
        # 研究问题类型匹配
        if research_question.research_type.lower() in [s.lower() for s in guide.suitable_for]:
            score += 0.25
        
        # 复杂度匹配
        complexity_scores = {
            ResearchComplexity.BEGINNER: {ResearchMethodology.QUANTITATIVE: 0.8},
            ResearchComplexity.INTERMEDIATE: {ResearchMethodology.QUALITATIVE: 0.8},
            ResearchComplexity.ADVANCED: {ResearchMethodology.MIXED_METHODS: 0.9}
        }
        score += complexity_scores.get(complexity, {}).get(methodology, 0.5) * 0.2
        
        # 约束条件评估
        if "timeline" in constraints:
            timeline_months = self._parse_timeline(guide.timeline_estimate)
            constraint_months = constraints["timeline"]
            if timeline_months <= constraint_months:
                score += 0.15
            else:
                score -= 0.1
        
        # 生成推荐理由
        reasoning = self._generate_recommendation_reasoning(methodology, research_question, domain, score)
        
        return MethodologyRecommendation(
            methodology=methodology,
            suitability_score=min(score, 1.0),
            reasoning=reasoning,
            prerequisites=self._identify_prerequisites(methodology, complexity),
            estimated_duration=guide.timeline_estimate,
            resource_requirements=guide.required_resources,
            success_factors=guide.advantages,
            potential_challenges=guide.limitations
        )
    
    def _parse_timeline(self, timeline_str: str) -> int:
        """解析时间线字符串为月数"""
        if "6-18" in timeline_str:
            return 12
        elif "8-24" in timeline_str:
            return 16
        else:
            return 12
    
    def _generate_recommendation_reasoning(self, methodology: ResearchMethodology,
                                         research_question: ResearchQuestion,
                                         domain: ResearchDomain,
                                         score: float) -> str:
        """生成推荐理由"""
        guide = self.methodology_database[methodology]
        
        reasoning_parts = [
            f"{methodology.value.replace('_', ' ').title()} methodology is {'highly' if score > 0.7 else 'moderately' if score > 0.5 else 'somewhat'} suitable for your research."
        ]
        
        if score > 0.7:
            reasoning_parts.append(f"This approach aligns well with {domain.value.replace('_', ' ')} research practices.")
        
        reasoning_parts.append(f"Key advantages include: {', '.join(guide.advantages[:2])}.")
        
        return " ".join(reasoning_parts)
    
    def _identify_prerequisites(self, methodology: ResearchMethodology, 
                              complexity: ResearchComplexity) -> List[str]:
        """识别前提条件"""
        base_prerequisites = {
            ResearchMethodology.QUANTITATIVE: ["Statistical knowledge", "Data analysis skills"],
            ResearchMethodology.QUALITATIVE: ["Interview skills", "Thematic analysis experience"]
        }
        
        prerequisites = base_prerequisites.get(methodology, ["Basic research skills"])
        
        # 根据复杂度调整
        if complexity in [ResearchComplexity.ADVANCED, ResearchComplexity.EXPERT]:
            prerequisites.extend(["Advanced methodological training", "Research supervision experience"])
        
        return prerequisites        "
""生成伦理部分"""
        ethics_list = "\n".join([f"- {consideration}" for consideration in research_design.ethical_considerations])
        
        return f"""## Ethical Considerations

### Key Ethical Issues
{ethics_list}

### Mitigation Strategies
""" + "\n".join([f"- {strategy}" for strategy in research_design.mitigation_strategies])
    
    def _generate_limitations_section(self, research_design: ResearchDesign) -> str:
        """生成局限性部分"""
        threats_list = "\n".join([f"- {threat}" for threat in research_design.validity_threats])
        
        return f"""## Limitations and Validity Threats

### Potential Threats to Validity
{threats_list}

### Mitigation Strategies
The following strategies will be employed to address these limitations:
""" + "\n".join([f"- {strategy}" for strategy in research_design.mitigation_strategies])