#!/usr/bin/env python3
"""知识演化追踪器

追踪知识随时间的演化过程
"""

import logging
import uuid
from collections import defaultdict
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

logger = logging.getLogger(__name__)


class KnowledgeEvolutionTracker:
    """知识演化追踪器"""

    def __init__(self):
        """初始化知识演化追踪器"""
        self.evolution_history = {}  # {knowledge_id: [evolution_events]}
        self.knowledge_lineage = {}  # {knowledge_id: lineage_info}
        self.evolution_patterns = {}  # {pattern_type: pattern_data}

        # 演化事件类型
        self.evolution_types = {
            "creation": "创建",
            "enhancement": "增强",
            "refinement": "优化",
            "expansion": "扩展",
            "correction": "修正",
            "merge": "合并",
            "split": "分割",
            "deprecation": "废弃"
        }

    def track_knowledge_change(
        self,
        knowledge_id: str,
        change_type: str,
        old_content: str = "",
        new_content: str = "",
        change_reason: str = "",
        timestamp: str = None
    ) -> str:
        """追踪知识变化"""
        try:
            change_id = str(uuid.uuid4())

            if timestamp is None:
                timestamp = datetime.now().isoformat()

            evolution_event = {
                "change_id": change_id,
                "knowledge_id": knowledge_id,
                "change_type": change_type,
                "old_content": old_content,
                "new_content": new_content,
                "change_reason": change_reason,
                "timestamp": timestamp,
                "impact_score": self._calculate_impact_score(old_content, new_content),
                "change_magnitude": self._calculate_change_magnitude(old_content, new_content)
            }

            # 添加到演化历史
            if knowledge_id not in self.evolution_history:
                self.evolution_history[knowledge_id] = []

            self.evolution_history[knowledge_id].append(evolution_event)

            # 更新谱系信息
            self._update_lineage_info(knowledge_id, evolution_event)

            logger.info(f"追踪知识变化: {change_id} for {knowledge_id}")
            return change_id

        except Exception as e:
            logger.error(f"追踪知识变化失败: {e}")
            return None
<<<<<<< HEAD

    def analyze_evolution_patterns(self, knowledge_topic: str = None) -> Dict[str, Any]:
=======
    
    def analyze_evolution_patterns(self, knowledge_topic: str = None) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析演化模式"""
        try:
            if knowledge_topic:
                # 分析特定主题的演化模式
                relevant_histories = {
                    k: v for k, v in self.evolution_history.items()
                    if knowledge_topic.lower() in k.lower()
                }
            else:
                # 分析所有知识的演化模式
                relevant_histories = self.evolution_history

            if not relevant_histories:
                return {"message": "没有相关的演化历史"}

            patterns = {
                "dominant_patterns": self._identify_dominant_patterns(relevant_histories),
                "evolution_velocity": self._calculate_evolution_velocity(relevant_histories),
                "change_frequency": self._analyze_change_frequency(relevant_histories),
                "quality_trends": self._analyze_quality_trends(relevant_histories),
                "lifecycle_stages": self._identify_lifecycle_stages(relevant_histories)
            }

            return patterns

        except Exception as e:
            logger.error(f"分析演化模式失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def generate_lineage_graph(self, knowledge_id: str) -> Dict[str, Any]:
=======
    
    def generate_lineage_graph(self, knowledge_id: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """生成谱系图"""
        try:
            if knowledge_id not in self.evolution_history:
                return {"error": f"知识项不存在: {knowledge_id}"}

            evolution_events = self.evolution_history[knowledge_id]

            # 构建谱系图数据结构
            lineage_graph = {
                "knowledge_id": knowledge_id,
                "nodes": [],
                "edges": [],
                "timeline": [],
                "statistics": {}
            }

            # 创建节点
            for i, event in enumerate(evolution_events):
                node = {
                    "node_id": f"{knowledge_id}_v{i+1}",
                    "version": i + 1,
                    "change_type": event["change_type"],
                    "timestamp": event["timestamp"],
                    "content_preview": event["new_content"][:100] + "..." if len(event["new_content"]) > 100 else event["new_content"],
                    "impact_score": event["impact_score"]
                }
                lineage_graph["nodes"].append(node)

                # 创建时间线条目
                timeline_entry = {
                    "timestamp": event["timestamp"],
                    "event_type": event["change_type"],
                    "description": event["change_reason"],
                    "version": i + 1
                }
                lineage_graph["timeline"].append(timeline_entry)

                # 创建边（连接到前一个版本）
                if i > 0:
                    edge = {
                        "from": f"{knowledge_id}_v{i}",
                        "to": f"{knowledge_id}_v{i+1}",
                        "relationship": "evolution",
                        "strength": 1.0 - (event["change_magnitude"] * 0.3)  # 变化越大，连续性越弱
                    }
                    lineage_graph["edges"].append(edge)

            # 计算统计信息
            lineage_graph["statistics"] = {
                "total_versions": len(evolution_events),
                "evolution_span": self._calculate_evolution_span(evolution_events),
                "most_common_change_type": self._get_most_common_change_type(evolution_events),
                "average_impact": sum(e["impact_score"] for e in evolution_events) / len(evolution_events)
            }

            return lineage_graph

        except Exception as e:
            logger.error(f"生成谱系图失败: {e}")
            return {"error": str(e)}

    def _calculate_impact_score(self, old_content: str, new_content: str) -> float:
        """计算影响分数"""
        try:
            if not old_content:
                return 1.0  # 新创建的内容影响最大

            if not new_content:
                return 0.9  # 删除内容影响很大

            # 基于内容变化程度计算影响
            old_len = len(old_content)
            new_len = len(new_content)

            # 长度变化影响
            length_change = abs(new_len - old_len) / max(old_len, 1)

            # 内容相似度影响
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, old_content, new_content).ratio()
            content_change = 1.0 - similarity

            # 综合影响分数
            impact_score = (length_change * 0.3 + content_change * 0.7)
            return min(max(impact_score, 0.0), 1.0)

        except Exception as e:
            logger.error(f"计算影响分数失败: {e}")
            return 0.5

    def _calculate_change_magnitude(self, old_content: str, new_content: str) -> float:
        """计算变化幅度"""
        try:
            if not old_content or not new_content:
                return 1.0

            # 基于编辑距离计算变化幅度
            import difflib

            diff = list(difflib.unified_diff(
                old_content.splitlines(),
                new_content.splitlines(),
                lineterm=''
            ))

            # 计算变化行数比例
            total_lines = max(len(old_content.splitlines()), len(new_content.splitlines()))
            changed_lines = len([line for line in diff if line.startswith('+') or line.startswith('-')])

            if total_lines == 0:
                return 0.0

            magnitude = changed_lines / total_lines
            return min(magnitude, 1.0)

        except Exception as e:
            logger.error(f"计算变化幅度失败: {e}")
            return 0.5
<<<<<<< HEAD

    def _update_lineage_info(self, knowledge_id: str, evolution_event: Dict[str, Any]) -> None:
=======
    
    def _update_lineage_info(self, knowledge_id: str, evolution_event: dict[str, Any]) -> None:
>>>>>>> feature/core-services-refactor
        """更新谱系信息"""
        try:
            if knowledge_id not in self.knowledge_lineage:
                self.knowledge_lineage[knowledge_id] = {
                    "creation_time": evolution_event["timestamp"],
                    "last_update": evolution_event["timestamp"],
                    "total_changes": 0,
                    "evolution_trajectory": []
                }

            lineage_info = self.knowledge_lineage[knowledge_id]
            lineage_info["last_update"] = evolution_event["timestamp"]
            lineage_info["total_changes"] += 1

            # 添加演化轨迹点
            trajectory_point = {
                "timestamp": evolution_event["timestamp"],
                "change_type": evolution_event["change_type"],
                "impact_score": evolution_event["impact_score"]
            }
            lineage_info["evolution_trajectory"].append(trajectory_point)

        except Exception as e:
            logger.error(f"更新谱系信息失败: {e}")
<<<<<<< HEAD

    def _identify_dominant_patterns(self, histories: Dict[str, List[Dict[str, Any]]]) -> List[str]:
=======
    
    def _identify_dominant_patterns(self, histories: dict[str, list[dict[str, Any]]]) -> list[str]:
>>>>>>> feature/core-services-refactor
        """识别主要模式"""
        try:
            pattern_counts = defaultdict(int)

            for knowledge_id, events in histories.items():
                # 分析变化类型序列
                change_sequence = [event["change_type"] for event in events]

                # 识别常见模式
                if len(change_sequence) >= 2:
                    for i in range(len(change_sequence) - 1):
                        pattern = f"{change_sequence[i]} -> {change_sequence[i+1]}"
                        pattern_counts[pattern] += 1

            # 返回最常见的模式
            sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
            return [pattern for pattern, count in sorted_patterns[:5]]

        except Exception as e:
            logger.error(f"识别主要模式失败: {e}")
            return []
<<<<<<< HEAD

    def _calculate_evolution_velocity(self, histories: Dict[str, List[Dict[str, Any]]]) -> float:
=======
    
    def _calculate_evolution_velocity(self, histories: dict[str, list[dict[str, Any]]]) -> float:
>>>>>>> feature/core-services-refactor
        """计算演化速度"""
        try:
            total_velocity = 0.0
            count = 0

            for knowledge_id, events in histories.items():
                if len(events) < 2:
                    continue

                # 计算时间跨度
                first_time = datetime.fromisoformat(events[0]["timestamp"])
                last_time = datetime.fromisoformat(events[-1]["timestamp"])
                time_span = (last_time - first_time).total_seconds()

                if time_span > 0:
                    # 变化次数 / 时间跨度（天）
                    velocity = len(events) / (time_span / 86400)  # 转换为天
                    total_velocity += velocity
                    count += 1

            return total_velocity / count if count > 0 else 0.0

        except Exception as e:
            logger.error(f"计算演化速度失败: {e}")
            return 0.0
<<<<<<< HEAD

    def _analyze_change_frequency(self, histories: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
=======
    
    def _analyze_change_frequency(self, histories: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析变化频率"""
        try:
            change_type_counts = defaultdict(int)
            total_changes = 0

            for knowledge_id, events in histories.items():
                for event in events:
                    change_type_counts[event["change_type"]] += 1
                    total_changes += 1

            # 计算频率
            frequency_analysis = {
                "total_changes": total_changes,
                "change_type_distribution": dict(change_type_counts),
                "most_frequent_change": max(change_type_counts, key=change_type_counts.get) if change_type_counts else None,
                "change_diversity": len(change_type_counts)
            }

            return frequency_analysis

        except Exception as e:
            logger.error(f"分析变化频率失败: {e}")
            return {}
