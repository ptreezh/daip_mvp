#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同行评议模拟机制

V0.2.3 - 学术研究场景核心功能
模拟真实的同行评议过程，提供多角度的学术评价
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import random
from pathlib import Path

from src.scenarios.enhanced_academic_research_scenario import PeerReviewCriteria, PeerReviewFeedback

logger = logging.getLogger(__name__)


class ReviewerExpertise(Enum):
    """评议者专业领域"""
    METHODOLOGY_EXPERT = "methodology_expert"
    DOMAIN_SPECIALIST = "domain_specialist"
    STATISTICAL_EXPERT = "statistical_expert"
    WRITING_SPECIALIST = "writing_specialist"
    ETHICS_REVIEWER = "ethics_reviewer"
    JUNIOR_RESEARCHER = "junior_researcher"
    SENIOR_RESEARCHER = "senior_researcher"
    INTERDISCIPLINARY_EXPERT = "interdisciplinary_expert"


class ReviewDecision(Enum):
    """评议决定"""
    ACCEPT = "accept"
    MINOR_REVISION = "minor_revision"
    MAJOR_REVISION = "major_revision"
    REJECT = "reject"
    RESUBMIT_ELSEWHERE = "resubmit_elsewhere"


@dataclass
class ReviewerProfile:
    """评议者档案"""
    reviewer_id: str
    name: str
    expertise_areas: List[ReviewerExpertise]
    experience_level: str  # junior, mid-career, senior
    review_style: str  # constructive, critical, balanced, encouraging
    bias_tendencies: List[str]  # methodological_purist, innovation_focused, etc.
    average_review_time: int  # days
    review_thoroughness: float  # 0-1 scale
    
    
@dataclass
class ManuscriptSection:
    """稿件章节"""
    section_name: str
    content: str
    word_count: int
    quality_indicators: Dict[str, float]


@dataclass
class ReviewAssignment:
    """评议分配"""
    manuscript_id: str
    reviewer_profiles: List[ReviewerProfile]
    review_deadline: datetime
    review_type: str  # initial, revision, final
    special_instructions: List[str]


