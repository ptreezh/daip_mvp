"""
@Time: 2025-08-03
@Author: Claude Code
@File: smart_reviewer_allocator_simple.py
@Description: Simplified version of SmartReviewerAllocator for testing without external dependencies
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
import threading
import time
import random


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
    """智能评审分配器 - 简化版本"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 评审员数据库
        self.reviewer_pool = {}
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
        
        # 加载评审员数据
        self._load_reviewer_profiles()
    
    async def select_reviewers(self, 
                            content_type: str,
                            content_tags: List[str],
                            required_count: int,
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """智能分配评审员"""
        try:
            self.logger.info(f"开始分配评审员: {content_type}")
            
            # 创建虚拟评审请求
            review_request = ReviewRequest(
                id=f"request_{datetime.now().isoformat()}",
                title=f"Review for {content_type}",
                content=content_type,
                content_type=content_type,
                author="system",
                submission_date=datetime.now(),
                deadline=datetime.now() + timedelta(days=7),
                required_reviewers=required_count,
                expertise_areas=content_tags,
                complexity_level="medium",
                priority=AllocationPriority.MEDIUM,
                keywords=content_tags,
                metadata=context or {}
            )
            
            criteria = AllocationCriteria()
            
            # 1. 候选评审员筛选
            candidates = await self._filter_candidates(review_request, criteria)
            
            if not candidates:
                return {
                    'success': False,
                    'error': 'No available reviewers',
                    'selected_reviewers': [],
                    'allocation_id': None
                }
            
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
            
            # 7. 选择评审员
            sorted_candidates = sorted(candidates, key=lambda x: final_scores.get(x.id, 0.0), reverse=True)
            selected_reviewers = sorted_candidates[:required_count]
            
            # 8. 生成分配结果
            allocation_id = f"alloc_{datetime.now().isoformat()}"
            
            result = {
                'success': True,
                'selected_reviewers': [r.id for r in selected_reviewers],
                'allocation_id': allocation_id,
                'scores': [final_scores.get(r.id, 0.0) for r in selected_reviewers],
                'total_candidates': len(candidates),
                'confidence_score': sum(final_scores.get(r.id, 0.0) for r in selected_reviewers) / len(selected_reviewers) if selected_reviewers else 0.0
            }
            
            self.logger.info(f"评审员分配完成: {allocation_id} -> {len(selected_reviewers)}位评审员")
            
            return result
            
        except Exception as e:
            self.logger.error(f"评审员分配失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'selected_reviewers': [],
                'allocation_id': None
            }
    
    async def _filter_candidates(self, 
                               review_request: ReviewRequest,
                               criteria: AllocationCriteria) -> List[ReviewerProfile]:
        """筛选候选评审员"""
        try:
            candidates = []
            
            for reviewer_id, reviewer in self.reviewer_pool.items():
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
                
                final_score = min(1.0, expertise_score + experience_bonus)
                scores[candidate.id] = final_score
            
            return scores
            
        except Exception as e:
            self.logger.error(f"计算专业匹配分数失败: {e}")
            return {candidate.id: 0.0 for candidate in candidates}
    
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
    
    def _calculate_match_score(self, reviewer: Dict[str, Any], required_skills: List[str], content_type: str) -> float:
        """计算匹配分数 (简化版本)"""
        try:
            # 基础分数
            base_score = 0.5
            
            # 技能匹配
            reviewer_skills = reviewer.get('expertise', [])
            skill_matches = len(set(required_skills) & set(reviewer_skills))
            skill_score = skill_matches / len(required_skills) if required_skills else 0.5
            
            # 工作负载调整
            workload = reviewer.get('workload', 0.5)
            workload_score = 1.0 - workload
            
            # 综合分数
            final_score = (base_score * 0.3 + skill_score * 0.5 + workload_score * 0.2)
            
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            self.logger.error(f"计算匹配分数失败: {e}")
            return 0.5
    
    def _load_reviewer_profiles(self):
        """加载评审员档案"""
        try:
            # 创建示例评审员
            sample_reviewers = [
                ReviewerProfile(
                    id="reviewer1",
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
                    id="reviewer2",
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
                    id="reviewer3",
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
                self.reviewer_pool[reviewer.id] = reviewer
            
            self.logger.info(f"加载了 {len(sample_reviewers)} 位评审员档案")
            
        except Exception as e:
            self.logger.error(f"加载评审员档案失败: {e}")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """获取评审员池统计信息"""
        try:
            return {
                "total_reviewers": len(self.reviewer_pool),
                "available_reviewers": len([r for r in self.reviewer_pool.values() if r.current_workload < r.max_workload]),
                "average_workload": sum(r.current_workload for r in self.reviewer_pool.values()) / len(self.reviewer_pool) if self.reviewer_pool else 0,
                "specialization_distribution": {
                    spec.value: len([r for r in self.reviewer_pool.values() if spec in r.specializations])
                    for spec in ReviewerSpecialization
                }
            }
        except Exception as e:
            self.logger.error(f"获取评审员池统计失败: {e}")
            return {}


# 使用示例
async def example_usage():
    """使用示例"""
    # 创建智能分配器
    allocator = SmartReviewerAllocator()
    
    # 分配评审员
    result = await allocator.select_reviewers(
        content_type='code_review',
        content_tags=['python', 'testing'],
        required_count=2
    )
    
    print(f"分配结果: {result}")
    
    # 获取统计信息
    stats = allocator.get_pool_stats()
    print(f"统计信息: {stats}")


if __name__ == "__main__":
    asyncio.run(example_usage())