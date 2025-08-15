"""@Time: 2025-08-03
@Author: DAIP-LIVE
@Description: V0.3.4 知识历史追溯系统 - 完整的知识变化追踪和版本控制
"""

import asyncio
import hashlib
import json
import logging
import threading
import time
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
from ..core_services.knowledge_retrieval_service import KnowledgeRetrievalService
from ..core_services.memory_agent import MemAgent


class TraceType(Enum):
    """追溯类型"""
    VERSION_HISTORY = "version_history"      # 版本历史
    EVOLUTION_PATH = "evolution_path"        # 演化路径
    CITATION_GRAPH = "citation_graph"        # 引用图谱
    INFLUENCE_ANALYSIS = "influence_analysis" # 影响分析
    TEMPORAL_TRENDS = "temporal_trends"       # 时间趋势
    KNOWLEDGE_LINEAGE = "knowledge_lineage"   # 知识谱系


class ChangeType(Enum):
    """变更类型"""
    CREATION = "creation"           # 创建
    MODIFICATION = "modification"   # 修改
    DELETION = "deletion"          # 删除
    MERGE = "merge"               # 合并
    SPLIT = "split"               # 拆分
    VALIDATION = "validation"     # 验证
    CONFLICT_RESOLUTION = "conflict_resolution"  # 冲突解决


@dataclass
class KnowledgeVersion:
    """知识版本"""
    version_id: str
    knowledge_id: str
    content: str
    timestamp: datetime
    author: str
    change_type: ChangeType
    change_summary: str
    parent_versions: list[str]
    child_versions: list[str]
    confidence: float
    metadata: dict[str, Any] = None


@dataclass
class EvolutionEvent:
    """演化事件"""
    event_id: str
    knowledge_id: str
    event_type: ChangeType
    timestamp: datetime
    description: str
    impact_score: float
    affected_knowledge: list[str]
    metadata: dict[str, Any] = None


@dataclass
class CitationLink:
    """引用链接"""
    source_id: str
    target_id: str
    citation_type: str
    strength: float
    timestamp: datetime
    context: str = ""
    metadata: dict[str, Any] = None


@dataclass
class LineageNode:
    """谱系节点"""
    node_id: str
    knowledge_id: str
    content: str
    timestamp: datetime
    parent_ids: list[str]
    children_ids: list[str]
    branch_type: str
    metadata: dict[str, Any] = None


@dataclass
class TraceResult:
    """追溯结果"""
    trace_type: TraceType
    knowledge_id: str
    timeline: list[KnowledgeVersion]
    evolution_events: list[EvolutionEvent]
    citation_links: list[CitationLink]
    lineage_tree: LineageNode
    statistics: dict[str, Any]
    insights: list[str]
    metadata: dict[str, Any] = None


