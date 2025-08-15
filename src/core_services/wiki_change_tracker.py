#!/usr/bin/env python3
"""Wiki变更追踪器

追踪和分析Wiki知识库的变更模式
"""

import logging
import uuid
from collections import Counter, defaultdict
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

logger = logging.getLogger(__name__)


class WikiChangeTracker:
    """Wiki变更追踪器"""

    def __init__(self):
        """初始化Wiki变更追踪器"""
        self.change_history = []
        self.tracked_entities = {}  # {entity_id: entity_info}
        self.change_patterns = {}
        self.contributors = {}  # {contributor_id: contributor_info}
<<<<<<< HEAD

    def track_change(self, change_data: Dict[str, Any]) -> str:
=======
    
    def track_change(self, change_data: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """追踪变更"""
        try:
            change_id = str(uuid.uuid4())

            change_record = {
                "change_id": change_id,
                "entity_id": change_data.get("entity_id"),
                "change_type": change_data.get("change_type", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "old_content": change_data.get("old_content"),
                "new_content": change_data.get("new_content"),
                "change_reason": change_data.get("change_reason", ""),
                "contributor": change_data.get("contributor", "anonymous"),
                "evidence": change_data.get("evidence", []),
                "impact_score": self._calculate_impact_score(change_data),
                "change_size": self._calculate_change_size(change_data)
            }

            # 添加到变更历史
            self.change_history.append(change_record)

            # 更新实体追踪信息
            entity_id = change_record["entity_id"]
            if entity_id not in self.tracked_entities:
                self.tracked_entities[entity_id] = {
                    "entity_id": entity_id,
                    "first_tracked": change_record["timestamp"],
                    "change_count": 0,
                    "contributors": set(),
                    "change_types": set()
                }

            entity_info = self.tracked_entities[entity_id]
            entity_info["change_count"] += 1
            entity_info["contributors"].add(change_record["contributor"])
            entity_info["change_types"].add(change_record["change_type"])
            entity_info["last_changed"] = change_record["timestamp"]

            # 更新贡献者信息
            contributor = change_record["contributor"]
            if contributor not in self.contributors:
                self.contributors[contributor] = {
                    "contributor_id": contributor,
                    "first_contribution": change_record["timestamp"],
                    "contribution_count": 0,
                    "entities_modified": set(),
                    "change_types": set()
                }

            contributor_info = self.contributors[contributor]
            contributor_info["contribution_count"] += 1
            contributor_info["entities_modified"].add(entity_id)
            contributor_info["change_types"].add(change_record["change_type"])
            contributor_info["last_contribution"] = change_record["timestamp"]

            logger.info(f"追踪变更: {change_id} for entity: {entity_id}")
            return change_id

        except Exception as e:
            logger.error(f"追踪变更失败: {e}")
            return None

    def get_change_history(
        self,
        entity_id: str = None,
        contributor: str = None,
        change_type: str = None,
        limit: int = None
    ) -> list[dict[str, Any]]:
        """获取变更历史"""
        try:
            filtered_history = self.change_history.copy()

            # 应用过滤条件
            if entity_id:
                filtered_history = [change for change in filtered_history if change["entity_id"] == entity_id]

            if contributor:
                filtered_history = [change for change in filtered_history if change["contributor"] == contributor]

            if change_type:
                filtered_history = [change for change in filtered_history if change["change_type"] == change_type]

            # 按时间倒序排列
            filtered_history.sort(key=lambda x: x["timestamp"], reverse=True)

            # 应用限制
            if limit:
                filtered_history = filtered_history[:limit]

            return filtered_history

        except Exception as e:
            logger.error(f"获取变更历史失败: {e}")
            return []
<<<<<<< HEAD

    def analyze_change_patterns(self) -> Dict[str, Any]:
=======
    
    def analyze_change_patterns(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析变更模式"""
        try:
            if not self.change_history:
                return {"message": "暂无变更历史"}

            patterns = {
                "frequent_contributors": self._analyze_frequent_contributors(),
                "change_types": self._analyze_change_types(),
                "temporal_patterns": self._analyze_temporal_patterns(),
                "entity_activity": self._analyze_entity_activity(),
                "change_velocity": self._calculate_change_velocity(),
                "collaboration_patterns": self._analyze_collaboration_patterns()
            }

            return patterns

        except Exception as e:
            logger.error(f"分析变更模式失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def get_entity_change_summary(self, entity_id: str) -> Dict[str, Any]:
=======
    
    def get_entity_change_summary(self, entity_id: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取实体变更摘要"""
        try:
            if entity_id not in self.tracked_entities:
                return {"error": f"实体未被追踪: {entity_id}"}

            entity_info = self.tracked_entities[entity_id]
            entity_changes = self.get_change_history(entity_id=entity_id)

            summary = {
                "entity_id": entity_id,
                "total_changes": entity_info["change_count"],
                "contributors": list(entity_info["contributors"]),
                "change_types": list(entity_info["change_types"]),
                "first_tracked": entity_info["first_tracked"],
                "last_changed": entity_info.get("last_changed"),
                "recent_changes": entity_changes[:5],  # 最近5次变更
                "change_frequency": self._calculate_entity_change_frequency(entity_id),
                "stability_score": self._calculate_entity_stability(entity_id)
            }

            return summary

        except Exception as e:
            logger.error(f"获取实体变更摘要失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def get_contributor_profile(self, contributor: str) -> Dict[str, Any]:
=======
    
    def get_contributor_profile(self, contributor: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取贡献者档案"""
        try:
            if contributor not in self.contributors:
                return {"error": f"贡献者不存在: {contributor}"}

            contributor_info = self.contributors[contributor]
            contributor_changes = self.get_change_history(contributor=contributor)

            profile = {
                "contributor_id": contributor,
                "total_contributions": contributor_info["contribution_count"],
                "entities_modified": list(contributor_info["entities_modified"]),
                "change_types": list(contributor_info["change_types"]),
                "first_contribution": contributor_info["first_contribution"],
                "last_contribution": contributor_info.get("last_contribution"),
                "recent_contributions": contributor_changes[:10],  # 最近10次贡献
                "contribution_frequency": self._calculate_contributor_frequency(contributor),
                "expertise_areas": self._identify_contributor_expertise(contributor),
                "collaboration_score": self._calculate_collaboration_score(contributor)
            }

            return profile

        except Exception as e:
            logger.error(f"获取贡献者档案失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def _calculate_impact_score(self, change_data: Dict[str, Any]) -> float:
=======
    
    def _calculate_impact_score(self, change_data: dict[str, Any]) -> float:
>>>>>>> feature/core-services-refactor
        """计算变更影响分数"""
        try:
            impact_score = 0.0

            # 基于变更类型的基础分数
            change_type = change_data.get("change_type", "unknown")
            type_scores = {
                "content_update": 0.7,
                "new_entry": 1.0,
                "deletion": 0.9,
                "restructure": 0.8,
                "correction": 0.6,
                "enhancement": 0.5
            }
            impact_score += type_scores.get(change_type, 0.3)

            # 基于变更大小
            old_content = change_data.get("old_content", "")
            new_content = change_data.get("new_content", "")

            if old_content and new_content:
                size_ratio = abs(len(new_content) - len(old_content)) / max(len(old_content), 1)
                impact_score += min(size_ratio, 0.5)

            # 基于证据数量
            evidence = change_data.get("evidence", [])
            impact_score += min(len(evidence) * 0.1, 0.3)

            return min(impact_score, 1.0)

        except Exception as e:
            logger.error(f"计算影响分数失败: {e}")
            return 0.0
<<<<<<< HEAD

    def _calculate_change_size(self, change_data: Dict[str, Any]) -> str:
=======
    
    def _calculate_change_size(self, change_data: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """计算变更大小"""
        try:
            old_content = change_data.get("old_content", "")
            new_content = change_data.get("new_content", "")

            if not old_content and new_content:
                return "large"  # 新增内容

            if old_content and not new_content:
                return "large"  # 删除内容

            if old_content and new_content:
                old_len = len(old_content)
                new_len = len(new_content)
                change_ratio = abs(new_len - old_len) / max(old_len, 1)

                if change_ratio > 0.5:
                    return "large"
                elif change_ratio > 0.2:
                    return "medium"
                else:
                    return "small"

            return "unknown"

        except Exception as e:
            logger.error(f"计算变更大小失败: {e}")
            return "unknown"
<<<<<<< HEAD

    def _analyze_frequent_contributors(self) -> List[Dict[str, Any]]:
=======
    
    def _analyze_frequent_contributors(self) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """分析频繁贡献者"""
        contributor_stats = []

        for contributor_id, info in self.contributors.items():
            contributor_stats.append({
                "contributor": contributor_id,
                "contribution_count": info["contribution_count"],
                "entities_count": len(info["entities_modified"]),
                "change_types_count": len(info["change_types"]),
                "activity_score": info["contribution_count"] * len(info["entities_modified"])
            })

        # 按活跃度排序
        contributor_stats.sort(key=lambda x: x["activity_score"], reverse=True)
        return contributor_stats[:10]  # 返回前10名
<<<<<<< HEAD

    def _analyze_change_types(self) -> Dict[str, Any]:
=======
    
    def _analyze_change_types(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析变更类型"""
        type_counter = Counter(change["change_type"] for change in self.change_history)

        return {
            "distribution": dict(type_counter),
            "most_common": type_counter.most_common(5),
            "total_types": len(type_counter)
        }
<<<<<<< HEAD

    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
=======
    
    def _analyze_temporal_patterns(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析时间模式"""
        try:
            if not self.change_history:
                return {}

            # 按小时统计
            hourly_changes = defaultdict(int)
            # 按日期统计
            daily_changes = defaultdict(int)
            # 按星期统计
            weekly_changes = defaultdict(int)

            for change in self.change_history:
                timestamp = datetime.fromisoformat(change["timestamp"])

                hourly_changes[timestamp.hour] += 1
                daily_changes[timestamp.date().isoformat()] += 1
                weekly_changes[timestamp.strftime("%A")] += 1

            return {
                "hourly_distribution": dict(hourly_changes),
                "daily_distribution": dict(daily_changes),
                "weekly_distribution": dict(weekly_changes),
                "peak_hour": max(hourly_changes, key=hourly_changes.get) if hourly_changes else None,
                "peak_day": max(weekly_changes, key=weekly_changes.get) if weekly_changes else None
            }

        except Exception as e:
            logger.error(f"分析时间模式失败: {e}")
            return {}
<<<<<<< HEAD

    def _analyze_entity_activity(self) -> List[Dict[str, Any]]:
=======
    
    def _analyze_entity_activity(self) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """分析实体活跃度"""
        entity_stats = []

        for entity_id, info in self.tracked_entities.items():
            entity_stats.append({
                "entity_id": entity_id,
                "change_count": info["change_count"],
                "contributor_count": len(info["contributors"]),
                "change_type_count": len(info["change_types"]),
                "activity_score": info["change_count"] * len(info["contributors"])
            })

        # 按活跃度排序
        entity_stats.sort(key=lambda x: x["activity_score"], reverse=True)
        return entity_stats[:10]  # 返回前10名
<<<<<<< HEAD

    def _calculate_change_velocity(self) -> Dict[str, float]:
=======
    
    def _calculate_change_velocity(self) -> dict[str, float]:
>>>>>>> feature/core-services-refactor
        """计算变更速度"""
        try:
            if len(self.change_history) < 2:
                return {"daily_velocity": 0.0, "weekly_velocity": 0.0}

            # 计算时间跨度
            first_change = datetime.fromisoformat(self.change_history[0]["timestamp"])
            last_change = datetime.fromisoformat(self.change_history[-1]["timestamp"])

            time_span = last_change - first_change
            total_changes = len(self.change_history)

            if time_span.days > 0:
                daily_velocity = total_changes / time_span.days
                weekly_velocity = daily_velocity * 7
            else:
                daily_velocity = total_changes
                weekly_velocity = total_changes

            return {
                "daily_velocity": daily_velocity,
                "weekly_velocity": weekly_velocity,
                "total_changes": total_changes,
                "time_span_days": time_span.days
            }

        except Exception as e:
            logger.error(f"计算变更速度失败: {e}")
            return {"daily_velocity": 0.0, "weekly_velocity": 0.0}
<<<<<<< HEAD

    def _analyze_collaboration_patterns(self) -> Dict[str, Any]:
=======
    
    def _analyze_collaboration_patterns(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析协作模式"""
        try:
            # 找出协作实体（多个贡献者修改的实体）
            collaborative_entities = []
            for entity_id, info in self.tracked_entities.items():
                if len(info["contributors"]) > 1:
                    collaborative_entities.append({
                        "entity_id": entity_id,
                        "contributor_count": len(info["contributors"]),
                        "contributors": list(info["contributors"])
                    })

            # 计算贡献者间的协作关系
            collaboration_pairs = defaultdict(int)
            for entity in collaborative_entities:
                contributors = entity["contributors"]
                for i in range(len(contributors)):
                    for j in range(i + 1, len(contributors)):
                        pair = tuple(sorted([contributors[i], contributors[j]]))
                        collaboration_pairs[pair] += 1

            return {
                "collaborative_entities": len(collaborative_entities),
                "top_collaborative_entities": sorted(collaborative_entities,
                                                   key=lambda x: x["contributor_count"],
                                                   reverse=True)[:5],
                "collaboration_pairs": dict(collaboration_pairs),
                "most_collaborative_pair": max(collaboration_pairs, key=collaboration_pairs.get) if collaboration_pairs else None
            }

        except Exception as e:
            logger.error(f"分析协作模式失败: {e}")
            return {}

    def _calculate_entity_change_frequency(self, entity_id: str) -> float:
        """计算实体变更频率"""
        try:
            entity_changes = self.get_change_history(entity_id=entity_id)
            if len(entity_changes) < 2:
                return 0.0

            first_change = datetime.fromisoformat(entity_changes[-1]["timestamp"])
            last_change = datetime.fromisoformat(entity_changes[0]["timestamp"])

            time_span = last_change - first_change
            if time_span.days > 0:
                return len(entity_changes) / time_span.days
            else:
                return len(entity_changes)

        except Exception as e:
            logger.error(f"计算实体变更频率失败: {e}")
            return 0.0

    def _calculate_entity_stability(self, entity_id: str) -> float:
        """计算实体稳定性"""
        try:
            entity_changes = self.get_change_history(entity_id=entity_id)
            if not entity_changes:
                return 1.0

            # 基于变更频率和影响分数计算稳定性
            total_impact = sum(change.get("impact_score", 0.0) for change in entity_changes)
            avg_impact = total_impact / len(entity_changes)

            frequency = self._calculate_entity_change_frequency(entity_id)

            # 稳定性与变更频率和影响成反比
            stability = 1.0 / (1.0 + frequency + avg_impact)
            return min(max(stability, 0.0), 1.0)

        except Exception as e:
            logger.error(f"计算实体稳定性失败: {e}")
            return 0.5

    def _calculate_contributor_frequency(self, contributor: str) -> float:
        """计算贡献者活跃频率"""
        try:
            contributor_changes = self.get_change_history(contributor=contributor)
            if len(contributor_changes) < 2:
                return 0.0

            first_contribution = datetime.fromisoformat(contributor_changes[-1]["timestamp"])
            last_contribution = datetime.fromisoformat(contributor_changes[0]["timestamp"])

            time_span = last_contribution - first_contribution
            if time_span.days > 0:
                return len(contributor_changes) / time_span.days
            else:
                return len(contributor_changes)

        except Exception as e:
            logger.error(f"计算贡献者频率失败: {e}")
            return 0.0
<<<<<<< HEAD

    def _identify_contributor_expertise(self, contributor: str) -> List[str]:
=======
    
    def _identify_contributor_expertise(self, contributor: str) -> list[str]:
>>>>>>> feature/core-services-refactor
        """识别贡献者专长领域"""
        try:
            contributor_changes = self.get_change_history(contributor=contributor)

            # 基于变更类型识别专长
            change_type_count = Counter(change["change_type"] for change in contributor_changes)

            # 基于实体类型识别专长（如果有的话）
            entity_types = []
            for change in contributor_changes:
                entity_id = change["entity_id"]
                # 这里可以根据实体ID或其他信息推断实体类型
                # 简化处理，直接使用变更类型
                entity_types.append(change["change_type"])

            expertise_areas = [change_type for change_type, count in change_type_count.most_common(3)]
            return expertise_areas

        except Exception as e:
            logger.error(f"识别贡献者专长失败: {e}")
            return []

    def _calculate_collaboration_score(self, contributor: str) -> float:
        """计算协作分数"""
        try:
            if contributor not in self.contributors:
                return 0.0

            contributor_info = self.contributors[contributor]

            # 基于修改的实体数量和其他贡献者的重叠度
            entities_modified = contributor_info["entities_modified"]
            collaboration_count = 0

            for entity_id in entities_modified:
                if entity_id in self.tracked_entities:
                    entity_contributors = self.tracked_entities[entity_id]["contributors"]
                    if len(entity_contributors) > 1:  # 有其他贡献者
                        collaboration_count += 1

            if entities_modified:
                collaboration_score = collaboration_count / len(entities_modified)
            else:
                collaboration_score = 0.0

            return collaboration_score

        except Exception as e:
            logger.error(f"计算协作分数失败: {e}")
            return 0.0
