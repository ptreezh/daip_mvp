#!/usr/bin/env python3
"""自适应学习系统

基于用户交互和反馈持续优化推荐和体验
"""

import logging
import math
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AdaptiveLearningSystem:
    """自适应学习系统"""
    
    def __init__(self):
        """初始化自适应学习系统"""
        self.learning_models = {
            "user_preference": UserPreferenceLearningModel(),
            "content_effectiveness": ContentEffectivenessModel(),
            "interaction_pattern": InteractionPatternModel(),
            "recommendation_quality": RecommendationQualityModel()
        }
        
        self.adaptation_strategies = {
            "immediate": self._immediate_adaptation,
            "gradual": self._gradual_adaptation,
            "batch": self._batch_adaptation
        }
        
        self.learning_history = {}  # {user_id: learning_history}
        
        logger.info("自适应学习系统初始化完成")
    
    def learn_from_interaction(self, interaction_data: dict[str, Any]) -> dict[str, Any]:
        """从交互中学习"""
        try:
            user_id = interaction_data.get("user_id")
            interaction_type = interaction_data.get("interaction_type")
            
            # 初始化用户学习历史
            if user_id not in self.learning_history:
                self.learning_history[user_id] = {
                    "interactions": [],
                    "learning_updates": [],
                    "model_states": {}
                }
            
            # 记录交互
            self.learning_history[user_id]["interactions"].append({
                **interaction_data,
                "timestamp": datetime.now().isoformat()
            })
            
            # 应用学习模型
            learning_updates = {}
            model_adjustments = {}
            
            for model_name, model in self.learning_models.items():
                try:
                    update_result = model.update(interaction_data)
                    learning_updates[model_name] = update_result
                    
                    # 获取模型调整
                    adjustment = model.get_adjustment_recommendation()
                    if adjustment:
                        model_adjustments[model_name] = adjustment
                        
                except Exception as e:
                    logger.warning(f"模型 {model_name} 学习失败: {e}")
            
            # 计算整体置信度变化
            confidence_change = self._calculate_confidence_change(
                interaction_data, learning_updates
            )
            
            # 记录学习更新
            learning_record = {
                "timestamp": datetime.now().isoformat(),
                "interaction_type": interaction_type,
                "learning_updates": learning_updates,
                "model_adjustments": model_adjustments,
                "confidence_change": confidence_change
            }
            
            self.learning_history[user_id]["learning_updates"].append(learning_record)
            
            result = {
                "user_id": user_id,
                "learning_timestamp": datetime.now().isoformat(),
                "learning_updates": learning_updates,
                "model_adjustments": model_adjustments,
                "confidence_change": confidence_change,
                "learning_effectiveness": self._evaluate_learning_effectiveness(user_id)
            }
            
            logger.info(f"交互学习完成: {user_id}, 置信度变化: {confidence_change:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"从交互中学习失败: {e}")
            return {"error": str(e)}
    
    def adapt_recommendations(
        self,
        user_id: str,
        current_recommendations: list[dict[str, Any]],
        adaptation_strategy: str = "immediate"
    ) -> dict[str, Any]:
        """适应性调整推荐"""
        try:
            # 获取用户学习历史
            user_history = self.learning_history.get(user_id, {})
            
            # 选择适应策略
            adaptation_func = self.adaptation_strategies.get(adaptation_strategy)
            if not adaptation_func:
                raise ValueError(f"未知的适应策略: {adaptation_strategy}")
            
            # 应用适应策略
            adapted_recommendations = adaptation_func(
                user_id, current_recommendations, user_history
            )
            
            # 计算适应效果
            adaptation_metrics = self._calculate_adaptation_metrics(
                current_recommendations, adapted_recommendations
            )
            
            result = {
                "user_id": user_id,
                "adaptation_time": datetime.now().isoformat(),
                "strategy_used": adaptation_strategy,
                "original_count": len(current_recommendations),
                "adapted_count": len(adapted_recommendations),
                "adapted_recommendations": adapted_recommendations,
                "adaptation_metrics": adaptation_metrics,
                "adaptation_reasoning": self._generate_adaptation_reasoning(
                    adaptation_strategy, adaptation_metrics
                )
            }
            
            logger.info(f"推荐适应完成: {user_id}, 策略: {adaptation_strategy}")
            return result
            
        except Exception as e:
            logger.error(f"适应推荐失败: {e}")
            return {"error": str(e)}
    
    def evaluate_learning_effectiveness(self, user_id: str) -> dict[str, Any]:
        """评估学习效果"""
        try:
            user_history = self.learning_history.get(user_id, {})
            interactions = user_history.get("interactions", [])
            learning_updates = user_history.get("learning_updates", [])
            
            if not interactions or not learning_updates:
                return {"effectiveness": "insufficient_data"}
            
            # 计算学习指标
            learning_metrics = {
                "interaction_count": len(interactions),
                "learning_update_count": len(learning_updates),
                "average_confidence_change": self._calculate_average_confidence_change(learning_updates),
                "learning_velocity": self._calculate_learning_velocity(learning_updates),
                "model_stability": self._calculate_model_stability(learning_updates),
                "prediction_accuracy": self._calculate_prediction_accuracy(user_id)
            }
            
            # 评估整体效果
            overall_effectiveness = self._evaluate_overall_effectiveness(learning_metrics)
            
            # 生成改进建议
            improvement_suggestions = self._generate_improvement_suggestions(learning_metrics)
            
            result = {
                "user_id": user_id,
                "evaluation_time": datetime.now().isoformat(),
                "learning_metrics": learning_metrics,
                "overall_effectiveness": overall_effectiveness,
                "improvement_suggestions": improvement_suggestions,
                "learning_trend": self._analyze_learning_trend(learning_updates),
                "next_optimization_targets": self._identify_optimization_targets(learning_metrics)
            }
            
            logger.info(f"学习效果评估完成: {user_id}, 效果: {overall_effectiveness}")
            return result
            
        except Exception as e:
            logger.error(f"评估学习效果失败: {e}")
            return {"error": str(e)}
    
    def _immediate_adaptation(
        self,
        user_id: str,
        recommendations: list[dict[str, Any]],
        user_history: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """即时适应策略"""
        adapted_recommendations = []
        
        # 获取最近的反馈
        recent_interactions = user_history.get("interactions", [])[-5:]
        
        for rec in recommendations:
            adapted_rec = rec.copy()
            
            # 根据最近反馈调整相关性分数
            topic = rec.get("topic", "")
            recent_feedback = self._get_recent_feedback_for_topic(recent_interactions, topic)
            
            if recent_feedback:
                score_adjustment = self._calculate_score_adjustment(recent_feedback)
                adapted_rec["relevance_score"] = max(0.0, min(1.0, 
                    rec.get("relevance_score", 0.5) + score_adjustment
                ))
                adapted_rec["adaptation_applied"] = "immediate_feedback"
            
            adapted_recommendations.append(adapted_rec)
        
        # 按调整后的分数重新排序
        adapted_recommendations.sort(
            key=lambda x: x.get("relevance_score", 0.0),
            reverse=True
        )
        
        return adapted_recommendations
    
    def _gradual_adaptation(
        self,
        user_id: str,
        recommendations: list[dict[str, Any]],
        user_history: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """渐进适应策略"""
        adapted_recommendations = []
        
        # 获取学习更新历史
        learning_updates = user_history.get("learning_updates", [])
        
        for rec in recommendations:
            adapted_rec = rec.copy()
            
            # 计算渐进调整
            topic = rec.get("topic", "")
            gradual_adjustment = self._calculate_gradual_adjustment(learning_updates, topic)
            
            if gradual_adjustment != 0:
                adapted_rec["relevance_score"] = max(0.0, min(1.0,
                    rec.get("relevance_score", 0.5) + gradual_adjustment
                ))
                adapted_rec["adaptation_applied"] = "gradual_learning"
            
            adapted_recommendations.append(adapted_rec)
        
        return adapted_recommendations
    
    def _batch_adaptation(
        self,
        user_id: str,
        recommendations: list[dict[str, Any]],
        user_history: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """批量适应策略"""
        adapted_recommendations = []
        
        # 分析用户行为模式
        interactions = user_history.get("interactions", [])
        behavior_patterns = self._analyze_behavior_patterns(interactions)
        
        for rec in recommendations:
            adapted_rec = rec.copy()
            
            # 根据行为模式调整
            pattern_score = self._calculate_pattern_score(rec, behavior_patterns)
            
            adapted_rec["relevance_score"] = (
                rec.get("relevance_score", 0.5) * 0.7 + pattern_score * 0.3
            )
            adapted_rec["adaptation_applied"] = "behavior_pattern"
            
            adapted_recommendations.append(adapted_rec)
        
        return adapted_recommendations
    
    def _calculate_confidence_change(
        self,
        interaction_data: dict[str, Any],
        learning_updates: dict[str, Any]
    ) -> float:
        """计算置信度变化"""
        user_feedback = interaction_data.get("user_feedback", {})
        
        if not user_feedback:
            return 0.0
        
        # 基于反馈计算置信度变化
        relevance = user_feedback.get("relevance", 0.5)
        usefulness = user_feedback.get("usefulness", 0.5)
        satisfaction = user_feedback.get("satisfaction", 0.5)
        
        # 计算综合反馈分数
        feedback_score = (relevance + usefulness + satisfaction) / 3
        
        # 转换为置信度变化（-0.5 到 +0.5）
        confidence_change = (feedback_score - 0.5) * 0.5
        
        return confidence_change
    
    def _evaluate_learning_effectiveness(self, user_id: str) -> str:
        """评估学习效果"""
        user_history = self.learning_history.get(user_id, {})
        learning_updates = user_history.get("learning_updates", [])
        
        if len(learning_updates) < 3:
            return "insufficient_data"
        
        # 计算最近的置信度变化趋势
        recent_changes = [
            update.get("confidence_change", 0.0)
            for update in learning_updates[-5:]
        ]
        
        avg_change = sum(recent_changes) / len(recent_changes)
        
        if avg_change > 0.1:
            return "highly_effective"
        elif avg_change > 0.05:
            return "moderately_effective"
        elif avg_change > -0.05:
            return "stable"
        else:
            return "needs_improvement"
    
    def _calculate_adaptation_metrics(
        self,
        original_recommendations: list[dict[str, Any]],
        adapted_recommendations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """计算适应指标"""
        if not original_recommendations or not adapted_recommendations:
            return {}
        
        # 计算分数变化
        original_scores = [r.get("relevance_score", 0.0) for r in original_recommendations]
        adapted_scores = [r.get("relevance_score", 0.0) for r in adapted_recommendations]
        
        score_change = sum(adapted_scores) - sum(original_scores)
        
        # 计算排序变化
        original_order = [r.get("topic", "") for r in original_recommendations]
        adapted_order = [r.get("topic", "") for r in adapted_recommendations]
        
        order_similarity = self._calculate_order_similarity(original_order, adapted_order)
        
        return {
            "score_change": score_change,
            "average_score_change": score_change / len(adapted_scores) if adapted_scores else 0.0,
            "order_similarity": order_similarity,
            "adaptation_intensity": 1.0 - order_similarity,
            "recommendations_modified": sum(1 for r in adapted_recommendations if "adaptation_applied" in r)
        }
    
    def _generate_adaptation_reasoning(
        self,
        strategy: str,
        metrics: dict[str, Any]
    ) -> str:
        """生成适应推理"""
        reasoning_parts = []
        
        strategy_descriptions = {
            "immediate": "基于最近用户反馈进行即时调整",
            "gradual": "基于历史学习数据进行渐进优化",
            "batch": "基于用户行为模式进行批量调整"
        }
        
        reasoning_parts.append(strategy_descriptions.get(strategy, "应用适应策略"))
        
        score_change = metrics.get("average_score_change", 0.0)
        if score_change > 0.05:
            reasoning_parts.append("显著提升了推荐相关性")
        elif score_change < -0.05:
            reasoning_parts.append("调整了推荐优先级")
        else:
            reasoning_parts.append("保持了推荐稳定性")
        
        modified_count = metrics.get("recommendations_modified", 0)
        if modified_count > 0:
            reasoning_parts.append(f"修改了{modified_count}个推荐项")
        
        return "，".join(reasoning_parts) + "。"
    
    def _get_recent_feedback_for_topic(
        self,
        interactions: list[dict[str, Any]],
        topic: str
    ) -> Optional[dict[str, Any]]:
        """获取主题的最近反馈"""
        for interaction in reversed(interactions):
            if topic.lower() in interaction.get("query", "").lower():
                return interaction.get("user_feedback")
        return None
    
    def _calculate_score_adjustment(self, feedback: dict[str, Any]) -> float:
        """计算分数调整"""
        relevance = feedback.get("relevance", 0.5)
        usefulness = feedback.get("usefulness", 0.5)
        
        # 基于反馈计算调整幅度
        feedback_score = (relevance + usefulness) / 2
        adjustment = (feedback_score - 0.5) * 0.2  # 最大调整±0.1
        
        return adjustment
    
    def _calculate_gradual_adjustment(
        self,
        learning_updates: list[dict[str, Any]],
        topic: str
    ) -> float:
        """计算渐进调整"""
        if not learning_updates:
            return 0.0
        
        # 计算该主题的历史置信度变化
        topic_changes = []
        for update in learning_updates[-10:]:  # 最近10次更新
            if topic in str(update):  # 简化的主题匹配
                topic_changes.append(update.get("confidence_change", 0.0))
        
        if not topic_changes:
            return 0.0
        
        # 计算加权平均（最近的权重更高）
        weights = [0.1 * (i + 1) for i in range(len(topic_changes))]
        weighted_sum = sum(change * weight for change, weight in zip(topic_changes, weights, strict=False))
        weight_sum = sum(weights)
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0
    
    def _analyze_behavior_patterns(self, interactions: list[dict[str, Any]]) -> dict[str, Any]:
        """分析行为模式"""
        if not interactions:
            return {}
        
        # 分析交互类型分布
        type_counts = defaultdict(int)
        for interaction in interactions:
            interaction_type = interaction.get("interaction_type", "unknown")
            type_counts[interaction_type] += 1
        
        # 分析时间模式
        time_patterns = self._analyze_time_patterns(interactions)
        
        # 分析内容偏好
        content_preferences = self._analyze_content_preferences(interactions)
        
        return {
            "interaction_types": dict(type_counts),
            "time_patterns": time_patterns,
            "content_preferences": content_preferences,
            "total_interactions": len(interactions)
        }
    
    def _calculate_pattern_score(
        self,
        recommendation: dict[str, Any],
        behavior_patterns: dict[str, Any]
    ) -> float:
        """计算模式分数"""
        base_score = 0.5
        
        # 根据交互类型偏好调整
        rec_type = recommendation.get("recommendation_type", "")
        type_preferences = behavior_patterns.get("interaction_types", {})
        
        if rec_type in type_preferences:
            type_frequency = type_preferences[rec_type]
            total_interactions = behavior_patterns.get("total_interactions", 1)
            type_preference_score = type_frequency / total_interactions
            base_score += (type_preference_score - 0.5) * 0.2
        
        # 根据内容偏好调整
        content_preferences = behavior_patterns.get("content_preferences", {})
        rec_topic = recommendation.get("topic", "")
        
        for preferred_topic, preference_strength in content_preferences.items():
            if preferred_topic.lower() in rec_topic.lower():
                base_score += preference_strength * 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _analyze_time_patterns(self, interactions: list[dict[str, Any]]) -> dict[str, Any]:
        """分析时间模式"""
        hour_counts = defaultdict(int)
        
        for interaction in interactions:
            timestamp = interaction.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour_counts[dt.hour] += 1
                except:
                    pass
        
        if not hour_counts:
            return {}
        
        # 找出最活跃的时间段
        most_active_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        
        return {
            "hourly_distribution": dict(hour_counts),
            "most_active_hour": most_active_hour,
            "activity_spread": len(hour_counts)
        }
    
    def _analyze_content_preferences(self, interactions: list[dict[str, Any]]) -> dict[str, float]:
        """分析内容偏好"""
        content_scores = defaultdict(float)
        
        for interaction in interactions:
            query = interaction.get("query", "").lower()
            feedback = interaction.get("user_feedback", {})
            
            # 提取关键词
            keywords = self._extract_keywords(query)
            
            # 根据反馈调整关键词分数
            feedback_score = feedback.get("satisfaction", 0.5) if feedback else 0.5
            
            for keyword in keywords:
                content_scores[keyword] += feedback_score
        
        # 归一化分数
        if content_scores:
            max_score = max(content_scores.values())
            content_scores = {k: v / max_score for k, v in content_scores.items()}
        
        return dict(content_scores)
    
    def _extract_keywords(self, text: str) -> list[str]:
        """提取关键词"""
        # 简化的关键词提取
        keywords = []
        
        key_terms = [
            "AI伦理", "人工智能", "机器学习", "算法", "透明度",
            "公平性", "隐私", "安全", "监管", "政策"
        ]
        
        for term in key_terms:
            if term.lower() in text:
                keywords.append(term)
        
        return keywords
    
    def _calculate_order_similarity(self, order1: list[str], order2: list[str]) -> float:
        """计算排序相似度"""
        if not order1 or not order2:
            return 0.0
        
        # 使用Kendall tau距离的简化版本
        common_items = set(order1) & set(order2)
        if not common_items:
            return 0.0
        
        # 计算相同项目的排序一致性
        consistent_pairs = 0
        total_pairs = 0
        
        for i, item1 in enumerate(order1):
            if item1 in common_items:
                for j, item2 in enumerate(order1[i+1:], i+1):
                    if item2 in common_items:
                        # 检查在order2中的相对位置是否一致
                        pos1_in_order2 = order2.index(item1) if item1 in order2 else -1
                        pos2_in_order2 = order2.index(item2) if item2 in order2 else -1
                        
                        if pos1_in_order2 != -1 and pos2_in_order2 != -1:
                            if pos1_in_order2 < pos2_in_order2:
                                consistent_pairs += 1
                            total_pairs += 1
        
        return consistent_pairs / total_pairs if total_pairs > 0 else 1.0
    
    def _calculate_average_confidence_change(self, learning_updates: list[dict[str, Any]]) -> float:
        """计算平均置信度变化"""
        if not learning_updates:
            return 0.0
        
        changes = [update.get("confidence_change", 0.0) for update in learning_updates]
        return sum(changes) / len(changes)
    
    def _calculate_learning_velocity(self, learning_updates: list[dict[str, Any]]) -> float:
        """计算学习速度"""
        if len(learning_updates) < 2:
            return 0.0
        
        # 计算置信度变化的变化率
        changes = [update.get("confidence_change", 0.0) for update in learning_updates]
        
        velocity = 0.0
        for i in range(1, len(changes)):
            velocity += abs(changes[i] - changes[i-1])
        
        return velocity / (len(changes) - 1)
    
    def _calculate_model_stability(self, learning_updates: list[dict[str, Any]]) -> float:
        """计算模型稳定性"""
        if not learning_updates:
            return 1.0
        
        changes = [update.get("confidence_change", 0.0) for update in learning_updates]
        
        if len(changes) < 2:
            return 1.0
        
        # 计算变化的标准差
        mean_change = sum(changes) / len(changes)
        variance = sum((x - mean_change) ** 2 for x in changes) / len(changes)
        std_dev = math.sqrt(variance)
        
        # 稳定性与标准差成反比
        stability = 1.0 / (1.0 + std_dev)
        
        return stability
    
    def _calculate_prediction_accuracy(self, user_id: str) -> float:
        """计算预测准确性"""
        # 简化的准确性计算
        user_history = self.learning_history.get(user_id, {})
        interactions = user_history.get("interactions", [])
        
        if not interactions:
            return 0.5
        
        # 基于用户反馈计算准确性
        feedback_scores = []
        for interaction in interactions:
            feedback = interaction.get("user_feedback", {})
            if feedback:
                relevance = feedback.get("relevance", 0.5)
                usefulness = feedback.get("usefulness", 0.5)
                avg_feedback = (relevance + usefulness) / 2
                feedback_scores.append(avg_feedback)
        
        if not feedback_scores:
            return 0.5
        
        return sum(feedback_scores) / len(feedback_scores)
    
    def _evaluate_overall_effectiveness(self, learning_metrics: dict[str, Any]) -> str:
        """评估整体效果"""
        confidence_change = learning_metrics.get("average_confidence_change", 0.0)
        prediction_accuracy = learning_metrics.get("prediction_accuracy", 0.5)
        model_stability = learning_metrics.get("model_stability", 0.5)
        
        # 综合评分
        overall_score = (
            confidence_change * 0.4 +
            (prediction_accuracy - 0.5) * 0.4 +
            (model_stability - 0.5) * 0.2
        )
        
        if overall_score > 0.15:
            return "excellent"
        elif overall_score > 0.05:
            return "good"
        elif overall_score > -0.05:
            return "fair"
        else:
            return "poor"
    
    def _generate_improvement_suggestions(self, learning_metrics: dict[str, Any]) -> list[str]:
        """生成改进建议"""
        suggestions = []
        
        confidence_change = learning_metrics.get("average_confidence_change", 0.0)
        if confidence_change < 0:
            suggestions.append("需要收集更多高质量的用户反馈")
        
        prediction_accuracy = learning_metrics.get("prediction_accuracy", 0.5)
        if prediction_accuracy < 0.6:
            suggestions.append("建议优化推荐算法以提高准确性")
        
        model_stability = learning_metrics.get("model_stability", 0.5)
        if model_stability < 0.7:
            suggestions.append("需要增强模型稳定性，减少过度调整")
        
        learning_velocity = learning_metrics.get("learning_velocity", 0.0)
        if learning_velocity < 0.01:
            suggestions.append("可以增加学习率以加快适应速度")
        elif learning_velocity > 0.1:
            suggestions.append("建议降低学习率以提高稳定性")
        
        if not suggestions:
            suggestions.append("当前学习效果良好，继续保持")
        
        return suggestions
    
    def _analyze_learning_trend(self, learning_updates: list[dict[str, Any]]) -> str:
        """分析学习趋势"""
        if len(learning_updates) < 3:
            return "insufficient_data"
        
        recent_changes = [
            update.get("confidence_change", 0.0)
            for update in learning_updates[-5:]
        ]
        
        # 计算趋势
        if len(recent_changes) >= 3:
            early_avg = sum(recent_changes[:2]) / 2
            late_avg = sum(recent_changes[-2:]) / 2
            
            if late_avg > early_avg + 0.05:
                return "improving"
            elif late_avg < early_avg - 0.05:
                return "declining"
            else:
                return "stable"
        
        return "stable"
    
    def _identify_optimization_targets(self, learning_metrics: dict[str, Any]) -> list[str]:
        """识别优化目标"""
        targets = []
        
        prediction_accuracy = learning_metrics.get("prediction_accuracy", 0.5)
        if prediction_accuracy < 0.7:
            targets.append("prediction_accuracy")
        
        model_stability = learning_metrics.get("model_stability", 0.5)
        if model_stability < 0.8:
            targets.append("model_stability")
        
        learning_velocity = learning_metrics.get("learning_velocity", 0.0)
        if learning_velocity < 0.02:
            targets.append("learning_speed")
        
        confidence_change = learning_metrics.get("average_confidence_change", 0.0)
        if confidence_change < 0.02:
            targets.append("user_satisfaction")
        
        return targets if targets else ["maintain_current_performance"]


class UserPreferenceLearningModel:
    """用户偏好学习模型"""
    
    def __init__(self):
        self.preference_weights = {}
        self.learning_rate = 0.1
    
    def update(self, interaction_data: dict[str, Any]) -> dict[str, Any]:
        """更新用户偏好"""
        user_feedback = interaction_data.get("user_feedback", {})
        query = interaction_data.get("query", "")
        
        # 简化的偏好更新逻辑
        if user_feedback and query:
            satisfaction = user_feedback.get("satisfaction", 0.5)
            adjustment = (satisfaction - 0.5) * self.learning_rate
            
            # 更新查询相关的偏好权重
            for word in query.lower().split():
                if word not in self.preference_weights:
                    self.preference_weights[word] = 0.5
                self.preference_weights[word] += adjustment
                self.preference_weights[word] = max(0.0, min(1.0, self.preference_weights[word]))
        
        return {
            "updated_preferences": len(self.preference_weights),
            "adjustment_applied": adjustment if 'adjustment' in locals() else 0.0
        }
    
    def get_adjustment_recommendation(self) -> Optional[dict[str, Any]]:
        """获取调整建议"""
        if not self.preference_weights:
            return None
        
        # 找出最强和最弱的偏好
        sorted_prefs = sorted(self.preference_weights.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "strongest_preference": sorted_prefs[0] if sorted_prefs else None,
            "weakest_preference": sorted_prefs[-1] if sorted_prefs else None,
            "total_preferences": len(self.preference_weights)
        }


class ContentEffectivenessModel:
    """内容效果模型"""
    
    def __init__(self):
        self.content_scores = {}
    
    def update(self, interaction_data: dict[str, Any]) -> dict[str, Any]:
        """更新内容效果"""
        content_type = interaction_data.get("content_type", "default")
        user_feedback = interaction_data.get("user_feedback", {})
        
        if user_feedback:
            usefulness = user_feedback.get("usefulness", 0.5)
            
            if content_type not in self.content_scores:
                self.content_scores[content_type] = []
            
            self.content_scores[content_type].append(usefulness)
            
            # 保持最近20个评分
            if len(self.content_scores[content_type]) > 20:
                self.content_scores[content_type] = self.content_scores[content_type][-20:]
        
        return {
            "content_type": content_type,
            "score_count": len(self.content_scores.get(content_type, [])),
            "average_score": sum(self.content_scores.get(content_type, [0.5])) / len(self.content_scores.get(content_type, [0.5]))
        }
    
    def get_adjustment_recommendation(self) -> Optional[dict[str, Any]]:
        """获取调整建议"""
        if not self.content_scores:
            return None
        
        # 计算各内容类型的平均分数
        avg_scores = {}
        for content_type, scores in self.content_scores.items():
            if scores:
                avg_scores[content_type] = sum(scores) / len(scores)
        
        if not avg_scores:
            return None
        
        best_content = max(avg_scores.items(), key=lambda x: x[1])
        worst_content = min(avg_scores.items(), key=lambda x: x[1])
        
        return {
            "best_performing_content": best_content,
            "worst_performing_content": worst_content,
            "content_type_count": len(avg_scores)
        }


class InteractionPatternModel:
    """交互模式模型"""
    
    def __init__(self):
        self.interaction_patterns = {}
    
    def update(self, interaction_data: dict[str, Any]) -> dict[str, Any]:
        """更新交互模式"""
        interaction_type = interaction_data.get("interaction_type", "unknown")
        timestamp = interaction_data.get("timestamp", datetime.now().isoformat())
        
        if interaction_type not in self.interaction_patterns:
            self.interaction_patterns[interaction_type] = {
                "count": 0,
                "timestamps": [],
                "success_rate": 0.5
            }
        
        pattern = self.interaction_patterns[interaction_type]
        pattern["count"] += 1
        pattern["timestamps"].append(timestamp)
        
        # 保持最近50个时间戳
        if len(pattern["timestamps"]) > 50:
            pattern["timestamps"] = pattern["timestamps"][-50:]
        
        # 更新成功率
        user_feedback = interaction_data.get("user_feedback", {})
        if user_feedback:
            satisfaction = user_feedback.get("satisfaction", 0.5)
            pattern["success_rate"] = (pattern["success_rate"] * 0.9 + satisfaction * 0.1)
        
        return {
            "interaction_type": interaction_type,
            "total_count": pattern["count"],
            "success_rate": pattern["success_rate"]
        }
    
    def get_adjustment_recommendation(self) -> Optional[dict[str, Any]]:
        """获取调整建议"""
        if not self.interaction_patterns:
            return None
        
        # 找出最成功和最不成功的交互类型
        success_rates = {
            itype: pattern["success_rate"]
            for itype, pattern in self.interaction_patterns.items()
        }
        
        best_interaction = max(success_rates.items(), key=lambda x: x[1])
        worst_interaction = min(success_rates.items(), key=lambda x: x[1])
        
        return {
            "most_successful_interaction": best_interaction,
            "least_successful_interaction": worst_interaction,
            "total_interaction_types": len(success_rates)
        }


class RecommendationQualityModel:
    """推荐质量模型"""
    
    def __init__(self):
        self.quality_history = []
        self.quality_trends = {}
    
    def update(self, interaction_data: dict[str, Any]) -> dict[str, Any]:
        """更新推荐质量"""
        user_feedback = interaction_data.get("user_feedback", {})
        
        if user_feedback:
            relevance = user_feedback.get("relevance", 0.5)
            usefulness = user_feedback.get("usefulness", 0.5)
            
            quality_score = (relevance + usefulness) / 2
            
            quality_record = {
                "timestamp": datetime.now().isoformat(),
                "quality_score": quality_score,
                "relevance": relevance,
                "usefulness": usefulness
            }
            
            self.quality_history.append(quality_record)
            
            # 保持最近100个记录
            if len(self.quality_history) > 100:
                self.quality_history = self.quality_history[-100:]
        
        return {
            "quality_records": len(self.quality_history),
            "latest_quality_score": quality_record["quality_score"] if 'quality_record' in locals() else 0.5,
            "average_quality": sum(r["quality_score"] for r in self.quality_history) / len(self.quality_history) if self.quality_history else 0.5
        }
    
    def get_adjustment_recommendation(self) -> Optional[dict[str, Any]]:
        """获取调整建议"""
        if len(self.quality_history) < 5:
            return None
        
        recent_scores = [r["quality_score"] for r in self.quality_history[-10:]]
        older_scores = [r["quality_score"] for r in self.quality_history[-20:-10]] if len(self.quality_history) >= 20 else []
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores) if older_scores else recent_avg
        
        trend = "improving" if recent_avg > older_avg + 0.05 else "declining" if recent_avg < older_avg - 0.05 else "stable"
        
        return {
            "quality_trend": trend,
            "recent_average": recent_avg,
            "quality_change": recent_avg - older_avg,
            "recommendation": "continue_current_approach" if trend == "improving" else "needs_optimization" if trend == "declining" else "maintain_stability"
        }