"""
@Time: 2025-08-03
@Author: DAIP-LIVE
@File: knowledge_association_engine.py
@Description: V0.3.4 知识关联发现引擎 - 知识点间的语义关联和相关性计算
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import numpy as np
from collections import defaultdict, Counter
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
from ..core_services.knowledge_retrieval_service import KnowledgeRetrievalService


class AssociationType(Enum):
    """关联类型枚举"""
    SEMANTIC_SIMILARITY = "semantic_similarity"  # 语义相似性
    CONCEPTUAL_RELATION = "conceptual_relation"  # 概念关系
    TEMPORAL_RELATION = "temporal_relation"  # 时间关系
    CAUSAL_RELATION = "causal_relation"  # 因果关系
    HIERARCHICAL_RELATION = "hierarchical_relation"  # 层次关系
    CROSS_DOMAIN_RELATION = "cross_domain_relation"  # 跨领域关系


@dataclass
class Association:
    """知识关联"""
    source_id: str
    target_id: str
    association_type: AssociationType
    strength: float  # 关联强度 0-1
    confidence: float  # 置信度 0-1
    description: str
    metadata: Dict[str, Any]
    discovered_time: datetime


@dataclass
class KnowledgeNode:
    """知识节点"""
    id: str
    title: str
    content: str
    type: str
    domain: str
    tags: List[str]
    properties: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


@dataclass
class AssociationPattern:
    """关联模式"""
    pattern_id: str
    pattern_type: str
    nodes: List[str]
    relations: List[Tuple[str, str, str]]  # (source, relation, target)
    frequency: int
    significance: float
    description: str


class SemanticAnalyzer:
    """语义分析器"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.similarity_threshold = 0.3
        
    async def analyze_semantic_relations(self, source_node: KnowledgeNode, 
                                       target_node: KnowledgeNode) -> List[Association]:
        """分析语义关系"""
        try:
            associations = []
            
            # 计算语义相似度
            semantic_similarity = self._calculate_semantic_similarity(source_node, target_node)
            
            if semantic_similarity > self.similarity_threshold:
                associations.append(Association(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    association_type=AssociationType.SEMANTIC_SIMILARITY,
                    strength=semantic_similarity,
                    confidence=min(0.9, semantic_similarity + 0.2),
                    description=f"语义相似度: {semantic_similarity:.2f}",
                    metadata={
                        'similarity_score': semantic_similarity,
                        'shared_keywords': self._find_shared_keywords(source_node, target_node)
                    },
                    discovered_time=datetime.now()
                ))
            
            # 分析概念关系
            conceptual_relations = await self._analyze_conceptual_relations(source_node, target_node)
            associations.extend(conceptual_relations)
            
            return associations
            
        except Exception as e:
            logging.error(f"语义关系分析失败: {e}")
            return []
    
    def _calculate_semantic_similarity(self, source: KnowledgeNode, target: KnowledgeNode) -> float:
        """计算语义相似度"""
        try:
            # 使用TF-IDF计算文本相似度
            texts = [source.content, target.content]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # 考虑标题相似度
            title_similarity = self._calculate_title_similarity(source.title, target.title)
            
            # 综合相似度
            combined_similarity = 0.7 * similarity + 0.3 * title_similarity
            
            return combined_similarity
            
        except Exception as e:
            logging.error(f"语义相似度计算失败: {e}")
            return 0.0
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """计算标题相似度"""
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _find_shared_keywords(self, source: KnowledgeNode, target: KnowledgeNode) -> List[str]:
        """查找共享关键词"""
        source_words = set(source.content.lower().split())
        target_words = set(target.content.lower().split())
        
        shared = source_words.intersection(target_words)
        # 过滤掉常见词
        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with'}
        shared = [word for word in shared if word not in stop_words and len(word) > 2]
        
        return shared[:10]  # 返回前10个共享词
    
    async def _analyze_conceptual_relations(self, source: KnowledgeNode, 
                                          target: KnowledgeNode) -> List[Association]:
        """分析概念关系"""
        relations = []
        
        # 检查领域关系
        if source.domain == target.domain:
            relations.append(Association(
                source_id=source.id,
                target_id=target.id,
                association_type=AssociationType.CONCEPTUAL_RELATION,
                strength=0.6,
                confidence=0.8,
                description=f"同领域概念: {source.domain}",
                metadata={'relation_subtype': 'same_domain'},
                discovered_time=datetime.now()
            ))
        
        # 检查标签关系
        shared_tags = set(source.tags).intersection(set(target.tags))
        if shared_tags:
            relations.append(Association(
                source_id=source.id,
                target_id=target.id,
                association_type=AssociationType.CONCEPTUAL_RELATION,
                strength=0.5,
                confidence=0.7,
                description=f"共享标签: {', '.join(shared_tags)}",
                metadata={'relation_subtype': 'shared_tags', 'shared_tags': list(shared_tags)},
                discovered_time=datetime.now()
            ))
        
        return relations