class KnowledgeHistoryTracker:
    """知识历史追溯系统"""
    
    def __init__(self, knowledge_retrieval: KnowledgeRetrievalService,
                 sskg_manager: EnhancedSSKGManager,
                 memory_agent: MemAgent):
        self.knowledge_retrieval = knowledge_retrieval
        self.sskg_manager = sskg_manager
        self.memory_agent = memory_agent
        self.logger = logging.getLogger(__name__)
        
        # 版本历史存储
        self.version_history = defaultdict(list)
        self.evolution_events = defaultdict(list)
        self.citation_links = defaultdict(list)
        self.lineage_nodes = {}
        
        # 索引
        self.knowledge_index = {}  # knowledge_id -> latest_version
        self.version_index = {}   # version_id -> knowledge_version
        self.temporal_index = defaultdict(list)  # timestamp -> version_ids
        
        # 统计
        self.change_statistics = defaultdict(lambda: {
            'total_changes': 0,
            'change_types': defaultdict(int),
            'active_contributors': set(),
            'evolution_rate': 0.0
        })
        
        # 持久化
        self.storage_path = "data/knowledge_history/"
        self.auto_save_interval = 300  # 5分钟自动保存
        
        # 启动后台任务
        self._start_background_tasks()
    
    async def track_knowledge_change(self, 
                                   knowledge_id: str,
                                   old_content: str,
                                   new_content: str,
                                   author: str,
                                   change_type: ChangeType,
                                   change_summary: str = "",
                                   metadata: dict[str, Any] = None) -> str:
        """追踪知识变更"""
        try:
            # 生成版本ID
            version_id = self._generate_version_id(knowledge_id)
            
            # 获取父版本
            parent_versions = self._get_parent_versions(knowledge_id)
            
            # 创建知识版本
            knowledge_version = KnowledgeVersion(
                version_id=version_id,
                knowledge_id=knowledge_id,
                content=new_content,
                timestamp=datetime.now(),
                author=author,
                change_type=change_type,
                change_summary=change_summary,
                parent_versions=parent_versions,
                child_versions=[],
                confidence=self._calculate_version_confidence(old_content, new_content),
                metadata=metadata or {}
            )
            
            # 更新索引
            self.version_index[version_id] = knowledge_version
            self.version_history[knowledge_id].append(knowledge_version)
            self.knowledge_index[knowledge_id] = version_id
            self.temporal_index[knowledge_version.timestamp].append(version_id)
            
            # 更新父子关系
            for parent_id in parent_versions:
                if parent_id in self.version_index:
                    self.version_index[parent_id].child_versions.append(version_id)
            
            # 记录演化事件
            await self._record_evolution_event(knowledge_id, change_type, change_summary)
            
            # 更新统计
            self._update_change_statistics(knowledge_id, change_type, author)
            
            # 分析引用关系
            await self._analyze_citation_relations(knowledge_id, new_content)
            
            self.logger.info(f"知识变更已追踪: {knowledge_id} -> {version_id}")
            
            return version_id
            
        except Exception as e:
            self.logger.error(f"追踪知识变更失败: {e}")
            return ""
    
    async def get_version_history(self, knowledge_id: str) -> list[KnowledgeVersion]:
        """获取版本历史"""
        try:
            # 从内存获取
            if knowledge_id in self.version_history:
                return self.version_history[knowledge_id]
            
            # 从存储加载
            return await self._load_version_history(knowledge_id)
            
        except Exception as e:
            self.logger.error(f"获取版本历史失败: {e}")
            return []
    
    async def trace_knowledge_evolution(self, 
                                      knowledge_id: str,
                                      trace_type: TraceType = TraceType.VERSION_HISTORY,
                                      depth: int = 5) -> TraceResult:
        """追溯知识演化"""
        try:
            result = TraceResult(
                trace_type=trace_type,
                knowledge_id=knowledge_id,
                timeline=[],
                evolution_events=[],
                citation_links=[],
                lineage_tree=None,
                statistics={},
                insights=[],
                metadata={}
            )
            
            # 获取版本历史
            version_history = await self.get_version_history(knowledge_id)
            result.timeline = version_history
            
            # 根据追溯类型获取不同信息
            if trace_type == TraceType.VERSION_HISTORY:
                result = await self._trace_version_history(result, knowledge_id)
            elif trace_type == TraceType.EVOLUTION_PATH:
                result = await self._trace_evolution_path(result, knowledge_id, depth)
            elif trace_type == TraceType.CITATION_GRAPH:
                result = await self._trace_citation_graph(result, knowledge_id)
            elif trace_type == TraceType.INFLUENCE_ANALYSIS:
                result = await self._trace_influence_analysis(result, knowledge_id)
            elif trace_type == TraceType.TEMPORAL_TRENDS:
                result = await self._trace_temporal_trends(result, knowledge_id)
            elif trace_type == TraceType.KNOWLEDGE_LINEAGE:
                result = await self._trace_knowledge_lineage(result, knowledge_id)
            
            # 生成洞察
            result.insights = await self._generate_insights(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"追溯知识演化失败: {e}")
            return TraceResult(
                trace_type=trace_type,
                knowledge_id=knowledge_id,
                timeline=[],
                evolution_events=[],
                citation_links=[],
                lineage_tree=None,
                statistics={},
                insights=[f"追溯失败: {str(e)}"],
                metadata={'error': str(e)}
            )
    
    async def compare_versions(self, 
                              version_id1: str, 
                              version_id2: str) -> dict[str, Any]:
        """比较版本差异"""
        try:
            version1 = self.version_index.get(version_id1)
            version2 = self.version_index.get(version_id2)
            
            if not version1 or not version2:
                return {"error": "版本不存在"}
            
            comparison = {
                "version1": {
                    "id": version1.version_id,
                    "content": version1.content,
                    "timestamp": version1.timestamp.isoformat(),
                    "author": version1.author,
                    "change_type": version1.change_type.value
                },
                "version2": {
                    "id": version2.version_id,
                    "content": version2.content,
                    "timestamp": version2.timestamp.isoformat(),
                    "author": version2.author,
                    "change_type": version2.change_type.value
                },
                "differences": self._calculate_version_differences(version1, version2),
                "similarity_score": self._calculate_version_similarity(version1, version2),
                "time_difference": (version2.timestamp - version1.timestamp).total_seconds()
            }
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"比较版本失败: {e}")
            return {"error": str(e)}
    
    async def restore_version(self, knowledge_id: str, version_id: str) -> bool:
        """恢复版本"""
        try:
            target_version = self.version_index.get(version_id)
            if not target_version:
                return False
            
            # 获取当前版本
            current_version_id = self.knowledge_index.get(knowledge_id)
            current_content = ""
            
            if current_version_id and current_version_id in self.version_index:
                current_content = self.version_index[current_version_id].content
            
            # 记录恢复操作
            await self.track_knowledge_change(
                knowledge_id=knowledge_id,
                old_content=current_content,
                new_content=target_version.content,
                author="system_restore",
                change_type=ChangeType.VALIDATION,
                change_summary=f"恢复到版本 {version_id}",
                metadata={"restored_from": version_id}
            )
            
            self.logger.info(f"版本已恢复: {knowledge_id} -> {version_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"恢复版本失败: {e}")
            return False
    
    async def get_knowledge_lineage(self, knowledge_id: str) -> LineageNode:
        """获取知识谱系"""
        try:
            # 构建谱系树
            lineage = await self._build_lineage_tree(knowledge_id)
            return lineage
            
        except Exception as e:
            self.logger.error(f"获取知识谱系失败: {e}")
            return None
    
    async def analyze_evolution_patterns(self, 
                                       knowledge_id: str,
                                       time_period: int = 30) -> dict[str, Any]:
        """分析演化模式"""
        try:
            # 获取时间范围内的版本
            cutoff_time = datetime.now() - timedelta(days=time_period)
            versions = await self.get_version_history(knowledge_id)
            
            recent_versions = [v for v in versions if v.timestamp >= cutoff_time]
            
            if not recent_versions:
                return {"error": "指定时间范围内无版本数据"}
            
            analysis = {
                "knowledge_id": knowledge_id,
                "time_period_days": time_period,
                "total_versions": len(recent_versions),
                "evolution_rate": len(recent_versions) / time_period,
                "change_frequency": self._analyze_change_frequency(recent_versions),
                "contributor_analysis": self._analyze_contributors(recent_versions),
                "content_evolution": self._analyze_content_evolution(recent_versions),
                "confidence_trend": self._analyze_confidence_trend(recent_versions),
                "patterns_identified": self._identify_evolution_patterns(recent_versions)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"分析演化模式失败: {e}")
            return {"error": str(e)}
    
    async def export_history(self, 
                            knowledge_id: str,
                            format: str = "json",
                            include_metadata: bool = True) -> str:
        """导出历史数据"""
        try:
            history_data = {
                "knowledge_id": knowledge_id,
                "export_time": datetime.now().isoformat(),
                "version_history": [asdict(v) for v in await self.get_version_history(knowledge_id)],
                "evolution_events": [asdict(e) for e in self.evolution_events.get(knowledge_id, [])],
                "citation_links": [asdict(l) for l in self.citation_links.get(knowledge_id, [])],
                "statistics": dict(self.change_statistics.get(knowledge_id, {}))
            }
            
            if format == "json":
                return json.dumps(history_data, indent=2, ensure_ascii=False)
            elif format == "csv":
                return self._export_to_csv(history_data)
            else:
                raise ValueError(f"不支持的格式: {format}")
                
        except Exception as e:
            self.logger.error(f"导出历史数据失败: {e}")
            return ""
    
    async def _trace_version_history(self, result: TraceResult, knowledge_id: str) -> TraceResult:
        """追溯版本历史"""
        try:
            versions = await self.get_version_history(knowledge_id)
            result.timeline = sorted(versions, key=lambda x: x.timestamp)
            
            # 计算统计信息
            result.statistics = {
                "total_versions": len(versions),
                "time_span": (versions[-1].timestamp - versions[0].timestamp).total_seconds() if len(versions) > 1 else 0,
                "average_time_between_versions": self._calculate_average_time_between_versions(versions),
                "most_active_author": self._find_most_active_author(versions),
                "change_type_distribution": self._calculate_change_type_distribution(versions)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"追溯版本历史失败: {e}")
            return result
    
    async def _trace_evolution_path(self, result: TraceResult, knowledge_id: str, depth: int) -> TraceResult:
        """追溯演化路径"""
        try:
            # 获取演化事件
            result.evolution_events = self.evolution_events.get(knowledge_id, [])
            
            # 构建演化路径
            evolution_path = []
            current_version = self.knowledge_index.get(knowledge_id)
            
            for _ in range(depth):
                if not current_version:
                    break
                
                version = self.version_index.get(current_version)
                if not version:
                    break
                
                evolution_path.append(version)
                
                # 回溯到父版本
                if version.parent_versions:
                    current_version = version.parent_versions[0]
                else:
                    break
            
            result.timeline = evolution_path
            
            return result
            
        except Exception as e:
            self.logger.error(f"追溯演化路径失败: {e}")
            return result
    
    async def _trace_citation_graph(self, result: TraceResult, knowledge_id: str) -> TraceResult:
        """追溯引用图谱"""
        try:
            # 获取引用链接
            result.citation_links = self.citation_links.get(knowledge_id, [])
            
            # 分析引用网络
            citation_network = self._analyze_citation_network(knowledge_id)
            
            result.statistics = {
                "total_citations": len(result.citation_links),
                "citation_sources": len(set(link.source_id for link in result.citation_links)),
                "citation_targets": len(set(link.target_id for link in result.citation_links)),
                "average_citation_strength": sum(link.strength for link in result.citation_links) / len(result.citation_links) if result.citation_links else 0,
                "network_analysis": citation_network
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"追溯引用图谱失败: {e}")
            return result
    
    async def _trace_influence_analysis(self, result: TraceResult, knowledge_id: str) -> TraceResult:
        """追溯影响分析"""
        try:
            # 分析知识的影响范围
            influence_analysis = await self._analyze_knowledge_influence(knowledge_id)
            
            result.statistics = influence_analysis
            
            # 获取被影响的版本
            influenced_versions = await self._get_influenced_versions(knowledge_id)
            
            result.timeline = [self.version_index.get(v_id) for v_id in influenced_versions if v_id in self.version_index]
            
            return result
            
        except Exception as e:
            self.logger.error(f"追溯影响分析失败: {e}")
            return result
    
    async def _trace_temporal_trends(self, result: TraceResult, knowledge_id: str) -> TraceResult:
        """追溯时间趋势"""
        try:
            versions = await self.get_version_history(knowledge_id)
            
            # 分析时间趋势
            temporal_analysis = self._analyze_temporal_trends(versions)
            
            result.statistics = temporal_analysis
            result.timeline = sorted(versions, key=lambda x: x.timestamp)
            
            return result
            
        except Exception as e:
            self.logger.error(f"追溯时间趋势失败: {e}")
            return result
    
    async def _trace_knowledge_lineage(self, result: TraceResult, knowledge_id: str) -> TraceResult:
        """追溯知识谱系"""
        try:
            lineage = await self.get_knowledge_lineage(knowledge_id)
            result.lineage_tree = lineage
            
            # 分析谱系统计
            lineage_stats = self._analyze_lineage_statistics(lineage)
            result.statistics = lineage_stats
            
            return result
            
        except Exception as e:
            self.logger.error(f"追溯知识谱系失败: {e}")
            return result
    
    def _generate_version_id(self, knowledge_id: str) -> str:
        """生成版本ID"""
        timestamp = datetime.now().isoformat()
        unique_string = f"{knowledge_id}_{timestamp}_{uuid.uuid4().hex[:8]}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _get_parent_versions(self, knowledge_id: str) -> list[str]:
        """获取父版本"""
        current_version = self.knowledge_index.get(knowledge_id)
        if current_version:
            return [current_version]
        return []
    
    def _calculate_version_confidence(self, old_content: str, new_content: str) -> float:
        """计算版本置信度"""
        try:
            # 简化的置信度计算
            if not old_content:
                return 0.8  # 新创建的版本
            
            # 基于内容变化量
            old_words = set(old_content.split())
            new_words = set(new_content.split())
            
            if not old_words or not new_words:
                return 0.5
            
            similarity = len(old_words & new_words) / len(old_words | new_words)
            
            # 相似度越高，置信度越高
            return min(1.0, similarity + 0.3)
            
        except Exception:
            return 0.5
    
    async def _record_evolution_event(self, knowledge_id: str, change_type: ChangeType, description: str):
        """记录演化事件"""
        try:
            event = EvolutionEvent(
                event_id=str(uuid.uuid4()),
                knowledge_id=knowledge_id,
                event_type=change_type,
                timestamp=datetime.now(),
                description=description,
                impact_score=self._calculate_impact_score(change_type),
                affected_knowledge=[knowledge_id],
                metadata={}
            )
            
            self.evolution_events[knowledge_id].append(event)
            
        except Exception as e:
            self.logger.error(f"记录演化事件失败: {e}")
    
    def _calculate_impact_score(self, change_type: ChangeType) -> float:
        """计算影响分数"""
        impact_scores = {
            ChangeType.CREATION: 1.0,
            ChangeType.MODIFICATION: 0.7,
            ChangeType.DELETION: 0.9,
            ChangeType.MERGE: 0.8,
            ChangeType.SPLIT: 0.6,
            ChangeType.VALIDATION: 0.4,
            ChangeType.CONFLICT_RESOLUTION: 0.9
        }
        return impact_scores.get(change_type, 0.5)
    
    def _update_change_statistics(self, knowledge_id: str, change_type: ChangeType, author: str):
        """更新变更统计"""
        stats = self.change_statistics[knowledge_id]
        stats['total_changes'] += 1
        stats['change_types'][change_type.value] += 1
        stats['active_contributors'].add(author)
        
        # 计算演化率
        if stats['total_changes'] > 1:
            time_span = datetime.now() - min(v.timestamp for v in self.version_history[knowledge_id])
            stats['evolution_rate'] = stats['total_changes'] / max(1, time_span.days)
    
    async def _analyze_citation_relations(self, knowledge_id: str, content: str):
        """分析引用关系"""
        try:
            # 简化的引用分析
            # 在实际实现中，这里应该使用NLP技术提取引用关系
            
            # 模拟一些引用关系
            citation_keywords = ['参考', '基于', '源自', '引用', 'according to']
            
            for keyword in citation_keywords:
                if keyword in content:
                    # 创建虚拟引用链接
                    citation_link = CitationLink(
                        source_id=knowledge_id,
                        target_id=f"cited_{keyword}_{uuid.uuid4().hex[:8]}",
                        citation_type="reference",
                        strength=0.7,
                        timestamp=datetime.now(),
                        context=f"包含关键词: {keyword}"
                    )
                    self.citation_links[knowledge_id].append(citation_link)
                    
        except Exception as e:
            self.logger.error(f"分析引用关系失败: {e}")
    
    def _calculate_version_differences(self, version1: KnowledgeVersion, version2: KnowledgeVersion) -> dict[str, Any]:
        """计算版本差异"""
        try:
            old_words = set(version1.content.split())
            new_words = set(version2.content.split())
            
            added_words = new_words - old_words
            removed_words = old_words - new_words
            common_words = old_words & new_words
            
            return {
                "added_content": len(added_words),
                "removed_content": len(removed_words),
                "common_content": len(common_words),
                "change_percentage": (len(added_words) + len(removed_words)) / max(1, len(old_words) + len(new_words)) * 100,
                "semantic_similarity": len(common_words) / max(1, len(old_words | new_words))
            }
            
        except Exception as e:
            self.logger.error(f"计算版本差异失败: {e}")
            return {}
    
    def _calculate_version_similarity(self, version1: KnowledgeVersion, version2: KnowledgeVersion) -> float:
        """计算版本相似度"""
        try:
            # 简化的相似度计算
            words1 = set(version1.content.split())
            words2 = set(version2.content.split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            
            return intersection / union
            
        except Exception:
            return 0.0
    
    async def _build_lineage_tree(self, knowledge_id: str) -> LineageNode:
        """构建谱系树"""
        try:
            # 获取所有相关版本
            versions = await self.get_version_history(knowledge_id)
            
            # 构建谱系节点
            lineage_map = {}
            
            for version in versions:
                node = LineageNode(
                    node_id=version.version_id,
                    knowledge_id=version.knowledge_id,
                    content=version.content[:100] + "..." if len(version.content) > 100 else version.content,
                    timestamp=version.timestamp,
                    parent_ids=version.parent_versions,
                    children_ids=version.child_versions,
                    branch_type=version.change_type.value,
                    metadata={"version": version}
                )
                lineage_map[version.version_id] = node
            
            # 找到根节点
            root_node = None
            for node in lineage_map.values():
                if not node.parent_ids:
                    root_node = node
                    break
            
            if not root_node and lineage_map:
                root_node = list(lineage_map.values())[0]
            
            return root_node
            
        except Exception as e:
            self.logger.error(f"构建谱系树失败: {e}")
            return None
    
    def _analyze_change_frequency(self, versions: list[KnowledgeVersion]) -> dict[str, float]:
        """分析变更频率"""
        try:
            if len(versions) < 2:
                return {"changes_per_day": 0.0, "average_interval": 0.0}
            
            time_span = (versions[-1].timestamp - versions[0].timestamp).total_seconds()
            changes_per_day = (len(versions) - 1) / max(1, time_span / 86400)
            
            intervals = []
            for i in range(1, len(versions)):
                interval = (versions[i].timestamp - versions[i-1].timestamp).total_seconds()
                intervals.append(interval)
            
            average_interval = sum(intervals) / len(intervals) if intervals else 0.0
            
            return {
                "changes_per_day": changes_per_day,
                "average_interval": average_interval,
                "max_interval": max(intervals) if intervals else 0.0,
                "min_interval": min(intervals) if intervals else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"分析变更频率失败: {e}")
            return {"changes_per_day": 0.0, "average_interval": 0.0}
    
    def _analyze_contributors(self, versions: list[KnowledgeVersion]) -> dict[str, Any]:
        """分析贡献者"""
        try:
            contributors = defaultdict(lambda: {"count": 0, "last_contribution": None})
            
            for version in versions:
                contributors[version.author]["count"] += 1
                if not contributors[version.author]["last_contribution"] or version.timestamp > contributors[version.author]["last_contribution"]:
                    contributors[version.author]["last_contribution"] = version.timestamp
            
            # 计算贡献比例
            total_changes = len(versions)
            contributor_stats = {}
            
            for author, stats in contributors.items():
                contributor_stats[author] = {
                    "contribution_count": stats["count"],
                    "contribution_percentage": stats["count"] / total_changes * 100,
                    "last_contribution": stats["last_contribution"].isoformat() if stats["last_contribution"] else None
                }
            
            return contributor_stats
            
        except Exception as e:
            self.logger.error(f"分析贡献者失败: {e}")
            return {}
    
    def _analyze_content_evolution(self, versions: list[KnowledgeVersion]) -> dict[str, Any]:
        """分析内容演化"""
        try:
            if not versions:
                return {}
            
            # 分析内容长度变化
            lengths = [len(version.content.split()) for version in versions]
            
            # 分析词汇变化
            all_words = set()
            for version in versions:
                all_words.update(version.content.split())
            
            # 分析主题变化（简化）
            topic_changes = []
            for i in range(1, len(versions)):
                prev_words = set(versions[i-1].content.split())
                curr_words = set(versions[i].content.split())
                
                new_words = curr_words - prev_words
                lost_words = prev_words - curr_words
                
                topic_changes.append({
                    "version_index": i,
                    "new_words_count": len(new_words),
                    "lost_words_count": len(lost_words),
                    "similarity": len(prev_words & curr_words) / max(1, len(prev_words | curr_words))
                })
            
            return {
                "content_length_trend": {
                    "initial_length": lengths[0] if lengths else 0,
                    "final_length": lengths[-1] if lengths else 0,
                    "average_length": sum(lengths) / len(lengths) if lengths else 0,
                    "growth_rate": (lengths[-1] - lengths[0]) / lengths[0] if lengths and lengths[0] > 0 else 0
                },
                "vocabulary_size": len(all_words),
                "topic_changes": topic_changes
            }
            
        except Exception as e:
            self.logger.error(f"分析内容演化失败: {e}")
            return {}
    
    def _analyze_confidence_trend(self, versions: list[KnowledgeVersion]) -> dict[str, Any]:
        """分析置信度趋势"""
        try:
            if not versions:
                return {}
            
            confidences = [version.confidence for version in versions]
            
            return {
                "initial_confidence": confidences[0],
                "final_confidence": confidences[-1],
                "average_confidence": sum(confidences) / len(confidences),
                "confidence_trend": "increasing" if confidences[-1] > confidences[0] else "decreasing",
                "max_confidence": max(confidences),
                "min_confidence": min(confidences)
            }
            
        except Exception as e:
            self.logger.error(f"分析置信度趋势失败: {e}")
            return {}
    
    def _identify_evolution_patterns(self, versions: list[KnowledgeVersion]) -> list[str]:
        """识别演化模式"""
        try:
            patterns = []
            
            if len(versions) < 3:
                return patterns
            
            # 分析变更频率模式
            intervals = []
            for i in range(1, len(versions)):
                interval = (versions[i].timestamp - versions[i-1].timestamp).total_seconds()
                intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                if max(intervals) > avg_interval * 3:
                    patterns.append("bursty_evolution")
                elif max(intervals) < avg_interval * 1.5:
                    patterns.append("steady_evolution")
            
            # 分析作者模式
            authors = [version.author for version in versions]
            unique_authors = set(authors)
            if len(unique_authors) == 1:
                patterns.append("single_author")
            elif len(unique_authors) > len(versions) * 0.7:
                patterns.append("collaborative_evolution")
            
            # 分析内容变化模式
            lengths = [len(version.content) for version in versions]
            if lengths[-1] > lengths[0] * 2:
                patterns.append("expanding_content")
            elif lengths[-1] < lengths[0] * 0.5:
                patterns.append("condensing_content")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"识别演化模式失败: {e}")
            return []
    
    async def _generate_insights(self, result: TraceResult) -> list[str]:
        """生成洞察"""
        insights = []
        
        try:
            # 基于版本数量的洞察
            if len(result.timeline) > 10:
                insights.append("该知识经历了频繁的演化，可能是一个活跃的研究领域")
            elif len(result.timeline) < 3:
                insights.append("该知识相对稳定，演化较少")
            
            # 基于变更类型的洞察
            if result.statistics.get('change_type_distribution'):
                change_types = result.statistics['change_type_distribution']
                if change_types.get('modification', 0) > 0.7:
                    insights.append("主要以渐进式改进为主")
                elif change_types.get('creation', 0) > 0.3:
                    insights.append("包含较多创新性内容")
            
            # 基于时间跨度的洞察
            time_span = result.statistics.get('time_span', 0)
            if time_span > 86400 * 365:  # 超过一年
                insights.append("该知识有长期演化历史")
            
            # 基于贡献者的洞察
            if result.statistics.get('most_active_author'):
                insights.append(f"主要贡献者: {result.statistics['most_active_author']}")
            
        except Exception as e:
            self.logger.error(f"生成洞察失败: {e}")
        
        return insights
    
    def _calculate_average_time_between_versions(self, versions: list[KnowledgeVersion]) -> float:
        """计算版本间平均时间"""
        if len(versions) < 2:
            return 0.0
        
        total_time = 0
        for i in range(1, len(versions)):
            total_time += (versions[i].timestamp - versions[i-1].timestamp).total_seconds()
        
        return total_time / (len(versions) - 1)
    
    def _find_most_active_author(self, versions: list[KnowledgeVersion]) -> str:
        """查找最活跃的作者"""
        author_counts = defaultdict(int)
        for version in versions:
            author_counts[version.author] += 1
        
        if author_counts:
            return max(author_counts, key=author_counts.get)
        return "unknown"
    
    def _calculate_change_type_distribution(self, versions: list[KnowledgeVersion]) -> dict[str, float]:
        """计算变更类型分布"""
        change_types = defaultdict(int)
        for version in versions:
            change_types[version.change_type.value] += 1
        
        total = len(versions)
        if total == 0:
            return {}
        
        return {change_type: count / total * 100 for change_type, count in change_types.items()}
    
    def _analyze_citation_network(self, knowledge_id: str) -> dict[str, Any]:
        """分析引用网络"""
        try:
            links = self.citation_links.get(knowledge_id, [])
            
            if not links:
                return {"network_density": 0.0, "centrality": 0.0}
            
            # 简化的网络分析
            sources = set(link.source_id for link in links)
            targets = set(link.target_id for link in links)
            
            network_density = len(links) / (len(sources) * len(targets)) if sources and targets else 0.0
            
            # 计算中心性
            centrality = len(links) / max(1, len(sources) + len(targets))
            
            return {
                "network_density": network_density,
                "centrality": centrality,
                "total_nodes": len(sources | targets),
                "total_edges": len(links)
            }
            
        except Exception as e:
            self.logger.error(f"分析引用网络失败: {e}")
            return {"network_density": 0.0, "centrality": 0.0}
    
    async def _analyze_knowledge_influence(self, knowledge_id: str) -> dict[str, Any]:
        """分析知识影响"""
        try:
            # 简化的影响分析
            versions = await self.get_version_history(knowledge_id)
            
            if not versions:
                return {}
            
            # 基于版本数量和变更频率评估影响
            total_changes = len(versions)
            time_span = (versions[-1].timestamp - versions[0].timestamp).total_seconds()
            evolution_rate = total_changes / max(1, time_span / 86400)
            
            # 基于置信度评估影响
            avg_confidence = sum(v.confidence for v in versions) / len(versions)
            
            return {
                "total_changes": total_changes,
                "evolution_rate": evolution_rate,
                "average_confidence": avg_confidence,
                "impact_score": evolution_rate * avg_confidence
            }
            
        except Exception as e:
            self.logger.error(f"分析知识影响失败: {e}")
            return {}
    
    async def _get_influenced_versions(self, knowledge_id: str) -> list[str]:
        """获取被影响的版本"""
        try:
            influenced = []
            
            # 查找所有引用该知识的版本
            for kid, links in self.citation_links.items():
                for link in links:
                    if link.target_id == knowledge_id:
                        influenced.extend(self.version_history.get(kid, []))
            
            return [v.version_id for v in influenced]
            
        except Exception as e:
            self.logger.error(f"获取被影响的版本失败: {e}")
            return []
    
    def _analyze_temporal_trends(self, versions: list[KnowledgeVersion]) -> dict[str, Any]:
        """分析时间趋势"""
        try:
            if not versions:
                return {}
            
            # 按月份分组统计
            monthly_stats = defaultdict(lambda: {"count": 0, "avg_confidence": 0.0})
            
            for version in versions:
                month_key = version.timestamp.strftime("%Y-%m")
                monthly_stats[month_key]["count"] += 1
                monthly_stats[month_key]["avg_confidence"] += version.confidence
            
            # 计算月平均置信度
            for month_stats in monthly_stats.values():
                if month_stats["count"] > 0:
                    month_stats["avg_confidence"] /= month_stats["count"]
            
            return {
                "monthly_statistics": dict(monthly_stats),
                "total_timespan_days": (versions[-1].timestamp - versions[0].timestamp).days,
                "peak_month": max(monthly_stats, key=lambda x: monthly_stats[x]["count"]) if monthly_stats else None
            }
            
        except Exception as e:
            self.logger.error(f"分析时间趋势失败: {e}")
            return {}
    
    def _analyze_lineage_statistics(self, lineage: LineageNode) -> dict[str, Any]:
        """分析谱系统计"""
        try:
            if not lineage:
                return {}
            
            # 递归统计
            stats = {
                "total_nodes": 0,
                "max_depth": 0,
                "branching_factor": 0,
                "leaf_nodes": 0
            }
            
            def _traverse_tree(node: LineageNode, depth: int):
                if not node:
                    return
                
                stats["total_nodes"] += 1
                stats["max_depth"] = max(stats["max_depth"], depth)
                
                if not node.children_ids:
                    stats["leaf_nodes"] += 1
                
                for child_id in node.children_ids:
                    # 这里应该递归遍历子节点
                    pass
            
            _traverse_tree(lineage, 0)
            
            # 计算分支因子
            if stats["total_nodes"] > 1:
                stats["branching_factor"] = (stats["total_nodes"] - 1) / (stats["total_nodes"] - stats["leaf_nodes"])
            
            return stats
            
        except Exception as e:
            self.logger.error(f"分析谱系统计失败: {e}")
            return {}
    
    def _export_to_csv(self, history_data: dict[str, Any]) -> str:
        """导出为CSV格式"""
        try:
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入版本历史
            writer.writerow(["Version ID", "Knowledge ID", "Timestamp", "Author", "Change Type", "Content Length"])
            for version in history_data["version_history"]:
                writer.writerow([
                    version["version_id"],
                    version["knowledge_id"],
                    version["timestamp"],
                    version["author"],
                    version["change_type"],
                    len(version["content"])
                ])
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"导出CSV失败: {e}")
            return ""
    
    async def _load_version_history(self, knowledge_id: str) -> list[KnowledgeVersion]:
        """加载版本历史"""
        # 简化实现，实际应该从持久化存储加载
        return []
    
    def _start_background_tasks(self):
        """启动后台任务"""
        def auto_save_task():
            while True:
                time.sleep(self.auto_save_interval)
                try:
                    # 自动保存历史数据
                    pass
                except Exception as e:
                    self.logger.error(f"后台自动保存失败: {e}")
        
        # 启动后台线程
        save_thread = threading.Thread(target=auto_save_task, daemon=True)
        save_thread.start()