class PeerReviewSimulator:
    """同行评议模拟器"""
    
    def __init__(self):
        self.reviewer_database = self._initialize_reviewer_database()
        self.review_criteria_weights = self._initialize_criteria_weights()
        self.review_templates = self._initialize_review_templates()
        
        logger.info("Peer Review Simulator initialized")
    
    def _initialize_reviewer_database(self) -> List[ReviewerProfile]:
        """初始化评议者数据库"""
        return [
            ReviewerProfile(
                reviewer_id="REV001",
                name="Dr. Sarah Chen",
                expertise_areas=[ReviewerExpertise.METHODOLOGY_EXPERT, ReviewerExpertise.STATISTICAL_EXPERT],
                experience_level="senior",
                review_style="critical",
                bias_tendencies=["methodological_purist", "statistical_rigor_focused"],
                average_review_time=14,
                review_thoroughness=0.9
            ),
            ReviewerProfile(
                reviewer_id="REV002", 
                name="Prof. Michael Rodriguez",
                expertise_areas=[ReviewerExpertise.DOMAIN_SPECIALIST, ReviewerExpertise.SENIOR_RESEARCHER],
                experience_level="senior",
                review_style="balanced",
                bias_tendencies=["practical_application_focused", "innovation_encouraging"],
                average_review_time=10,
                review_thoroughness=0.8
            ),
            ReviewerProfile(
                reviewer_id="REV003",
                name="Dr. Emily Watson",
                expertise_areas=[ReviewerExpertise.WRITING_SPECIALIST, ReviewerExpertise.ETHICS_REVIEWER],
                experience_level="mid-career",
                review_style="constructive",
                bias_tendencies=["clarity_focused", "ethical_considerations_strict"],
                average_review_time=12,
                review_thoroughness=0.85
            ),
            ReviewerProfile(
                reviewer_id="REV004",
                name="Dr. James Liu",
                expertise_areas=[ReviewerExpertise.JUNIOR_RESEARCHER, ReviewerExpertise.INTERDISCIPLINARY_EXPERT],
                experience_level="junior",
                review_style="encouraging",
                bias_tendencies=["innovation_focused", "interdisciplinary_supportive"],
                average_review_time=16,
                review_thoroughness=0.7
            ),
            ReviewerProfile(
                reviewer_id="REV005",
                name="Prof. Anna Kowalski",
                expertise_areas=[ReviewerExpertise.METHODOLOGY_EXPERT, ReviewerExpertise.DOMAIN_SPECIALIST],
                experience_level="senior",
                review_style="critical",
                bias_tendencies=["theoretical_rigor_focused", "replication_advocate"],
                average_review_time=8,
                review_thoroughness=0.95
            )
        ]
    
    def _initialize_criteria_weights(self) -> Dict[ReviewerExpertise, Dict[PeerReviewCriteria, float]]:
        """初始化评议标准权重"""
        return {
            ReviewerExpertise.METHODOLOGY_EXPERT: {
                PeerReviewCriteria.METHODOLOGY: 0.3,
                PeerReviewCriteria.STATISTICAL_VALIDITY: 0.25,
                PeerReviewCriteria.REPRODUCIBILITY: 0.2,
                PeerReviewCriteria.NOVELTY: 0.1,
                PeerReviewCriteria.SIGNIFICANCE: 0.1,
                PeerReviewCriteria.CLARITY: 0.05
            },
            ReviewerExpertise.DOMAIN_SPECIALIST: {
                PeerReviewCriteria.SIGNIFICANCE: 0.25,
                PeerReviewCriteria.NOVELTY: 0.2,
                PeerReviewCriteria.CONTRIBUTION: 0.2,
                PeerReviewCriteria.LITERATURE_REVIEW: 0.15,
                PeerReviewCriteria.METHODOLOGY: 0.1,
                PeerReviewCriteria.CLARITY: 0.1
            },
            ReviewerExpertise.STATISTICAL_EXPERT: {
                PeerReviewCriteria.STATISTICAL_VALIDITY: 0.4,
                PeerReviewCriteria.METHODOLOGY: 0.25,
                PeerReviewCriteria.REPRODUCIBILITY: 0.2,
                PeerReviewCriteria.CLARITY: 0.1,
                PeerReviewCriteria.SIGNIFICANCE: 0.05
            },
            ReviewerExpertise.WRITING_SPECIALIST: {
                PeerReviewCriteria.CLARITY: 0.3,
                PeerReviewCriteria.PRESENTATION: 0.25,
                PeerReviewCriteria.LITERATURE_REVIEW: 0.2,
                PeerReviewCriteria.CONTRIBUTION: 0.15,
                PeerReviewCriteria.METHODOLOGY: 0.1
            },
            ReviewerExpertise.ETHICS_REVIEWER: {
                PeerReviewCriteria.ETHICAL_CONSIDERATIONS: 0.4,
                PeerReviewCriteria.METHODOLOGY: 0.2,
                PeerReviewCriteria.SIGNIFICANCE: 0.15,
                PeerReviewCriteria.CLARITY: 0.15,
                PeerReviewCriteria.REPRODUCIBILITY: 0.1
            }
        }
    
    def _initialize_review_templates(self) -> Dict[str, Dict[str, str]]:
        """初始化评议模板"""
        return {
            "constructive": {
                "opening": "This manuscript addresses an important topic and makes several valuable contributions to the field.",
                "strength_intro": "The strengths of this work include:",
                "weakness_intro": "Areas that could be strengthened include:",
                "suggestion_intro": "I suggest the following improvements:",
                "closing": "With these revisions, this work would make a solid contribution to the literature."
            },
            "critical": {
                "opening": "This manuscript tackles a relevant research question, but several significant issues need to be addressed.",
                "strength_intro": "The paper has some notable strengths:",
                "weakness_intro": "However, there are several concerns:",
                "suggestion_intro": "The following revisions are necessary:",
                "closing": "These issues must be thoroughly addressed before the manuscript can be considered for publication."
            },
            "balanced": {
                "opening": "This manuscript presents interesting findings on an important topic.",
                "strength_intro": "The work demonstrates several strengths:",
                "weakness_intro": "There are also some areas for improvement:",
                "suggestion_intro": "I recommend the following enhancements:",
                "closing": "Overall, this is a solid contribution that would benefit from the suggested revisions."
            },
            "encouraging": {
                "opening": "This manuscript shows promise and addresses a timely research question.",
                "strength_intro": "The authors should be commended for:",
                "weakness_intro": "Some aspects could be enhanced:",
                "suggestion_intro": "Consider the following suggestions to strengthen the work:",
                "closing": "This research has potential and I encourage the authors to continue developing these ideas."
            }
        }
    
    async def assign_reviewers(self, manuscript_sections: List[ManuscriptSection],
                             research_domain: str,
                             num_reviewers: int = 3) -> ReviewAssignment:
        """分配评议者"""
        try:
            logger.info(f"Assigning {num_reviewers} reviewers for {research_domain} manuscript")
            
            # 根据研究领域和稿件特点选择合适的评议者
            suitable_reviewers = await self._select_suitable_reviewers(
                manuscript_sections, research_domain, num_reviewers
            )
            
            # 创建评议分配
            assignment = ReviewAssignment(
                manuscript_id=f"MS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                reviewer_profiles=suitable_reviewers,
                review_deadline=datetime.now() + timedelta(days=21),  # 3周评议期
                review_type="initial",
                special_instructions=await self._generate_special_instructions(manuscript_sections)
            )
            
            logger.info(f"Assigned reviewers: {[r.name for r in suitable_reviewers]}")
            return assignment
            
        except Exception as e:
            logger.error(f"Error assigning reviewers: {e}")
            raise
    
    async def _select_suitable_reviewers(self, manuscript_sections: List[ManuscriptSection],
                                       research_domain: str,
                                       num_reviewers: int) -> List[ReviewerProfile]:
        """选择合适的评议者"""
        # 分析稿件需求
        manuscript_needs = await self._analyze_manuscript_needs(manuscript_sections)
        
        # 为每个评议者计算适合度分数
        reviewer_scores = []
        for reviewer in self.reviewer_database:
            score = await self._calculate_reviewer_suitability(reviewer, manuscript_needs, research_domain)
            reviewer_scores.append((reviewer, score))
        
        # 按分数排序并选择多样化的评议者组合
        reviewer_scores.sort(key=lambda x: x[1], reverse=True)
        
        selected_reviewers = []
        expertise_covered = set()
        
        for reviewer, score in reviewer_scores:
            if len(selected_reviewers) >= num_reviewers:
                break
            
            # 确保专业领域多样性
            reviewer_expertise = set(reviewer.expertise_areas)
            if not selected_reviewers or not reviewer_expertise.issubset(expertise_covered):
                selected_reviewers.append(reviewer)
                expertise_covered.update(reviewer_expertise)
        
        # 如果还需要更多评议者，按分数补充
        while len(selected_reviewers) < num_reviewers and len(selected_reviewers) < len(self.reviewer_database):
            for reviewer, score in reviewer_scores:
                if reviewer not in selected_reviewers:
                    selected_reviewers.append(reviewer)
                    break
        
        return selected_reviewers
    
    async def _analyze_manuscript_needs(self, manuscript_sections: List[ManuscriptSection]) -> Dict[str, float]:
        """分析稿件评议需求"""
        needs = {
            "methodology_complexity": 0.0,
            "statistical_analysis": 0.0,
            "writing_quality": 0.0,
            "ethical_considerations": 0.0,
            "domain_expertise": 0.0,
            "interdisciplinary": 0.0
        }
        
        for section in manuscript_sections:
            content_lower = section.content.lower()
            
            # 方法论复杂度
            methodology_indicators = ["experimental", "statistical", "analysis", "model", "algorithm"]
            methodology_score = sum(1 for indicator in methodology_indicators if indicator in content_lower)
            needs["methodology_complexity"] += methodology_score / len(methodology_indicators)
            
            # 统计分析需求
            stats_indicators = ["statistical", "significance", "correlation", "regression", "anova"]
            stats_score = sum(1 for indicator in stats_indicators if indicator in content_lower)
            needs["statistical_analysis"] += stats_score / len(stats_indicators)
            
            # 写作质量评估需求
            writing_indicators = ["unclear", "confusing", "poorly written", "grammar"]
            writing_issues = sum(1 for indicator in writing_indicators if indicator in content_lower)
            needs["writing_quality"] += 1.0 if writing_issues > 0 else 0.5
            
            # 伦理考虑
            ethics_indicators = ["ethical", "consent", "approval", "participants", "human subjects"]
            ethics_score = sum(1 for indicator in ethics_indicators if indicator in content_lower)
            needs["ethical_considerations"] += ethics_score / len(ethics_indicators)
            
            # 跨学科性
            interdisciplinary_indicators = ["interdisciplinary", "multidisciplinary", "cross-field"]
            interdisciplinary_score = sum(1 for indicator in interdisciplinary_indicators if indicator in content_lower)
            needs["interdisciplinary"] += interdisciplinary_score / len(interdisciplinary_indicators)
        
        # 标准化分数
        num_sections = len(manuscript_sections)
        for key in needs:
            needs[key] = min(needs[key] / num_sections, 1.0)
        
        needs["domain_expertise"] = 0.8  # 默认需要领域专业知识
        
        return needs
    
    async def _calculate_reviewer_suitability(self, reviewer: ReviewerProfile,
                                            manuscript_needs: Dict[str, float],
                                            research_domain: str) -> float:
        """计算评议者适合度"""
        score = 0.0
        
        # 专业领域匹配
        expertise_match = 0.0
        for expertise in reviewer.expertise_areas:
            if expertise == ReviewerExpertise.METHODOLOGY_EXPERT:
                expertise_match += manuscript_needs["methodology_complexity"] * 0.3
            elif expertise == ReviewerExpertise.STATISTICAL_EXPERT:
                expertise_match += manuscript_needs["statistical_analysis"] * 0.3
            elif expertise == ReviewerExpertise.WRITING_SPECIALIST:
                expertise_match += manuscript_needs["writing_quality"] * 0.2
            elif expertise == ReviewerExpertise.ETHICS_REVIEWER:
                expertise_match += manuscript_needs["ethical_considerations"] * 0.2
            elif expertise == ReviewerExpertise.DOMAIN_SPECIALIST:
                expertise_match += manuscript_needs["domain_expertise"] * 0.4
            elif expertise == ReviewerExpertise.INTERDISCIPLINARY_EXPERT:
                expertise_match += manuscript_needs["interdisciplinary"] * 0.3
        
        score += expertise_match
        
        # 经验水平权重
        experience_weights = {"junior": 0.7, "mid-career": 0.85, "senior": 1.0}
        score *= experience_weights.get(reviewer.experience_level, 0.8)
        
        # 评议彻底性
        score *= reviewer.review_thoroughness
        
        # 添加一些随机性以模拟现实情况
        score += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, score))
    
    async def _generate_special_instructions(self, manuscript_sections: List[ManuscriptSection]) -> List[str]:
        """生成特殊评议指导"""
        instructions = []
        
        # 基于稿件内容生成指导
        total_word_count = sum(section.word_count for section in manuscript_sections)
        
        if total_word_count > 8000:
            instructions.append("Please pay special attention to the conciseness and focus of the manuscript")
        
        # 检查是否有方法论章节
        has_methodology = any("method" in section.section_name.lower() for section in manuscript_sections)
        if has_methodology:
            instructions.append("Please evaluate the methodological rigor and reproducibility carefully")
        
        # 检查是否有结果章节
        has_results = any("result" in section.section_name.lower() for section in manuscript_sections)
        if has_results:
            instructions.append("Please assess the statistical analysis and interpretation of results")
        
        instructions.append("Please provide constructive feedback to help improve the manuscript")
        
        return instructions
    
    async def conduct_peer_review(self, assignment: ReviewAssignment,
                                manuscript_sections: List[ManuscriptSection]) -> List[PeerReviewFeedback]:
        """进行同行评议"""
        try:
            logger.info(f"Conducting peer review with {len(assignment.reviewer_profiles)} reviewers")
            
            reviews = []
            
            for reviewer in assignment.reviewer_profiles:
                review = await self._generate_individual_review(reviewer, manuscript_sections)
                reviews.append(review)
            
            logger.info(f"Generated {len(reviews)} peer reviews")
            return reviews
            
        except Exception as e:
            logger.error(f"Error conducting peer review: {e}")
            return []
    
    async def _generate_individual_review(self, reviewer: ReviewerProfile,
                                        manuscript_sections: List[ManuscriptSection]) -> PeerReviewFeedback:
        """生成个人评议"""
        try:
            # 根据评议者特点评估各项标准
            criteria_scores = await self._evaluate_criteria(reviewer, manuscript_sections)
            
            # 计算总体分数
            overall_score = await self._calculate_overall_score(reviewer, criteria_scores)
            
            # 生成评议内容
            strengths = await self._identify_manuscript_strengths(reviewer, manuscript_sections)
            weaknesses = await self._identify_manuscript_weaknesses(reviewer, manuscript_sections)
            suggestions = await self._generate_improvement_suggestions(reviewer, weaknesses)
            detailed_comments = await self._generate_detailed_comments(reviewer, manuscript_sections)
            
            # 确定推荐决定
            recommendation = await self._determine_recommendation(overall_score, len(weaknesses))
            
            # 评议者信心水平
            confidence_level = await self._calculate_confidence_level(reviewer, manuscript_sections)
            
            review = PeerReviewFeedback(
                reviewer_id=reviewer.reviewer_id,
                reviewer_expertise=[exp.value for exp in reviewer.expertise_areas],
                overall_score=overall_score,
                criteria_scores=criteria_scores,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions,
                recommendation=recommendation,
                detailed_comments=detailed_comments,
                confidence_level=confidence_level
            )
            
            return review
            
        except Exception as e:
            logger.error(f"Error generating individual review: {e}")
            raise
    
    async def _evaluate_criteria(self, reviewer: ReviewerProfile,
                               manuscript_sections: List[ManuscriptSection]) -> Dict[PeerReviewCriteria, float]:
        """评估各项标准"""
        scores = {}
        
        # 获取评议者的权重偏好
        weights = {}
        for expertise in reviewer.expertise_areas:
            if expertise in self.review_criteria_weights:
                for criterion, weight in self.review_criteria_weights[expertise].items():
                    weights[criterion] = max(weights.get(criterion, 0), weight)
        
        # 为每个标准生成分数
        for criterion in PeerReviewCriteria:
            base_score = await self._evaluate_single_criterion(criterion, manuscript_sections)
            
            # 根据评议者特点调整分数
            if criterion in weights:
                # 专业领域的评议者更严格
                if weights[criterion] > 0.2:
                    base_score *= random.uniform(0.8, 1.0)
                else:
                    base_score *= random.uniform(0.9, 1.1)
            
            # 根据评议者风格调整
            if reviewer.review_style == "critical":
                base_score *= random.uniform(0.7, 0.9)
            elif reviewer.review_style == "encouraging":
                base_score *= random.uniform(1.0, 1.2)
            
            scores[criterion] = max(0.0, min(1.0, base_score))
        
        return scores
    
    async def _evaluate_single_criterion(self, criterion: PeerReviewCriteria,
                                       manuscript_sections: List[ManuscriptSection]) -> float:
        """评估单个标准"""
        # 简化的标准评估（实际实现中会更复杂）
        base_scores = {
            PeerReviewCriteria.NOVELTY: random.uniform(0.6, 0.9),
            PeerReviewCriteria.SIGNIFICANCE: random.uniform(0.5, 0.8),
            PeerReviewCriteria.METHODOLOGY: random.uniform(0.6, 0.85),
            PeerReviewCriteria.CLARITY: random.uniform(0.7, 0.9),
            PeerReviewCriteria.REPRODUCIBILITY: random.uniform(0.5, 0.8),
            PeerReviewCriteria.ETHICAL_CONSIDERATIONS: random.uniform(0.8, 0.95),
            PeerReviewCriteria.STATISTICAL_VALIDITY: random.uniform(0.6, 0.85),
            PeerReviewCriteria.LITERATURE_REVIEW: random.uniform(0.7, 0.9),
            PeerReviewCriteria.CONTRIBUTION: random.uniform(0.6, 0.8),
            PeerReviewCriteria.PRESENTATION: random.uniform(0.7, 0.9)
        }
        
        return base_scores.get(criterion, 0.7)
    
    async def _calculate_overall_score(self, reviewer: ReviewerProfile,
                                     criteria_scores: Dict[PeerReviewCriteria, float]) -> float:
        """计算总体分数"""
        # 根据评议者专业领域加权平均
        weights = {}
        total_weight = 0
        
        for expertise in reviewer.expertise_areas:
            if expertise in self.review_criteria_weights:
                for criterion, weight in self.review_criteria_weights[expertise].items():
                    weights[criterion] = max(weights.get(criterion, 0), weight)
                    total_weight += weight
        
        if not weights:
            # 如果没有特定权重，使用平均值
            return sum(criteria_scores.values()) / len(criteria_scores)
        
        # 加权平均
        weighted_sum = sum(criteria_scores[criterion] * weights.get(criterion, 0.1) 
                          for criterion in criteria_scores)
        
        return weighted_sum / max(sum(weights.values()), 1.0)
    
    async def _identify_manuscript_strengths(self, reviewer: ReviewerProfile,
                                           manuscript_sections: List[ManuscriptSection]) -> List[str]:
        """识别稿件优点"""
        strengths = []
        
        # 基于评议者专业领域生成优点
        for expertise in reviewer.expertise_areas:
            if expertise == ReviewerExpertise.METHODOLOGY_EXPERT:
                strengths.extend([
                    "The research design is well-structured and appropriate for the research questions",
                    "The methodology section provides sufficient detail for replication"
                ])
            elif expertise == ReviewerExpertise.WRITING_SPECIALIST:
                strengths.extend([
                    "The manuscript is generally well-written and clearly structured",
                    "The literature review is comprehensive and well-integrated"
                ])
            elif expertise == ReviewerExpertise.DOMAIN_SPECIALIST:
                strengths.extend([
                    "The research addresses an important gap in the literature",
                    "The findings contribute meaningfully to the field"
                ])
        
        # 根据评议者风格调整
        if reviewer.review_style == "encouraging":
            strengths.append("The authors demonstrate a good understanding of the research area")
        
        return strengths[:4]  # 限制优点数量
    
    async def _identify_manuscript_weaknesses(self, reviewer: ReviewerProfile,
                                            manuscript_sections: List[ManuscriptSection]) -> List[str]:
        """识别稿件弱点"""
        weaknesses = []
        
        # 基于评议者专业领域和偏见生成弱点
        for expertise in reviewer.expertise_areas:
            if expertise == ReviewerExpertise.METHODOLOGY_EXPERT:
                if "methodological_purist" in reviewer.bias_tendencies:
                    weaknesses.extend([
                        "The sample size may be insufficient for the proposed analyses",
                        "Some methodological choices need better justification"
                    ])
            elif expertise == ReviewerExpertise.STATISTICAL_EXPERT:
                weaknesses.extend([
                    "The statistical analysis could be more robust",
                    "Effect sizes should be reported alongside significance tests"
                ])
            elif expertise == ReviewerExpertise.WRITING_SPECIALIST:
                weaknesses.extend([
                    "Some sections could be more concise",
                    "The discussion could better integrate the findings with existing literature"
                ])
        
        # 根据评议者风格调整
        if reviewer.review_style == "critical":
            weaknesses.append("The theoretical framework needs strengthening")
        
        return weaknesses[:5]  # 限制弱点数量
    
    async def _generate_improvement_suggestions(self, reviewer: ReviewerProfile,
                                              weaknesses: List[str]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        for weakness in weaknesses:
            if "sample size" in weakness.lower():
                suggestions.append("Consider conducting a power analysis to justify the sample size")
            elif "statistical" in weakness.lower():
                suggestions.append("Include confidence intervals and effect sizes in the results")
            elif "concise" in weakness.lower():
                suggestions.append("Consider condensing repetitive sections to improve readability")
            elif "literature" in weakness.lower():
                suggestions.append("Expand the discussion of how findings relate to existing theories")
            elif "theoretical" in weakness.lower():
                suggestions.append("Strengthen the theoretical foundation in the introduction")
        
        # 添加通用建议
        suggestions.extend([
            "Consider addressing the limitations more thoroughly",
            "Provide more specific implications for future research"
        ])
        
        return suggestions[:6]  # 限制建议数量
    
    async def _generate_detailed_comments(self, reviewer: ReviewerProfile,
                                        manuscript_sections: List[ManuscriptSection]) -> Dict[str, str]:
        """生成详细评论"""
        comments = {}
        
        for section in manuscript_sections:
            section_name = section.section_name.lower()
            
            if "abstract" in section_name:
                comments["Abstract"] = "The abstract effectively summarizes the study, though it could be more specific about the key findings."
            elif "introduction" in section_name:
                comments["Introduction"] = "The introduction provides good context, but the research gap could be articulated more clearly."
            elif "method" in section_name:
                comments["Methodology"] = "The methodology is generally sound, though some procedures need more detailed description."
            elif "result" in section_name:
                comments["Results"] = "The results are presented clearly, but additional statistical details would strengthen the analysis."
            elif "discussion" in section_name:
                comments["Discussion"] = "The discussion interprets the findings well, but could better address study limitations."
        
        return comments
    
    async def _determine_recommendation(self, overall_score: float, num_weaknesses: int) -> str:
        """确定推荐决定"""
        if overall_score >= 0.8 and num_weaknesses <= 2:
            return ReviewDecision.ACCEPT.value
        elif overall_score >= 0.7 and num_weaknesses <= 3:
            return ReviewDecision.MINOR_REVISION.value
        elif overall_score >= 0.5 and num_weaknesses <= 5:
            return ReviewDecision.MAJOR_REVISION.value
        else:
            return ReviewDecision.REJECT.value
    
    async def _calculate_confidence_level(self, reviewer: ReviewerProfile,
                                        manuscript_sections: List[ManuscriptSection]) -> float:
        """计算信心水平"""
        base_confidence = 0.8
        
        # 根据经验水平调整
        experience_multipliers = {"junior": 0.7, "mid-career": 0.85, "senior": 1.0}
        base_confidence *= experience_multipliers.get(reviewer.experience_level, 0.8)
        
        # 根据专业匹配度调整
        if len(reviewer.expertise_areas) >= 2:
            base_confidence *= 1.1
        
        # 添加随机变化
        confidence = base_confidence * random.uniform(0.9, 1.1)
        
        return max(0.5, min(1.0, confidence))
    
    async def synthesize_reviews(self, reviews: List[PeerReviewFeedback]) -> Dict[str, Any]:
        """综合评议结果"""
        try:
            logger.info(f"Synthesizing {len(reviews)} peer reviews")
            
            if not reviews:
                return {"error": "No reviews to synthesize"}
            
            # 计算平均分数
            avg_overall_score = sum(review.overall_score for review in reviews) / len(reviews)
            
            # 综合标准分数
            criteria_averages = {}
            for criterion in PeerReviewCriteria:
                scores = [review.criteria_scores.get(criterion, 0) for review in reviews]
                criteria_averages[criterion.value] = sum(scores) / len(scores)
            
            # 统计推荐决定
            recommendations = [review.recommendation for review in reviews]
            recommendation_counts = {}
            for rec in recommendations:
                recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
            
            # 确定最终决定
            final_decision = max(recommendation_counts.items(), key=lambda x: x[1])[0]
            
            # 收集所有优点和缺点
            all_strengths = []
            all_weaknesses = []
            all_suggestions = []
            
            for review in reviews:
                all_strengths.extend(review.strengths)
                all_weaknesses.extend(review.weaknesses)
                all_suggestions.extend(review.suggestions)
            
            # 去重并排序
            unique_strengths = list(set(all_strengths))
            unique_weaknesses = list(set(all_weaknesses))
            unique_suggestions = list(set(all_suggestions))
            
            synthesis = {
                "overall_assessment": {
                    "average_score": round(avg_overall_score, 2),
                    "final_decision": final_decision,
                    "reviewer_consensus": len(set(recommendations)) == 1
                },
                "criteria_scores": {k: round(v, 2) for k, v in criteria_averages.items()},
                "recommendation_distribution": recommendation_counts,
                "consolidated_feedback": {
                    "strengths": unique_strengths[:8],
                    "weaknesses": unique_weaknesses[:8],
                    "suggestions": unique_suggestions[:10]
                },
                "reviewer_details": [
                    {
                        "reviewer_id": review.reviewer_id,
                        "expertise": review.reviewer_expertise,
                        "score": review.overall_score,
                        "recommendation": review.recommendation,
                        "confidence": review.confidence_level
                    }
                    for review in reviews
                ]
            }
            
            logger.info(f"Review synthesis completed. Final decision: {final_decision}")
            return synthesis
            
        except Exception as e:
            logger.error(f"Error synthesizing reviews: {e}")
            return {"error": "Error synthesizing reviews"}
    
    async def generate_review_report(self, synthesis: Dict[str, Any]) -> str:
        """生成评议报告"""
        try:
            logger.info("Generating peer review report")
            
            if "error" in synthesis:
                return f"Error: {synthesis['error']}"
            
            overall = synthesis["overall_assessment"]
            criteria = synthesis["criteria_scores"]
            feedback = synthesis["consolidated_feedback"]
            
            report_sections = [
                "# Peer Review Report",
                "",
                f"**Overall Score**: {overall['average_score']}/1.00",
                f"**Final Decision**: {overall['final_decision'].replace('_', ' ').title()}",
                f"**Reviewer Consensus**: {'Yes' if overall['reviewer_consensus'] else 'No'}",
                "",
                "## Criteria Scores",
                ""
            ]
            
            for criterion, score in criteria.items():
                report_sections.append(f"- **{criterion.replace('_', ' ').title()}**: {score}/1.00")
            
            report_sections.extend([
                "",
                "## Reviewer Recommendations",
                ""
            ])
            
            for decision, count in synthesis["recommendation_distribution"].items():
                report_sections.append(f"- **{decision.replace('_', ' ').title()}**: {count} reviewer(s)")
            
            report_sections.extend([
                "",
                "## Consolidated Feedback",
                "",
                "### Strengths",
                ""
            ])
            
            for strength in feedback["strengths"]:
                report_sections.append(f"✅ {strength}")
            
            report_sections.extend([
                "",
                "### Areas for Improvement",
                ""
            ])
            
            for weakness in feedback["weaknesses"]:
                report_sections.append(f"⚠️ {weakness}")
            
            report_sections.extend([
                "",
                "### Suggestions",
                ""
            ])
            
            for suggestion in feedback["suggestions"]:
                report_sections.append(f"💡 {suggestion}")
            
            report_sections.extend([
                "",
                "## Reviewer Details",
                ""
            ])
            
            for reviewer in synthesis["reviewer_details"]:
                report_sections.extend([
                    f"**Reviewer {reviewer['reviewer_id']}**",
                    f"- Expertise: {', '.join(reviewer['expertise'])}",
                    f"- Score: {reviewer['score']}/1.00",
                    f"- Recommendation: {reviewer['recommendation'].replace('_', ' ').title()}",
                    f"- Confidence: {reviewer['confidence']:.2f}/1.00",
                    ""
                ])
            
            report = "\n".join(report_sections)
            
            logger.info("Peer review report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating review report: {e}")
            return "Error generating peer review report"