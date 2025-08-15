#!/usr/bin/env python3
"""上下文协作创建引擎

支持用户与系统协作优化提示和上下文
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """协作类型枚举"""
    PROMPT_OPTIMIZATION = "prompt_optimization"
    CONTEXT_ENHANCEMENT = "context_enhancement"
    PERSONALIZATION = "personalization"
    QUALITY_IMPROVEMENT = "quality_improvement"


class SuggestionType(Enum):
    """建议类型枚举"""
    STRUCTURE = "structure"
    CONTENT = "content"
    STYLE = "style"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"


@dataclass
class CollaborationSession:
    """协作会话"""
    session_id: str
    user_id: str
    collaboration_type: CollaborationType
    original_context: str
    current_context: str
    iterations: list[dict[str, Any]]
    quality_scores: list[float]
    user_preferences: dict[str, Any]
    created_at: str
    last_updated: str


@dataclass
class ContextSuggestion:
    """上下文建议"""
    suggestion_id: str
    suggestion_type: SuggestionType
    title: str
    description: str
    original_text: str
    suggested_text: str
    confidence: float
    reasoning: str
    impact_score: float


class ContextCollaborationEngine:
    """上下文协作创建引擎"""
    
    def __init__(self):
        """初始化上下文协作创建引擎"""
        self.active_sessions = {}  # {session_id: CollaborationSession}
        self.quality_evaluator = ContextQualityEvaluator()
        self.suggestion_generator = ContextSuggestionGenerator()
        self.personalization_engine = PersonalizationEngine()
        
        # 协作模式配置
        self.collaboration_modes = {
            "guided": {
                "description": "系统引导的协作模式",
                "system_initiative": 0.7,
                "user_control": 0.3,
                "suggestion_frequency": "high"
            },
            "balanced": {
                "description": "平衡的协作模式",
                "system_initiative": 0.5,
                "user_control": 0.5,
                "suggestion_frequency": "medium"
            },
            "user_driven": {
                "description": "用户主导的协作模式",
                "system_initiative": 0.3,
                "user_control": 0.7,
                "suggestion_frequency": "low"
            }
        }
        
        logger.info("上下文协作创建引擎初始化完成")
    
    def start_collaboration_session(
        self,
        user_id: str,
        initial_context: str,
        collaboration_type: CollaborationType,
        user_preferences: dict[str, Any] = None
    ) -> dict[str, Any]:
        """开始协作会话"""
        try:
            session_id = f"collab_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 创建协作会话
            session = CollaborationSession(
                session_id=session_id,
                user_id=user_id,
                collaboration_type=collaboration_type,
                original_context=initial_context,
                current_context=initial_context,
                iterations=[],
                quality_scores=[],
                user_preferences=user_preferences or {},
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
            
            self.active_sessions[session_id] = session
            
            # 初始质量评估
            initial_quality = self.quality_evaluator.evaluate_context(initial_context)
            session.quality_scores.append(initial_quality["overall_score"])
            
            # 生成初始建议
            initial_suggestions = self.suggestion_generator.generate_suggestions(
                initial_context,
                collaboration_type,
                user_preferences
            )
            
            # 记录初始迭代
            initial_iteration = {
                "iteration_number": 0,
                "timestamp": datetime.now().isoformat(),
                "context": initial_context,
                "quality_score": initial_quality["overall_score"],
                "suggestions": initial_suggestions,
                "user_action": "session_start",
                "system_response": "initial_analysis"
            }
            
            session.iterations.append(initial_iteration)
            
            result = {
                "session_id": session_id,
                "collaboration_type": collaboration_type.value,
                "initial_quality": initial_quality,
                "initial_suggestions": initial_suggestions,
                "collaboration_modes": self.collaboration_modes,
                "session_status": "active",
                "next_steps": self._generate_next_steps(session, initial_suggestions)
            }
            
            logger.info(f"协作会话开始: {session_id}, 类型: {collaboration_type.value}")
            return result
            
        except Exception as e:
            logger.error(f"开始协作会话失败: {e}")
            return {"error": str(e)}
    
    def process_user_input(
        self,
        session_id: str,
        user_input: dict[str, Any]
    ) -> dict[str, Any]:
        """处理用户输入"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"协作会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # 解析用户输入
            action_type = user_input.get("action_type", "modify")
            modified_context = user_input.get("context", session.current_context)
            user_feedback = user_input.get("feedback", {})
            selected_suggestions = user_input.get("selected_suggestions", [])
            
            # 应用用户修改
            if action_type == "modify":
                session.current_context = modified_context
            elif action_type == "apply_suggestions":
                session.current_context = self._apply_suggestions(
                    session.current_context,
                    selected_suggestions
                )
            elif action_type == "revert":
                revert_to = user_input.get("revert_to", 0)
                if revert_to < len(session.iterations):
                    session.current_context = session.iterations[revert_to]["context"]
            
            # 评估新的上下文质量
            new_quality = self.quality_evaluator.evaluate_context(session.current_context)
            session.quality_scores.append(new_quality["overall_score"])
            
            # 更新用户偏好
            if user_feedback:
                session.user_preferences = self._update_user_preferences(
                    session.user_preferences,
                    user_feedback
                )
            
            # 生成新建议
            new_suggestions = self.suggestion_generator.generate_suggestions(
                session.current_context,
                session.collaboration_type,
                session.user_preferences
            )
            
            # 记录迭代
            iteration = {
                "iteration_number": len(session.iterations),
                "timestamp": datetime.now().isoformat(),
                "context": session.current_context,
                "quality_score": new_quality["overall_score"],
                "suggestions": new_suggestions,
                "user_action": action_type,
                "user_input": user_input,
                "quality_improvement": new_quality["overall_score"] - session.quality_scores[-2] if len(session.quality_scores) > 1 else 0
            }
            
            session.iterations.append(iteration)
            session.last_updated = datetime.now().isoformat()
            
            # 生成响应
            result = {
                "session_id": session_id,
                "iteration_number": iteration["iteration_number"],
                "updated_context": session.current_context,
                "quality_assessment": new_quality,
                "quality_improvement": iteration["quality_improvement"],
                "new_suggestions": new_suggestions,
                "collaboration_progress": self._calculate_collaboration_progress(session),
                "next_steps": self._generate_next_steps(session, new_suggestions)
            }
            
            logger.info(f"用户输入处理完成: {session_id}, 迭代: {iteration['iteration_number']}")
            return result
            
        except Exception as e:
            logger.error(f"处理用户输入失败: {e}")
            return {"error": str(e)}
    
    def get_personalized_recommendations(
        self,
        session_id: str,
        context_type: str = "general"
    ) -> dict[str, Any]:
        """获取个性化推荐"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"协作会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # 生成个性化推荐
            recommendations = self.personalization_engine.generate_recommendations(
                user_id=session.user_id,
                current_context=session.current_context,
                user_preferences=session.user_preferences,
                collaboration_history=session.iterations,
                context_type=context_type
            )
            
            result = {
                "session_id": session_id,
                "context_type": context_type,
                "recommendations": recommendations,
                "personalization_confidence": recommendations.get("confidence", 0.5),
                "recommendation_reasoning": recommendations.get("reasoning", ""),
                "applicable_suggestions": self._filter_applicable_suggestions(
                    recommendations.get("suggestions", []),
                    session.current_context
                )
            }
            
            logger.info(f"个性化推荐生成完成: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"获取个性化推荐失败: {e}")
            return {"error": str(e)}
    
    def finalize_collaboration(
        self,
        session_id: str,
        user_satisfaction: dict[str, Any] = None
    ) -> dict[str, Any]:
        """完成协作"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"协作会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # 计算协作统计
            collaboration_stats = self._calculate_collaboration_stats(session)
            
            # 生成协作报告
            collaboration_report = {
                "session_id": session_id,
                "user_id": session.user_id,
                "collaboration_type": session.collaboration_type.value,
                "duration": self._calculate_session_duration(session),
                "iterations_count": len(session.iterations),
                "quality_improvement": session.quality_scores[-1] - session.quality_scores[0] if session.quality_scores else 0,
                "final_context": session.current_context,
                "collaboration_stats": collaboration_stats,
                "user_satisfaction": user_satisfaction,
                "learned_preferences": session.user_preferences,
                "completion_time": datetime.now().isoformat()
            }
            
            # 保存协作经验
            self._save_collaboration_experience(session, collaboration_report)
            
            # 清理会话
            del self.active_sessions[session_id]
            
            logger.info(f"协作完成: {session_id}, 质量提升: {collaboration_report['quality_improvement']:.3f}")
            return collaboration_report
            
        except Exception as e:
            logger.error(f"完成协作失败: {e}")
            return {"error": str(e)}
    
    def _apply_suggestions(
        self,
        context: str,
        suggestions: list[dict[str, Any]]
    ) -> str:
        """应用建议"""
        modified_context = context
        
        # 按影响分数排序，先应用影响大的建议
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: x.get("impact_score", 0),
            reverse=True
        )
        
        for suggestion in sorted_suggestions:
            original_text = suggestion.get("original_text", "")
            suggested_text = suggestion.get("suggested_text", "")
            
            if original_text and suggested_text and original_text in modified_context:
                modified_context = modified_context.replace(original_text, suggested_text)
        
        return modified_context
    
    def _update_user_preferences(
        self,
        current_preferences: dict[str, Any],
        feedback: dict[str, Any]
    ) -> dict[str, Any]:
        """更新用户偏好"""
        updated_preferences = current_preferences.copy()
        
        # 处理建议反馈
        suggestion_feedback = feedback.get("suggestion_feedback", {})
        for suggestion_id, rating in suggestion_feedback.items():
            if "suggestion_ratings" not in updated_preferences:
                updated_preferences["suggestion_ratings"] = {}
            updated_preferences["suggestion_ratings"][suggestion_id] = rating
        
        # 处理风格偏好
        style_preferences = feedback.get("style_preferences", {})
        if style_preferences:
            if "style" not in updated_preferences:
                updated_preferences["style"] = {}
            updated_preferences["style"].update(style_preferences)
        
        # 处理协作模式偏好
        collaboration_mode = feedback.get("preferred_collaboration_mode")
        if collaboration_mode:
            updated_preferences["collaboration_mode"] = collaboration_mode
        
        return updated_preferences
    
    def _calculate_collaboration_progress(self, session: CollaborationSession) -> dict[str, Any]:
        """计算协作进度"""
        if not session.quality_scores:
            return {"progress": 0.0, "status": "starting"}
        
        initial_quality = session.quality_scores[0]
        current_quality = session.quality_scores[-1]
        
        # 计算质量改进进度
        quality_improvement = current_quality - initial_quality
        
        # 计算迭代效率
        iteration_efficiency = quality_improvement / len(session.iterations) if session.iterations else 0
        
        # 确定协作状态
        if quality_improvement > 0.2:
            status = "excellent_progress"
        elif quality_improvement > 0.1:
            status = "good_progress"
        elif quality_improvement > 0:
            status = "moderate_progress"
        else:
            status = "needs_improvement"
        
        return {
            "progress": min(1.0, max(0.0, quality_improvement / 0.3)),  # 假设0.3为最大期望改进
            "status": status,
            "quality_improvement": quality_improvement,
            "iteration_efficiency": iteration_efficiency,
            "iterations_completed": len(session.iterations)
        }
    
    def _generate_next_steps(
        self,
        session: CollaborationSession,
        suggestions: list[dict[str, Any]]
    ) -> list[str]:
        """生成下一步建议"""
        next_steps = []
        
        # 基于当前质量分数生成建议
        current_quality = session.quality_scores[-1] if session.quality_scores else 0.5
        
        if current_quality < 0.6:
            next_steps.append("建议重点关注内容的清晰度和完整性")
        
        if current_quality < 0.7:
            next_steps.append("可以考虑优化上下文的结构和逻辑")
        
        # 基于建议生成下一步
        high_impact_suggestions = [
            s for s in suggestions
            if s.get("impact_score", 0) > 0.7
        ]
        
        if high_impact_suggestions:
            next_steps.append(f"有{len(high_impact_suggestions)}个高影响力建议可以应用")
        
        # 基于协作类型生成建议
        if session.collaboration_type == CollaborationType.PROMPT_OPTIMIZATION:
            next_steps.append("可以尝试调整提示的具体性和指导性")
        elif session.collaboration_type == CollaborationType.CONTEXT_ENHANCEMENT:
            next_steps.append("考虑添加更多相关背景信息")
        
        if not next_steps:
            next_steps.append("继续迭代优化，或考虑完成当前协作")
        
        return next_steps
    
    def _calculate_collaboration_stats(self, session: CollaborationSession) -> dict[str, Any]:
        """计算协作统计"""
        stats = {
            "total_iterations": len(session.iterations),
            "quality_scores": session.quality_scores,
            "average_quality": sum(session.quality_scores) / len(session.quality_scores) if session.quality_scores else 0,
            "quality_trend": "improving" if len(session.quality_scores) > 1 and session.quality_scores[-1] > session.quality_scores[0] else "stable",
            "suggestions_generated": sum(len(iter.get("suggestions", [])) for iter in session.iterations),
            "user_actions": [iter.get("user_action") for iter in session.iterations],
            "collaboration_efficiency": self._calculate_efficiency(session)
        }
        
        return stats
    
    def _calculate_efficiency(self, session: CollaborationSession) -> float:
        """计算协作效率"""
        if not session.quality_scores or len(session.quality_scores) < 2:
            return 0.0
        
        quality_improvement = session.quality_scores[-1] - session.quality_scores[0]
        iterations_count = len(session.iterations)
        
        # 效率 = 质量改进 / 迭代次数
        efficiency = quality_improvement / iterations_count if iterations_count > 0 else 0.0
        
        return max(0.0, efficiency)
    
    def _calculate_session_duration(self, session: CollaborationSession) -> str:
        """计算会话持续时间"""
        try:
            start_time = datetime.fromisoformat(session.created_at)
            end_time = datetime.fromisoformat(session.last_updated)
            duration = end_time - start_time
            
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            if hours > 0:
                return f"{hours}小时{minutes}分钟"
            else:
                return f"{minutes}分钟"
                
        except Exception:
            return "未知"
    
    def _filter_applicable_suggestions(
        self,
        suggestions: list[dict[str, Any]],
        current_context: str
    ) -> list[dict[str, Any]]:
        """过滤适用的建议"""
        applicable = []
        
        for suggestion in suggestions:
            original_text = suggestion.get("original_text", "")
            if not original_text or original_text in current_context:
                applicable.append(suggestion)
        
        return applicable
    
    def _save_collaboration_experience(
        self,
        session: CollaborationSession,
        report: dict[str, Any]
    ):
        """保存协作经验"""
        # 简化实现，实际应该保存到持久化存储
        logger.info(f"保存协作经验: {session.session_id}")


