#!/usr/bin/env python3
"""用户兴趣画像器

分析用户行为，构建个性化兴趣档案
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

logger = logging.getLogger(__name__)


class UserInterestProfiler:
    """用户兴趣画像器"""

    def __init__(self):
        """初始化用户兴趣画像器"""
        self.interest_categories = {
            "AI伦理": ["伦理", "道德", "责任", "公平", "透明"],
            "技术实现": ["算法", "模型", "架构", "实现", "优化"],
            "政策法规": ["法律", "政策", "监管", "合规", "标准"],
            "应用场景": ["医疗", "金融", "教育", "交通", "制造"],
            "社会影响": ["就业", "隐私", "安全", "社会", "文化"],
            "学术研究": ["论文", "研究", "理论", "实验", "分析"]
        }

        self.user_interactions = {}  # {user_id: interaction_history}

        logger.info("用户兴趣画像器初始化完成")
<<<<<<< HEAD

    def analyze_user_behavior(self, user_behavior: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def analyze_user_behavior(self, user_behavior: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析用户行为"""
        try:
            user_id = user_behavior.get("user_id")
            interactions = user_behavior.get("interactions", [])

            # 更新用户交互历史
            if user_id not in self.user_interactions:
                self.user_interactions[user_id] = []

            self.user_interactions[user_id].extend(interactions)

            # 分析兴趣分数
            interest_scores = self._calculate_interest_scores(interactions)

            # 识别主导兴趣
            dominant_interests = self._identify_dominant_interests(interest_scores)

            # 分析交互模式
            interaction_patterns = self._analyze_interaction_patterns(interactions)

            # 计算兴趣演化趋势
            interest_trends = self._calculate_interest_trends(user_id)

            analysis_result = {
                "user_id": user_id,
                "analysis_time": datetime.now().isoformat(),
                "interest_scores": interest_scores,
                "dominant_interests": dominant_interests,
                "interaction_patterns": interaction_patterns,
                "interest_trends": interest_trends,
                "total_interactions": len(self.user_interactions.get(user_id, [])),
                "analysis_confidence": self._calculate_analysis_confidence(interactions)
            }

            logger.info(f"用户行为分析完成: {user_id}, 主要兴趣: {dominant_interests}")
            return analysis_result

        except Exception as e:
            logger.error(f"分析用户行为失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def update_interest_profile(self, user_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def update_interest_profile(self, user_id: str, feedback: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """更新兴趣档案"""
        try:
            # 获取当前档案
            current_profile = self._get_current_profile(user_id)

            # 根据反馈调整兴趣分数
            adjusted_scores = self._adjust_scores_based_on_feedback(
                current_profile.get("interest_scores", {}),
                feedback
            )

            # 更新档案
            updated_profile = {
                "user_id": user_id,
                "last_updated": datetime.now().isoformat(),
                "interest_scores": adjusted_scores,
                "feedback_history": current_profile.get("feedback_history", []) + [feedback],
                "profile_version": current_profile.get("profile_version", 0) + 1
            }

            # 保存更新后的档案
            self._save_profile(user_id, updated_profile)

            logger.info(f"用户兴趣档案更新完成: {user_id}")
            return updated_profile

        except Exception as e:
            logger.error(f"更新兴趣档案失败: {e}")
            return {"error": str(e)}

    def get_personalized_recommendations(
        self,
        user_id: str,
        context: dict[str, Any] = None,
        recommendation_count: int = 5
    ) -> dict[str, Any]:
        """获取个性化推荐"""
        try:
            # 获取用户档案
            user_profile = self._get_current_profile(user_id)
            interest_scores = user_profile.get("interest_scores", {})

            # 生成推荐
            recommendations = []

            # 基于兴趣分数推荐主题
            sorted_interests = sorted(
                interest_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for interest, score in sorted_interests[:recommendation_count]:
                recommendation = {
                    "topic": interest,
                    "relevance_score": score,
                    "recommendation_type": "interest_based",
                    "reasoning": f"基于您对{interest}的高度兴趣（分数: {score:.2f}）",
                    "suggested_actions": self._get_suggested_actions(interest),
                    "related_topics": self._get_related_topics(interest)
                }
                recommendations.append(recommendation)

            # 考虑上下文信息
            if context:
                contextual_recommendations = self._generate_contextual_recommendations(
                    user_profile, context
                )
                recommendations.extend(contextual_recommendations)

            result = {
                "user_id": user_id,
                "recommendation_time": datetime.now().isoformat(),
                "recommendations": recommendations[:recommendation_count],
                "user_profile_summary": {
                    "top_interests": sorted_interests[:3],
                    "profile_maturity": self._calculate_profile_maturity(user_profile),
                    "last_activity": self._get_last_activity_time(user_id)
                }
            }

            logger.info(f"个性化推荐生成完成: {user_id}, {len(recommendations)}个推荐")
            return result

        except Exception as e:
            logger.error(f"获取个性化推荐失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def _calculate_interest_scores(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
=======
    
    def _calculate_interest_scores(self, interactions: list[dict[str, Any]]) -> dict[str, float]:
>>>>>>> feature/core-services-refactor
        """计算兴趣分数"""
        scores = defaultdict(float)

        for interaction in interactions:
            content = interaction.get("content", "").lower()
            interaction_type = interaction.get("type", "")

            # 根据交互类型设置权重
            type_weights = {
                "query": 1.0,
                "debate_participation": 1.5,
                "knowledge_creation": 2.0,
                "feedback": 0.8,
                "sharing": 1.2
            }

            weight = type_weights.get(interaction_type, 1.0)

            # 计算每个兴趣类别的分数
            for category, keywords in self.interest_categories.items():
                category_score = 0
                for keyword in keywords:
                    if keyword in content:
                        category_score += 1

                if category_score > 0:
                    scores[category] += category_score * weight

        # 归一化分数
        if scores:
            max_score = max(scores.values())
            scores = {k: v / max_score for k, v in scores.items()}

        return dict(scores)
<<<<<<< HEAD

    def _identify_dominant_interests(self, interest_scores: Dict[str, float]) -> List[str]:
=======
    
    def _identify_dominant_interests(self, interest_scores: dict[str, float]) -> list[str]:
>>>>>>> feature/core-services-refactor
        """识别主导兴趣"""
        if not interest_scores:
            return []

        # 找出分数高于平均值的兴趣
        avg_score = sum(interest_scores.values()) / len(interest_scores)
        dominant = [
            interest for interest, score in interest_scores.items()
            if score > avg_score
        ]

        # 按分数排序
        dominant.sort(key=lambda x: interest_scores[x], reverse=True)

        return dominant[:3]  # 返回前3个主导兴趣
<<<<<<< HEAD

    def _analyze_interaction_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
=======
    
    def _analyze_interaction_patterns(self, interactions: list[dict[str, Any]]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析交互模式"""
        if not interactions:
            return {}

        # 按类型统计交互
        type_counts = defaultdict(int)
        time_distribution = defaultdict(int)

        for interaction in interactions:
            interaction_type = interaction.get("type", "unknown")
            type_counts[interaction_type] += 1

            # 分析时间分布
            timestamp = interaction.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    time_distribution[f"{hour:02d}:00"] += 1
                except:
                    pass

        # 计算活跃度
        total_interactions = len(interactions)
        most_active_type = max(type_counts.items(), key=lambda x: x[1]) if type_counts else ("none", 0)

        return {
            "total_interactions": total_interactions,
            "interaction_types": dict(type_counts),
            "most_active_type": most_active_type[0],
            "activity_frequency": most_active_type[1] / total_interactions if total_interactions > 0 else 0,
            "time_distribution": dict(time_distribution),
            "engagement_level": self._calculate_engagement_level(interactions)
        }
<<<<<<< HEAD

    def _calculate_interest_trends(self, user_id: str) -> Dict[str, Any]:
=======
    
    def _calculate_interest_trends(self, user_id: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """计算兴趣演化趋势"""
        user_history = self.user_interactions.get(user_id, [])

        if len(user_history) < 2:
            return {"trend": "insufficient_data"}

        # 按时间分组分析兴趣变化
        recent_interactions = [
            i for i in user_history
            if self._is_recent_interaction(i, days=7)
        ]

        older_interactions = [
            i for i in user_history
            if not self._is_recent_interaction(i, days=7)
        ]

        if not recent_interactions or not older_interactions:
            return {"trend": "insufficient_historical_data"}

        recent_scores = self._calculate_interest_scores(recent_interactions)
        older_scores = self._calculate_interest_scores(older_interactions)

        # 计算变化趋势
        trends = {}
        for category in self.interest_categories.keys():
            recent_score = recent_scores.get(category, 0)
            older_score = older_scores.get(category, 0)

            if older_score > 0:
                change = (recent_score - older_score) / older_score
                trends[category] = {
                    "change_rate": change,
                    "direction": "increasing" if change > 0.1 else "decreasing" if change < -0.1 else "stable",
                    "recent_score": recent_score,
                    "previous_score": older_score
                }

        return {
            "trend_analysis": trends,
            "overall_activity": "increasing" if len(recent_interactions) > len(older_interactions) else "stable",
            "analysis_period": "7_days"
        }

    def _adjust_scores_based_on_feedback(
        self,
        current_scores: dict[str, float],
        feedback: dict[str, Any]
    ) -> dict[str, float]:
        """根据反馈调整分数"""
        adjusted_scores = current_scores.copy()

        feedback_type = feedback.get("type", "")
        feedback_content = feedback.get("content", {})

        if feedback_type == "relevance_rating":
            # 根据相关性评分调整
            for topic, rating in feedback_content.items():
                if topic in adjusted_scores:
                    # 根据评分调整分数（1-5分制）
                    adjustment = (rating - 3) * 0.1  # -0.2 到 +0.2 的调整
                    adjusted_scores[topic] = max(0, min(1, adjusted_scores[topic] + adjustment))

        elif feedback_type == "interest_declaration":
            # 用户主动声明兴趣
            declared_interests = feedback_content.get("interests", [])
            for interest in declared_interests:
                if interest in adjusted_scores:
                    adjusted_scores[interest] = min(1.0, adjusted_scores[interest] + 0.2)

        return adjusted_scores
<<<<<<< HEAD

    def _get_suggested_actions(self, interest: str) -> List[str]:
=======
    
    def _get_suggested_actions(self, interest: str) -> list[str]:
>>>>>>> feature/core-services-refactor
        """获取建议行动"""
        action_map = {
            "AI伦理": [
                "参与AI伦理相关的辩论讨论",
                "阅读最新的AI伦理研究报告",
                "关注AI伦理政策发展动态"
            ],
            "技术实现": [
                "深入学习相关算法原理",
                "参与技术实现的案例分析",
                "关注最新技术发展趋势"
            ],
            "政策法规": [
                "跟踪相关法律法规更新",
                "参与政策讨论和意见征集",
                "了解国际监管发展动态"
            ]
        }

        return action_map.get(interest, ["探索相关主题", "参与相关讨论"])
<<<<<<< HEAD

    def _get_related_topics(self, interest: str) -> List[str]:
=======
    
    def _get_related_topics(self, interest: str) -> list[str]:
>>>>>>> feature/core-services-refactor
        """获取相关主题"""
        related_map = {
            "AI伦理": ["算法公平性", "AI透明度", "隐私保护"],
            "技术实现": ["机器学习", "深度学习", "算法优化"],
            "政策法规": ["数据保护法", "AI监管框架", "行业标准"]
        }

        return related_map.get(interest, [])

    def _generate_contextual_recommendations(
        self,
        user_profile: dict[str, Any],
        context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """生成上下文相关推荐"""
        recommendations = []

        current_topic = context.get("current_topic", "")
        if current_topic:
            # 基于当前主题推荐相关内容
            recommendation = {
                "topic": f"深入探讨: {current_topic}",
                "relevance_score": 0.8,
                "recommendation_type": "contextual",
                "reasoning": f"基于您当前正在讨论的主题: {current_topic}",
                "suggested_actions": [f"继续深入分析{current_topic}"],
                "related_topics": []
            }
            recommendations.append(recommendation)

        return recommendations
<<<<<<< HEAD

    def _calculate_engagement_level(self, interactions: List[Dict[str, Any]]) -> str:
=======
    
    def _calculate_engagement_level(self, interactions: list[dict[str, Any]]) -> str:
>>>>>>> feature/core-services-refactor
        """计算参与度水平"""
        if not interactions:
            return "none"

        total_interactions = len(interactions)

        if total_interactions >= 20:
            return "high"
        elif total_interactions >= 10:
            return "medium"
        elif total_interactions >= 5:
            return "low"
        else:
            return "minimal"
<<<<<<< HEAD

    def _is_recent_interaction(self, interaction: Dict[str, Any], days: int = 7) -> bool:
=======
    
    def _is_recent_interaction(self, interaction: dict[str, Any], days: int = 7) -> bool:
>>>>>>> feature/core-services-refactor
        """判断是否为近期交互"""
        timestamp = interaction.get("timestamp", "")
        if not timestamp:
            return False

        try:
            interaction_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            cutoff_time = datetime.now() - timedelta(days=days)
            return interaction_time > cutoff_time
        except:
            return False
<<<<<<< HEAD

    def _get_current_profile(self, user_id: str) -> Dict[str, Any]:
=======
    
    def _get_current_profile(self, user_id: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取当前档案"""
        # 简化实现，实际应该从持久化存储中获取
        return {
            "user_id": user_id,
            "interest_scores": {},
            "feedback_history": [],
            "profile_version": 0
        }
<<<<<<< HEAD

    def _save_profile(self, user_id: str, profile: Dict[str, Any]):
        """保存档案"""
        # 简化实现，实际应该保存到持久化存储
        logger.info(f"保存用户档案: {user_id}")

    def _calculate_profile_maturity(self, profile: Dict[str, Any]) -> str:
=======
    
    def _save_profile(self, user_id: str, profile: dict[str, Any]):
        """保存档案"""
        # 简化实现，实际应该保存到持久化存储
        logger.info(f"保存用户档案: {user_id}")
    
    def _calculate_profile_maturity(self, profile: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """计算档案成熟度"""
        version = profile.get("profile_version", 0)
        feedback_count = len(profile.get("feedback_history", []))

        if version >= 10 and feedback_count >= 5:
            return "mature"
        elif version >= 5 and feedback_count >= 2:
            return "developing"
        else:
            return "new"

    def _get_last_activity_time(self, user_id: str) -> str:
        """获取最后活动时间"""
        user_history = self.user_interactions.get(user_id, [])
        if not user_history:
            return "never"

        latest_interaction = max(
            user_history,
            key=lambda x: x.get("timestamp", ""),
            default={}
        )

        return latest_interaction.get("timestamp", "unknown")
<<<<<<< HEAD

    def _calculate_analysis_confidence(self, interactions: List[Dict[str, Any]]) -> float:
=======
    
    def _calculate_analysis_confidence(self, interactions: list[dict[str, Any]]) -> float:
>>>>>>> feature/core-services-refactor
        """计算分析置信度"""
        if not interactions:
            return 0.0

        # 基于交互数量和多样性计算置信度
        interaction_count = len(interactions)
        type_diversity = len(set(i.get("type", "") for i in interactions))

        count_score = min(interaction_count / 20, 1.0)  # 20个交互为满分
        diversity_score = min(type_diversity / 5, 1.0)  # 5种类型为满分

        return (count_score + diversity_score) / 2
