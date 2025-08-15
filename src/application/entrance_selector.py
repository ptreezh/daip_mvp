"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : entrance_selector.py
@Description:
    Entrance Selector - Intelligent entrance selection service for DAIP backend.
    Analyzes user context and behavior to recommend optimal entrance types.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from ..domain.domain_services import EntranceSelectorService
from ..domain.entities import User
from ..domain.value_objects import EntranceType


class UserBehaviorPattern(Enum):
    """用户行为模式枚举"""
    EFFICIENCY_FOCUSED = "efficiency_focused"      # 效率导向
    COLLABORATION_FOCUSED = "collaboration_focused"  # 协作导向
    ANALYSIS_FOCUSED = "analysis_focused"          # 分析导向
    LEARNING_FOCUSED = "learning_focused"          # 学习导向
    MIXED = "mixed"                                # 混合模式


class ContextComplexity(Enum):
    """上下文复杂度枚举"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    behavior_pattern: UserBehaviorPattern
    expertise_level: float  # 0.0 - 1.0
    preferred_interaction_style: str
    typical_session_duration: float  # 分钟
    task_complexity_preference: float  # 0.0 - 1.0
    entrance_usage_history: dict[EntranceType, int] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)
    satisfaction_scores: dict[EntranceType, float] = field(default_factory=dict)


@dataclass
class ContextFeatures:
    """上下文特征"""
    query_complexity: float
    time_sensitivity: float
    collaboration_need: float
    analysis_depth: float
    user_expertise: float
    session_duration: float
    interaction_frequency: float
    task_count: int
    message_count: int
    extracted_at: datetime = field(default_factory=datetime.now)


@dataclass
class SelectionResult:
    """选择结果"""
    recommended_entrance: EntranceType
    confidence: float
    reasoning: list[str]
    alternative_options: list[tuple[EntranceType, float]]
    context_features: ContextFeatures
    user_profile: UserProfile
    selection_timestamp: datetime = field(default_factory=datetime.now)


class EntranceSelector:
    """智能入口选择器 - 分析用户上下文和行为以推荐最优入口类型"""
    
    def __init__(self):
        # 基础选择器服务
        self.base_selector = EntranceSelectorService()
        
        # 用户画像存储
        self.user_profiles: dict[str, UserProfile] = {}
        
        # 选择历史记录
        self.selection_history: list[dict[str, Any]] = []
        
        # 机器学习模型（简化版）
        self.selection_model = self._initialize_selection_model()
        
        # 配置参数
        self.config = {
            "learning_rate": 0.1,
            "confidence_threshold": 0.6,
            "max_history_size": 1000,
            "profile_update_interval": 3600,  # 1小时
            "behavior_analysis_window": 7 * 24 * 3600,  # 7天
            "enable_adaptive_learning": True
        }
        
        # 特征权重
        self.feature_weights = {
            "time_sensitivity": 0.25,
            "query_complexity": 0.20,
            "collaboration_need": 0.20,
            "analysis_depth": 0.15,
            "user_expertise": 0.10,
            "session_duration": 0.05,
            "interaction_frequency": 0.05
        }
        
        # 入口特征映射
        self.entrance_profiles = {
            EntranceType.SECRETARIAT: {
                "time_sensitivity": 0.8,    # 高时间敏感性
                "query_complexity": 0.4,    # 中等查询复杂度
                "collaboration_need": 0.2,  # 低协作需求
                "analysis_depth": 0.6,      # 中等分析深度
                "user_expertise": 0.7,      # 高用户专业度
                "session_duration": 0.3,    # 短会话持续时间
                "interaction_frequency": 0.8 # 高交互频率
            },
            EntranceType.FORUM: {
                "time_sensitivity": 0.3,    # 低时间敏感性
                "query_complexity": 0.8,    # 高查询复杂度
                "collaboration_need": 0.9,  # 高协作需求
                "analysis_depth": 0.9,      # 高分析深度
                "user_expertise": 0.6,      # 中等用户专业度
                "session_duration": 0.8,    # 长会话持续时间
                "interaction_frequency": 0.4 # 中等交互频率
            }
        }
        
        # 后台任务
        self._profile_update_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def start(self):
        """启动选择器"""
        if self._is_running:
            return
        
        self._is_running = True
        
        # 启动后台任务
        self._profile_update_task = asyncio.create_task(self._periodic_profile_update())
        
        logging.info("Entrance Selector started")
    
    async def stop(self):
        """停止选择器"""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # 取消后台任务
        if self._profile_update_task:
            self._profile_update_task.cancel()
        
        logging.info("Entrance Selector stopped")
    
    async def select_optimal_entrance(self, user: User, context: dict[str, Any]) -> SelectionResult:
        """选择最优入口类型"""
        # 获取或创建用户画像
        user_profile = await self._get_or_create_user_profile(user)
        
        # 提取上下文特征
        context_features = await self._extract_context_features(user, context, user_profile)
        
        # 分析上下文复杂度
        context_complexity = self._analyze_context_complexity(context_features)
        
        # 使用基础选择器进行初步选择
        base_recommendation = await self.base_selector.select_entrance(user, context)
        
        # 使用机器学习模型进行精细选择
        ml_recommendation = await self._ml_based_selection(user_profile, context_features)
        
        # 综合选择结果
        final_recommendation = await self._combine_recommendations(
            base_recommendation, ml_recommendation, user_profile, context_features
        )
        
        # 生成选择结果
        selection_result = SelectionResult(
            recommended_entrance=final_recommendation["entrance"],
            confidence=final_recommendation["confidence"],
            reasoning=final_recommendation["reasoning"],
            alternative_options=final_recommendation["alternatives"],
            context_features=context_features,
            user_profile=user_profile
        )
        
        # 记录选择历史
        await self._record_selection(user.user_id, selection_result, context)
        
        # 更新用户画像
        await self._update_user_profile(user.user_id, selection_result, context)
        
        return selection_result
    
    async def _get_or_create_user_profile(self, user: User) -> UserProfile:
        """获取或创建用户画像"""
        if user.user_id not in self.user_profiles:
            # 分析用户历史行为
            behavior_pattern = await self._analyze_user_behavior_pattern(user.user_id)
            
            # 创建新用户画像
            user_profile = UserProfile(
                user_id=user.user_id,
                behavior_pattern=behavior_pattern,
                expertise_level=0.5,  # 默认中等专业度
                preferred_interaction_style="balanced",
                typical_session_duration=15.0,  # 默认15分钟
                task_complexity_preference=0.5,
                entrance_usage_history={
                    EntranceType.SECRETARIAT: 0,
                    EntranceType.FORUM: 0
                },
                satisfaction_scores={
                    EntranceType.SECRETARIAT: 0.5,
                    EntranceType.FORUM: 0.5
                }
            )
            
            self.user_profiles[user.user_id] = user_profile
        
        return self.user_profiles[user.user_id]
    
    async def _analyze_user_behavior_pattern(self, user_id: str) -> UserBehaviorPattern:
        """分析用户行为模式"""
        # 简化的行为模式分析
        # 在实际应用中，这里应该分析用户的历史会话数据
        
        # 默认返回混合模式
        return UserBehaviorPattern.MIXED
    
    async def _extract_context_features(self, user: User, context: dict[str, Any], user_profile: UserProfile) -> ContextFeatures:
        """提取上下文特征"""
        # 基础特征提取
        query = context.get("query", "")
        time_limit = context.get("time_limit")
        session_history = context.get("session_history", [])
        
        # 查询复杂度
        query_complexity = self._analyze_query_complexity(query)
        
        # 时间敏感性
        time_sensitivity = self._analyze_time_sensitivity(time_limit, query)
        
        # 协作需求
        collaboration_need = self._analyze_collaboration_need(query, context)
        
        # 分析深度
        analysis_depth = self._analyze_analysis_depth(query, context)
        
        # 用户专业度
        user_expertise = user_profile.expertise_level
        
        # 会话持续时间
        session_duration = self._estimate_session_duration(query, user_profile)
        
        # 交互频率
        interaction_frequency = self._analyze_interaction_frequency(session_history)
        
        # 任务和消息数量
        task_count = len(context.get("recent_tasks", []))
        message_count = len(context.get("recent_messages", []))
        
        return ContextFeatures(
            query_complexity=query_complexity,
            time_sensitivity=time_sensitivity,
            collaboration_need=collaboration_need,
            analysis_depth=analysis_depth,
            user_expertise=user_expertise,
            session_duration=session_duration,
            interaction_frequency=interaction_frequency,
            task_count=task_count,
            message_count=message_count
        )
    
    def _analyze_query_complexity(self, query: str) -> float:
        """分析查询复杂度"""
        if not query:
            return 0.0
        
        # 基于长度
        length_score = min(len(query) / 500, 1.0)
        
        # 基于复杂度关键词
        complexity_keywords = [
            "分析", "评估", "比较", "综合", "深入", "详细", "全面", "多角度",
            "analyze", "evaluate", "compare", "comprehensive", "detailed", "multi-angle"
        ]
        
        complexity_count = sum(1 for keyword in complexity_keywords if keyword in query)
        complexity_score = min(complexity_count / 3, 1.0)
        
        # 基于问题类型
        question_words = ["为什么", "如何", "怎么样", "what", "why", "how", "explain"]
        has_questions = any(word in query for word in question_words)
        
        # 综合评分
        final_score = (length_score * 0.3 + complexity_score * 0.5 + (0.5 if has_questions else 0.0) * 0.2)
        
        return min(final_score, 1.0)
    
    def _analyze_time_sensitivity(self, time_limit: Optional[int], query: str) -> float:
        """分析时间敏感性"""
        # 基于关键词
        urgent_keywords = ["紧急", "立即", "马上", "快速", " ASAP", "urgent", "immediately", "quickly"]
        
        if any(keyword in query.lower() for keyword in urgent_keywords):
            return 0.9
        
        # 基于时间限制
        if time_limit:
            if time_limit <= 300:  # 5分钟内
                return 0.95
            elif time_limit <= 1800:  # 30分钟内
                return 0.7
            elif time_limit <= 3600:  # 1小时内
                return 0.5
        
        return 0.3  # 默认低时间敏感性
    
    def _analyze_collaboration_need(self, query: str, context: dict[str, Any]) -> float:
        """分析协作需求"""
        # 基于关键词
        collaboration_keywords = [
            "讨论", "协作", "合作", "团队", "多角度", "不同观点",
            "discuss", "collaborate", "team", "multi-angle", "different perspectives"
        ]
        
        collaboration_count = sum(1 for keyword in collaboration_keywords if keyword in query.lower())
        
        # 基于上下文
        participants = context.get("participants", [])
        participant_count = len(participants)
        
        # 综合评分
        keyword_score = min(collaboration_count / 2, 1.0)
        participant_score = min(participant_count / 5, 1.0)
        
        return (keyword_score * 0.7 + participant_score * 0.3)
    
    def _analyze_analysis_depth(self, query: str, context: dict[str, Any]) -> float:
        """分析分析深度"""
        # 基于关键词
        depth_keywords = [
            "深度", "详细", "全面", "彻底", "深入研究", "深度分析",
            "deep", "detailed", "comprehensive", "thorough", "in-depth"
        ]
        
        depth_count = sum(1 for keyword in depth_keywords if keyword in query.lower())
        keyword_score = min(depth_count / 2, 1.0)
        
        # 基于查询长度
        length_score = min(len(query) / 300, 1.0)
        
        # 基于上下文复杂度
        context_complexity = context.get("complexity", 0.5)
        
        return (keyword_score * 0.4 + length_score * 0.3 + context_complexity * 0.3)
    
    def _estimate_session_duration(self, query: str, user_profile: UserProfile) -> float:
        """估算会话持续时间"""
        # 基于查询复杂度
        complexity = self._analyze_query_complexity(query)
        
        # 基于用户历史模式
        historical_duration = user_profile.typical_session_duration
        
        # 综合估算
        if complexity > 0.7:
            estimated_duration = historical_duration * 1.5
        elif complexity < 0.3:
            estimated_duration = historical_duration * 0.7
        else:
            estimated_duration = historical_duration
        
        return max(5.0, min(120.0, estimated_duration))  # 限制在5-120分钟之间
    
    def _analyze_interaction_frequency(self, session_history: list[dict[str, Any]]) -> float:
        """分析交互频率"""
        if not session_history:
            return 0.5
        
        # 计算平均交互间隔
        total_duration = 0
        total_interactions = 0
        
        for session in session_history:
            duration = session.get("duration", 0)
            interactions = session.get("interactions", 0)
            
            total_duration += duration
            total_interactions += interactions
        
        if total_duration == 0:
            return 0.5
        
        avg_frequency = total_interactions / total_duration  # 交互次数/分钟
        
        # 标准化到0-1范围
        normalized_frequency = min(avg_frequency / 10, 1.0)
        
        return normalized_frequency
    
    def _analyze_context_complexity(self, features: ContextFeatures) -> ContextComplexity:
        """分析上下文复杂度"""
        # 计算综合复杂度分数
        complexity_score = (
            features.query_complexity * 0.3 +
            features.collaboration_need * 0.2 +
            features.analysis_depth * 0.2 +
            features.task_count * 0.15 +
            features.message_count * 0.15
        )
        
        # 标准化到0-1范围
        complexity_score = min(complexity_score, 1.0)
        
        # 映射到复杂度等级
        if complexity_score < 0.25:
            return ContextComplexity.SIMPLE
        elif complexity_score < 0.5:
            return ContextComplexity.MODERATE
        elif complexity_score < 0.75:
            return ContextComplexity.COMPLEX
        else:
            return ContextComplexity.VERY_COMPLEX
    
    async def _ml_based_selection(self, user_profile: UserProfile, features: ContextFeatures) -> dict[str, Any]:
        """基于机器学习的选择"""
        # 计算每个入口的匹配度
        entrance_scores = {}
        
        for entrance_type, profile in self.entrance_profiles.items():
            # 计算特征相似度
            similarity_score = self._calculate_feature_similarity(features, profile)
            
            # 考虑用户偏好
            preference_score = user_profile.satisfaction_scores.get(entrance_type, 0.5)
            
            # 考虑使用频率
            usage_count = user_profile.entrance_usage_history.get(entrance_type, 0)
            usage_score = min(usage_count / 10, 1.0)  # 标准化到0-1
            
            # 综合评分
            final_score = (
                similarity_score * 0.6 +
                preference_score * 0.3 +
                usage_score * 0.1
            )
            
            entrance_scores[entrance_type] = final_score
        
        # 选择最佳入口
        best_entrance = max(entrance_scores, key=entrance_scores.get)
        best_score = entrance_scores[best_entrance]
        
        # 生成推理过程
        reasoning = self._generate_reasoning(best_entrance, features, entrance_scores)
        
        # 生成备选方案
        alternatives = [
            (entrance, score) for entrance, score in entrance_scores.items()
            if entrance != best_entrance
        ]
        alternatives.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "entrance": best_entrance,
            "confidence": best_score,
            "reasoning": reasoning,
            "alternatives": alternatives[:2],  # 前2个备选方案
            "scores": entrance_scores
        }
    
    def _calculate_feature_similarity(self, features: ContextFeatures, profile: dict[str, float]) -> float:
        """计算特征相似度"""
        similarity_score = 0.0
        
        for feature_name, weight in self.feature_weights.items():
            if feature_name in features.__dict__ and feature_name in profile:
                feature_value = getattr(features, feature_name)
                profile_value = profile[feature_name]
                
                # 计算相似度（使用余弦相似度的简化版本）
                similarity = 1.0 - abs(feature_value - profile_value)
                similarity_score += similarity * weight
        
        return similarity_score
    
    def _generate_reasoning(self, entrance: EntranceType, features: ContextFeatures, scores: dict[EntranceType, float]) -> list[str]:
        """生成选择推理"""
        reasoning = []
        
        if entrance == EntranceType.SECRETARIAT:
            if features.time_sensitivity > 0.7:
                reasoning.append("查询具有高时间敏感性，适合快速处理")
            if features.query_complexity < 0.6:
                reasoning.append("查询复杂度适中，适合结构化处理")
            if features.interaction_frequency > 0.7:
                reasoning.append("用户偏好高频率交互，适合效率型入口")
        
        elif entrance == EntranceType.FORUM:
            if features.collaboration_need > 0.7:
                reasoning.append("查询需要多角度协作讨论")
            if features.analysis_depth > 0.7:
                reasoning.append("需要深度分析和综合思考")
            if features.query_complexity > 0.7:
                reasoning.append("查询复杂度高，适合深入探讨")
        
        # 添加分数比较
        score_diff = scores[entrance] - scores.get(EntranceType.SECRETARIAT if entrance == EntranceType.FORUM else EntranceType.FORUM, 0)
        if score_diff > 0.2:
            reasoning.append(f"推荐入口具有显著优势（+{score_diff:.2f}）")
        
        return reasoning
    
    async def _combine_recommendations(self, base_entrance: EntranceType, ml_result: dict[str, Any], 
                                    user_profile: UserProfile, features: ContextFeatures) -> dict[str, Any]:
        """综合推荐结果"""
        # 如果两者一致，直接返回
        if base_entrance == ml_result["entrance"]:
            return {
                "entrance": base_entrance,
                "confidence": max(0.8, ml_result["confidence"]),
                "reasoning": ["基础选择器和机器学习模型一致推荐"] + ml_result["reasoning"],
                "alternatives": ml_result["alternatives"]
            }
        
        # 如果不一致，进行权衡
        base_weight = 0.4
        ml_weight = 0.6
        
        # 计算综合分数
        base_score = 0.7  # 基础选择器的默认分数
        ml_score = ml_result["confidence"]
        
        # 考虑用户偏好
        user_preference = user_profile.satisfaction_scores.get(base_entrance, 0.5)
        user_preference_ml = user_profile.satisfaction_scores.get(ml_result["entrance"], 0.5)
        
        base_final_score = base_score * base_weight + user_preference * 0.2
        ml_final_score = ml_score * ml_weight + user_preference_ml * 0.2
        
        # 选择最终推荐
        if ml_final_score > base_final_score:
            final_entrance = ml_result["entrance"]
            final_confidence = ml_final_score
            reasoning = ["机器学习模型推荐占优"] + ml_result["reasoning"]
            alternatives = [(base_entrance, base_final_score)] + ml_result["alternatives"]
        else:
            final_entrance = base_entrance
            final_confidence = base_final_score
            reasoning = ["基础选择器推荐占优"]
            alternatives = [(ml_result["entrance"], ml_final_score)] + [
                (alt, score * 0.8) for alt, score in ml_result["alternatives"]
            ]
        
        return {
            "entrance": final_entrance,
            "confidence": final_confidence,
            "reasoning": reasoning,
            "alternatives": alternatives[:3]
        }
    
    async def _record_selection(self, user_id: str, result: SelectionResult, context: dict[str, Any]):
        """记录选择历史"""
        selection_record = {
            "user_id": user_id,
            "selected_entrance": result.recommended_entrance.value,
            "confidence": result.confidence,
            "context_features": {
                "query_complexity": result.context_features.query_complexity,
                "time_sensitivity": result.context_features.time_sensitivity,
                "collaboration_need": result.context_features.collaboration_need,
                "analysis_depth": result.context_features.analysis_depth
            },
            "timestamp": result.selection_timestamp.isoformat(),
            "context_summary": context.get("query", "")[:100] + "..." if len(context.get("query", "")) > 100 else context.get("query", "")
        }
        
        self.selection_history.append(selection_record)
        
        # 限制历史记录大小
        if len(self.selection_history) > self.config["max_history_size"]:
            self.selection_history = self.selection_history[-self.config["max_history_size"]:]
    
    async def _update_user_profile(self, user_id: str, result: SelectionResult, context: dict[str, Any]):
        """更新用户画像"""
        if user_id not in self.user_profiles:
            return
        
        profile = self.user_profiles[user_id]
        
        # 更新使用历史
        selected_entrance = result.recommended_entrance
        profile.entrance_usage_history[selected_entrance] = profile.entrance_usage_history.get(selected_entrance, 0) + 1
        
        # 更新最后活动时间
        profile.last_activity = datetime.now()
        
        # 更新典型会话持续时间
        estimated_duration = result.context_features.session_duration
        profile.typical_session_duration = (
            profile.typical_session_duration * 0.8 + estimated_duration * 0.2
        )
        
        # 更新任务复杂度偏好
        query_complexity = result.context_features.query_complexity
        profile.task_complexity_preference = (
            profile.task_complexity_preference * 0.8 + query_complexity * 0.2
        )
    
    async def _periodic_profile_update(self):
        """定期更新用户画像"""
        while self._is_running:
            try:
                await asyncio.sleep(self.config["profile_update_interval"])
                
                # 分析所有用户画像
                for user_id, profile in self.user_profiles.items():
                    await self._analyze_and_update_profile(user_id, profile)
                
                logging.info(f"Updated {len(self.user_profiles)} user profiles")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in profile update task: {e}")
    
    async def _analyze_and_update_profile(self, user_id: str, profile: UserProfile):
        """分析和更新用户画像"""
        # 分析用户选择模式
        recent_selections = [
            s for s in self.selection_history 
            if s["user_id"] == user_id and 
            (datetime.now() - datetime.fromisoformat(s["timestamp"])).total_seconds() < self.config["behavior_analysis_window"]
        ]
        
        if not recent_selections:
            return
        
        # 分析入口使用偏好
        entrance_usage = {}
        for selection in recent_selections:
            entrance = selection["selected_entrance"]
            entrance_usage[entrance] = entrance_usage.get(entrance, 0) + 1
        
        # 更新满意度分数（简化版）
        for entrance, count in entrance_usage.items():
            try:
                entrance_enum = EntranceType(entrance)
                avg_confidence = sum(
                    s["confidence"] for s in recent_selections 
                    if s["selected_entrance"] == entrance
                ) / count
                
                profile.satisfaction_scores[entrance_enum] = avg_confidence
            except ValueError:
                pass
    
    def _initialize_selection_model(self) -> dict[str, Any]:
        """初始化选择模型"""
        # 简化的模型初始化
        return {
            "model_type": "weighted_similarity",
            "feature_weights": self.feature_weights.copy(),
            "entrance_profiles": self.entrance_profiles.copy(),
            "last_trained": datetime.now().isoformat()
        }
    
    async def record_user_feedback(self, user_id: str, entrance: EntranceType, satisfaction: float):
        """记录用户反馈"""
        if user_id not in self.user_profiles:
            return
        
        profile = self.user_profiles[user_id]
        
        # 更新满意度分数
        current_satisfaction = profile.satisfaction_scores.get(entrance, 0.5)
        updated_satisfaction = current_satisfaction * 0.9 + satisfaction * 0.1
        
        profile.satisfaction_scores[entrance] = updated_satisfaction
        
        # 通知基础选择器
        self.base_selector.learn_from_feedback(user_id, entrance, satisfaction)
    
    async def get_selection_insights(self, user_id: str) -> dict[str, Any]:
        """获取选择洞察"""
        if user_id not in self.user_profiles:
            return {"error": "User profile not found"}
        
        profile = self.user_profiles[user_id]
        
        # 分析用户选择模式
        total_usage = sum(profile.entrance_usage_history.values())
        if total_usage == 0:
            return {
                "user_id": user_id,
                "message": "No usage history available",
                "profile": profile
            }
        
        # 计算使用分布
        usage_distribution = {
            entrance.value: count / total_usage 
            for entrance, count in profile.entrance_usage_history.items()
        }
        
        # 分析满意度趋势
        satisfaction_trend = {
            entrance.value: score 
            for entrance, score in profile.satisfaction_scores.items()
        }
        
        # 生成洞察
        insights = []
        
        # 最常用的入口
        most_used = max(profile.entrance_usage_history.items(), key=lambda x: x[1])
        insights.append(f"最常用的入口: {most_used[0].value} ({most_used[1]}次)")
        
        # 最满意的入口
        most_satisfied = max(profile.satisfaction_scores.items(), key=lambda x: x[1])
        insights.append(f"最满意的入口: {most_satisfied[0].value} (满意度: {most_satisfied[1]:.2f})")
        
        # 行为模式洞察
        if profile.behavior_pattern == UserBehaviorPattern.EFFICIENCY_FOCUSED:
            insights.append("用户表现出效率导向的行为模式")
        elif profile.behavior_pattern == UserBehaviorPattern.COLLABORATION_FOCUSED:
            insights.append("用户表现出协作导向的行为模式")
        
        return {
            "user_id": user_id,
            "usage_distribution": usage_distribution,
            "satisfaction_trend": satisfaction_trend,
            "behavior_pattern": profile.behavior_pattern.value,
            "expertise_level": profile.expertise_level,
            "typical_session_duration": profile.typical_session_duration,
            "insights": insights,
            "last_updated": profile.last_activity.isoformat()
        }
    
    async def get_system_statistics(self) -> dict[str, Any]:
        """获取系统统计信息"""
        total_users = len(self.user_profiles)
        total_selections = len(self.selection_history)
        
        # 入口使用统计
        entrance_stats = {}
        for entrance_type in EntranceType:
            usage_count = sum(
                1 for s in self.selection_history 
                if s["selected_entrance"] == entrance_type.value
            )
            entrance_stats[entrance_type.value] = usage_count
        
        # 平均置信度
        avg_confidence = sum(s["confidence"] for s in self.selection_history) / total_selections if total_selections > 0 else 0
        
        # 用户满意度统计
        satisfaction_scores = []
        for profile in self.user_profiles.values():
            satisfaction_scores.extend(profile.satisfaction_scores.values())
        
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        
        return {
            "total_users": total_users,
            "total_selections": total_selections,
            "entrance_statistics": entrance_stats,
            "average_confidence": avg_confidence,
            "average_satisfaction": avg_satisfaction,
            "model_info": self.selection_model,
            "is_running": self._is_running
        }