class ContextQualityEvaluator:
    """上下文质量评估器"""
    
    def __init__(self):
        """初始化质量评估器"""
        self.evaluation_criteria = {
            "clarity": {
                "weight": 0.25,
                "description": "清晰度",
                "evaluator": self._evaluate_clarity
            },
            "completeness": {
                "weight": 0.25,
                "description": "完整性",
                "evaluator": self._evaluate_completeness
            },
            "relevance": {
                "weight": 0.2,
                "description": "相关性",
                "evaluator": self._evaluate_relevance
            },
            "structure": {
                "weight": 0.15,
                "description": "结构性",
                "evaluator": self._evaluate_structure
            },
            "specificity": {
                "weight": 0.15,
                "description": "具体性",
                "evaluator": self._evaluate_specificity
            }
        }
    
    def evaluate_context(self, context: str) -> dict[str, Any]:
        """评估上下文质量"""
        try:
            scores = {}
            detailed_feedback = {}
            
            # 对每个标准进行评估
            for criterion, config in self.evaluation_criteria.items():
                evaluator = config["evaluator"]
                score, feedback = evaluator(context)
                scores[criterion] = score
                detailed_feedback[criterion] = feedback
            
            # 计算加权总分
            overall_score = sum(
                scores[criterion] * config["weight"]
                for criterion, config in self.evaluation_criteria.items()
            )
            
            # 生成改进建议
            improvement_suggestions = self._generate_improvement_suggestions(scores, detailed_feedback)
            
            result = {
                "overall_score": overall_score,
                "criterion_scores": scores,
                "detailed_feedback": detailed_feedback,
                "improvement_suggestions": improvement_suggestions,
                "quality_level": self._determine_quality_level(overall_score),
                "evaluation_timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"评估上下文质量失败: {e}")
            return {
                "overall_score": 0.5,
                "error": str(e)
            }
    
    def _evaluate_clarity(self, context: str) -> tuple[float, str]:
        """评估清晰度"""
        # 简化的清晰度评估
        score = 0.5
        feedback = "基础清晰度评估"
        
        # 检查句子长度
        sentences = re.split(r'[.!?。！？]', context)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / len([s for s in sentences if s.strip()]) if sentences else 0
        
        if avg_sentence_length < 15:
            score += 0.2
            feedback += "，句子长度适中"
        elif avg_sentence_length > 30:
            score -= 0.1
            feedback += "，句子可能过长"
        
        # 检查专业术语密度
        technical_terms = len(re.findall(r'[A-Z]{2,}|[a-z]+(?:[A-Z][a-z]*)+', context))
        if technical_terms / len(context.split()) < 0.1:
            score += 0.1
            feedback += "，术语使用适度"
        
        return min(1.0, max(0.0, score)), feedback
    
    def _evaluate_completeness(self, context: str) -> tuple[float, str]:
        """评估完整性"""
        score = 0.5
        feedback = "基础完整性评估"
        
        # 检查长度
        word_count = len(context.split())
        if word_count > 50:
            score += 0.2
            feedback += "，内容较为充实"
        elif word_count < 20:
            score -= 0.2
            feedback += "，内容可能过于简短"
        
        # 检查结构元素
        has_context = "背景" in context or "context" in context.lower()
        has_objective = "目标" in context or "目的" in context or "objective" in context.lower()
        has_requirements = "要求" in context or "需要" in context or "requirement" in context.lower()
        
        structure_score = sum([has_context, has_objective, has_requirements]) / 3
        score += structure_score * 0.3
        
        if structure_score > 0.6:
            feedback += "，包含关键结构元素"
        
        return min(1.0, max(0.0, score)), feedback
    
    def _evaluate_relevance(self, context: str) -> tuple[float, str]:
        """评估相关性"""
        score = 0.6  # 默认中等相关性
        feedback = "相关性评估"
        
        # 检查主题一致性（简化实现）
        context_lower = context.lower()
        
        # AI相关关键词
        ai_keywords = ["ai", "人工智能", "机器学习", "算法", "模型", "智能"]
        ai_mentions = sum(1 for keyword in ai_keywords if keyword in context_lower)
        
        if ai_mentions > 0:
            score += min(0.3, ai_mentions * 0.1)
            feedback += f"，包含{ai_mentions}个AI相关术语"
        
        return min(1.0, max(0.0, score)), feedback
    
    def _evaluate_structure(self, context: str) -> tuple[float, str]:
        """评估结构性"""
        score = 0.5
        feedback = "结构性评估"
        
        # 检查段落结构
        paragraphs = [p.strip() for p in context.split('\n') if p.strip()]
        if len(paragraphs) > 1:
            score += 0.2
            feedback += f"，包含{len(paragraphs)}个段落"
        
        # 检查列表或编号
        has_lists = bool(re.search(r'[1-9]\.|•|·|-\s', context))
        if has_lists:
            score += 0.2
            feedback += "，包含列表结构"
        
        # 检查逻辑连接词
        connectors = ["因此", "所以", "但是", "然而", "首先", "其次", "最后"]
        connector_count = sum(1 for conn in connectors if conn in context)
        if connector_count > 0:
            score += min(0.2, connector_count * 0.05)
            feedback += "，使用了逻辑连接词"
        
        return min(1.0, max(0.0, score)), feedback
    
    def _evaluate_specificity(self, context: str) -> tuple[float, str]:
        """评估具体性"""
        score = 0.5
        feedback = "具体性评估"
        
        # 检查数字和具体数据
        numbers = len(re.findall(r'\d+', context))
        if numbers > 0:
            score += min(0.3, numbers * 0.1)
            feedback += f"，包含{numbers}个具体数据"
        
        # 检查具体示例
        example_indicators = ["例如", "比如", "举例", "示例", "案例"]
        examples = sum(1 for indicator in example_indicators if indicator in context)
        if examples > 0:
            score += min(0.2, examples * 0.1)
            feedback += "，包含具体示例"
        
        # 检查模糊词汇
        vague_words = ["一些", "很多", "大量", "少量", "可能", "也许"]
        vague_count = sum(1 for word in vague_words if word in context)
        if vague_count > 3:
            score -= 0.1
            feedback += "，存在较多模糊表达"
        
        return min(1.0, max(0.0, score)), feedback
    
    def _generate_improvement_suggestions(
        self,
        scores: dict[str, float],
        feedback: dict[str, str]
    ) -> list[str]:
        """生成改进建议"""
        suggestions = []
        
        # 找出得分最低的标准
        lowest_score_criterion = min(scores.items(), key=lambda x: x[1])
        criterion, score = lowest_score_criterion
        
        if score < 0.6:
            if criterion == "clarity":
                suggestions.append("建议简化句子结构，使用更清晰的表达")
            elif criterion == "completeness":
                suggestions.append("建议补充更多背景信息和具体要求")
            elif criterion == "relevance":
                suggestions.append("建议增强内容与主题的相关性")
            elif criterion == "structure":
                suggestions.append("建议改善内容的组织结构和逻辑性")
            elif criterion == "specificity":
                suggestions.append("建议添加更多具体的数据和示例")
        
        # 通用建议
        if all(score < 0.7 for score in scores.values()):
            suggestions.append("整体质量有待提升，建议全面优化")
        
        return suggestions
    
    def _determine_quality_level(self, overall_score: float) -> str:
        """确定质量等级"""
        if overall_score >= 0.9:
            return "优秀"
        elif overall_score >= 0.8:
            return "良好"
        elif overall_score >= 0.7:
            return "中等"
        elif overall_score >= 0.6:
            return "及格"
        else:
            return "需要改进"


class ContextSuggestionGenerator:
    """上下文建议生成器"""
    
    def __init__(self):
        """初始化建议生成器"""
        self.suggestion_templates = {
            SuggestionType.STRUCTURE: [
                {
                    "pattern": r"^(.{200,}?)$",
                    "suggestion": "考虑将长段落分解为多个较短的段落",
                    "confidence": 0.7
                },
                {
                    "pattern": r"^(?!.*[1-9]\.)(?!.*•)(.+)$",
                    "suggestion": "考虑使用编号或项目符号来组织内容",
                    "confidence": 0.6
                }
            ],
            SuggestionType.CONTENT: [
                {
                    "pattern": r"(?!.*背景)(?!.*context)(.+)",
                    "suggestion": "建议添加相关背景信息",
                    "confidence": 0.8
                },
                {
                    "pattern": r"(?!.*示例)(?!.*例如)(.+)",
                    "suggestion": "考虑添加具体示例来说明要点",
                    "confidence": 0.7
                }
            ],
            SuggestionType.CLARITY: [
                {
                    "pattern": r"(.{50,}?[，,]){3,}",
                    "suggestion": "考虑简化复杂句子，提高可读性",
                    "confidence": 0.8
                }
            ]
        }
    
    def generate_suggestions(
        self,
        context: str,
        collaboration_type: CollaborationType,
        user_preferences: dict[str, Any] = None
    ) -> list[dict[str, Any]]:
        """生成建议"""
        try:
            suggestions = []
            suggestion_id = 0
            
            # 基于模板生成建议
            for suggestion_type, templates in self.suggestion_templates.items():
                for template in templates:
                    if re.search(template["pattern"], context, re.DOTALL):
                        suggestion = ContextSuggestion(
                            suggestion_id=f"sugg_{suggestion_id}",
                            suggestion_type=suggestion_type,
                            title=template["suggestion"],
                            description=self._generate_detailed_description(template, context),
                            original_text=self._extract_relevant_text(context, template["pattern"]),
                            suggested_text=self._generate_suggested_text(context, template),
                            confidence=template["confidence"],
                            reasoning=self._generate_reasoning(template, collaboration_type),
                            impact_score=self._calculate_impact_score(template, context)
                        )
                        
                        suggestions.append({
                            "suggestion_id": suggestion.suggestion_id,
                            "type": suggestion.suggestion_type.value,
                            "title": suggestion.title,
                            "description": suggestion.description,
                            "original_text": suggestion.original_text,
                            "suggested_text": suggestion.suggested_text,
                            "confidence": suggestion.confidence,
                            "reasoning": suggestion.reasoning,
                            "impact_score": suggestion.impact_score
                        })
                        
                        suggestion_id += 1
            
            # 基于协作类型生成特定建议
            type_specific_suggestions = self._generate_type_specific_suggestions(
                context, collaboration_type, suggestion_id
            )
            suggestions.extend(type_specific_suggestions)
            
            # 基于用户偏好过滤和排序
            if user_preferences:
                suggestions = self._filter_by_preferences(suggestions, user_preferences)
            
            # 按影响分数排序
            suggestions.sort(key=lambda x: x["impact_score"], reverse=True)
            
            return suggestions[:10]  # 返回前10个建议
            
        except Exception as e:
            logger.error(f"生成建议失败: {e}")
            return []
    
    def _generate_detailed_description(self, template: dict[str, Any], context: str) -> str:
        """生成详细描述"""
        base_description = template["suggestion"]
        
        # 添加上下文相关的详细信息
        context_length = len(context)
        if context_length > 500:
            base_description += "。当前内容较长，结构化组织将显著提升可读性。"
        elif context_length < 100:
            base_description += "。当前内容较短，可以考虑添加更多细节。"
        
        return base_description
    
    def _extract_relevant_text(self, context: str, pattern: str) -> str:
        """提取相关文本"""
        match = re.search(pattern, context, re.DOTALL)
        if match:
            return match.group(0)[:100] + "..." if len(match.group(0)) > 100 else match.group(0)
        return ""
    
    def _generate_suggested_text(self, context: str, template: dict[str, Any]) -> str:
        """生成建议文本"""
        # 简化实现，实际应该基于具体模板生成
        if "段落" in template["suggestion"]:
            # 尝试分段
            sentences = re.split(r'[.。]', context)
            if len(sentences) > 2:
                mid_point = len(sentences) // 2
                return f"{'.'.join(sentences[:mid_point])}.\\n\\n{'.'.join(sentences[mid_point:])}"
        
        return context  # 默认返回原文本
    
    def _generate_reasoning(self, template: dict[str, Any], collaboration_type: CollaborationType) -> str:
        """生成推理说明"""
        base_reasoning = f"基于{collaboration_type.value}的需求，"
        
        if "结构" in template["suggestion"]:
            base_reasoning += "良好的结构有助于提高内容的可读性和理解性"
        elif "背景" in template["suggestion"]:
            base_reasoning += "充分的背景信息有助于读者更好地理解上下文"
        elif "示例" in template["suggestion"]:
            base_reasoning += "具体示例能够使抽象概念更加清晰易懂"
        else:
            base_reasoning += "此改进将提升整体质量"
        
        return base_reasoning
    
    def _calculate_impact_score(self, template: dict[str, Any], context: str) -> float:
        """计算影响分数"""
        base_score = template["confidence"]
        
        # 根据上下文特征调整影响分数
        context_length = len(context)
        
        if "结构" in template["suggestion"] and context_length > 300:
            base_score += 0.2  # 长文本的结构化影响更大
        
        if "背景" in template["suggestion"] and context_length < 200:
            base_score += 0.1  # 短文本更需要背景信息
        
        return min(1.0, base_score)
    
    def _generate_type_specific_suggestions(
        self,
        context: str,
        collaboration_type: CollaborationType,
        start_id: int
    ) -> list[dict[str, Any]]:
        """生成特定类型的建议"""
        suggestions = []
        
        if collaboration_type == CollaborationType.PROMPT_OPTIMIZATION:
            if "请" not in context and "帮助" not in context:
                suggestions.append({
                    "suggestion_id": f"sugg_{start_id}",
                    "type": "content",
                    "title": "添加明确的请求语句",
                    "description": "提示应该包含明确的请求或指令",
                    "original_text": context[:50] + "...",
                    "suggested_text": f"请{context}",
                    "confidence": 0.8,
                    "reasoning": "明确的请求语句有助于AI更好地理解用户意图",
                    "impact_score": 0.9
                })
        
        elif collaboration_type == CollaborationType.CONTEXT_ENHANCEMENT:
            if "目标" not in context and "目的" not in context:
                suggestions.append({
                    "suggestion_id": f"sugg_{start_id + 1}",
                    "type": "content",
                    "title": "明确目标或目的",
                    "description": "添加明确的目标描述有助于提供更准确的上下文",
                    "original_text": context[:50] + "...",
                    "suggested_text": f"目标：[请描述具体目标]\\n\\n{context}",
                    "confidence": 0.85,
                    "reasoning": "明确的目标有助于理解上下文的意图和方向",
                    "impact_score": 0.8
                })
        
        return suggestions
    
    def _filter_by_preferences(
        self,
        suggestions: list[dict[str, Any]],
        user_preferences: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """根据用户偏好过滤建议"""
        filtered_suggestions = []
        
        # 获取用户偏好的建议类型
        preferred_types = user_preferences.get("preferred_suggestion_types", [])
        min_confidence = user_preferences.get("min_confidence", 0.5)
        
        for suggestion in suggestions:
            # 过滤置信度
            if suggestion["confidence"] < min_confidence:
                continue
            
            # 过滤类型偏好
            if preferred_types and suggestion["type"] not in preferred_types:
                continue
            
            filtered_suggestions.append(suggestion)
        
        return filtered_suggestions


class PersonalizationEngine:
    """个性化引擎"""
    
    def __init__(self):
        """初始化个性化引擎"""
        self.user_profiles = {}  # {user_id: profile}
        
    def generate_recommendations(
        self,
        user_id: str,
        current_context: str,
        user_preferences: dict[str, Any],
        collaboration_history: list[dict[str, Any]],
        context_type: str = "general"
    ) -> dict[str, Any]:
        """生成个性化推荐"""
        try:
            # 分析用户历史行为
            behavior_analysis = self._analyze_user_behavior(collaboration_history)
            
            # 生成个性化建议
            personalized_suggestions = self._generate_personalized_suggestions(
                current_context,
                user_preferences,
                behavior_analysis,
                context_type
            )
            
            # 计算推荐置信度
            confidence = self._calculate_recommendation_confidence(
                user_preferences,
                behavior_analysis
            )
            
            # 生成推荐理由
            reasoning = self._generate_recommendation_reasoning(
                behavior_analysis,
                user_preferences
            )
            
            result = {
                "user_id": user_id,
                "context_type": context_type,
                "suggestions": personalized_suggestions,
                "confidence": confidence,
                "reasoning": reasoning,
                "behavior_insights": behavior_analysis,
                "recommendation_timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"生成个性化推荐失败: {e}")
            return {
                "suggestions": [],
                "confidence": 0.5,
                "reasoning": "个性化推荐生成失败",
                "error": str(e)
            }
    
    def _analyze_user_behavior(self, collaboration_history: list[dict[str, Any]]) -> dict[str, Any]:
        """分析用户行为"""
        if not collaboration_history:
            return {"pattern": "insufficient_data"}
        
        # 分析用户行为模式
        action_counts = {}
        quality_improvements = []
        
        for iteration in collaboration_history:
            action = iteration.get("user_action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
            
            quality_improvement = iteration.get("quality_improvement", 0)
            if quality_improvement != 0:
                quality_improvements.append(quality_improvement)
        
        # 确定用户类型
        user_type = self._determine_user_type(action_counts)
        
        # 计算平均质量改进
        avg_improvement = sum(quality_improvements) / len(quality_improvements) if quality_improvements else 0
        
        return {
            "user_type": user_type,
            "action_patterns": action_counts,
            "average_quality_improvement": avg_improvement,
            "collaboration_effectiveness": "high" if avg_improvement > 0.1 else "medium" if avg_improvement > 0 else "low",
            "total_iterations": len(collaboration_history)
        }
    
    def _determine_user_type(self, action_counts: dict[str, int]) -> str:
        """确定用户类型"""
        total_actions = sum(action_counts.values())
        if total_actions == 0:
            return "new_user"
        
        modify_ratio = action_counts.get("modify", 0) / total_actions
        apply_suggestions_ratio = action_counts.get("apply_suggestions", 0) / total_actions
        
        if modify_ratio > 0.6:
            return "hands_on_editor"
        elif apply_suggestions_ratio > 0.6:
            return "suggestion_follower"
        else:
            return "balanced_collaborator"
    
    def _generate_personalized_suggestions(
        self,
        context: str,
        user_preferences: dict[str, Any],
        behavior_analysis: dict[str, Any],
        context_type: str
    ) -> list[dict[str, Any]]:
        """生成个性化建议"""
        suggestions = []
        
        user_type = behavior_analysis.get("user_type", "balanced_collaborator")
        
        # 基于用户类型生成建议
        if user_type == "hands_on_editor":
            suggestions.append({
                "type": "workflow",
                "title": "建议采用渐进式编辑方式",
                "description": "基于您的编辑习惯，建议分步骤逐步完善内容",
                "confidence": 0.8
            })
        
        elif user_type == "suggestion_follower":
            suggestions.append({
                "type": "workflow",
                "title": "提供更多具体的修改建议",
                "description": "为您准备了详细的修改建议，可以直接应用",
                "confidence": 0.9
            })
        
        # 基于上下文类型生成建议
        if context_type == "prompt":
            suggestions.append({
                "type": "content",
                "title": "优化提示结构",
                "description": "建议使用'角色-任务-格式'的结构来组织提示",
                "confidence": 0.7
            })
        
        return suggestions
    
    def _calculate_recommendation_confidence(
        self,
        user_preferences: dict[str, Any],
        behavior_analysis: dict[str, Any]
    ) -> float:
        """计算推荐置信度"""
        base_confidence = 0.5
        
        # 基于历史数据量调整置信度
        total_iterations = behavior_analysis.get("total_iterations", 0)
        if total_iterations > 5:
            base_confidence += 0.2
        elif total_iterations > 2:
            base_confidence += 0.1
        
        # 基于协作效果调整置信度
        effectiveness = behavior_analysis.get("collaboration_effectiveness", "medium")
        if effectiveness == "high":
            base_confidence += 0.2
        elif effectiveness == "low":
            base_confidence -= 0.1
        
        # 基于用户偏好完整性调整置信度
        if len(user_preferences) > 3:
            base_confidence += 0.1
        
        return min(1.0, max(0.0, base_confidence))
    
    def _generate_recommendation_reasoning(
        self,
        behavior_analysis: dict[str, Any],
        user_preferences: dict[str, Any]
    ) -> str:
        """生成推荐理由"""
        user_type = behavior_analysis.get("user_type", "balanced_collaborator")
        effectiveness = behavior_analysis.get("collaboration_effectiveness", "medium")
        
        reasoning_parts = []
        
        # 基于用户类型的理由
        type_descriptions = {
            "hands_on_editor": "您倾向于直接编辑内容",
            "suggestion_follower": "您更喜欢采用系统建议",
            "balanced_collaborator": "您在编辑和采用建议之间保持平衡",
            "new_user": "基于新用户的一般模式"
        }
        
        reasoning_parts.append(type_descriptions.get(user_type, "基于您的协作模式"))
        
        # 基于效果的理由
        if effectiveness == "high":
            reasoning_parts.append("您的协作效果很好")
        elif effectiveness == "low":
            reasoning_parts.append("建议调整协作策略以提高效果")
        
        # 基于偏好的理由
        if user_preferences:
            reasoning_parts.append("结合您的个人偏好设置")
        
        return "，".join(reasoning_parts) + "，为您定制了这些推荐。"