"""
@Time: 2025-08-03
@Author: DAIP-LIVE
@File: smart_reviewer_allocator.py
@Description: V0.3.5 智能评审分配器 - 基于专业匹配和工作负载的评审员智能分配
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict, Counter
import heapq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import threading
import time

from ..core_services.knowledge_retrieval_service import KnowledgeRetrievalService
from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
from ..core_services.memory_agent import MemAgent


class ReviewerSpecialization(Enum):
    """评审员专业领域"""
    AI_ML = "ai_ml"                    # 人工智能/机器学习
    SOFTWARE_ENGINEERING = "software_engineering"  # 软件工程
    DATA_SCIENCE = "data_science"       # 数据科学
    RESEARCH_METHODOLOGY = "research_methodology"  # 研究方法
    DOMAIN_EXPERT = "domain_expert"     # 领域专家
    TECHNICAL_WRITING = "technical_writing"  # 技术写作
    ETHICS_COMPLIANCE = "ethics_compliance"  # 伦理合规
    USER_EXPERIENCE = "user_experience"  # 用户体验


class ExperienceLevel(Enum):
    """经验等级"""
    JUNIOR = "junior"          # 初级 (1-3年)
    INTERMEDIATE = "intermediate"  # 中级 (3-5年)
    SENIOR = "senior"          # 高级 (5-10年)
    EXPERT = "expert"          # 专家 (10年以上)


class AllocationPriority(Enum):
    """分配优先级"""
    HIGH = "high"              # 高优先级
    MEDIUM = "medium"          # 中等优先级
    LOW = "low"               # 低优先级


@dataclass
class ReviewRequest:
    """评审请求"""
    id: str
    title: str
    content: str
    content_type: str
    author: str
    submission_date: datetime
    deadline: datetime
    required_reviewers: int
    expertise_areas: List[str]
    complexity_level: str
    priority: AllocationPriority
    keywords: List[str]
    metadata: Dict[str, Any] = None


@dataclass
class ReviewerProfile:
    """评审员档案"""
    id: str
    name: str
    email: str
    specializations: List[ReviewerSpecialization]
    experience_level: ExperienceLevel
    expertise_keywords: List[str]
    availability_score: float  # 0-1
    current_workload: int      # 当前评审任务数
    max_workload: int         # 最大工作负载
    review_history: List[Dict]  # 评审历史
    performance_metrics: Dict[str, float]
    response_time_avg: float   # 平均响应时间(小时)
    quality_score: float      # 历史质量评分
    conflicts_of_interest: List[str]  # 利益冲突
    last_active: datetime
    metadata: Dict[str, Any] = None


@dataclass
class AllocationCriteria:
    """分配标准"""
    min_expertise_match: float = 0.7      # 最小专业匹配度
    max_workload_threshold: float = 0.8   # 最大工作负载阈值
    min_quality_score: float = 0.6        # 最小质量分数
    max_response_time: float = 24.0        # 最大响应时间(小时)
    consider_diversity: bool = True        # 是否考虑多样性
    balance_workload: bool = True          # 是否平衡工作负载
    avoid_conflicts: bool = True           # 是否避免冲突


@dataclass
class AllocationResult:
    """分配结果"""
    review_request_id: str
    allocated_reviewers: List[ReviewerProfile]
    allocation_scores: List[float]
    allocation_reasons: List[str]
    total_candidates: int
    selection_process: str
    confidence_score: float
    metadata: Dict[str, Any] = None


class SmartReviewerAllocator:
    """智能评审分配器"""
    
    def __init__(self, knowledge_retrieval: KnowledgeRetrievalService,
                 sskg_manager: EnhancedSSKGManager,
                 memory_agent: MemAgent):
        self.knowledge_retrieval = knowledge_retrieval
        self.sskg_manager = sskg_manager
        self.memory_agent = memory_agent
        self.logger = logging.getLogger(__name__)
        
        # 评审员数据库
        self.reviewer_profiles = {}
        self.allocation_history = []
        
        # 专业领域关键词
        self.domain_keywords = {
            ReviewerSpecialization.AI_ML: [
                "人工智能", "机器学习", "深度学习", "神经网络", "算法", "模型",
                "AI", "ML", "DL", "neural network", "algorithm", "model"
            ],
            ReviewerSpecialization.SOFTWARE_ENGINEERING: [
                "软件工程", "代码", "架构", "设计模式", "测试", "部署",
                "software", "code", "architecture", "design pattern", "testing"
            ],
            ReviewerSpecialization.DATA_SCIENCE: [
                "数据科学", "数据分析", "统计", "可视化", "大数据",
                "data science", "data analysis", "statistics", "visualization"
            ],
            ReviewerSpecialization.RESEARCH_METHODOLOGY: [
                "研究方法", "实验设计", "统计分析", "假设检验", "学术写作",
                "research methodology", "experimental design", "statistical analysis"
            ],
            ReviewerSpecialization.DOMAIN_EXPERT: [
                "领域专家", "行业经验", "实践应用", "案例研究", "最佳实践",
                "domain expert", "industry experience", "practical application"
            ]
        }
        
        # 初始化向量化器
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # 加载评审员数据
        self._load_reviewer_profiles()
        
        # 启动后台优化任务
        self._start_background_tasks()
    
    async def allocate_reviewers(self, 
                                review_request: ReviewRequest,
                                criteria: AllocationCriteria = None) -> AllocationResult:
        """智能分配评审员"""
        try:
            if criteria is None:
                criteria = AllocationCriteria()
            
            self.logger.info(f"开始分配评审员: {review_request.id}")
            
            # 1. 候选评审员筛选
            candidates = await self._filter_candidates(review_request, criteria)
            
            # 2. 专业匹配度计算
            expertise_scores = await self._calculate_expertise_scores(review_request, candidates)
            
            # 3. 工作负载评估
            workload_scores = self._calculate_workload_scores(candidates, criteria)
            
            # 4. 质量和性能评估
            quality_scores = self._calculate_quality_scores(candidates, criteria)
            
            # 5. 冲突检测
            conflict_scores = self._calculate_conflict_scores(review_request, candidates)
            
            # 6. 综合评分和排序
            final_scores = self._calculate_final_scores(
                expertise_scores, workload_scores, quality_scores, conflict_scores
            )
            
            # 7. 多样性考虑
            diversified_candidates = self._apply_diversity_selection(
                candidates, final_scores, review_request.required_reviewers, criteria
            )
            
            # 8. 生成分配结果
            allocation_result = AllocationResult(
                review_request_id=review_request.id,
                allocated_reviewers=diversified_candidates,
                allocation_scores=[final_scores.get(r.id, 0.0) for r in diversified_candidates],
                allocation_reasons=self._generate_allocation_reasons(diversified_candidates, review_request),
                total_candidates=len(candidates),
                selection_process="intelligent_allocation",
                confidence_score=self._calculate_confidence_score(diversified_candidates, final_scores),
                metadata={
                    "criteria_used": asdict(criteria),
                    "allocation_time": datetime.now().isoformat(),
                    "candidate_count": len(candidates)
                }
            )
            
            # 9. 更新评审员工作负载
            await self._update_reviewer_workload(diversified_candidates)
            
            # 10. 记录分配历史
            self._record_allocation(allocation_result)
            
            self.logger.info(f"评审员分配完成: {review_request.id} -> {len(diversified_candidates)}位评审员")
            
            return allocation_result
            
        except Exception as e:
            self.logger.error(f"评审员分配失败: {e}")
            # 返回默认结果
            return AllocationResult(
                review_request_id=review_request.id,
                allocated_reviewers=[],
                allocation_scores=[],
                allocation_reasons=[f"分配失败: {str(e)}"],
                total_candidates=0,
                selection_process="fallback",
                confidence_score=0.0,
                metadata={"error": str(e)}
            )
    
    async def _filter_candidates(self, 
                               review_request: ReviewRequest,
                               criteria: AllocationCriteria) -> List[ReviewerProfile]:
        """筛选候选评审员"""
        try:
            candidates = []
            
            for reviewer_id, reviewer in self.reviewer_profiles.items():
                # 基础可用性检查
                if not self._is_reviewer_available(reviewer, criteria):
                    continue
                
                # 利益冲突检查
                if criteria.avoid_conflicts and self._has_conflict_of_interest(review_request, reviewer):
                    continue
                
                # 专业领域匹配检查
                expertise_match = await self._check_expertise_match(review_request, reviewer)
                if expertise_match < criteria.min_expertise_match:
                    continue
                
                candidates.append(reviewer)
            
            self.logger.info(f"筛选出 {len(candidates)} 位候选评审员")
            return candidates
            
        except Exception as e:
            self.logger.error(f"筛选候选评审员失败: {e}")
            return []
    
    def _is_reviewer_available(self, reviewer: ReviewerProfile, criteria: AllocationCriteria) -> bool:
        """检查评审员可用性"""
        try:
            # 工作负载检查
            workload_ratio = reviewer.current_workload / reviewer.max_workload
            if workload_ratio > criteria.max_workload_threshold:
                return False
            
            # 质量分数检查
            if reviewer.quality_score < criteria.min_quality_score:
                return False
            
            # 响应时间检查
            if reviewer.response_time_avg > criteria.max_response_time:
                return False
            
            # 活跃度检查
            days_inactive = (datetime.now() - reviewer.last_active).days
            if days_inactive > 30:  # 超过30天未活跃
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查评审员可用性失败: {e}")
            return False
    
    def _has_conflict_of_interest(self, review_request: ReviewRequest, reviewer: ReviewerProfile) -> bool:
        """检查利益冲突"""
        try:
            # 作者冲突
            if review_request.author.lower() in [conflict.lower() for conflict in reviewer.conflicts_of_interest]:
                return True
            
            # 机构冲突
            author_institution = review_request.metadata.get("institution", "").lower()
            for conflict in reviewer.conflicts_of_interest:
                if conflict.lower() in author_institution:
                    return True
            
            # 项目冲突
            project_id = review_request.metadata.get("project_id", "")
            if project_id and any(project_id in conflict for conflict in reviewer.conflicts_of_interest):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"检查利益冲突失败: {e}")
            return False
    
    async def _check_expertise_match(self, review_request: ReviewRequest, reviewer: ReviewerProfile) -> float:
        """检查专业匹配度"""
        try:
            # 提取关键词
            request_keywords = set(review_request.keywords + review_request.expertise_areas)
            reviewer_keywords = set(reviewer.expertise_keywords)
            
            if not request_keywords or not reviewer_keywords:
                return 0.0
            
            # 计算关键词重叠度
            intersection = request_keywords & reviewer_keywords
            union = request_keywords | reviewer_keywords
            
            jaccard_similarity = len(intersection) / len(union) if union else 0.0
            
            # 专业领域匹配
            specialization_match = 0.0
            for spec in reviewer.specializations:
                spec_keywords = set(self.domain_keywords.get(spec, []))
                if spec_keywords:
                    spec_intersection = request_keywords & spec_keywords
                    spec_union = request_keywords | spec_keywords
                    spec_similarity = len(spec_intersection) / len(spec_union) if spec_union else 0.0
                    specialization_match = max(specialization_match, spec_similarity)
            
            # 综合匹配度
            final_match = (jaccard_similarity * 0.6 + specialization_match * 0.4)
            
            return min(1.0, final_match)
            
        except Exception as e:
            self.logger.error(f"检查专业匹配度失败: {e}")
            return 0.0
    
    async def _calculate_expertise_scores(self, 
                                       review_request: ReviewRequest,
                                       candidates: List[ReviewerProfile]) -> Dict[str, float]:
        """计算专业匹配分数"""
        try:
            scores = {}
            
            for candidate in candidates:
                # 使用语义相似度计算
                expertise_score = await self._check_expertise_match(review_request, candidate)
                
                # 经验等级加成
                experience_bonus = {
                    ExperienceLevel.JUNIOR: 0.0,
                    ExperienceLevel.INTERMEDIATE: 0.1,
                    ExperienceLevel.SENIOR: 0.2,
                    ExperienceLevel.EXPERT: 0.3
                }.get(candidate.experience_level, 0.0)
                
                # 历史相关评审加成
                relevance_bonus = self._calculate_relevance_bonus(review_request, candidate)
                
                final_score = min(1.0, expertise_score + experience_bonus + relevance_bonus)
                scores[candidate.id] = final_score
            
            return scores
            
        except Exception as e:
            self.logger.error(f"计算专业匹配分数失败: {e}")
            return {candidate.id: 0.0 for candidate in candidates}
    
    def _calculate_relevance_bonus(self, review_request: ReviewRequest, reviewer: ReviewerProfile) -> float:
        """计算相关性加成"""
        try:
            bonus = 0.0
            
            # 检查历史评审中的相关领域
            for review in reviewer.review_history:
                if review.get("domain") in review_request.expertise_areas:
                    bonus += 0.05
            
            # 检查关键词匹配
            for keyword in review_request.keywords:
                if keyword in reviewer.expertise_keywords:
                    bonus += 0.03
            
            return min(0.2, bonus)
            
        except Exception as e:
            self.logger.error(f"计算相关性加成失败: {e}")
            return 0.0
    
    def _calculate_workload_scores(self, 
                                 candidates: List[ReviewerProfile],
                                 criteria: AllocationCriteria) -> Dict[str, float]:
        """计算工作负载分数"""
        try:
            scores = {}
            
            for candidate in candidates:
                # 工作负载比例
                workload_ratio = candidate.current_workload / candidate.max_workload
                
                # 工作负载分数 (负载越低分数越高)
                if workload_ratio < 0.3:
                    workload_score = 1.0
                elif workload_ratio < 0.6:
                    workload_score = 0.8
                elif workload_ratio < 0.8:
                    workload_score = 0.6
                else:
                    workload_score = 0.3
                
                # 可用性分数
                availability_score = candidate.availability_score
                
                # 最终工作负载分数
                final_score = (workload_score * 0.7 + availability_score * 0.3)
                scores[candidate.id] = final_score
            
            return scores
            
        except Exception as e:
            self.logger.error(f"计算工作负载分数失败: {e}")
            return {candidate.id: 0.0 for candidate in candidates}
    
    def _calculate_quality_scores(self, 
                                candidates: List[ReviewerProfile],
                                criteria: AllocationCriteria) -> Dict[str, float]:
        """计算质量分数"""
        try:
            scores = {}
            
            for candidate in candidates:
                # 历史质量分数
                quality_score = candidate.quality_score
                
                # 响应时间分数 (响应越快分数越高)
                response_time_score = max(0.0, 1.0 - candidate.response_time_avg / 48.0)
                
                # 完成率分数
                completion_rate = candidate.performance_metrics.get("completion_rate", 0.8)
                
                # 综合质量分数
                final_score = (quality_score * 0.5 + response_time_score * 0.3 + completion_rate * 0.2)
                scores[candidate.id] = final_score
            
            return scores
            
        except Exception as e:
            self.logger.error(f"计算质量分数失败: {e}")
            return {candidate.id: 0.0 for candidate in candidates}
    
    def _calculate_conflict_scores(self, 
                                  review_request: ReviewRequest,
                                  candidates: List[ReviewerProfile]) -> Dict[str, float]:
        """计算冲突分数"""
        try:
            scores = {}
            
            for candidate in candidates:
                # 检查潜在冲突
                has_conflict = self._has_conflict_of_interest(review_request, candidate)
                
                # 冲突分数 (有冲突分数为0，无冲突为1)
                conflict_score = 0.0 if has_conflict else 1.0
                
                scores[candidate.id] = conflict_score
            
            return scores
            
        except Exception as e:
            self.logger.error(f"计算冲突分数失败: {e}")
            return {candidate.id: 1.0 for candidate in candidates}
    
    def _calculate_final_scores(self, 
                              expertise_scores: Dict[str, float],
                              workload_scores: Dict[str, float],
                              quality_scores: Dict[str, float],
                              conflict_scores: Dict[str, float]) -> Dict[str, float]:
        """计算最终综合分数"""
        try:
            final_scores = {}
            
            # 权重设置
            weights = {
                "expertise": 0.4,    # 专业匹配度
                "workload": 0.25,    # 工作负载
                "quality": 0.25,     # 质量表现
                "conflict": 0.1      # 冲突避免
            }
            
            for reviewer_id in expertise_scores.keys():
                final_score = (
                    expertise_scores.get(reviewer_id, 0.0) * weights["expertise"] +
                    workload_scores.get(reviewer_id, 0.0) * weights["workload"] +
                    quality_scores.get(reviewer_id, 0.0) * weights["quality"] +
                    conflict_scores.get(reviewer_id, 0.0) * weights["conflict"]
                )
                
                final_scores[reviewer_id] = final_score
            
            return final_scores
            
        except Exception as e:
            self.logger.error(f"计算最终分数失败: {e}")
            return {}
    
    def _apply_diversity_selection(self, 
                                 candidates: List[ReviewerProfile],
                                 scores: Dict[str, float],
                                 required_count: int,
                                 criteria: AllocationCriteria) -> List[ReviewerProfile]:
        """应用多样性选择"""
        try:
            if not criteria.consider_diversity:
                # 直接选择分数最高的
                sorted_candidates = sorted(candidates, key=lambda x: scores.get(x.id, 0.0), reverse=True)
                return sorted_candidates[:required_count]
            
            # 多样性选择算法
            selected = []
            remaining = candidates.copy()
            
            # 首先选择分数最高的
            if remaining:
                best_candidate = max(remaining, key=lambda x: scores.get(x.id, 0.0))
                selected.append(best_candidate)
                remaining.remove(best_candidate)
            
            # 然后选择多样性补充
            while len(selected) < required_count and remaining:
                # 计算多样性分数
                diversity_scores = []
                for candidate in remaining:
                    diversity_score = self._calculate_diversity_score(candidate, selected)
                    total_score = scores.get(candidate.id, 0.0) * 0.7 + diversity_score * 0.3
                    diversity_scores.append((candidate, total_score))
                
                # 选择多样性分数最高的
                diversity_scores.sort(key=lambda x: x[1], reverse=True)
                next_candidate = diversity_scores[0][0]
                
                selected.append(next_candidate)
                remaining.remove(next_candidate)
            
            return selected
            
        except Exception as e:
            self.logger.error(f"多样性选择失败: {e}")
            # 降级为简单选择
            sorted_candidates = sorted(candidates, key=lambda x: scores.get(x.id, 0.0), reverse=True)
            return sorted_candidates[:required_count]
    
    def _calculate_diversity_score(self, candidate: ReviewerProfile, selected: List[ReviewerProfile]) -> float:
        """计算多样性分数"""
        try:
            if not selected:
                return 0.0
            
            diversity_score = 0.0
            
            # 专业领域多样性
            selected_specializations = set()
            for reviewer in selected:
                selected_specializations.update(reviewer.specializations)
            
            candidate_specializations = set(candidate.specializations)
            new_specializations = candidate_specializations - selected_specializations
            
            diversity_score += len(new_specializations) * 0.1
            
            # 经验等级多样性
            experience_levels = [r.experience_level for r in selected]
            if candidate.experience_level not in experience_levels:
                diversity_score += 0.05
            
            # 机构多样性 (如果有机构信息)
            selected_institutions = set()
            for reviewer in selected:
                institution = reviewer.metadata.get("institution", "")
                if institution:
                    selected_institutions.add(institution)
            
            candidate_institution = candidate.metadata.get("institution", "")
            if candidate_institution and candidate_institution not in selected_institutions:
                diversity_score += 0.05
            
            return min(0.3, diversity_score)
            
        except Exception as e:
            self.logger.error(f"计算多样性分数失败: {e}")
            return 0.0
    
    def _generate_allocation_reasons(self, 
                                  selected_reviewers: List[ReviewerProfile],
                                  review_request: ReviewRequest) -> List[str]:
        """生成分配原因"""
        try:
            reasons = []
            
            for reviewer in selected_reviewers:
                reason_parts = []
                
                # 专业匹配
                expertise_match = " ".join([spec.value for spec in reviewer.specializations])
                reason_parts.append(f"专业领域: {expertise_match}")
                
                # 经验等级
                reason_parts.append(f"经验等级: {reviewer.experience_level.value}")
                
                # 质量评分
                reason_parts.append(f"质量评分: {reviewer.quality_score:.2f}")
                
                # 工作负载
                workload_ratio = reviewer.current_workload / reviewer.max_workload
                reason_parts.append(f"工作负载: {workload_ratio:.1%}")
                
                reasons.append("; ".join(reason_parts))
            
            return reasons
            
        except Exception as e:
            self.logger.error(f"生成分配原因失败: {e}")
            return ["分配原因生成失败"] * len(selected_reviewers)
    
    def _calculate_confidence_score(self, 
                                  selected_reviewers: List[ReviewerProfile],
                                  scores: Dict[str, float]) -> float:
        """计算分配置信度"""
        try:
            if not selected_reviewers:
                return 0.0
            
            # 基于分数分布计算置信度
            selected_scores = [scores.get(r.id, 0.0) for r in selected_reviewers]
            avg_score = sum(selected_scores) / len(selected_scores)
            score_std = np.std(selected_scores) if len(selected_scores) > 1 else 0.0
            
            # 分数越高、分布越集中，置信度越高
            confidence = avg_score * (1.0 - score_std)
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.error(f"计算置信度失败: {e}")
            return 0.0
    
    async def _update_reviewer_workload(self, selected_reviewers: List[ReviewerProfile]):
        """更新评审员工作负载"""
        try:
            for reviewer in selected_reviewers:
                reviewer.current_workload += 1
                reviewer.last_active = datetime.now()
                
                # 更新内存中的数据
                self.reviewer_profiles[reviewer.id] = reviewer
                
                # 异步保存到持久化存储
                await self._save_reviewer_profile(reviewer)
            
        except Exception as e:
            self.logger.error(f"更新评审员工作负载失败: {e}")
    
    def _record_allocation(self, allocation_result: AllocationResult):
        """记录分配历史"""
        try:
            self.allocation_history.append({
                "timestamp": datetime.now().isoformat(),
                "review_request_id": allocation_result.review_request_id,
                "allocated_reviewers": [r.id for r in allocation_result.allocated_reviewers],
                "allocation_scores": allocation_result.allocation_scores,
                "confidence_score": allocation_result.confidence_score
            })
            
            # 限制历史记录数量
            if len(self.allocation_history) > 1000:
                self.allocation_history = self.allocation_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"记录分配历史失败: {e}")
    
    def _load_reviewer_profiles(self):
        """加载评审员档案"""
        try:
            # 这里应该从数据库或文件加载
            # 简化实现，创建一些示例数据
            self._create_sample_reviewers()
            
        except Exception as e:
            self.logger.error(f"加载评审员档案失败: {e}")
    
    def _create_sample_reviewers(self):
        """创建示例评审员"""
        try:
            sample_reviewers = [
                ReviewerProfile(
                    id="reviewer_001",
                    name="张博士",
                    email="zhang@example.com",
                    specializations=[ReviewerSpecialization.AI_ML, ReviewerSpecialization.DATA_SCIENCE],
                    experience_level=ExperienceLevel.EXPERT,
                    expertise_keywords=["人工智能", "机器学习", "深度学习", "数据挖掘"],
                    availability_score=0.9,
                    current_workload=2,
                    max_workload=5,
                    review_history=[],
                    performance_metrics={"completion_rate": 0.95, "quality_score": 0.88},
                    response_time_avg=12.0,
                    quality_score=0.88,
                    conflicts_of_interest=[],
                    last_active=datetime.now() - timedelta(days=5),
                    metadata={"institution": "清华大学", "department": "计算机科学"}
                ),
                ReviewerProfile(
                    id="reviewer_002",
                    name="李教授",
                    email="li@example.com",
                    specializations=[ReviewerSpecialization.SOFTWARE_ENGINEERING, ReviewerSpecialization.RESEARCH_METHODOLOGY],
                    experience_level=ExperienceLevel.SENIOR,
                    expertise_keywords=["软件架构", "设计模式", "测试", "研究方法"],
                    availability_score=0.8,
                    current_workload=1,
                    max_workload=4,
                    review_history=[],
                    performance_metrics={"completion_rate": 0.92, "quality_score": 0.85},
                    response_time_avg=8.0,
                    quality_score=0.85,
                    conflicts_of_interest=["竞争公司A"],
                    last_active=datetime.now() - timedelta(days=2),
                    metadata={"institution": "北京大学", "department": "软件工程"}
                ),
                ReviewerProfile(
                    id="reviewer_003",
                    name="王研究员",
                    email="wang@example.com",
                    specializations=[ReviewerSpecialization.DOMAIN_EXPERT, ReviewerSpecialization.ETHICS_COMPLIANCE],
                    experience_level=ExperienceLevel.SENIOR,
                    expertise_keywords=["行业应用", "最佳实践", "伦理合规", "隐私保护"],
                    availability_score=0.7,
                    current_workload=3,
                    max_workload=6,
                    review_history=[],
                    performance_metrics={"completion_rate": 0.90, "quality_score": 0.82},
                    response_time_avg=16.0,
                    quality_score=0.82,
                    conflicts_of_interest=[],
                    last_active=datetime.now() - timedelta(days=1),
                    metadata={"institution": "中科院", "department": "自动化研究所"}
                )
            ]
            
            for reviewer in sample_reviewers:
                self.reviewer_profiles[reviewer.id] = reviewer
            
            self.logger.info(f"加载了 {len(sample_reviewers)} 位评审员档案")
            
        except Exception as e:
            self.logger.error(f"创建示例评审员失败: {e}")
    
    async def _save_reviewer_profile(self, reviewer: ReviewerProfile):
        """保存评审员档案"""
        # 简化实现，实际应该保存到数据库
        pass
    
    def _start_background_tasks(self):
        """启动后台任务"""
        def workload_optimization_task():
            while True:
                time.sleep(3600)  # 每小时执行一次
                try:
                    self._optimize_workload_distribution()
                except Exception as e:
                    self.logger.error(f"工作负载优化失败: {e}")
        
        # 启动后台线程
        optimization_thread = threading.Thread(target=workload_optimization_task, daemon=True)
        optimization_thread.start()
    
    def _optimize_workload_distribution(self):
        """优化工作负载分布"""
        try:
            # 分析当前工作负载分布
            reviewers = list(self.reviewer_profiles.values())
            avg_workload = sum(r.current_workload for r in reviewers) / len(reviewers)
            
            # 识别过载和空闲的评审员
            overloaded = [r for r in reviewers if r.current_workload > avg_workload * 1.5]
            underloaded = [r for r in reviewers if r.current_workload < avg_workload * 0.5]
            
            self.logger.info(f"工作负载优化: 过载 {len(overloaded)}, 空闲 {len(underloaded)}")
            
        except Exception as e:
            self.logger.error(f"工作负载分布优化失败: {e}")
    
    async def get_allocator_statistics(self) -> Dict[str, Any]:
        """获取分配器统计信息"""
        try:
            stats = {
                "total_reviewers": len(self.reviewer_profiles),
                "total_allocations": len(self.allocation_history),
                "average_allocation_score": 0.0,
                "workload_distribution": {},
                "specialization_distribution": {},
                "recent_allocations": []
            }
            
            # 计算平均分配分数
            if self.allocation_history:
                recent_scores = [alloc["confidence_score"] for alloc in self.allocation_history[-10:]]
                stats["average_allocation_score"] = sum(recent_scores) / len(recent_scores)
            
            # 工作负载分布
            for reviewer in self.reviewer_profiles.values():
                workload_ratio = reviewer.current_workload / reviewer.max_workload
                if workload_ratio > 0.8:
                    stats["workload_distribution"]["high"] = stats["workload_distribution"].get("high", 0) + 1
                elif workload_ratio > 0.5:
                    stats["workload_distribution"]["medium"] = stats["workload_distribution"].get("medium", 0) + 1
                else:
                    stats["workload_distribution"]["low"] = stats["workload_distribution"].get("low", 0) + 1
            
            # 专业领域分布
            for reviewer in self.reviewer_profiles.values():
                for spec in reviewer.specializations:
                    stats["specialization_distribution"][spec.value] = stats["specialization_distribution"].get(spec.value, 0) + 1
            
            # 最近分配记录
            stats["recent_allocations"] = self.allocation_history[-5:] if self.allocation_history else []
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取分配器统计失败: {e}")
            return {}
    
    async def add_reviewer(self, reviewer: ReviewerProfile) -> bool:
        """添加评审员"""
        try:
            self.reviewer_profiles[reviewer.id] = reviewer
            await self._save_reviewer_profile(reviewer)
            self.logger.info(f"添加评审员: {reviewer.name} ({reviewer.id})")
            return True
        except Exception as e:
            self.logger.error(f"添加评审员失败: {e}")
            return False
    
    async def update_reviewer_performance(self, reviewer_id: str, performance_data: Dict[str, float]):
        """更新评审员表现数据"""
        try:
            if reviewer_id in self.reviewer_profiles:
                reviewer = self.reviewer_profiles[reviewer_id]
                reviewer.performance_metrics.update(performance_data)
                
                # 更新质量分数
                if "quality_score" in performance_data:
                    reviewer.quality_score = performance_data["quality_score"]
                
                await self._save_reviewer_profile(reviewer)
                self.logger.info(f"更新评审员表现: {reviewer_id}")
                return True
            else:
                self.logger.warning(f"评审员不存在: {reviewer_id}")
                return False
        except Exception as e:
            self.logger.error(f"更新评审员表现失败: {e}")
            return False


# 使用示例
async def example_usage():
    """使用示例"""
    # 初始化组件
    knowledge_retrieval = KnowledgeRetrievalService()
    sskg_manager = EnhancedSSKGManager()
    memory_agent = MemAgent()
    
    # 创建智能分配器
    allocator = SmartReviewerAllocator(knowledge_retrieval, sskg_manager, memory_agent)
    
    # 创建评审请求
    review_request = ReviewRequest(
        id="review_request_001",
        title="基于深度学习的图像识别系统",
        content="本文提出了一种新的深度学习架构...",
        content_type="research_paper",
        author="researcher_001",
        submission_date=datetime.now(),
        deadline=datetime.now() + timedelta(days=7),
        required_reviewers=2,
        expertise_areas=["人工智能", "深度学习", "计算机视觉"],
        complexity_level="medium",
        priority=AllocationPriority.HIGH,
        keywords=["深度学习", "图像识别", "CNN", "计算机视觉"],
        metadata={"institution": "清华大学", "project_id": "AI_VISION_001"}
    )
    
    # 分配评审员
    allocation_result = await allocator.allocate_reviewers(review_request)
    
    print(f"分配结果:")
    print(f"  评审请求: {allocation_result.review_request_id}")
    print(f"  分配评审员: {len(allocation_result.allocated_reviewers)}")
    print(f"  置信度: {allocation_result.confidence_score:.2f}")
    
    for i, reviewer in enumerate(allocation_result.allocated_reviewers):
        print(f"  评审员 {i+1}: {reviewer.name} (分数: {allocation_result.allocation_scores[i]:.2f})")
        print(f"    原因: {allocation_result.allocation_reasons[i]}")
    
    # 获取统计信息
    stats = await allocator.get_allocator_statistics()
    print(f"\n分配器统计:")
    print(f"  总评审员数: {stats['total_reviewers']}")
    print(f"  总分配次数: {stats['total_allocations']}")
    print(f"  平均分配分数: {stats['average_allocation_score']:.2f}")


if __name__ == "__main__":
    asyncio.run(example_usage())