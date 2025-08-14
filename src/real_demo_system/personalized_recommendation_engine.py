#!/usr/bin/env python3
"""个性化推荐引擎

基于用户兴趣和知识图谱生成个性化推荐
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PersonalizedRecommendationEngine:
    """个性化推荐引擎"""

    def __init__(self):
        """初始化个性化推荐引擎"""
        self.recommendation_strategies = {
            "interest_based": self._generate_interest_based_recommendations,
            "knowledge_graph": self._generate_knowledge_graph_recommendations,
            "collaborative": self._generate_collaborative_recommendations,
            "content_based": self._generate_content_based_recommendations
        }

        self.recommendation_weights = {
            "interest_based": 0.4,
            "knowledge_graph": 0.3,
            "collaborative": 0.2,
            "content_based": 0.1
        }

        logger.info("个性化推荐引擎初始化完成")

    def generate_recommendations(
        self,
        user_profile: Dict[str, Any],
        knowledge_graph: Any = None,
        recommendation_count: int = 5,
        strategy: str = "hybrid"
    ) -> Dict[str, Any]:
        """生成个性化推荐"""
        try:
            user_id = user_profile.get("user_id", "unknown")

            if strategy == "hybrid":
                # 混合推荐策略
                recommendations = self._generate_hybrid_recommendations(
                    user_profile, knowledge_graph, recommendation_count
                )
            else:
                # 单一策略推荐
                strategy_func = self.recommendation_strategies.get(strategy)
                if not strategy_func:
                    raise ValueError(f"未知的推荐策略: {strategy}")

                recommendations = strategy_func(
                    user_profile, knowledge_graph, recommendation_count
                )

            # 计算推荐置信度
            confidence_scores = self._calculate_recommendation_confidence(recommendations)

            # 生成推荐理由
            reasoning = self._generate_recommendation_reasoning(
                user_profile, recommendations, strategy
            )

            result = {
                "user_id": user_id,
                "recommendation_time": datetime.now().isoformat(),
                "strategy_used": strategy,
                "recommended_topics": recommendations,
                "confidence_scores": confidence_scores,
                "reasoning": reasoning,
                "metadata": {
                    "total_recommendations": len(recommendations),
                    "user_expertise_level": user_profile.get("expertise_level", "unknown"),
                    "recommendation_diversity": self._calculate_diversity(recommendations)
                }
            }

            logger.info(f"个性化推荐生成完成: {user_id}, {len(recommendations)}个推荐")
            return result

        except Exception as e:
            logger.error(f"生成个性化推荐失败: {e}")
            return {
                "error": str(e),
                "recommended_topics": [],
                "confidence_scores": {},
                "reasoning": "推荐生成失败"
            }

    def _generate_hybrid_recommendations(
        self,
        user_profile: Dict[str, Any],
        knowledge_graph: Any,
        recommendation_count: int
    ) -> List[Dict[str, Any]]:
        """生成混合推荐"""
        all_recommendations = []

        # 使用不同策略生成推荐
        for strategy, weight in self.recommendation_weights.items():
            strategy_func = self.recommendation_strategies[strategy]
            strategy_count = max(1, int(recommendation_count * weight))

            try:
                strategy_recommendations = strategy_func(
                    user_profile, knowledge_graph, strategy_count
                )

                # 为每个推荐添加策略信息和权重
                for rec in strategy_recommendations:
                    rec["strategy"] = strategy
                    rec["strategy_weight"] = weight

                all_recommendations.extend(strategy_recommendations)

            except Exception as e:
                logger.warning(f"策略 {strategy} 推荐生成失败: {e}")

        # 去重和排序
        unique_recommendations = self._deduplicate_recommendations(all_recommendations)
        sorted_recommendations = self._sort_recommendations(unique_recommendations)

        return sorted_recommendations[:recommendation_count]

    def _generate_interest_based_recommendations(
        self,
        user_profile: Dict[str, Any],
        knowledge_graph: Any,
        recommendation_count: int
    ) -> List[Dict[str, Any]]:
        """基于兴趣的推荐"""
        recommendations = []
        user_interests = user_profile.get("interests", {})

        if not user_interests:
            return []

        # 按兴趣分数排序
        sorted_interests = sorted(
            user_interests.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for interest, score in sorted_interests[:recommendation_count]:
            recommendation = {
                "topic": interest,
                "relevance_score": score,
                "recommendation_type": "interest_based",
                "description": f"基于您对{interest}的兴趣推荐",
                "suggested_depth": self._suggest_exploration_depth(score),
                "related_concepts": self._get_related_concepts(interest),
                "learning_path": self._generate_learning_path(interest, user_profile)
            }
            recommendations.append(recommendation)

        return recommendations

    def _generate_knowledge_graph_recommendations(
        self,
        user_profile: Dict[str, Any],
        knowledge_graph: Any,
        recommendation_count: int
    ) -> List[Dict[str, Any]]:
        """基于知识图谱的推荐"""
        recommendations = []

        if not knowledge_graph or not hasattr(knowledge_graph, 'knowledge_nodes'):
            return []

        # 获取用户最感兴趣的概念
        user_interests = user_profile.get("interests", {})
        if not user_interests:
            return []

        top_interest = max(user_interests.items(), key=lambda x: x[1])[0]

        # 在知识图谱中查找相关概念
        related_concepts = knowledge_graph.query_knowledge(
            top_interest,
            query_type="related_concepts",
            max_results=recommendation_count
        )

        for concept in related_concepts:
            recommendation = {
                "topic": concept["concept"],
                "relevance_score": concept.get("relation_strength", 0.5),
                "recommendation_type": "knowledge_graph",
                "description": f"基于知识图谱中与{top_interest}的关联推荐",
                "graph_context": {
                    "source_concept": top_interest,
                    "relation_type": "related",
                    "graph_importance": concept.get("importance", 0.5)
                },
                "exploration_suggestions": self._generate_exploration_suggestions(concept)
            }
            recommendations.append(recommendation)

        return recommendations

    def _generate_collaborative_recommendations(
        self,
        user_profile: Dict[str, Any],
        knowledge_graph: Any,
        recommendation_count: int
    ) -> List[Dict[str, Any]]:
        """协同过滤推荐"""
        recommendations = []

        # 模拟协同过滤逻辑（实际实现需要用户行为数据）
        user_interests = user_profile.get("interests", {})
        expertise_level = user_profile.get("expertise_level", "intermediate")

        # 基于相似用户的推荐主题
        collaborative_topics = self._get_collaborative_topics(user_interests, expertise_level)

        for i, topic in enumerate(collaborative_topics[:recommendation_count]):
            recommendation = {
                "topic": topic["name"],
                "relevance_score": topic["score"],
                "recommendation_type": "collaborative",
                "description": f"与您兴趣相似的用户也关注{topic['name']}",
                "similarity_basis": topic["similarity_reason"],
                "community_engagement": topic.get("engagement_level", "medium")
            }
            recommendations.append(recommendation)

        return recommendations

    def _generate_content_based_recommendations(
        self,
        user_profile: Dict[str, Any],
        knowledge_graph: Any,
        recommendation_count: int
    ) -> List[Dict[str, Any]]:
        """基于内容的推荐"""
        recommendations = []

        preferred_content_types = user_profile.get("preferred_content_types", ["analysis"])
        user_interests = user_profile.get("interests", {})

        # 为每种内容类型生成推荐
        for content_type in preferred_content_types[:recommendation_count]:
            if user_interests:
                top_interest = max(user_interests.items(), key=lambda x: x[1])[0]

                recommendation = {
                    "topic": f"{content_type}类型的{top_interest}内容",
                    "relevance_score": 0.7,
                    "recommendation_type": "content_based",
                    "description": f"基于您偏好的{content_type}内容类型推荐",
                    "content_format": content_type,
                    "estimated_duration": self._estimate_content_duration(content_type),
                    "difficulty_level": self._match_difficulty_level(
                        user_profile.get("expertise_level", "intermediate")
                    )
                }
                recommendations.append(recommendation)

        return recommendations

    def _deduplicate_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重推荐"""
        seen_topics = set()
        unique_recommendations = []

        for rec in recommendations:
            topic = rec.get("topic", "")
            if topic not in seen_topics:
                seen_topics.add(topic)
                unique_recommendations.append(rec)

        return unique_recommendations

    def _sort_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """排序推荐"""
        # 综合考虑相关性分数和策略权重
        def sort_key(rec):
            relevance = rec.get("relevance_score", 0.0)
            strategy_weight = rec.get("strategy_weight", 0.0)
            return relevance * strategy_weight

        return sorted(recommendations, key=sort_key, reverse=True)

    def _calculate_recommendation_confidence(self, recommendations: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算推荐置信度"""
        confidence_scores = {}

        for rec in recommendations:
            topic = rec.get("topic", "")
            relevance = rec.get("relevance_score", 0.0)
            strategy = rec.get("strategy", "unknown")

            # 基于策略和相关性计算置信度
            base_confidence = relevance
            strategy_bonus = {
                "interest_based": 0.2,
                "knowledge_graph": 0.15,
                "collaborative": 0.1,
                "content_based": 0.05
            }.get(strategy, 0.0)

            confidence = min(1.0, base_confidence + strategy_bonus)
            confidence_scores[topic] = confidence

        return confidence_scores

    def _generate_recommendation_reasoning(
        self,
        user_profile: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        strategy: str
    ) -> str:
        """生成推荐理由"""
        user_interests = user_profile.get("interests", {})
        expertise_level = user_profile.get("expertise_level", "intermediate")

        if not recommendations:
            return "暂无推荐内容"

        top_interest = ""
        if user_interests:
            top_interest = max(user_interests.items(), key=lambda x: x[1])[0]

        reasoning_parts = []

        if strategy == "hybrid":
            reasoning_parts.append(f"基于您的主要兴趣领域（{top_interest}）")
            reasoning_parts.append(f"结合您的专业水平（{expertise_level}）")
            reasoning_parts.append("使用多种推荐策略综合分析")
        else:
            strategy_descriptions = {
                "interest_based": f"基于您对{top_interest}的高度兴趣",
                "knowledge_graph": "基于知识图谱中的概念关联",
                "collaborative": "基于相似用户的偏好模式",
                "content_based": "基于您偏好的内容类型"
            }
            reasoning_parts.append(strategy_descriptions.get(strategy, "基于推荐算法分析"))

        reasoning_parts.append(f"为您推荐了{len(recommendations)}个相关主题")

        return "，".join(reasoning_parts) + "。"

    def _calculate_diversity(self, recommendations: List[Dict[str, Any]]) -> float:
        """计算推荐多样性"""
        if not recommendations:
            return 0.0

        # 计算推荐类型的多样性
        types = set(rec.get("recommendation_type", "") for rec in recommendations)
        type_diversity = len(types) / len(recommendations)

        # 计算相关性分数的分布
        scores = [rec.get("relevance_score", 0.0) for rec in recommendations]
        if len(set(scores)) == 1:
            score_diversity = 0.0
        else:
            score_range = max(scores) - min(scores)
            score_diversity = score_range

        return (type_diversity + score_diversity) / 2

    def _suggest_exploration_depth(self, interest_score: float) -> str:
        """建议探索深度"""
        if interest_score >= 0.8:
            return "deep"
        elif interest_score >= 0.6:
            return "moderate"
        else:
            return "surface"

    def _get_related_concepts(self, interest: str) -> List[str]:
        """获取相关概念"""
        concept_map = {
            "AI伦理": ["算法公平性", "AI透明度", "隐私保护", "责任AI"],
            "技术实现": ["机器学习", "深度学习", "算法优化", "模型部署"],
            "政策法规": ["数据保护法", "AI监管", "行业标准", "合规要求"]
        }

        return concept_map.get(interest, [])

    def _generate_learning_path(self, interest: str, user_profile: Dict[str, Any]) -> List[str]:
        """生成学习路径"""
        expertise_level = user_profile.get("expertise_level", "intermediate")

        learning_paths = {
            "AI伦理": {
                "beginner": ["AI伦理基础", "伦理框架介绍", "案例分析"],
                "intermediate": ["伦理评估方法", "实践应用", "政策分析"],
                "advanced": ["伦理理论研究", "跨文化伦理", "未来挑战"]
            }
        }

        return learning_paths.get(interest, {}).get(expertise_level, ["基础学习", "实践应用"])

    def _generate_exploration_suggestions(self, concept: Dict[str, Any]) -> List[str]:
        """生成探索建议"""
        concept_type = concept.get("node_type", "concept")

        suggestions_map = {
            "concept": ["深入理解概念定义", "查看相关案例", "探索应用场景"],
            "technology": ["了解技术原理", "查看实现方案", "分析技术趋势"],
            "principle": ["学习原则内容", "理解应用场景", "分析实践案例"]
        }

        return suggestions_map.get(concept_type, ["进一步探索", "查看相关内容"])

    def _get_collaborative_topics(self, user_interests: Dict[str, float], expertise_level: str) -> List[Dict[str, Any]]:
        """获取协同过滤主题"""
        # 模拟协同过滤结果
        base_topics = [
            {"name": "AI安全性", "score": 0.8, "similarity_reason": "兴趣相似度", "engagement_level": "high"},
            {"name": "算法透明度", "score": 0.7, "similarity_reason": "专业水平匹配", "engagement_level": "medium"},
            {"name": "数据治理", "score": 0.6, "similarity_reason": "领域关联", "engagement_level": "medium"}
        ]

        # 根据用户兴趣调整分数
        if "AI伦理" in user_interests:
            base_topics[0]["score"] += 0.1

        return base_topics

    def _estimate_content_duration(self, content_type: str) -> str:
        """估算内容时长"""
        duration_map = {
            "analysis": "15-30分钟",
            "case_study": "20-40分钟",
            "tutorial": "30-60分钟",
            "discussion": "10-20分钟"
        }

        return duration_map.get(content_type, "15-30分钟")

    def _match_difficulty_level(self, expertise_level: str) -> str:
        """匹配难度级别"""
        level_map = {
            "beginner": "入门",
            "intermediate": "中级",
            "advanced": "高级",
            "expert": "专家"
        }

        return level_map.get(expertise_level, "中级")