# 使用示例
async def example_usage():
    """使用示例"""
    # 初始化组件
    knowledge_retrieval = KnowledgeRetrievalService()
    sskg_manager = EnhancedSSKGManager()
    memory_agent = MemAgent()
    
    # 创建历史追溯系统
    tracker = KnowledgeHistoryTracker(knowledge_retrieval, sskg_manager, memory_agent)
    
    # 模拟知识变更
    knowledge_id = "test_knowledge_001"
    
    # 创建初始版本
    version1 = await tracker.track_knowledge_change(
        knowledge_id=knowledge_id,
        old_content="",
        new_content="这是初始版本的知识内容",
        author="user1",
        change_type=ChangeType.CREATION,
        change_summary="创建初始版本"
    )
    
    # 修改版本
    version2 = await tracker.track_knowledge_change(
        knowledge_id=knowledge_id,
        old_content="这是初始版本的知识内容",
        new_content="这是更新后的知识内容，增加了一些新的信息",
        author="user2",
        change_type=ChangeType.MODIFICATION,
        change_summary="添加新信息"
    )
    
    # 获取版本历史
    history = await tracker.get_version_history(knowledge_id)
    print(f"版本历史数量: {len(history)}")
    
    # 追溯演化
    evolution_trace = await tracker.trace_knowledge_evolution(
        knowledge_id=knowledge_id,
        trace_type=TraceType.VERSION_HISTORY
    )
    
    print(f"演化洞察: {evolution_trace.insights}")
    
    # 比较版本
    comparison = await tracker.compare_versions(version1, version2)
    print(f"版本相似度: {comparison.get('similarity_score', 0.0):.2f}")
    
    # 分析演化模式
    patterns = await tracker.analyze_evolution_patterns(knowledge_id)
    print(f"演化模式: {patterns.get('patterns_identified', [])}")


if __name__ == "__main__":
    asyncio.run(example_usage())