class GraphMiner:
    """图挖掘器"""
    
    def __init__(self):
        self.min_pattern_frequency = 2
        self.significance_threshold = 0.5
        
    async def discover_patterns(self, knowledge_id: str, 
                              sskg_manager: EnhancedSSKGManager) -> List[AssociationPattern]:
        """发现关联模式"""
        try:
            # 获取知识子图
            subgraph = await sskg_manager.get_knowledge_subgraph(knowledge_id, max_depth=3)
            
            if not subgraph:
                return []
            
            # 转换为NetworkX图
            nx_graph = self._convert_to_networkx(subgraph)
            
            # 发现模式
            patterns = []
            
            # 发现频繁路径模式
            path_patterns = self._discover_path_patterns(nx_graph)
            patterns.extend(path_patterns)
            
            # 发现社区结构
            community_patterns = self._discover_community_patterns(nx_graph)
            patterns.extend(community_patterns)
            
            # 发现中心节点模式
            centrality_patterns = self._discover_centrality_patterns(nx_graph)
            patterns.extend(centrality_patterns)
            
            return patterns
            
        except Exception as e:
            logging.error(f"模式发现失败: {e}")
            return []
    
    def _convert_to_networkx(self, subgraph: Dict) -> nx.Graph:
        """转换为NetworkX图"""
        G = nx.Graph()
        
        # 添加节点
        for node in subgraph.get('nodes', []):
            G.add_node(node['id'], **node.get('properties', {}))
        
        # 添加边
        for edge in subgraph.get('edges', []):
            G.add_edge(
                edge['source'], 
                edge['target'], 
                relation=edge.get('relation', 'related'),
                weight=edge.get('weight', 1.0)
            )
        
        return G
    
    def _discover_path_patterns(self, G: nx.Graph) -> List[AssociationPattern]:
        """发现路径模式"""
        patterns = []
        
        # 发现长度为2的频繁路径
        path_length = 2
        path_counts = Counter()
        
        for source in G.nodes():
            for target in G.nodes():
                if source != target:
                    try:
                        paths = list(nx.all_simple_paths(G, source, target, cutoff=path_length))
                        for path in paths:
                            if len(path) == path_length + 1:
                                path_key = ' -> '.join(path)
                                path_counts[path_key] += 1
                    except nx.NetworkXNoPath:
                        continue
        
        # 过滤频繁路径
        for path, count in path_counts.items():
            if count >= self.min_pattern_frequency:
                nodes = path.split(' -> ')
                relations = []
                
                # 构建关系列表
                for i in range(len(nodes) - 1):
                    edge_data = G.get_edge_data(nodes[i], nodes[i+1])
                    relation = edge_data.get('relation', 'related') if edge_data else 'related'
                    relations.append((nodes[i], relation, nodes[i+1]))
                
                pattern = AssociationPattern(
                    pattern_id=f"path_pattern_{len(patterns)}",
                    pattern_type="frequent_path",
                    nodes=nodes,
                    relations=relations,
                    frequency=count,
                    significance=count / len(G.nodes()),
                    description=f"频繁路径: {path} (出现次数: {count})"
                )
                patterns.append(pattern)
        
        return patterns
    
    def _discover_community_patterns(self, G: nx.Graph) -> List[AssociationPattern]:
        """发现社区模式"""
        patterns = []
        
        try:
            # 使用Louvain算法发现社区
            communities = nx.community.louvain_communities(G)
            
            for i, community in enumerate(communities):
                if len(community) >= 3:  # 只考虑有3个以上节点的社区
                    # 构建社区内的关系
                    relations = []
                    for source in community:
                        for target in community:
                            if source != target and G.has_edge(source, target):
                                edge_data = G.get_edge_data(source, target)
                                relation = edge_data.get('relation', 'related')
                                relations.append((source, relation, target))
                    
                    pattern = AssociationPattern(
                        pattern_id=f"community_{i}",
                        pattern_type="community",
                        nodes=list(community),
                        relations=relations,
                        frequency=len(relations),
                        significance=len(community) / len(G.nodes()),
                        description=f"社区结构: 节点数{len(community)}, 关系数{len(relations)}"
                    )
                    patterns.append(pattern)
                    
        except Exception as e:
            logging.error(f"社区发现失败: {e}")
        
        return patterns
    
    def _discover_centrality_patterns(self, G: nx.Graph) -> List[AssociationPattern]:
        """发现中心性模式"""
        patterns = []
        
        try:
            # 计算中心性指标
            centrality_measures = {
                'degree': nx.degree_centrality(G),
                'betweenness': nx.betweenness_centrality(G),
                'closeness': nx.closeness_centrality(G),
                'pagerank': nx.pagerank(G)
            }
            
            # 为每个中心性指标找到高中心性节点
            for measure_name, centrality in centrality_measures.items():
                # 找到前20%的高中心性节点
                sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
                top_nodes = sorted_nodes[:max(1, len(sorted_nodes) // 5)]
                
                if top_nodes:
                    top_node_ids = [node_id for node_id, score in top_nodes]
                    avg_centrality = np.mean([score for _, score in top_nodes])
                    
                    # 构建这些节点之间的关系
                    relations = []
                    for source in top_node_ids:
                        for target in top_node_ids:
                            if source != target and G.has_edge(source, target):
                                edge_data = G.get_edge_data(source, target)
                                relation = edge_data.get('relation', 'related')
                                relations.append((source, relation, target))
                    
                    pattern = AssociationPattern(
                        pattern_id=f"centrality_{measure_name}",
                        pattern_type=f"high_{measure_name}_centrality",
                        nodes=top_node_ids,
                        relations=relations,
                        frequency=len(relations),
                        significance=avg_centrality,
                        description=f"高{measure_name}中心性节点: 平均中心性{avg_centrality:.3f}"
                    )
                    patterns.append(pattern)
                    
        except Exception as e:
            logging.error(f"中心性模式发现失败: {e}")
        
        return patterns


class PatternDetector:
    """模式检测器"""
    
    def __init__(self):
        self.pattern_templates = [
            {
                'name': 'causal_chain',
                'description': '因果链模式',
                'relations': ['CAUSES', 'LEADS_TO', 'RESULTS_IN']
            },
            {
                'name': 'hierarchical_structure',
                'description': '层次结构模式',
                'relations': ['PART_OF', 'SUBTYPE_OF', 'INSTANCE_OF']
            },
            {
                'name': 'contradiction_pattern',
                'description': '矛盾模式',
                'relations': ['CONTRADICTS', 'OPPOSES', 'CONFLICTS_WITH']
            }
        ]
    
    async def detect_hidden_patterns(self, knowledge_id: str,
                                   sskg_manager: EnhancedSSKGManager) -> List[AssociationPattern]:
        """检测隐藏模式"""
        try:
            patterns = []
            
            # 获取相关知识
            related_knowledge = await sskg_manager.find_related_nodes(
                knowledge_id, max_depth=2
            )
            
            # 基于模板检测模式
            for template in self.pattern_templates:
                template_patterns = await self._detect_template_patterns(
                    template, related_knowledge
                )
                patterns.extend(template_patterns)
            
            # 检测时间模式
            temporal_patterns = await self._detect_temporal_patterns(related_knowledge)
            patterns.extend(temporal_patterns)
            
            # 检测跨领域模式
            cross_domain_patterns = await self._detect_cross_domain_patterns(related_knowledge)
            patterns.extend(cross_domain_patterns)
            
            return patterns
            
        except Exception as e:
            logging.error(f"隐藏模式检测失败: {e}")
            return []
    
    async def _detect_template_patterns(self, template: Dict, 
                                      related_knowledge: List[Dict]) -> List[AssociationPattern]:
        """基于模板检测模式"""
        patterns = []
        
        try:
            # 构建关系图
            relation_graph = self._build_relation_graph(related_knowledge)
            
            # 查找匹配模板的模式
            template_relations = template['relations']
            
            for source_node in relation_graph:
                for target_node in relation_graph[source_node]:
                    relation = relation_graph[source_node][target_node]
                    
                    if relation in template_relations:
                        # 检查是否形成模式
                        pattern_nodes = [source_node, target_node]
                        pattern_relations = [(source_node, relation, target_node)]
                        
                        # 查找扩展模式
                        extended_pattern = self._extend_pattern(
                            pattern_nodes, pattern_relations, relation_graph, template_relations
                        )
                        
                        if len(extended_pattern['nodes']) >= 3:
                            pattern = AssociationPattern(
                                pattern_id=f"{template['name']}_{len(patterns)}",
                                pattern_type=template['name'],
                                nodes=extended_pattern['nodes'],
                                relations=extended_pattern['relations'],
                                frequency=1,  # 可以通过历史数据统计
                                significance=len(extended_pattern['nodes']) * 0.1,
                                description=f"{template['description']}: {len(extended_pattern['nodes'])}个节点"
                            )
                            patterns.append(pattern)
                            
        except Exception as e:
            logging.error(f"模板模式检测失败: {e}")
        
        return patterns
    
    def _build_relation_graph(self, related_knowledge: List[Dict]) -> Dict[str, Dict[str, str]]:
        """构建关系图"""
        graph = defaultdict(dict)
        
        for item in related_knowledge:
            source_id = item.get('id', '')
            relations = item.get('relations', [])
            
            for relation in relations:
                target_id = relation.get('target', '')
                relation_type = relation.get('type', '')
                
                if source_id and target_id and relation_type:
                    graph[source_id][target_id] = relation_type
        
        return graph
    
    def _extend_pattern(self, nodes: List[str], relations: List[Tuple[str, str, str]],
                        graph: Dict[str, Dict[str, str]], 
                        template_relations: List[str]) -> Dict[str, Any]:
        """扩展模式"""
        extended_nodes = nodes.copy()
        extended_relations = relations.copy()
        
        # 尝试扩展最后一个节点
        last_node = nodes[-1]
        
        for next_node in graph.get(last_node, {}):
            if graph[last_node][next_node] in template_relations and next_node not in extended_nodes:
                extended_nodes.append(next_node)
                extended_relations.append((last_node, graph[last_node][next_node], next_node))
                break
        
        return {
            'nodes': extended_nodes,
            'relations': extended_relations
        }
    
    async def _detect_temporal_patterns(self, related_knowledge: List[Dict]) -> List[AssociationPattern]:
        """检测时间模式"""
        patterns = []
        
        try:
            # 按时间排序知识项
            time_sorted = sorted(
                related_knowledge,
                key=lambda x: x.get('created_time', ''),
                reverse=True
            )
            
            # 检测时间序列模式
            if len(time_sorted) >= 3:
                # 检测进化模式
                evolution_pattern = self._detect_evolution_pattern(time_sorted)
                if evolution_pattern:
                    patterns.append(evolution_pattern)
                
                # 检测周期性模式
                periodic_pattern = self._detect_periodic_pattern(time_sorted)
                if periodic_pattern:
                    patterns.append(periodic_pattern)
                    
        except Exception as e:
            logging.error(f"时间模式检测失败: {e}")
        
        return patterns
    
    def _detect_evolution_pattern(self, time_sorted: List[Dict]) -> Optional[AssociationPattern]:
        """检测进化模式"""
        try:
            # 检查是否有版本演进关系
            version_pattern = re.compile(r'v\d+\.?\d*|version\s*\d+|rev\d+', re.IGNORECASE)
            
            versioned_items = []
            for item in time_sorted[:10]:  # 检查前10个
                title = item.get('title', '')
                if version_pattern.search(title):
                    versioned_items.append(item)
            
            if len(versioned_items) >= 3:
                nodes = [item.get('id', '') for item in versioned_items]
                relations = []
                
                # 构建时间序列关系
                for i in range(len(nodes) - 1):
                    relations.append((nodes[i], 'EVOLVES_TO', nodes[i+1]))
                
                return AssociationPattern(
                    pattern_id="evolution_pattern",
                    pattern_type="temporal_evolution",
                    nodes=nodes,
                    relations=relations,
                    frequency=len(nodes),
                    significance=len(nodes) * 0.15,
                    description=f"进化模式: {len(nodes)}个版本演进"
                )
            
        except Exception as e:
            logging.error(f"进化模式检测失败: {e}")
        
        return None
    
    def _detect_periodic_pattern(self, time_sorted: List[Dict]) -> Optional[AssociationPattern]:
        """检测周期性模式"""
        # 简化实现，实际应该分析时间间隔
        return None
    
    async def _detect_cross_domain_patterns(self, related_knowledge: List[Dict]) -> List[AssociationPattern]:
        """检测跨领域模式"""
        patterns = []
        
        try:
            # 按领域分组
            domain_groups = defaultdict(list)
            for item in related_knowledge:
                domain = item.get('domain', 'general')
                domain_groups[domain].append(item)
            
            # 检测跨领域连接
            domains = list(domain_groups.keys())
            
            for i, domain1 in enumerate(domains):
                for domain2 in domains[i+1:]:
                    # 查找跨领域连接
                    cross_connections = self._find_cross_domain_connections(
                        domain_groups[domain1], domain_groups[domain2]
                    )
                    
                    if cross_connections:
                        pattern = AssociationPattern(
                            pattern_id=f"cross_domain_{domain1}_{domain2}",
                            pattern_type="cross_domain",
                            nodes=[conn['source'] for conn in cross_connections] + 
                                  [conn['target'] for conn in cross_connections],
                            relations=[(conn['source'], conn['relation'], conn['target']) 
                                      for conn in cross_connections],
                            frequency=len(cross_connections),
                            significance=len(cross_connections) * 0.2,
                            description=f"跨领域模式: {domain1} <-> {domain2}"
                        )
                        patterns.append(pattern)
                        
        except Exception as e:
            logging.error(f"跨领域模式检测失败: {e}")
        
        return patterns
    
    def _find_cross_domain_connections(self, domain1_items: List[Dict], 
                                      domain2_items: List[Dict]) -> List[Dict]:
        """查找跨领域连接"""
        connections = []
        
        # 简化实现：基于标题相似度
        domain1_titles = [item.get('title', '').lower() for item in domain1_items]
        domain2_titles = [item.get('title', '').lower() for item in domain2_items]
        
        for i, title1 in enumerate(domain1_titles):
            for j, title2 in enumerate(domain2_titles):
                # 简单的标题匹配
                if any(word in title2 for word in title1.split() if len(word) > 3):
                    connections.append({
                        'source': domain1_items[i].get('id', ''),
                        'target': domain2_items[j].get('id', ''),
                        'relation': 'CROSS_DOMAIN_RELATED'
                    })
                    break
        
        return connections[:5]  # 限制连接数量


class RelationExtractor:
    """关系提取器"""
    
    def __init__(self):
        self.relation_patterns = {
            'CAUSES': [
                r'causes?',
                r'leads to',
                r'results in',
                r'produces?',
                r'generates?',
                r'creates?',
            ],
            'PART_OF': [
                r'part of',
                r'component of',
                r'element of',
                r'subset of',
                r'section of',
            ],
            'SIMILAR_TO': [
                r'similar to',
                r'like',
                r'resembles?',
                r'analogous to',
                r'comparable to',
            ],
            'CONTRADICTS': [
                r'contradicts?',
                r'opposes?',
                r'conflicts with',
                r'inconsistent with',
                r'contrary to',
            ]
        }
    
    async def extract_relations(self, text: str) -> List[Tuple[str, str, str]]:
        """从文本中提取关系"""
        relations = []
        
        try:
            sentences = text.split('.')
            
            for sentence in sentences:
                # 对每个句子应用关系模式
                for relation_type, patterns in self.relation_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, sentence, re.IGNORECASE)
                        for match in matches:
                            # 简化的实体提取
                            entities = self._extract_entities_from_sentence(sentence, match)
                            if len(entities) >= 2:
                                relations.append((entities[0], relation_type, entities[1]))
            
        except Exception as e:
            logging.error(f"关系提取失败: {e}")
        
        return relations
    
    def _extract_entities_from_sentence(self, sentence: str, match) -> List[str]:
        """从句子中提取实体"""
        # 简化实现：基于名词短语提取
        words = sentence.split()
        entities = []
        
        # 简单的名词短语识别
        current_entity = []
        for word in words:
            if len(word) > 2 and word.isalpha():  # 简单过滤
                current_entity.append(word)
            elif current_entity:
                entities.append(' '.join(current_entity))
                current_entity = []
        
        if current_entity:
            entities.append(' '.join(current_entity))
        
        return entities[:2]  # 返回前两个实体


class KnowledgeAssociationEngine:
    """知识关联发现引擎主类"""
    
    def __init__(self, sskg_manager: EnhancedSSKGManager,
                 knowledge_retrieval: KnowledgeRetrievalService):
        self.semantic_analyzer = SemanticAnalyzer()
        self.graph_miner = GraphMiner()
        self.pattern_detector = PatternDetector()
        self.relation_extractor = RelationExtractor()
        self.sskg_manager = sskg_manager
        self.knowledge_retrieval = knowledge_retrieval
        self.logger = logging.getLogger(__name__)
    
    async def discover_associations(self, knowledge_id: str) -> List[Association]:
        """发现知识点间的深层关联关系"""
        try:
            associations = []
            
            # 获取源知识节点
            source_knowledge = await self._get_knowledge_node(knowledge_id)
            if not source_knowledge:
                return []
            
            # 获取相关知识
            related_knowledge = await self._get_related_knowledge(knowledge_id)
            
            # 分析语义关联
            for related_node in related_knowledge:
                semantic_relations = await self.semantic_analyzer.analyze_semantic_relations(
                    source_knowledge, related_node
                )
                associations.extend(semantic_relations)
            
            # 分析时间关联
            temporal_relations = await self._analyze_temporal_relations(
                source_knowledge, related_knowledge
            )
            associations.extend(temporal_relations)
            
            # 分析因果关联
            causal_relations = await self._analyze_causal_relations(
                source_knowledge, related_knowledge
            )
            associations.extend(causal_relations)
            
            # 分析层次关联
            hierarchical_relations = await self._analyze_hierarchical_relations(
                source_knowledge, related_knowledge
            )
            associations.extend(hierarchical_relations)
            
            # 去重和排序
            unique_associations = self._deduplicate_associations(associations)
            sorted_associations = self._rank_associations(unique_associations)
            
            return sorted_associations[:50]  # 返回前50个关联
            
        except Exception as e:
            self.logger.error(f"关联发现失败: {e}")
            return []
    
    async def discover_patterns(self, knowledge_id: str) -> List[AssociationPattern]:
        """发现关联模式"""
        try:
            patterns = []
            
            # 图模式发现
            graph_patterns = await self.graph_miner.discover_patterns(
                knowledge_id, self.sskg_manager
            )
            patterns.extend(graph_patterns)
            
            # 隐藏模式检测
            hidden_patterns = await self.pattern_detector.detect_hidden_patterns(
                knowledge_id, self.sskg_manager
            )
            patterns.extend(hidden_patterns)
            
            # 排序模式
            sorted_patterns = self._rank_patterns(patterns)
            
            return sorted_patterns[:20]  # 返回前20个模式
            
        except Exception as e:
            self.logger.error(f"模式发现失败: {e}")
            return []
    
    async def _get_knowledge_node(self, knowledge_id: str) -> Optional[KnowledgeNode]:
        """获取知识节点"""
        try:
            # 从知识检索服务获取知识详情
            knowledge_data = await self.knowledge_retrieval.get_knowledge_by_id(knowledge_id)
            
            if knowledge_data:
                return KnowledgeNode(
                    id=knowledge_data.get('id', knowledge_id),
                    title=knowledge_data.get('title', ''),
                    content=knowledge_data.get('content', ''),
                    type=knowledge_data.get('type', 'CONCEPT'),
                    domain=knowledge_data.get('domain', 'general'),
                    tags=knowledge_data.get('tags', []),
                    properties=knowledge_data.get('properties', {}),
                    embedding=knowledge_data.get('embedding')
                )
            
        except Exception as e:
            self.logger.error(f"获取知识节点失败: {e}")
        
        return None
    
    async def _get_related_knowledge(self, knowledge_id: str) -> List[KnowledgeNode]:
        """获取相关知识"""
        try:
            # 从SSKG获取相关知识
            related_nodes = await self.sskg_manager.find_related_nodes(
                knowledge_id, max_depth=2
            )
            
            knowledge_nodes = []
            for node in related_nodes:
                knowledge_node = KnowledgeNode(
                    id=node.get('id', ''),
                    title=node.get('title', ''),
                    content=node.get('content', ''),
                    type=node.get('type', 'CONCEPT'),
                    domain=node.get('domain', 'general'),
                    tags=node.get('tags', []),
                    properties=node.get('properties', {})
                )
                knowledge_nodes.append(knowledge_node)
            
            return knowledge_nodes
            
        except Exception as e:
            self.logger.error(f"获取相关知识失败: {e}")
            return []
    
    async def _analyze_temporal_relations(self, source: KnowledgeNode,
                                       targets: List[KnowledgeNode]) -> List[Association]:
        """分析时间关系"""
        temporal_relations = []
        
        try:
            source_time = self._parse_time(source.properties.get('created_time', ''))
            
            for target in targets:
                target_time = self._parse_time(target.properties.get('created_time', ''))
                
                if source_time and target_time:
                    time_diff = abs((source_time - target_time).days)
                    
                    if time_diff <= 7:  # 一周内
                        relation_type = AssociationType.TEMPORAL_RELATION
                        strength = max(0.1, 1.0 - time_diff / 365.0)
                        
                        temporal_relations.append(Association(
                            source_id=source.id,
                            target_id=target.id,
                            association_type=relation_type,
                            strength=strength,
                            confidence=0.7,
                            description=f"时间相近: {time_diff}天",
                            metadata={'time_diff_days': time_diff},
                            discovered_time=datetime.now()
                        ))
                        
        except Exception as e:
            self.logger.error(f"时间关系分析失败: {e}")
        
        return temporal_relations
    
    async def _analyze_causal_relations(self, source: KnowledgeNode,
                                      targets: List[KnowledgeNode]) -> List[Association]:
        """分析因果关系"""
        causal_relations = []
        
        try:
            # 从内容中提取因果关系
            source_relations = await self.relation_extractor.extract_relations(source.content)
            
            for relation in source_relations:
                source_entity, relation_type, target_entity = relation
                
                if relation_type == 'CAUSES':
                    # 在目标知识中查找匹配的实体
                    for target in targets:
                        if target_entity.lower() in target.content.lower():
                            causal_relations.append(Association(
                                source_id=source.id,
                                target_id=target.id,
                                association_type=AssociationType.CAUSAL_RELATION,
                                strength=0.6,
                                confidence=0.8,
                                description=f"因果关系: {source_entity} -> {target_entity}",
                                metadata={
                                    'source_entity': source_entity,
                                    'target_entity': target_entity,
                                    'relation_type': relation_type
                                },
                                discovered_time=datetime.now()
                            ))
                            break
                        
        except Exception as e:
            self.logger.error(f"因果关系分析失败: {e}")
        
        return causal_relations
    
    async def _analyze_hierarchical_relations(self, source: KnowledgeNode,
                                           targets: List[KnowledgeNode]) -> List[Association]:
        """分析层次关系"""
        hierarchical_relations = []
        
        try:
            # 基于标题和内容分析层次关系
            for target in targets:
                # 检查包含关系
                if self._is_part_of_relation(source, target):
                    hierarchical_relations.append(Association(
                        source_id=source.id,
                        target_id=target.id,
                        association_type=AssociationType.HIERARCHICAL_RELATION,
                        strength=0.7,
                        confidence=0.8,
                        description="层次关系: 部分关系",
                        metadata={'relation_subtype': 'part_of'},
                        discovered_time=datetime.now()
                    ))
                elif self._is_subtype_relation(source, target):
                    hierarchical_relations.append(Association(
                        source_id=source.id,
                        target_id=target.id,
                        association_type=AssociationType.HIERARCHICAL_RELATION,
                        strength=0.6,
                        confidence=0.7,
                        description="层次关系: 子类型关系",
                        metadata={'relation_subtype': 'subtype_of'},
                        discovered_time=datetime.now()
                    ))
                        
        except Exception as e:
            self.logger.error(f"层次关系分析失败: {e}")
        
        return hierarchical_relations
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """解析时间字符串"""
        try:
            if not time_str:
                return None
            
            # 尝试不同的时间格式
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d',
                '%d-%m-%Y %H:%M:%S',
                '%d-%m-%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"时间解析失败: {e}")
            return None
    
    def _is_part_of_relation(self, source: KnowledgeNode, target: KnowledgeNode) -> bool:
        """检查是否为部分关系"""
        # 简化实现：基于标题包含关系
        source_lower = source.title.lower()
        target_lower = target.title.lower()
        
        part_of_indicators = ['part of', 'component of', 'section of', 'element of']
        
        for indicator in part_of_indicators:
            if indicator in source_lower and target_lower in source_lower:
                return True
        
        return False
    
    def _is_subtype_relation(self, source: KnowledgeNode, target: KnowledgeNode) -> bool:
        """检查是否为子类型关系"""
        # 简化实现：基于类型和领域关系
        if source.type != target.type:
            return False
        
        # 检查标题是否包含类型指示词
        source_lower = source.title.lower()
        target_lower = target.title.lower()
        
        subtype_indicators = ['type of', 'kind of', 'form of', 'variant of']
        
        for indicator in subtype_indicators:
            if indicator in source_lower and target_lower in source_lower:
                return True
        
        return False
    
    def _deduplicate_associations(self, associations: List[Association]) -> List[Association]:
        """去重关联"""
        seen = set()
        unique_associations = []
        
        for association in associations:
            # 创建唯一标识
            key = (association.source_id, association.target_id, association.association_type)
            
            if key not in seen:
                seen.add(key)
                unique_associations.append(association)
        
        return unique_associations
    
    def _rank_associations(self, associations: List[Association]) -> List[Association]:
        """排序关联"""
        # 基于强度和置信度排序
        def sort_key(association):
            return (association.strength * 0.6 + association.confidence * 0.4)
        
        return sorted(associations, key=sort_key, reverse=True)
    
    def _rank_patterns(self, patterns: List[AssociationPattern]) -> List[AssociationPattern]:
        """排序模式"""
        # 基于显著性和频率排序
        def sort_key(pattern):
            return (pattern.significance * 0.7 + pattern.frequency * 0.3)
        
        return sorted(patterns, key=sort_key, reverse=True)


# 使用示例
async def example_usage():
    """使用示例"""
    # 初始化组件
    sskg_manager = EnhancedSSKGManager()
    knowledge_retrieval = KnowledgeRetrievalService()
    
    # 创建关联发现引擎
    association_engine = KnowledgeAssociationEngine(sskg_manager, knowledge_retrieval)
    
    # 发现关联
    knowledge_id = "example_knowledge_001"
    associations = await association_engine.discover_associations(knowledge_id)
    
    print(f"发现关联数量: {len(associations)}")
    for i, association in enumerate(associations[:5]):
        print(f"{i+1}. {association.source_id} -> {association.target_id}")
        print(f"   类型: {association.association_type.value}")
        print(f"   强度: {association.strength:.2f}")
        print(f"   描述: {association.description}")
        print()
    
    # 发现模式
    patterns = await association_engine.discover_patterns(knowledge_id)
    
    print(f"发现模式数量: {len(patterns)}")
    for i, pattern in enumerate(patterns[:3]):
        print(f"{i+1}. {pattern.pattern_type}")
        print(f"   节点数: {len(pattern.nodes)}")
        print(f"   描述: {pattern.description}")
        print()


if __name__ == "__main__":
    asyncio.run(example_usage())