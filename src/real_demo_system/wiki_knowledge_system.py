"""Wiki知识沉淀系统

实现知识的积累、管理和检索，将辩论结果和分析过程沉淀为可复用的知识。
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class KnowledgeType(Enum):
    """知识类型"""
    CONCEPT = "concept"
    ANALYSIS = "analysis"
    DEBATE_RESULT = "debate_result"
    CONSENSUS = "consensus"
    METHODOLOGY = "methodology"
    CASE_STUDY = "case_study"


class KnowledgeStatus(Enum):
    """知识状态"""
    DRAFT = "draft"
    REVIEWED = "reviewed"
    VALIDATED = "validated"
    ARCHIVED = "archived"


@dataclass
class KnowledgeEntry:
    """知识条目"""
    entry_id: str
    title: str
    content: str
    knowledge_type: KnowledgeType
    status: KnowledgeStatus
    tags: list[str]
    related_entries: list[str]
    source_data: dict[str, Any]
    quality_score: float
    created_at: datetime
    updated_at: datetime
    version: int
    contributors: list[str]
    
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data['knowledge_type'] = self.knowledge_type.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class KnowledgeGraph:
    """知识图谱"""
    nodes: dict[str, dict[str, Any]]
    edges: list[dict[str, Any]]
    clusters: dict[str, list[str]]


class WikiKnowledgeSystem:
    """Wiki知识沉淀系统
    
    负责将辩论结果、分析过程和洞察沉淀为结构化的知识库。
    """
    
    def __init__(self, storage_path: str = "data/wiki_knowledge"):
        """初始化知识系统
        
        Args:
            storage_path: 知识存储路径
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 知识库
        self.knowledge_entries: dict[str, KnowledgeEntry] = {}
        self.knowledge_graph = KnowledgeGraph(nodes={}, edges=[], clusters={})
        self.tag_index: dict[str, set[str]] = {}
        self.search_index: dict[str, set[str]] = {}
        
        # 加载现有知识
        self._load_existing_knowledge()
        
        logger.info(f"WikiKnowledgeSystem initialized with {len(self.knowledge_entries)} entries")
    
    def _load_existing_knowledge(self):
        """加载现有知识"""
        try:
            knowledge_file = self.storage_path / "knowledge_entries.json"
            if knowledge_file.exists():
                with open(knowledge_file, encoding='utf-8') as f:
                    data = json.load(f)
                    
                for entry_data in data.get('entries', []):
                    entry = KnowledgeEntry(
                        entry_id=entry_data['entry_id'],
                        title=entry_data['title'],
                        content=entry_data['content'],
                        knowledge_type=KnowledgeType(entry_data['knowledge_type']),
                        status=KnowledgeStatus(entry_data['status']),
                        tags=entry_data['tags'],
                        related_entries=entry_data['related_entries'],
                        source_data=entry_data['source_data'],
                        quality_score=entry_data['quality_score'],
                        created_at=datetime.fromisoformat(entry_data['created_at']),
                        updated_at=datetime.fromisoformat(entry_data['updated_at']),
                        version=entry_data['version'],
                        contributors=entry_data['contributors']
                    )
                    self.knowledge_entries[entry.entry_id] = entry
                    self._update_indices(entry)
                    
        except Exception as e:
            logger.error(f"Failed to load existing knowledge: {e}")
    
    def _save_knowledge(self):
        """保存知识到文件"""
        try:
            knowledge_file = self.storage_path / "knowledge_entries.json"
            data = {
                'entries': [entry.to_dict() for entry in self.knowledge_entries.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save knowledge: {e}")
    
    async def distill_debate_knowledge(
        self, 
        debate_transcript: dict[str, Any],
        consensus_result: dict[str, Any]
    ) -> str:
        """从辩论中提炼知识
        
        Args:
            debate_transcript: 辩论记录
            consensus_result: 共识结果
            
        Returns:
            知识条目ID
        """
        # 生成知识条目ID
        content_hash = hashlib.md5(
            f"{debate_transcript['topic']}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
        entry_id = f"debate_knowledge_{content_hash}"
        
        # 构建知识提炼提示
        distillation_prompt = f"""
        从以下辩论过程中提炼可复用的知识：
        
        辩论主题: {debate_transcript['topic']}
        参与角色: {len(debate_transcript['transcript'])} 个角色
        
        辩论过程摘要:
        {self._summarize_debate_transcript(debate_transcript['transcript'])}
        
        共识结果:
        {consensus_result.get('consensus_analysis', '无共识分析')}
        
        请提炼出以下知识内容：
        1. 核心概念和定义
        2. 关键洞察和发现
        3. 方法论和分析框架
        4. 可复用的决策原则
        5. 相关案例和证据
        
        请以结构化的方式组织这些知识，便于后续检索和应用。
        """
        
        try:
            # 这里应该调用LLM进行知识提炼，暂时使用简化版本
            distilled_content = f"""
# {debate_transcript['topic']} - 辩论知识总结

## 核心概念
基于多角色辩论的分析结果，本主题涉及以下核心概念：
- 认知多样性在决策中的价值
- 不同专业背景带来的视角差异
- 共识形成的动态过程

## 关键洞察
1. 多角色参与能够揭示单一视角的盲点
2. 认知差异是创新和深度分析的源泉
3. 共识不等于一致，而是在分歧中找到平衡

## 方法论框架
- 结构化辩论流程
- 认知档案分析
- 共识计算算法

## 决策原则
- 重视多元化观点
- 基于证据的推理
- 透明的决策过程

## 相关证据
- 参与角色数: {len(set(arg['role_id'] for arg in debate_transcript['transcript']))}
- 论证总数: {len(debate_transcript['transcript'])}
- 认知多样性分数: {debate_transcript.get('metrics', {}).get('cognitive_diversity_score', 0)}
"""
            
            # 提取标签
            tags = self._extract_tags_from_content(distilled_content)
            tags.extend(['辩论', '共识', '多角色分析'])
            
            # 创建知识条目
            knowledge_entry = KnowledgeEntry(
                entry_id=entry_id,
                title=f"{debate_transcript['topic']} - 辩论分析",
                content=distilled_content,
                knowledge_type=KnowledgeType.DEBATE_RESULT,
                status=KnowledgeStatus.DRAFT,
                tags=list(set(tags)),
                related_entries=[],
                source_data={
                    'debate_id': debate_transcript.get('debate_id'),
                    'debate_transcript': debate_transcript,
                    'consensus_result': consensus_result
                },
                quality_score=0.7,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                contributors=['system']
            )
            
            # 存储知识条目
            self.knowledge_entries[entry_id] = knowledge_entry
            self._update_indices(knowledge_entry)
            self._save_knowledge()
            
            logger.info(f"Distilled debate knowledge: {entry_id}")
            return entry_id
            
        except Exception as e:
            logger.error(f"Failed to distill debate knowledge: {e}")
            return ""
    
    def _summarize_debate_transcript(self, transcript: list[dict[str, Any]]) -> str:
        """总结辩论记录"""
        if not transcript:
            return "无辩论记录"
        
        summary_parts = []
        
        # 按角色分组论证
        role_arguments = {}
        for arg in transcript:
            role_name = arg.get('role_name', 'Unknown')
            if role_name not in role_arguments:
                role_arguments[role_name] = []
            role_arguments[role_name].append(arg)
        
        # 为每个角色生成摘要
        for role_name, arguments in role_arguments.items():
            arg_types = [arg.get('argument_type', 'unknown') for arg in arguments]
            summary_parts.append(f"- {role_name}: {len(arguments)}个论证 ({', '.join(set(arg_types))})")
        
        return "\n".join(summary_parts)
    
    def _extract_tags_from_content(self, content: str) -> list[str]:
        """从内容中提取标签"""
        # 简化的标签提取
        tags = []
        
        # 基于关键词提取
        keywords = {
            'AI': ['AI', '人工智能', 'artificial intelligence'],
            '伦理': ['伦理', '道德', 'ethics', 'moral'],
            '决策': ['决策', '选择', 'decision', 'choice'],
            '分析': ['分析', '评估', 'analysis', 'evaluation'],
            '风险': ['风险', '危险', 'risk', 'danger'],
            '策略': ['策略', '战略', 'strategy', 'strategic']
        }
        
        content_lower = content.lower()
        for tag, words in keywords.items():
            if any(word.lower() in content_lower for word in words):
                tags.append(tag)
        
        return tags
    
    def _update_indices(self, entry: KnowledgeEntry):
        """更新索引"""
        # 更新标签索引
        for tag in entry.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(entry.entry_id)
        
        # 更新搜索索引
        search_terms = entry.title.lower().split() + entry.content.lower().split()
        for term in search_terms:
            if len(term) > 2:  # 忽略太短的词
                if term not in self.search_index:
                    self.search_index[term] = set()
                self.search_index[term].add(entry.entry_id)
    
    async def create_analysis_knowledge(
        self,
        title: str,
        analysis_content: str,
        source_data: dict[str, Any],
        tags: Optional[list[str]] = None
    ) -> str:
        """创建分析知识条目
        
        Args:
            title: 知识标题
            analysis_content: 分析内容
            source_data: 源数据
            tags: 标签列表
            
        Returns:
            知识条目ID
        """
        # 生成条目ID
        content_hash = hashlib.md5(f"{title}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        entry_id = f"analysis_{content_hash}"
        
        # 处理标签
        if tags is None:
            tags = self._extract_tags_from_content(analysis_content)
        
        # 创建知识条目
        knowledge_entry = KnowledgeEntry(
            entry_id=entry_id,
            title=title,
            content=analysis_content,
            knowledge_type=KnowledgeType.ANALYSIS,
            status=KnowledgeStatus.DRAFT,
            tags=tags,
            related_entries=[],
            source_data=source_data,
            quality_score=0.6,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1,
            contributors=['system']
        )
        
        # 存储知识条目
        self.knowledge_entries[entry_id] = knowledge_entry
        self._update_indices(knowledge_entry)
        self._save_knowledge()
        
        logger.info(f"Created analysis knowledge: {entry_id}")
        return entry_id
    
    def search_knowledge(
        self,
        query: str,
        knowledge_types: Optional[list[KnowledgeType]] = None,
        tags: Optional[list[str]] = None,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """搜索知识
        
        Args:
            query: 搜索查询
            knowledge_types: 知识类型过滤
            tags: 标签过滤
            limit: 结果限制
            
        Returns:
            搜索结果
        """
        candidate_entries = set()
        
        # 基于查询词搜索
        query_terms = query.lower().split()
        for term in query_terms:
            if term in self.search_index:
                candidate_entries.update(self.search_index[term])
        
        # 基于标签搜索
        if tags:
            tag_entries = set()
            for tag in tags:
                if tag in self.tag_index:
                    tag_entries.update(self.tag_index[tag])
            if tag_entries:
                candidate_entries = candidate_entries.intersection(tag_entries) if candidate_entries else tag_entries
        
        # 如果没有候选结果，返回所有条目
        if not candidate_entries:
            candidate_entries = set(self.knowledge_entries.keys())
        
        # 过滤和排序结果
        results = []
        for entry_id in candidate_entries:
            entry = self.knowledge_entries[entry_id]
            
            # 类型过滤
            if knowledge_types and entry.knowledge_type not in knowledge_types:
                continue
            
            # 计算相关性分数
            relevance_score = self._calculate_relevance_score(entry, query, tags)
            
            results.append({
                'entry': entry.to_dict(),
                'relevance_score': relevance_score
            })
        
        # 按相关性排序
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:limit]
    
    def _calculate_relevance_score(
        self, 
        entry: KnowledgeEntry, 
        query: str, 
        tags: Optional[list[str]]
    ) -> float:
        """计算相关性分数"""
        score = 0.0
        
        # 标题匹配
        query_lower = query.lower()
        if query_lower in entry.title.lower():
            score += 0.5
        
        # 内容匹配
        content_lower = entry.content.lower()
        query_terms = query_lower.split()
        matching_terms = sum(1 for term in query_terms if term in content_lower)
        score += (matching_terms / len(query_terms)) * 0.3
        
        # 标签匹配
        if tags:
            matching_tags = len(set(tags).intersection(set(entry.tags)))
            score += (matching_tags / len(tags)) * 0.2
        
        # 质量分数
        score += entry.quality_score * 0.1
        
        # 新鲜度分数
        days_old = (datetime.now() - entry.updated_at).days
        freshness = max(0, 1 - days_old / 365)  # 一年后新鲜度为0
        score += freshness * 0.1
        
        return min(score, 1.0)
    
    def get_knowledge_by_id(self, entry_id: str) -> Optional[dict[str, Any]]:
        """根据ID获取知识条目"""
        if entry_id in self.knowledge_entries:
            return self.knowledge_entries[entry_id].to_dict()
        return None
    
    def get_related_knowledge(self, entry_id: str, limit: int = 5) -> list[dict[str, Any]]:
        """获取相关知识"""
        if entry_id not in self.knowledge_entries:
            return []
        
        entry = self.knowledge_entries[entry_id]
        
        # 基于标签找相关知识
        related_entries = set()
        for tag in entry.tags:
            if tag in self.tag_index:
                related_entries.update(self.tag_index[tag])
        
        # 移除自身
        related_entries.discard(entry_id)
        
        # 计算相关性并排序
        results = []
        for related_id in related_entries:
            related_entry = self.knowledge_entries[related_id]
            
            # 计算标签重叠度
            tag_overlap = len(set(entry.tags).intersection(set(related_entry.tags)))
            relevance = tag_overlap / max(len(entry.tags), 1)
            
            results.append({
                'entry': related_entry.to_dict(),
                'relevance_score': relevance
            })
        
        # 按相关性排序
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:limit]
    
    def get_knowledge_statistics(self) -> dict[str, Any]:
        """获取知识库统计信息"""
        total_entries = len(self.knowledge_entries)
        
        # 按类型统计
        type_distribution = {}
        status_distribution = {}
        
        for entry in self.knowledge_entries.values():
            entry_type = entry.knowledge_type.value
            entry_status = entry.status.value
            
            type_distribution[entry_type] = type_distribution.get(entry_type, 0) + 1
            status_distribution[entry_status] = status_distribution.get(entry_status, 0) + 1
        
        # 标签统计
        tag_counts = {}
        for tag, entry_ids in self.tag_index.items():
            tag_counts[tag] = len(entry_ids)
        
        # 最受欢迎的标签
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_entries": total_entries,
            "type_distribution": type_distribution,
            "status_distribution": status_distribution,
            "total_tags": len(self.tag_index),
            "popular_tags": popular_tags,
            "search_index_size": len(self.search_index),
            "last_updated": max(
                (entry.updated_at for entry in self.knowledge_entries.values()),
                default=datetime.now()
            ).isoformat()
        }
    
    def export_knowledge_graph(self) -> dict[str, Any]:
        """导出知识图谱"""
        # 构建节点
        nodes = {}
        for entry_id, entry in self.knowledge_entries.items():
            nodes[entry_id] = {
                "id": entry_id,
                "title": entry.title,
                "type": entry.knowledge_type.value,
                "tags": entry.tags,
                "quality_score": entry.quality_score
            }
        
        # 构建边（基于标签相似性）
        edges = []
        entry_ids = list(self.knowledge_entries.keys())
        
        for i, entry_id1 in enumerate(entry_ids):
            for entry_id2 in entry_ids[i+1:]:
                entry1 = self.knowledge_entries[entry_id1]
                entry2 = self.knowledge_entries[entry_id2]
                
                # 计算标签相似性
                common_tags = set(entry1.tags).intersection(set(entry2.tags))
                if common_tags:
                    similarity = len(common_tags) / len(set(entry1.tags).union(set(entry2.tags)))
                    if similarity > 0.2:  # 相似性阈值
                        edges.append({
                            "source": entry_id1,
                            "target": entry_id2,
                            "weight": similarity,
                            "common_tags": list(common_tags)
                        })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": self.get_knowledge_statistics()
        }