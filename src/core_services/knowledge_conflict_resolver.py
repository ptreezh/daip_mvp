#!/usr/bin/env python3
"""知识冲突解决器

自动识别和处理知识矛盾
"""

import logging
import re
import uuid
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class KnowledgeConflictResolver:
    """知识冲突解决器"""

    def __init__(self):
        """初始化知识冲突解决器"""
        self.conflict_detection_rules = self._initialize_detection_rules()
        self.resolution_strategies = self._initialize_resolution_strategies()
        self.conflict_history = []

        # 冲突类型定义
        self.conflict_types = {
            "contradictory_claims": "矛盾声明",
            "inconsistent_data": "数据不一致",
            "temporal_conflicts": "时间冲突",
            "source_disagreement": "来源分歧",
            "confidence_conflicts": "置信度冲突"
        }

    def detect_conflicts(self, knowledge_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """检测知识冲突"""
        try:
            conflicts = []

            # 两两比较知识项
            for i in range(len(knowledge_items)):
                for j in range(i + 1, len(knowledge_items)):
                    item1 = knowledge_items[i]
                    item2 = knowledge_items[j]

                    # 应用检测规则
                    for rule_name, rule_func in self.conflict_detection_rules.items():
                        conflict = rule_func(item1, item2)
                        if conflict:
                            conflict["conflict_id"] = str(uuid.uuid4())
                            conflict["detection_rule"] = rule_name
                            conflict["timestamp"] = datetime.now().isoformat()
                            conflicts.append(conflict)

            # 记录冲突历史
            for conflict in conflicts:
                self.conflict_history.append({
                    "conflict_id": conflict["conflict_id"],
                    "detection_time": conflict["timestamp"],
                    "conflict_type": conflict["conflict_type"],
                    "status": "detected"
                })

            return conflicts

        except Exception as e:
            logger.error(f"检测知识冲突失败: {e}")
            return []

    def resolve_conflict(self, conflict: dict[str, Any]) -> dict[str, Any]:
        """解决冲突"""
        try:
            conflict_type = conflict.get("conflict_type", "unknown")

            # 选择解决策略
            strategy_name = self._select_resolution_strategy(conflict)
            strategy_func = self.resolution_strategies.get(strategy_name)

            if not strategy_func:
                return {"error": f"未找到解决策略: {strategy_name}"}

            # 应用解决策略
            resolution = strategy_func(conflict)

            # 添加元数据
            resolution.update({
                "resolution_id": str(uuid.uuid4()),
                "conflict_id": conflict.get("conflict_id"),
                "strategy": strategy_name,
                "resolution_time": datetime.now().isoformat()
            })

            # 更新冲突历史
            for history_item in self.conflict_history:
                if history_item["conflict_id"] == conflict.get("conflict_id"):
                    history_item["status"] = "resolved"
                    history_item["resolution_id"] = resolution["resolution_id"]
                    history_item["resolution_time"] = resolution["resolution_time"]
                    break

            return resolution

        except Exception as e:
            logger.error(f"解决冲突失败: {e}")
            return {"error": str(e)}

    def validate_resolution(self, resolution: dict[str, Any]) -> dict[str, Any]:
        """验证解决方案"""
        try:
            validation_result = {
                "is_valid": True,
                "validation_score": 0.0,
                "validation_issues": [],
                "validation_time": datetime.now().isoformat()
            }

            # 检查必要字段
            required_fields = ["resolved_content", "confidence_score", "evidence"]
            for field in required_fields:
                if field not in resolution:
                    validation_result["validation_issues"].append(f"缺少必要字段: {field}")
                    validation_result["is_valid"] = False

            if not validation_result["is_valid"]:
                validation_result["validation_score"] = 0.0
                return validation_result

            # 评估解决方案质量
            quality_score = 0.0

            # 内容质量评估
            content = resolution.get("resolved_content", "")
            if len(content) > 50:
                quality_score += 0.3
            elif len(content) > 20:
                quality_score += 0.2
            else:
                quality_score += 0.1

            # 置信度评估
            confidence = resolution.get("confidence_score", 0.0)
            if confidence >= 0.8:
                quality_score += 0.3
            elif confidence >= 0.6:
                quality_score += 0.2
            else:
                quality_score += 0.1

            # 证据质量评估
            evidence = resolution.get("evidence", [])
            if len(evidence) >= 3:
                quality_score += 0.3
            elif len(evidence) >= 2:
                quality_score += 0.2
            elif len(evidence) >= 1:
                quality_score += 0.1

            # 一致性检查
            if self._check_internal_consistency(resolution):
                quality_score += 0.1
            else:
                validation_result["validation_issues"].append("内部一致性检查失败")

            validation_result["validation_score"] = min(quality_score, 1.0)

            # 如果分数太低，标记为无效
            if validation_result["validation_score"] < 0.5:
                validation_result["is_valid"] = False
                validation_result["validation_issues"].append("解决方案质量分数过低")

            return validation_result

        except Exception as e:
            logger.error(f"验证解决方案失败: {e}")
            return {"is_valid": False, "error": str(e)}

    def _initialize_detection_rules(self) -> dict[str, callable]:
        """初始化冲突检测规则"""
        return {
            "contradictory_claims": self._detect_contradictory_claims,
            "inconsistent_data": self._detect_inconsistent_data,
            "temporal_conflicts": self._detect_temporal_conflicts,
            "source_disagreement": self._detect_source_disagreement,
            "confidence_conflicts": self._detect_confidence_conflicts
        }

    def _initialize_resolution_strategies(self) -> dict[str, callable]:
        """初始化解决策略"""
        return {
            "evidence_weighting": self._resolve_by_evidence_weighting,
            "source_credibility": self._resolve_by_source_credibility,
            "temporal_priority": self._resolve_by_temporal_priority,
            "confidence_based": self._resolve_by_confidence,
            "synthesis": self._resolve_by_synthesis
        }

    def _detect_contradictory_claims(self, item1: dict[str, Any], item2: dict[str, Any]) -> Optional[dict[str, Any]]:
        """检测矛盾声明"""
        try:
            content1 = item1.get("content", "").lower()
            content2 = item2.get("content", "").lower()

            # 简单的矛盾检测逻辑
            contradictory_pairs = [
                ("安全", "危险"), ("可靠", "不可靠"), ("准确", "不准确"),
                ("有效", "无效"), ("成功", "失败"), ("支持", "反对"),
                ("是", "不是"), ("能", "不能"), ("会", "不会")
            ]

            for pos, neg in contradictory_pairs:
                if (pos in content1 and neg in content2) or (neg in content1 and pos in content2):
                    return {
                        "conflict_type": "contradictory_claims",
                        "conflicting_items": [item1, item2],
                        "severity": "high",
                        "description": f"检测到矛盾声明: '{pos}' vs '{neg}'",
                        "confidence": 0.8
                    }

            # 检查数值矛盾
            numbers1 = re.findall(r'\d+(?:\.\d+)?%?', content1)
            numbers2 = re.findall(r'\d+(?:\.\d+)?%?', content2)

            if numbers1 and numbers2:
                # 简化处理：如果数值差异很大，可能存在矛盾
                try:
                    num1 = float(numbers1[0].replace('%', ''))
                    num2 = float(numbers2[0].replace('%', ''))

                    if abs(num1 - num2) > 20:  # 差异超过20的阈值
                        return {
                            "conflict_type": "contradictory_claims",
                            "conflicting_items": [item1, item2],
                            "severity": "medium",
                            "description": f"数值差异较大: {num1} vs {num2}",
                            "confidence": 0.6
                        }
                except ValueError:
                    pass

            return None

        except Exception as e:
            logger.error(f"检测矛盾声明失败: {e}")
            return None

    def _detect_inconsistent_data(self, item1: dict[str, Any], item2: dict[str, Any]) -> Optional[dict[str, Any]]:
        """检测数据不一致"""
        try:
            # 检查相同主题的不同数据
            title1 = item1.get("title", "").lower()
            title2 = item2.get("title", "").lower()

            # 如果标题相似但内容不同，可能存在数据不一致
            similarity = SequenceMatcher(None, title1, title2).ratio()

            if similarity > 0.7:  # 标题相似
                content1 = item1.get("content", "")
                content2 = item2.get("content", "")
                content_similarity = SequenceMatcher(None, content1, content2).ratio()

                if content_similarity < 0.5:  # 但内容差异较大
                    return {
                        "conflict_type": "inconsistent_data",
                        "conflicting_items": [item1, item2],
                        "severity": "medium",
                        "description": "相似主题但数据不一致",
                        "confidence": 0.7
                    }

            return None

        except Exception as e:
            logger.error(f"检测数据不一致失败: {e}")
            return None

    def _detect_temporal_conflicts(self, item1: dict[str, Any], item2: dict[str, Any]) -> Optional[dict[str, Any]]:
        """检测时间冲突"""
        try:
            timestamp1 = item1.get("timestamp")
            timestamp2 = item2.get("timestamp")

            if not timestamp1 or not timestamp2:
                return None

            # 如果较新的信息与较旧的信息矛盾，可能存在时间冲突
            time1 = datetime.fromisoformat(timestamp1.replace('Z', '+00:00'))
            time2 = datetime.fromisoformat(timestamp2.replace('Z', '+00:00'))

            # 简化处理：检查是否存在明显的时间顺序问题
            time_diff = abs((time2 - time1).days)

            if time_diff > 30:  # 时间差超过30天
                # 检查内容是否存在矛盾
                content1 = item1.get("content", "").lower()
                content2 = item2.get("content", "").lower()

                if "最新" in content1 and "过时" in content2:
                    return {
                        "conflict_type": "temporal_conflicts",
                        "conflicting_items": [item1, item2],
                        "severity": "low",
                        "description": "时间顺序可能存在问题",
                        "confidence": 0.5
                    }

            return None

        except Exception as e:
            logger.error(f"检测时间冲突失败: {e}")
            return None

    def _detect_source_disagreement(self, item1: dict[str, Any], item2: dict[str, Any]) -> Optional[dict[str, Any]]:
        """检测来源分歧"""
        try:
            source1 = item1.get("source", "")
            source2 = item2.get("source", "")

            if not source1 or not source2 or source1 == source2:
                return None

            # 检查不同来源是否对同一主题有不同观点
            content1 = item1.get("content", "").lower()
            content2 = item2.get("content", "").lower()

            # 简单的主题相似性检查
            common_keywords = set(content1.split()) & set(content2.split())

            if len(common_keywords) > 3:  # 有足够的共同关键词
                # 检查观点是否不同
                sentiment1 = self._analyze_sentiment(content1)
                sentiment2 = self._analyze_sentiment(content2)

                if abs(sentiment1 - sentiment2) > 0.5:  # 情感倾向差异较大
                    return {
                        "conflict_type": "source_disagreement",
                        "conflicting_items": [item1, item2],
                        "severity": "medium",
                        "description": f"不同来源观点分歧: {source1} vs {source2}",
                        "confidence": 0.6
                    }

            return None

        except Exception as e:
            logger.error(f"检测来源分歧失败: {e}")
            return None

    def _detect_confidence_conflicts(self, item1: dict[str, Any], item2: dict[str, Any]) -> Optional[dict[str, Any]]:
        """检测置信度冲突"""
        try:
            confidence1 = item1.get("confidence", 0.5)
            confidence2 = item2.get("confidence", 0.5)

            # 如果置信度差异很大且内容相关，可能存在冲突
            confidence_diff = abs(confidence1 - confidence2)

            if confidence_diff > 0.4:  # 置信度差异超过0.4
                content1 = item1.get("content", "")
                content2 = item2.get("content", "")

                # 检查内容相似性
                similarity = SequenceMatcher(None, content1, content2).ratio()

                if similarity > 0.3:  # 内容有一定相似性
                    return {
                        "conflict_type": "confidence_conflicts",
                        "conflicting_items": [item1, item2],
                        "severity": "low",
                        "description": f"相似内容但置信度差异较大: {confidence1:.2f} vs {confidence2:.2f}",
                        "confidence": 0.4
                    }

            return None

        except Exception as e:
            logger.error(f"检测置信度冲突失败: {e}")
            return None

    def _select_resolution_strategy(self, conflict: dict[str, Any]) -> str:
        """选择解决策略"""
        conflict_type = conflict.get("conflict_type", "unknown")
        severity = conflict.get("severity", "medium")

        # 基于冲突类型和严重程度选择策略
        if conflict_type == "contradictory_claims":
            if severity == "high":
                return "evidence_weighting"
            else:
                return "synthesis"
        elif conflict_type == "inconsistent_data":
            return "source_credibility"
        elif conflict_type == "temporal_conflicts":
            return "temporal_priority"
        elif conflict_type == "source_disagreement":
            return "source_credibility"
        elif conflict_type == "confidence_conflicts":
            return "confidence_based"
        else:
            return "synthesis"  # 默认策略

    def _resolve_by_evidence_weighting(self, conflict: dict[str, Any]) -> dict[str, Any]:
        """基于证据权重解决冲突"""
        try:
            conflicting_items = conflict.get("conflicting_items", [])

            # 评估每个项目的证据强度
            evidence_scores = []
            for item in conflicting_items:
                score = 0.0

                # 基于来源可信度
                source = item.get("source", "")
                if "学术" in source or "研究" in source:
                    score += 0.4
                elif "官方" in source or "权威" in source:
                    score += 0.3
                else:
                    score += 0.1

                # 基于置信度
                confidence = item.get("confidence", 0.5)
                score += confidence * 0.3

                # 基于内容质量
                content = item.get("content", "")
                if len(content) > 100:
                    score += 0.2
                elif len(content) > 50:
                    score += 0.1

                evidence_scores.append(score)

            # 选择证据最强的项目
            best_index = evidence_scores.index(max(evidence_scores))
            best_item = conflicting_items[best_index]

            return {
                "resolved_content": f"基于证据权重分析，采纳以下观点：{best_item.get('content', '')}",
                "confidence_score": max(evidence_scores),
                "evidence": [f"证据评分: {score:.2f}" for score in evidence_scores],
                "resolution_method": "evidence_weighting",
                "selected_item": best_item.get("id", "unknown")
            }

        except Exception as e:
            logger.error(f"基于证据权重解决冲突失败: {e}")
            return {"error": str(e)}

    def _resolve_by_source_credibility(self, conflict: dict[str, Any]) -> dict[str, Any]:
        """基于来源可信度解决冲突"""
        try:
            conflicting_items = conflict.get("conflicting_items", [])

            # 评估来源可信度
            credibility_scores = []
            for item in conflicting_items:
                source = item.get("source", "").lower()

                if any(keyword in source for keyword in ["学术期刊", "研究院", "大学"]):
                    score = 0.9
                elif any(keyword in source for keyword in ["政府", "官方", "权威机构"]):
                    score = 0.8
                elif any(keyword in source for keyword in ["专业媒体", "行业报告"]):
                    score = 0.6
                else:
                    score = 0.4

                credibility_scores.append(score)

            # 选择可信度最高的来源
            best_index = credibility_scores.index(max(credibility_scores))
            best_item = conflicting_items[best_index]

            return {
                "resolved_content": f"基于来源可信度分析，采纳来自'{best_item.get('source', '')}'的观点：{best_item.get('content', '')}",
                "confidence_score": max(credibility_scores),
                "evidence": [f"来源可信度: {score:.2f}" for score in credibility_scores],
                "resolution_method": "source_credibility",
                "selected_source": best_item.get("source", "unknown")
            }

        except Exception as e:
            logger.error(f"基于来源可信度解决冲突失败: {e}")
            return {"error": str(e)}

    def _resolve_by_temporal_priority(self, conflict: dict[str, Any]) -> dict[str, Any]:
        """基于时间优先级解决冲突"""
        try:
            conflicting_items = conflict.get("conflicting_items", [])

            # 找到最新的项目
            latest_item = None
            latest_time = None

            for item in conflicting_items:
                timestamp = item.get("timestamp")
                if timestamp:
                    try:
                        time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        if latest_time is None or time > latest_time:
                            latest_time = time
                            latest_item = item
                    except ValueError:
                        continue

            if latest_item:
                return {
                    "resolved_content": f"基于时间优先级，采纳最新信息：{latest_item.get('content', '')}",
                    "confidence_score": 0.7,
                    "evidence": [f"最新时间: {latest_time.isoformat()}"],
                    "resolution_method": "temporal_priority",
                    "selected_timestamp": latest_item.get("timestamp")
                }
            else:
                return {"error": "无法确定时间优先级"}

        except Exception as e:
            logger.error(f"基于时间优先级解决冲突失败: {e}")
            return {"error": str(e)}

    def _resolve_by_confidence(self, conflict: dict[str, Any]) -> dict[str, Any]:
        """基于置信度解决冲突"""
        try:
            conflicting_items = conflict.get("conflicting_items", [])

            # 选择置信度最高的项目
            best_item = max(conflicting_items, key=lambda x: x.get("confidence", 0.0))

            return {
                "resolved_content": f"基于置信度分析，采纳置信度最高的观点：{best_item.get('content', '')}",
                "confidence_score": best_item.get("confidence", 0.0),
                "evidence": [f"置信度: {item.get('confidence', 0.0):.2f}" for item in conflicting_items],
                "resolution_method": "confidence_based",
                "selected_confidence": best_item.get("confidence", 0.0)
            }

        except Exception as e:
            logger.error(f"基于置信度解决冲突失败: {e}")
            return {"error": str(e)}

    def _resolve_by_synthesis(self, conflict: dict[str, Any]) -> dict[str, Any]:
        """通过综合解决冲突"""
        try:
            conflicting_items = conflict.get("conflicting_items", [])

            # 提取所有观点
            viewpoints = [item.get("content", "") for item in conflicting_items]

            # 简单的综合策略：寻找共同点和差异点
            common_themes = self._find_common_themes(viewpoints)
            differences = self._identify_differences(viewpoints)

            # 生成综合观点
            synthesized_content = f"综合分析表明：{common_themes}。同时需要注意：{differences}。"

            # 计算综合置信度
            confidences = [item.get("confidence", 0.5) for item in conflicting_items]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

            return {
                "resolved_content": synthesized_content,
                "confidence_score": avg_confidence * 0.8,  # 综合后置信度略降
                "evidence": [f"综合了{len(conflicting_items)}个观点", f"平均置信度: {avg_confidence:.2f}"],
                "resolution_method": "synthesis",
                "synthesis_components": len(conflicting_items)
            }

        except Exception as e:
            logger.error(f"通过综合解决冲突失败: {e}")
            return {"error": str(e)}

    def _analyze_sentiment(self, text: str) -> float:
        """简单的情感分析"""
        positive_words = ["好", "优秀", "成功", "有效", "安全", "可靠", "准确"]
        negative_words = ["坏", "失败", "无效", "危险", "不可靠", "错误", "风险"]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        total_words = len(text.split())
        if total_words == 0:
            return 0.5

        sentiment_score = (positive_count - negative_count) / total_words
        return max(0.0, min(1.0, sentiment_score + 0.5))  # 归一化到0-1

    def _check_internal_consistency(self, resolution: dict[str, Any]) -> bool:
        """检查内部一致性"""
        try:
            content = resolution.get("resolved_content", "")
            confidence = resolution.get("confidence_score", 0.0)

            # 简单的一致性检查
            if confidence > 0.8 and len(content) < 20:
                return False  # 高置信度但内容太少

            if confidence < 0.3 and "确定" in content:
                return False  # 低置信度但用确定性语言

            return True

        except Exception as e:
            logger.error(f"检查内部一致性失败: {e}")
            return False

    def _find_common_themes(self, viewpoints: list[str]) -> str:
        """寻找共同主题"""
        try:
            # 简单的关键词提取和共同点识别
            all_words = []
            for viewpoint in viewpoints:
                words = viewpoint.split()
                all_words.extend(words)

            # 找出出现频率较高的词
            word_count = {}
            for word in all_words:
                if len(word) > 2:  # 忽略太短的词
                    word_count[word] = word_count.get(word, 0) + 1

            common_words = [word for word, count in word_count.items() if count > 1]

            if common_words:
                return f"各方都提到了{', '.join(common_words[:3])}等关键概念"
            else:
                return "各方观点存在一定共识基础"

        except Exception as e:
            logger.error(f"寻找共同主题失败: {e}")
            return "存在一定共识"

    def _identify_differences(self, viewpoints: list[str]) -> str:
        """识别差异点"""
        try:
            if len(viewpoints) < 2:
                return "观点单一"

            # 简单的差异识别
            differences = []

            for i, viewpoint in enumerate(viewpoints):
                if "不" in viewpoint or "否" in viewpoint:
                    differences.append(f"观点{i+1}持否定态度")
                elif "是" in viewpoint or "确实" in viewpoint:
                    differences.append(f"观点{i+1}持肯定态度")

            if differences:
                return "; ".join(differences)
            else:
                return "各方观点在表述方式上存在差异"

        except Exception as e:
            logger.error(f"识别差异点失败: {e}")
            return "存在观点差异"

    def get_conflict_statistics(self) -> dict[str, Any]:
        """获取冲突统计"""
        try:
            stats = {
                "total_conflicts": len(self.conflict_history),
                "resolved_conflicts": len([c for c in self.conflict_history if c["status"] == "resolved"]),
                "pending_conflicts": len([c for c in self.conflict_history if c["status"] == "detected"]),
                "conflict_types": {},
                "resolution_success_rate": 0.0
            }

            # 统计冲突类型
            for conflict in self.conflict_history:
                conflict_type = conflict["conflict_type"]
                stats["conflict_types"][conflict_type] = stats["conflict_types"].get(conflict_type, 0) + 1

            # 计算解决成功率
            if stats["total_conflicts"] > 0:
                stats["resolution_success_rate"] = stats["resolved_conflicts"] / stats["total_conflicts"]

            return stats

        except Exception as e:
            logger.error(f"获取冲突统计失败: {e}")
            return {"error": str(e)}