<<<<<<< HEAD

    def _analyze_quality_trends(self, histories: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
=======
    
    def _analyze_quality_trends(self, histories: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析质量趋势"""
        try:
            quality_trends = {
                "improving_knowledge": 0,
                "declining_knowledge": 0,
                "stable_knowledge": 0,
                "average_impact_trend": 0.0
            }

            for knowledge_id, events in histories.items():
                if len(events) < 2:
                    quality_trends["stable_knowledge"] += 1
                    continue

                # 分析影响分数趋势
                impact_scores = [event["impact_score"] for event in events]

                # 简单的趋势分析
                first_half_avg = sum(impact_scores[:len(impact_scores)//2]) / (len(impact_scores)//2) if len(impact_scores) >= 2 else impact_scores[0]
                second_half_avg = sum(impact_scores[len(impact_scores)//2:]) / (len(impact_scores) - len(impact_scores)//2)

                if second_half_avg > first_half_avg * 1.1:
                    quality_trends["improving_knowledge"] += 1
                elif second_half_avg < first_half_avg * 0.9:
                    quality_trends["declining_knowledge"] += 1
                else:
                    quality_trends["stable_knowledge"] += 1

                quality_trends["average_impact_trend"] += (second_half_avg - first_half_avg)

            # 计算平均趋势
            total_knowledge = len(histories)
            if total_knowledge > 0:
                quality_trends["average_impact_trend"] /= total_knowledge

            return quality_trends

        except Exception as e:
            logger.error(f"分析质量趋势失败: {e}")
            return {}
<<<<<<< HEAD

    def _identify_lifecycle_stages(self, histories: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
=======
    
    def _identify_lifecycle_stages(self, histories: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """识别生命周期阶段"""
        try:
            lifecycle_analysis = {
                "creation_stage": 0,
                "growth_stage": 0,
                "maturity_stage": 0,
                "maintenance_stage": 0,
                "decline_stage": 0
            }

            for knowledge_id, events in histories.items():
                if not events:
                    continue

                # 基于变化类型和频率判断生命周期阶段
                change_types = [event["change_type"] for event in events]
                recent_changes = change_types[-3:] if len(change_types) >= 3 else change_types

                if "creation" in change_types and len(events) <= 2:
                    lifecycle_analysis["creation_stage"] += 1
                elif any(ct in recent_changes for ct in ["enhancement", "expansion"]):
                    lifecycle_analysis["growth_stage"] += 1
                elif any(ct in recent_changes for ct in ["refinement", "correction"]):
                    lifecycle_analysis["maturity_stage"] += 1
                elif "deprecation" in recent_changes:
                    lifecycle_analysis["decline_stage"] += 1
                else:
                    lifecycle_analysis["maintenance_stage"] += 1

            return lifecycle_analysis

        except Exception as e:
            logger.error(f"识别生命周期阶段失败: {e}")
            return {}
<<<<<<< HEAD

    def _calculate_evolution_span(self, events: List[Dict[str, Any]]) -> str:
=======
    
    def _calculate_evolution_span(self, events: list[dict[str, Any]]) -> str:
>>>>>>> feature/core-services-refactor
        """计算演化时间跨度"""
        try:
            if len(events) < 2:
                return "0 days"

            first_time = datetime.fromisoformat(events[0]["timestamp"])
            last_time = datetime.fromisoformat(events[-1]["timestamp"])

            time_span = last_time - first_time
            days = time_span.days

            if days == 0:
                hours = time_span.seconds // 3600
                return f"{hours} hours"
            else:
                return f"{days} days"

        except Exception as e:
            logger.error(f"计算演化时间跨度失败: {e}")
            return "unknown"
<<<<<<< HEAD

    def _get_most_common_change_type(self, events: List[Dict[str, Any]]) -> str:
=======
    
    def _get_most_common_change_type(self, events: list[dict[str, Any]]) -> str:
>>>>>>> feature/core-services-refactor
        """获取最常见的变化类型"""
        try:
            change_counts = defaultdict(int)

            for event in events:
                change_counts[event["change_type"]] += 1

            if change_counts:
                return max(change_counts, key=change_counts.get)
            else:
                return "unknown"

        except Exception as e:
            logger.error(f"获取最常见变化类型失败: {e}")
            return "unknown"
<<<<<<< HEAD

    def get_evolution_statistics(self) -> Dict[str, Any]:
=======
    
    def get_evolution_statistics(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取演化统计"""
        try:
            stats = {
                "total_knowledge_items": len(self.evolution_history),
                "total_evolution_events": sum(len(events) for events in self.evolution_history.values()),
                "most_evolved_knowledge": None,
                "evolution_type_distribution": defaultdict(int),
                "average_evolution_frequency": 0.0
            }

            # 找出演化最多的知识项
            if self.evolution_history:
                most_evolved = max(self.evolution_history.items(), key=lambda x: len(x[1]))
                stats["most_evolved_knowledge"] = {
                    "knowledge_id": most_evolved[0],
                    "evolution_count": len(most_evolved[1])
                }

            # 统计演化类型分布
            for events in self.evolution_history.values():
                for event in events:
                    stats["evolution_type_distribution"][event["change_type"]] += 1

            # 计算平均演化频率
            if self.evolution_history:
                total_frequency = 0.0
                for knowledge_id, events in self.evolution_history.items():
                    if len(events) >= 2:
                        first_time = datetime.fromisoformat(events[0]["timestamp"])
                        last_time = datetime.fromisoformat(events[-1]["timestamp"])
                        time_span = (last_time - first_time).total_seconds()
                        if time_span > 0:
                            frequency = len(events) / (time_span / 86400)  # 每天的变化次数
                            total_frequency += frequency

                stats["average_evolution_frequency"] = total_frequency / len(self.evolution_history)

            return stats

        except Exception as e:
            logger.error(f"获取演化统计失败: {e}")
            return {"error": str(e)}
