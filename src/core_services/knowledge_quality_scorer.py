#!/usr/bin/env python3
"""知识质量评分器

评估知识条目的质量和可信度
"""

import logging
import re
import statistics
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

logger = logging.getLogger(__name__)


class KnowledgeQualityScorer:
    """知识质量评分器"""

    def __init__(self):
        """初始化知识质量评分器"""
        self.quality_metrics = [
            "accuracy",
            "completeness",
            "reliability",
            "clarity",
            "currency",
            "relevance"
        ]
        self.scoring_history = []

        # 质量评分权重
        self.metric_weights = {
            "accuracy": 0.25,
            "completeness": 0.20,
            "reliability": 0.20,
            "clarity": 0.15,
            "currency": 0.10,
            "relevance": 0.10
        }
<<<<<<< HEAD

    def score_knowledge(self, knowledge_data: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def score_knowledge(self, knowledge_data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """评估知识质量"""
        try:
            score_result = {
                "knowledge_id": knowledge_data.get("id", "unknown"),
                "title": knowledge_data.get("title", ""),
                "timestamp": datetime.now().isoformat(),
                "scores": {},
                "overall_score": 0.0,
                "quality_grade": "",
                "recommendations": []
            }

            # 计算各项质量指标
            score_result["scores"]["accuracy_score"] = self.evaluate_accuracy(knowledge_data)
            score_result["scores"]["completeness_score"] = self.assess_completeness(knowledge_data)
            score_result["scores"]["reliability_score"] = self._evaluate_reliability(knowledge_data)
            score_result["scores"]["clarity_score"] = self._evaluate_clarity(knowledge_data)
            score_result["scores"]["currency_score"] = self._evaluate_currency(knowledge_data)
            score_result["scores"]["relevance_score"] = self._evaluate_relevance(knowledge_data)

            # 计算总体质量分数
            overall_score = 0.0
            for metric, weight in self.metric_weights.items():
                score_key = f"{metric}_score"
                if score_key in score_result["scores"]:
                    overall_score += score_result["scores"][score_key] * weight

            score_result["overall_score"] = overall_score
            score_result["quality_grade"] = self._determine_quality_grade(overall_score)
            score_result["recommendations"] = self._generate_recommendations(score_result["scores"])

            # 记录评分历史
            self.scoring_history.append(score_result)

            return score_result

        except Exception as e:
            logger.error(f"评估知识质量失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def evaluate_accuracy(self, knowledge_data: Dict[str, Any]) -> float:
=======
    
    def evaluate_accuracy(self, knowledge_data: dict[str, Any]) -> float:
>>>>>>> feature/core-services-refactor
        """评估准确性"""
        try:
            accuracy_score = 0.0

            # 基于证据质量评估
            evidence = knowledge_data.get("evidence", [])
            if evidence:
                evidence_quality = self._assess_evidence_quality(evidence)
                accuracy_score += evidence_quality * 0.4

            # 基于来源可信度评估
            sources = knowledge_data.get("sources", [])
            if sources:
                source_credibility = self._assess_source_credibility(sources)
                accuracy_score += source_credibility * 0.3

            # 基于作者专业度评估
            author_expertise = knowledge_data.get("author_expertise", 0.5)
            accuracy_score += author_expertise * 0.2

            # 基于同行验证评估
            peer_validation = knowledge_data.get("peer_validation", 0.0)
            accuracy_score += peer_validation * 0.1

            return min(accuracy_score, 1.0)

        except Exception as e:
            logger.error(f"评估准确性失败: {e}")
            return 0.0
<<<<<<< HEAD

    def assess_completeness(self, knowledge_data: Dict[str, Any]) -> float:
=======
    
    def assess_completeness(self, knowledge_data: dict[str, Any]) -> float:
>>>>>>> feature/core-services-refactor
        """评估完整性"""
        try:
            completeness_score = 0.0

            # 内容长度评估
            content = knowledge_data.get("content", "")
            if len(content) > 500:
                completeness_score += 0.3
            elif len(content) > 200:
                completeness_score += 0.2
            elif len(content) > 100:
                completeness_score += 0.1

            # 结构完整性评估
            required_fields = ["title", "content", "sources"]
            present_fields = sum(1 for field in required_fields if knowledge_data.get(field))
            completeness_score += (present_fields / len(required_fields)) * 0.3

            # 引用和参考资料评估
            references = knowledge_data.get("references", [])
            if references:
                completeness_score += min(len(references) * 0.1, 0.2)

            # 示例和案例评估
            examples = knowledge_data.get("examples", [])
            if examples:
                completeness_score += min(len(examples) * 0.05, 0.1)

            # 相关链接评估
            related_links = knowledge_data.get("related_links", [])
            if related_links:
                completeness_score += min(len(related_links) * 0.02, 0.1)

            return min(completeness_score, 1.0)

        except Exception as e:
            logger.error(f"评估完整性失败: {e}")
            return 0.0
<<<<<<< HEAD

    def _evaluate_reliability(self, knowledge_data: Dict[str, Any]) -> float:
=======
    
    def _evaluate_reliability(self, knowledge_data: dict[str, Any]) -> float:
>>>>>>> feature/core-services-refactor
        """评估可靠性"""
        try:
            reliability_score = 0.0

            # 来源多样性评估
            sources = knowledge_data.get("sources", [])
            if len(sources) >= 3:
                reliability_score += 0.3
            elif len(sources) >= 2:
                reliability_score += 0.2
            elif len(sources) >= 1:
                reliability_score += 0.1

            # 发布时间评估
            publication_date = knowledge_data.get("publication_date")
            if publication_date:
                currency_factor = self._calculate_currency_factor(publication_date)
                reliability_score += currency_factor * 0.2

            # 更新频率评估
            update_history = knowledge_data.get("update_history", [])
            if update_history:
                update_factor = min(len(update_history) * 0.1, 0.2)
                reliability_score += update_factor

            # 验证状态评估
            verification_status = knowledge_data.get("verification_status", "unverified")
            if verification_status == "verified":
                reliability_score += 0.2
            elif verification_status == "peer_reviewed":
                reliability_score += 0.3

            # 争议程度评估
            controversy_level = knowledge_data.get("controversy_level", 0.0)
            reliability_score += (1.0 - controversy_level) * 0.1

            return min(reliability_score, 1.0)

        except Exception as e:
            logger.error(f"评估可靠性失败: {e}")
            return 0.0
<<<<<<< HEAD

    def _evaluate_clarity(self, knowledge_data: Dict[str, Any]) -> float:
=======
    
    def _evaluate_clarity(self, knowledge_data: dict[str, Any]) -> float:
>>>>>>> feature/core-services-refactor
        """评估清晰度"""
        try:
            clarity_score = 0.0

            content = knowledge_data.get("content", "")
            if not content:
                return 0.0

            # 句子长度评估
            sentences = re.split(r'[.!?]+', content)
            if sentences:
                avg_sentence_length = statistics.mean(len(s.split()) for s in sentences if s.strip())
                if 10 <= avg_sentence_length <= 25:
                    clarity_score += 0.3
                elif 5 <= avg_sentence_length <= 35:
                    clarity_score += 0.2
                else:
                    clarity_score += 0.1

            # 段落结构评估
            paragraphs = content.split('\n\n')
            if len(paragraphs) > 1:
                clarity_score += 0.2

            # 专业术语解释评估
            technical_terms = knowledge_data.get("technical_terms", [])
            explained_terms = knowledge_data.get("explained_terms", [])
            if technical_terms and explained_terms:
                explanation_ratio = len(explained_terms) / len(technical_terms)
                clarity_score += explanation_ratio * 0.2

            # 格式化评估
            if knowledge_data.get("formatted", False):
                clarity_score += 0.1

            # 可读性评估（简化版）
            readability_score = self._calculate_readability(content)
            clarity_score += readability_score * 0.2

            return min(clarity_score, 1.0)

        except Exception as e:
            logger.error(f"评估清晰度失败: {e}")
            return 0.0
<<<<<<< HEAD

    def _evaluate_currency(self, knowledge_data: Dict[str, Any]) -> float:
=======
    
    def _evaluate_currency(self, knowledge_data: dict[str, Any]) -> float:
>>>>>>> feature/core-services-refactor
        """评估时效性"""
        try:
            # 获取最后更新时间
            last_updated = knowledge_data.get("last_updated")
            if not last_updated:
                last_updated = knowledge_data.get("created_date")

            if not last_updated:
                return 0.5  # 默认中等时效性

            return self._calculate_currency_factor(last_updated)

        except Exception as e:
            logger.error(f"评估时效性失败: {e}")
            return 0.0
<<<<<<< HEAD

    def _evaluate_relevance(self, knowledge_data: Dict[str, Any]) -> float:
=======
    
    def _evaluate_relevance(self, knowledge_data: dict[str, Any]) -> float:
>>>>>>> feature/core-services-refactor
        """评估相关性"""
        try:
            relevance_score = 0.0

            # 标签匹配评估
            tags = knowledge_data.get("tags", [])
            if tags:
                relevance_score += min(len(tags) * 0.1, 0.3)

            # 分类准确性评估
            category = knowledge_data.get("category")
            if category:
                relevance_score += 0.2

            # 关键词密度评估
            keywords = knowledge_data.get("keywords", [])
            content = knowledge_data.get("content", "")
            if keywords and content:
                keyword_density = self._calculate_keyword_density(content, keywords)
                relevance_score += keyword_density * 0.3

            # 用户反馈评估
            user_ratings = knowledge_data.get("user_ratings", [])
            if user_ratings:
                avg_rating = statistics.mean(user_ratings)
                relevance_score += (avg_rating / 5.0) * 0.2  # 假设5分制

            return min(relevance_score, 1.0)

        except Exception as e:
            logger.error(f"评估相关性失败: {e}")
            return 0.0
<<<<<<< HEAD

    def _assess_evidence_quality(self, evidence: List[str]) -> float:
=======
    
    def _assess_evidence_quality(self, evidence: list[str]) -> float:
>>>>>>> feature/core-services-refactor
        """评估证据质量"""
        if not evidence:
            return 0.0

        quality_score = 0.0

        for item in evidence:
            # 简单的证据质量评估
            if "实验" in item or "研究" in item or "数据" in item:
                quality_score += 0.3
            elif "专家" in item or "权威" in item:
                quality_score += 0.2
            else:
                quality_score += 0.1

        return min(quality_score / len(evidence), 1.0)
<<<<<<< HEAD

    def _assess_source_credibility(self, sources: List[str]) -> float:
=======
    
    def _assess_source_credibility(self, sources: list[str]) -> float:
>>>>>>> feature/core-services-refactor
        """评估来源可信度"""
        if not sources:
            return 0.0

        credibility_score = 0.0

        for source in sources:
            # 简单的来源可信度评估
            if any(keyword in source.lower() for keyword in ["学术", "期刊", "大学", "研究院"]):
                credibility_score += 0.4
            elif any(keyword in source.lower() for keyword in ["政府", "官方", "权威"]):
                credibility_score += 0.3
            elif any(keyword in source.lower() for keyword in ["新闻", "媒体"]):
                credibility_score += 0.2
            else:
                credibility_score += 0.1

        return min(credibility_score / len(sources), 1.0)

    def _calculate_currency_factor(self, date_string: str) -> float:
        """计算时效性因子"""
        try:
            from datetime import datetime

            if isinstance(date_string, str):
                # 尝试解析日期
                try:
                    date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                except:
                    return 0.5  # 解析失败，返回中等值
            else:
                return 0.5

            # 计算距今天数
            days_ago = (datetime.now() - date).days

            # 时效性评分（越新越好）
            if days_ago <= 30:
                return 1.0
            elif days_ago <= 90:
                return 0.8
            elif days_ago <= 180:
                return 0.6
            elif days_ago <= 365:
                return 0.4
            else:
                return 0.2

        except Exception as e:
            logger.error(f"计算时效性因子失败: {e}")
            return 0.5

    def _calculate_readability(self, content: str) -> float:
        """计算可读性（简化版）"""
        try:
            if not content:
                return 0.0

            # 简单的可读性指标
            words = content.split()
            sentences = re.split(r'[.!?]+', content)

            if not words or not sentences:
                return 0.0

            avg_words_per_sentence = len(words) / len(sentences)

            # 理想的每句话词数在10-20之间
            if 10 <= avg_words_per_sentence <= 20:
                return 1.0
            elif 5 <= avg_words_per_sentence <= 30:
                return 0.7
            else:
                return 0.4

        except Exception as e:
            logger.error(f"计算可读性失败: {e}")
            return 0.0
<<<<<<< HEAD

    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> float:
=======
    
    def _calculate_keyword_density(self, content: str, keywords: list[str]) -> float:
>>>>>>> feature/core-services-refactor
        """计算关键词密度"""
        try:
            if not content or not keywords:
                return 0.0

            content_lower = content.lower()
            total_words = len(content.split())
            keyword_count = 0

            for keyword in keywords:
                keyword_count += content_lower.count(keyword.lower())

            density = keyword_count / total_words if total_words > 0 else 0.0

            # 理想的关键词密度在2%-8%之间
            if 0.02 <= density <= 0.08:
                return 1.0
            elif 0.01 <= density <= 0.15:
                return 0.7
            else:
                return 0.4

        except Exception as e:
            logger.error(f"计算关键词密度失败: {e}")
            return 0.0

    def _determine_quality_grade(self, overall_score: float) -> str:
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
<<<<<<< HEAD

    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
=======
    
    def _generate_recommendations(self, scores: dict[str, float]) -> list[str]:
>>>>>>> feature/core-services-refactor
        """生成改进建议"""
        recommendations = []

        if scores.get("accuracy_score", 0.0) < 0.7:
            recommendations.append("增加可靠的证据和来源以提高准确性")

        if scores.get("completeness_score", 0.0) < 0.7:
            recommendations.append("补充更多详细信息和相关内容")

        if scores.get("reliability_score", 0.0) < 0.7:
            recommendations.append("增加权威来源和同行验证")

        if scores.get("clarity_score", 0.0) < 0.7:
            recommendations.append("改进文本结构和表达清晰度")

        if scores.get("currency_score", 0.0) < 0.7:
            recommendations.append("更新内容以保持时效性")

        if scores.get("relevance_score", 0.0) < 0.7:
            recommendations.append("优化关键词和标签以提高相关性")

        if not recommendations:
            recommendations.append("内容质量良好，继续保持")

        return recommendations
<<<<<<< HEAD

    def get_scoring_statistics(self) -> Dict[str, Any]:
=======
    
    def get_scoring_statistics(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取评分统计"""
        try:
            if not self.scoring_history:
                return {"message": "暂无评分历史"}

            stats = {
                "total_scored": len(self.scoring_history),
                "average_scores": {},
                "quality_distribution": {},
                "recent_scores": self.scoring_history[-10:]
            }

            # 计算平均分数
            for metric in self.quality_metrics:
                score_key = f"{metric}_score"
                scores = [item["scores"].get(score_key, 0.0) for item in self.scoring_history]
                stats["average_scores"][metric] = statistics.mean(scores) if scores else 0.0

            # 质量等级分布
            grades = [item["quality_grade"] for item in self.scoring_history]
            for grade in grades:
                stats["quality_distribution"][grade] = stats["quality_distribution"].get(grade, 0) + 1

            return stats

        except Exception as e:
            logger.error(f"获取评分统计失败: {e}")
            return {"error": str(e)}
