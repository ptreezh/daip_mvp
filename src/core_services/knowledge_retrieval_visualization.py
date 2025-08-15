#!/usr/bin/env python3
"""@Time    : 2025-08-03 17:30:00
@Author  : DAIP-LIVE Team
@File    : knowledge_retrieval_visualization.py
@Description:
    V0.3.4 知识检索和可视化系统
    
    核心功能：
    - 多模态知识检索：支持文本、语义、概念等多种检索方式
    - 智能知识图谱构建：自动构建和维护知识图谱
    - 交互式可视化界面：提供直观的知识可视化
    - 实时知识发现：动态发现知识间的关联
    - 知识质量评估：评估知识的可靠性和时效性
"""

import asyncio
import logging
import uuid

# 延迟加载的可视化库
_plotly_go = None
_plotly_px = None
_plotly_subplots = None

def _get_plotly_go():
    global _plotly_go
    if _plotly_go is None:
        try:
            import plotly.graph_objects as go
            _plotly_go = go
        except ImportError:
            raise ImportError("plotly.graph_objects is required for visualization")
    return _plotly_go

def _get_plotly_px():
    global _plotly_px
    if _plotly_px is None:
        try:
            import plotly.express as px
            _plotly_px = px
        except ImportError:
            raise ImportError("plotly.express is required for visualization")
    return _plotly_px

def _get_plotly_subplots():
    global _plotly_subplots
    if _plotly_subplots is None:
        try:
            from plotly.subplots import make_subplots
            _plotly_subplots = make_subplots
        except ImportError:
            raise ImportError("plotly.subplots is required for visualization")
    return _plotly_subplots

# 延迟加载的机器学习库
_sklearn_tfidf = None
_sklearn_cluster = None
_sklearn_decomposition = None
_sklearn_metrics = None

def _get_sklearn_tfidf():
    global _sklearn_tfidf
    if _sklearn_tfidf is None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            _sklearn_tfidf = TfidfVectorizer
        except ImportError:
            raise ImportError("sklearn.feature_extraction.text is required for analysis")
    return _sklearn_tfidf

def _get_sklearn_cluster():
    global _sklearn_cluster
    if _sklearn_cluster is None:
        try:
            from sklearn.cluster import DBSCAN, KMeans
            _sklearn_cluster = {'DBSCAN': DBSCAN, 'KMeans': KMeans}
        except ImportError:
            raise ImportError("sklearn.cluster is required for analysis")
    return _sklearn_cluster

def _get_sklearn_decomposition():
    global _sklearn_decomposition
    if _sklearn_decomposition is None:
        try:
            from sklearn.decomposition import PCA, TSNE
            _sklearn_decomposition = {'PCA': PCA, 'TSNE': TSNE}
        except ImportError:
            raise ImportError("sklearn.decomposition is required for analysis")
    return _sklearn_decomposition

def _get_sklearn_metrics():
    global _sklearn_metrics
    if _sklearn_metrics is None:
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            _sklearn_metrics = cosine_similarity
        except ImportError:
            raise ImportError("sklearn.metrics.pairwise is required for analysis")
    return _sklearn_metrics

# 延迟加载的networkx
_networkx = None

def _get_networkx():
    global _networkx
    if _networkx is None:
        try:
            import networkx as nx
            _networkx = nx
        except ImportError:
            raise ImportError("networkx is required for graph analysis")
    return _networkx

# 延迟加载的numpy
_numpy = None

def _get_numpy():
    global _numpy
    if _numpy is None:
        try:
            import numpy as np
            _numpy = np
        except ImportError:
            raise ImportError("numpy is required for analysis")
    return _numpy


# 导入现有组件
from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
from src.core_services.memory_agent import MemAgent
from src.core_services.role_manager import RoleManager

logger = logging.getLogger(__name__)

class RetrievalMode(Enum):
    """检索模式"""
    SEMANTIC = "semantic"           # 语义检索
    CONCEPTUAL = "conceptual"       # 概念检索
    TEMPORAL = "temporal"           # 时间检索
    ASSOCIATIVE = "associative"     # 关联检索
    MULTI_MODAL = "multi_modal"     # 多模态检索
    EXPLORATORY = "exploratory"     # 探索性检索

class VisualizationType(Enum):
    """可视化类型"""
    KNOWLEDGE_GRAPH = "knowledge_graph"
    CONCEPT_MAP = "concept_map"
    TIMELINE = "timeline"
    CLUSTER_MAP = "cluster_map"
    RELATIONSHIP_MATRIX = "relationship_matrix"
    INTERACTIVE_3D = "interactive_3d"

class KnowledgeQuality(Enum):
    """知识质量等级"""
    HIGH = "high"           # 高质量：权威、准确、时效
    MEDIUM = "medium"       # 中等质量：较可靠、部分验证
    LOW = "low"            # 低质量：存疑、需验证
    UNCERTAIN = "uncertain" # 不确定：缺乏验证

@dataclass
class KnowledgeNode:
    """知识节点"""
    node_id: str
    content: str
    node_type: str
    importance: float = 0.5
    quality: KnowledgeQuality = KnowledgeQuality.MEDIUM
    source_memories: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    temporal_info: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0

@dataclass
class KnowledgeRelation:
    """知识关系"""
    relation_id: str
    source_node: str
    target_node: str
    relation_type: str
    strength: float = 0.5
    confidence: float = 0.5
    evidence: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    verified: bool = False

@dataclass
class RetrievalQuery:
    """检索查询"""
    query_id: str
    query_text: str
    retrieval_mode: RetrievalMode
    filters: Dict[str, Any] = field(default_factory=dict)
    max_results: int = 20
    include_related: bool = True
    visualization_request: Optional[VisualizationType] = None
    user_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetrievalResult:
    """检索结果"""
    query_id: str
    matched_nodes: List[KnowledgeNode]
    related_relations: List[KnowledgeRelation]
    relevance_scores: List[float]
    clusters: Optional[Dict[str, List[str]]] = None
    visualization_data: Optional[Dict[str, Any]] = None
    quality_assessment: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    total_results: int = 0

class KnowledgeRetrievalEngine:
    """知识检索引擎"""
    
    def __init__(self, 
                 mem_agent: MemAgent,
                 sskg_manager: EnhancedSSKGManager,
                 role_manager: RoleManager):
        
        # 核心组件
        self.mem_agent = mem_agent
        self.sskg_manager = sskg_manager
        self.role_manager = role_manager
        
        # 知识图谱
        nx = _get_networkx()
        self.knowledge_graph = nx.DiGraph()
        self.knowledge_nodes: Dict[str, KnowledgeNode] = {}
        self.knowledge_relations: Dict[str, KnowledgeRelation] = {}
        
        # 检索索引
        self.semantic_index = {}
        self.concept_index = {}
        self.temporal_index = {}
        
        # 机器学习模型
        TfidfVectorizer = _get_sklearn_tfidf()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.embeddings_matrix = None
        self.clustering_models = {}
        
        # 可视化引擎
        self.visualization_engine = KnowledgeVisualizationEngine()
        
        # 质量评估器
        self.quality_assessor = KnowledgeQualityAssessor()
        
        # 性能统计
        self.retrieval_stats = {
            "total_queries": 0,
            "avg_response_time": 0.0,
            "cache_hit_rate": 0.0,
            "quality_distribution": {}
        }
        
        # 缓存系统
        self.query_cache = {}
        self.cache_ttl = timedelta(hours=1)
        
        logger.info("知识检索引擎初始化完成")
    
    async def initialize(self):
        """初始化检索引擎"""
        # 1. 构建知识图谱
        await self._build_initial_knowledge_graph()
        
        # 2. 构建检索索引
        await self._build_retrieval_indices()
        
        # 3. 训练机器学习模型
        await self._train_ml_models()
        
        # 4. 启动后台任务
        asyncio.create_task(self._knowledge_maintenance_loop())
        asyncio.create_task(self._quality_monitoring_loop())
        asyncio.create_task(self._cache_cleanup_loop())
        
        logger.info("知识检索引擎初始化完成")
    
    async def retrieve_knowledge(self, query: RetrievalQuery) -> RetrievalResult:
        """知识检索主接口"""
        start_time = datetime.now()
        
        # 1. 检查缓存
        cached_result = await self._check_query_cache(query)
        if cached_result:
            self.retrieval_stats["cache_hit_rate"] += 0.01
            return cached_result
        
        # 2. 预处理查询
        processed_query = await self._preprocess_query(query)
        
        # 3. 根据检索模式执行检索
        if query.retrieval_mode == RetrievalMode.SEMANTIC:
            raw_results = await self._semantic_retrieval(processed_query)
        elif query.retrieval_mode == RetrievalMode.CONCEPTUAL:
            raw_results = await self._conceptual_retrieval(processed_query)
        elif query.retrieval_mode == RetrievalMode.TEMPORAL:
            raw_results = await self._temporal_retrieval(processed_query)
        elif query.retrieval_mode == RetrievalMode.ASSOCIATIVE:
            raw_results = await self._associative_retrieval(processed_query)
        elif query.retrieval_mode == RetrievalMode.MULTI_MODAL:
            raw_results = await self._multi_modal_retrieval(processed_query)
        else:  # EXPLORATORY
            raw_results = await self._exploratory_retrieval(processed_query)
        
        # 4. 后处理和重排序
        processed_results = await self._postprocess_results(query, raw_results)
        
        # 5. 生成可视化数据
        visualization_data = None
        if query.visualization_request:
            visualization_data = await self.visualization_engine.generate_visualization(
                query.visualization_request, processed_results, query
            )
        
        # 6. 质量评估
        quality_assessment = await self.quality_assessor.assess_results(processed_results)
        
        # 7. 构建最终结果
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = RetrievalResult(
            query_id=query.query_id,
            matched_nodes=processed_results["nodes"],
            related_relations=processed_results["relations"],
            relevance_scores=processed_results["scores"],
            clusters=processed_results.get("clusters"),
            visualization_data=visualization_data,
            quality_assessment=quality_assessment,
            processing_time=processing_time,
            total_results=len(processed_results["nodes"])
        )
        
        # 8. 缓存结果
        await self._cache_query_result(query, result)
        
        # 9. 更新统计
        await self._update_retrieval_stats(query, result)
        
        return result
    
    async def discover_knowledge_patterns(self, 
                                        analysis_scope: str = "global",
                                        pattern_types: List[str] = None) -> Dict[str, Any]:
        """知识模式发现"""
        if pattern_types is None:
            pattern_types = ["clusters", "communities", "temporal_patterns", "emerging_concepts"]
        
        discovery_results = {}
        
        # 1. 聚类分析
        if "clusters" in pattern_types:
            clusters = await self._discover_knowledge_clusters()
            discovery_results["clusters"] = clusters
        
        # 2. 社区发现
        if "communities" in pattern_types:
            communities = await self._discover_knowledge_communities()
            discovery_results["communities"] = communities
        
        # 3. 时间模式分析
        if "temporal_patterns" in pattern_types:
            temporal_patterns = await self._discover_temporal_patterns()
            discovery_results["temporal_patterns"] = temporal_patterns
        
        # 4. 新兴概念发现
        if "emerging_concepts" in pattern_types:
            emerging_concepts = await self._discover_emerging_concepts()
            discovery_results["emerging_concepts"] = emerging_concepts
        
        # 5. 关联规则挖掘
        if "association_rules" in pattern_types:
            association_rules = await self._discover_association_rules()
            discovery_results["association_rules"] = association_rules
        
        return {
            "discovery_scope": analysis_scope,
            "pattern_types_analyzed": pattern_types,
            "discovery_results": discovery_results,
            "discovery_timestamp": datetime.now().isoformat(),
            "pattern_quality_scores": await self._evaluate_pattern_quality(discovery_results)
        }
    
    async def build_interactive_knowledge_map(self, 
                                            focus_concept: Optional[str] = None,
                                            depth: int = 3,
                                            layout_algorithm: str = "force_directed") -> Dict[str, Any]:
        """构建交互式知识地图"""
        # 1. 确定地图范围
        if focus_concept:
            subgraph_nodes = await self._get_concept_neighborhood(focus_concept, depth)
        else:
            subgraph_nodes = list(self.knowledge_nodes.keys())[:100]  # 限制节点数量
        
        # 2. 提取子图
        subgraph = self.knowledge_graph.subgraph(subgraph_nodes)
        
        # 3. 计算布局
        layout_coords = await self._calculate_graph_layout(subgraph, layout_algorithm)
        
        # 4. 准备节点数据
        nodes_data = []
        for node_id in subgraph_nodes:
            if node_id in self.knowledge_nodes:
                node = self.knowledge_nodes[node_id]
                nodes_data.append({
                    "id": node_id,
                    "label": node.content[:50] + "..." if len(node.content) > 50 else node.content,
                    "type": node.node_type,
                    "importance": node.importance,
                    "quality": node.quality.value,
                    "x": layout_coords[node_id][0],
                    "y": layout_coords[node_id][1],
                    "size": 10 + node.importance * 20,
                    "color": self._get_node_color(node)
                })
        
        # 5. 准备边数据
        edges_data = []
        for edge in subgraph.edges():
            source, target = edge
            if edge in self.knowledge_relations:
                relation = self.knowledge_relations[f"{source}_{target}"]
                edges_data.append({
                    "source": source,
                    "target": target,
                    "label": relation.relation_type,
                    "strength": relation.strength,
                    "confidence": relation.confidence,
                    "width": 1 + relation.strength * 5
                })
        
        # 6. 生成交互式可视化
        interactive_map = await self.visualization_engine.create_interactive_map(
            nodes_data, edges_data, layout_algorithm
        )
        
        return {
            "map_data": interactive_map,
            "focus_concept": focus_concept,
            "total_nodes": len(nodes_data),
            "total_edges": len(edges_data),
            "layout_algorithm": layout_algorithm,
            "depth": depth,
            "generation_timestamp": datetime.now().isoformat()
        }
    
    async def _build_initial_knowledge_graph(self):
        """构建初始知识图谱"""
        # 1. 从记忆中提取知识节点
        all_memories = await self.mem_agent.get_all_memories()
        
        for memory in all_memories:
            # 创建知识节点
            node = KnowledgeNode(
                node_id=f"node_{memory.id}",
                content=memory.content,
                node_type=memory.memory_type.value,
                importance=memory.importance,
                source_memories=[memory.id],
                metadata=memory.metadata or {}
            )
            
            self.knowledge_nodes[node.node_id] = node
            self.knowledge_graph.add_node(node.node_id, **node.__dict__)
        
        # 2. 从SSKG中提取关系
        sskg_relations = await self.sskg_manager.get_all_relations()
        
        for relation_data in sskg_relations:
            relation = KnowledgeRelation(
                relation_id=f"rel_{uuid.uuid4().hex[:8]}",
                source_node=relation_data.get("source"),
                target_node=relation_data.get("target"),
                relation_type=relation_data.get("type", "related"),
                strength=relation_data.get("strength", 0.5),
                confidence=relation_data.get("confidence", 0.5)
            )
            
            self.knowledge_relations[relation.relation_id] = relation
            self.knowledge_graph.add_edge(
                relation.source_node, 
                relation.target_node,
                relation_type=relation.relation_type,
                strength=relation.strength
            )
        
        logger.info(f"构建了包含 {len(self.knowledge_nodes)} 个节点和 {len(self.knowledge_relations)} 个关系的知识图谱")
    
    async def _semantic_retrieval(self, query: RetrievalQuery) -> Dict[str, Any]:
        """语义检索"""
        # 1. 计算查询向量
        query_embedding = await self._get_query_embedding(query.query_text)
        
        # 2. 计算相似度
        similarities = []
        matching_nodes = []
        
        for node_id, node in self.knowledge_nodes.items():
            if node.embedding:
                cosine_similarity = _get_sklearn_metrics()
                similarity = cosine_similarity([query_embedding], [node.embedding])[0][0]
                if similarity > 0.3:  # 相似度阈值
                    similarities.append(similarity)
                    matching_nodes.append(node)
        
        # 3. 排序
        sorted_pairs = sorted(zip(similarities, matching_nodes, strict=False), key=lambda x: x[0], reverse=True)
        
        # 4. 提取相关关系
        related_relations = []
        for _, node in sorted_pairs[:query.max_results]:
            node_relations = [rel for rel in self.knowledge_relations.values() 
                            if rel.source_node == node.node_id or rel.target_node == node.node_id]
            related_relations.extend(node_relations)
        
        return {
            "nodes": [node for _, node in sorted_pairs[:query.max_results]],
            "relations": related_relations,
            "scores": [score for score, _ in sorted_pairs[:query.max_results]]
        }
    
    async def _conceptual_retrieval(self, query: RetrievalQuery) -> Dict[str, Any]:
        """概念检索"""
        # 1. 提取查询概念
        query_concepts = await self._extract_concepts(query.query_text)
        
        # 2. 查找概念匹配的节点
        matching_nodes = []
        scores = []
        
        for node_id, node in self.knowledge_nodes.items():
            node_concepts = set(node.related_concepts)
            concept_overlap = len(set(query_concepts) & node_concepts)
            
            if concept_overlap > 0:
                score = concept_overlap / max(len(query_concepts), len(node_concepts))
                matching_nodes.append(node)
                scores.append(score)
        
        # 3. 排序和筛选
        sorted_pairs = sorted(zip(scores, matching_nodes, strict=False), key=lambda x: x[0], reverse=True)
        
        return {
            "nodes": [node for _, node in sorted_pairs[:query.max_results]],
            "relations": [],
            "scores": [score for score, _ in sorted_pairs[:query.max_results]]
        }
    
    async def _temporal_retrieval(self, query: RetrievalQuery) -> Dict[str, Any]:
        """时间检索"""
        # 1. 解析时间约束
        time_filters = query.filters.get("temporal", {})
        start_time = time_filters.get("start_time")
        end_time = time_filters.get("end_time")
        
        # 2. 筛选符合时间条件的节点
        matching_nodes = []
        scores = []
        
        for node_id, node in self.knowledge_nodes.items():
            node_time = node.created_at
            
            time_match = True
            if start_time and node_time < start_time:
                time_match = False
            if end_time and node_time > end_time:
                time_match = False
            
            if time_match:
                # 基于时间新近性计算分数
                days_ago = (datetime.now() - node_time).days
                score = max(0, 1 - days_ago / 365)  # 一年内的内容权重较高
                
                matching_nodes.append(node)
                scores.append(score)
        
        # 3. 排序
        sorted_pairs = sorted(zip(scores, matching_nodes, strict=False), key=lambda x: x[0], reverse=True)
        
        return {
            "nodes": [node for _, node in sorted_pairs[:query.max_results]],
            "relations": [],
            "scores": [score for score, _ in sorted_pairs[:query.max_results]]
        }
    
    async def _associative_retrieval(self, query: RetrievalQuery) -> Dict[str, Any]:
        """关联检索"""
        # 1. 从查询中识别种子节点
        seed_nodes = await self._identify_seed_nodes(query.query_text)
        
        # 2. 基于图遍历找到关联节点
        associated_nodes = []
        scores = []
        
        for seed_node_id in seed_nodes:
            if seed_node_id in self.knowledge_graph:
                # 使用PageRank算法计算关联强度
                nx = _get_networkx()
                neighbors = list(nx.neighbors(self.knowledge_graph, seed_node_id))
                
                for neighbor_id in neighbors:
                    if neighbor_id in self.knowledge_nodes:
                        # 计算关联强度
                        nx = _get_networkx()
                        path_length = nx.shortest_path_length(
                            self.knowledge_graph, seed_node_id, neighbor_id
                        )
                        score = 1.0 / path_length if path_length > 0 else 1.0
                        
                        associated_nodes.append(self.knowledge_nodes[neighbor_id])
                        scores.append(score)
        
        # 3. 去重和排序
        unique_pairs = list(set(zip(scores, [node.node_id for node in associated_nodes], strict=False)))
        sorted_pairs = sorted(unique_pairs, key=lambda x: x[0], reverse=True)
        
        final_nodes = [self.knowledge_nodes[node_id] for _, node_id in sorted_pairs[:query.max_results]]
        final_scores = [score for score, _ in sorted_pairs[:query.max_results]]
        
        return {
            "nodes": final_nodes,
            "relations": [],
            "scores": final_scores
        }
    
    async def _multi_modal_retrieval(self, query: RetrievalQuery) -> Dict[str, Any]:
        """多模态检索"""
        # 1. 执行多种检索模式
        semantic_results = await self._semantic_retrieval(query)
        conceptual_results = await self._conceptual_retrieval(query)
        temporal_results = await self._temporal_retrieval(query)
        
        # 2. 融合结果
        all_nodes = {}
        all_scores = {}
        
        # 语义检索权重：0.4
        for i, node in enumerate(semantic_results["nodes"]):
            node_id = node.node_id
            score = semantic_results["scores"][i] * 0.4
            
            if node_id in all_scores:
                all_scores[node_id] += score
            else:
                all_nodes[node_id] = node
                all_scores[node_id] = score
        
        # 概念检索权重：0.3
        for i, node in enumerate(conceptual_results["nodes"]):
            node_id = node.node_id
            score = conceptual_results["scores"][i] * 0.3
            
            if node_id in all_scores:
                all_scores[node_id] += score
            else:
                all_nodes[node_id] = node
                all_scores[node_id] = score
        
        # 时间检索权重：0.3
        for i, node in enumerate(temporal_results["nodes"]):
            node_id = node.node_id
            score = temporal_results["scores"][i] * 0.3
            
            if node_id in all_scores:
                all_scores[node_id] += score
            else:
                all_nodes[node_id] = node
                all_scores[node_id] = score
        
        # 3. 排序和筛选
        sorted_pairs = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        
        final_nodes = [all_nodes[node_id] for node_id, _ in sorted_pairs[:query.max_results]]
        final_scores = [score for _, score in sorted_pairs[:query.max_results]]
        
        return {
            "nodes": final_nodes,
            "relations": [],
            "scores": final_scores
        }
    
    async def _exploratory_retrieval(self, query: RetrievalQuery) -> Dict[str, Any]:
        """探索性检索"""
        # 1. 随机游走发现
        random_walk_nodes = await self._random_walk_discovery(query.query_text)
        
        # 2. 聚类中心发现
        cluster_centers = await self._discover_cluster_centers()
        
        # 3. 高重要性节点
        high_importance_nodes = [
            node for node in self.knowledge_nodes.values()
            if node.importance > 0.7
        ]
        
        # 4. 合并结果
        exploratory_nodes = random_walk_nodes + cluster_centers + high_importance_nodes
        
        # 5. 去重和评分
        unique_nodes = list({node.node_id: node for node in exploratory_nodes}.values())
        scores = [node.importance for node in unique_nodes]
        
        # 6. 排序
        sorted_pairs = sorted(zip(scores, unique_nodes, strict=False), key=lambda x: x[0], reverse=True)
        
        return {
            "nodes": [node for _, node in sorted_pairs[:query.max_results]],
            "relations": [],
            "scores": [score for score, _ in sorted_pairs[:query.max_results]]
        }
    
    def _get_graph_density(self):
        """获取图密度（延迟加载networkx）"""
        try:
            nx = _get_networkx()
            return nx.density(self.knowledge_graph)
        except ImportError:
            return 0.0
    
    def _get_connected_components(self):
        """获取连通组件数量（延迟加载networkx）"""
        try:
            nx = _get_networkx()
            return nx.number_connected_components(self.knowledge_graph.to_undirected())
        except ImportError:
            return 0

    def get_retrieval_statistics(self) -> Dict[str, Any]:
        """获取检索统计信息"""
        return {
            "knowledge_base_stats": {
                "total_nodes": len(self.knowledge_nodes),
                "total_relations": len(self.knowledge_relations),
                "graph_density": self._get_graph_density(),
                "connected_components": self._get_connected_components()
            },
            "retrieval_performance": self.retrieval_stats,
            "quality_distribution": {
                quality.value: len([n for n in self.knowledge_nodes.values() if n.quality == quality])
                for quality in KnowledgeQuality
            },
            "node_type_distribution": {
                node_type: len([n for n in self.knowledge_nodes.values() if n.node_type == node_type])
                for node_type in set(n.node_type for n in self.knowledge_nodes.values())
            },
            "cache_statistics": {
                "cache_size": len(self.query_cache),
                "cache_hit_rate": self.retrieval_stats.get("cache_hit_rate", 0.0)
            }
        }

class KnowledgeVisualizationEngine:
    """知识可视化引擎"""
    
    def __init__(self):
        self.color_schemes = {
            "concept": "#3498db",
            "entity": "#e74c3c",
            "event": "#f39c12",
            "relationship": "#2ecc71",
            "high_quality": "#27ae60",
            "medium_quality": "#f39c12",
            "low_quality": "#e74c3c"
        }
    
    async def generate_visualization(self, 
                                   viz_type: VisualizationType,
                                   results: Dict[str, Any],
                                   query: RetrievalQuery) -> Dict[str, Any]:
        """生成可视化数据"""
        if viz_type == VisualizationType.KNOWLEDGE_GRAPH:
            return await self._create_knowledge_graph_viz(results, query)
        elif viz_type == VisualizationType.CONCEPT_MAP:
            return await self._create_concept_map_viz(results, query)
        elif viz_type == VisualizationType.TIMELINE:
            return await self._create_timeline_viz(results, query)
        elif viz_type == VisualizationType.CLUSTER_MAP:
            return await self._create_cluster_map_viz(results, query)
        elif viz_type == VisualizationType.RELATIONSHIP_MATRIX:
            return await self._create_relationship_matrix_viz(results, query)
        elif viz_type == VisualizationType.INTERACTIVE_3D:
            return await self._create_interactive_3d_viz(results, query)
        else:
            return {"error": f"不支持的可视化类型: {viz_type}"}
    
    async def _create_knowledge_graph_viz(self, results: Dict[str, Any], query: RetrievalQuery) -> Dict[str, Any]:
        """创建知识图谱可视化"""
        nodes = results["nodes"]
        relations = results.get("relations", [])
        
        # 节点数据
        go = _get_plotly_go()
        node_trace = go.Scatter(
            x=[],
            y=[],
            mode='markers+text',
            text=[],
            textposition="middle center",
            marker=dict(
                size=[],
                color=[],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Importance")
            ),
            hovertemplate='<b>%{text}</b><br>Importance: %{marker.color}<extra></extra>'
        )
        
        # 边数据
        edge_trace = go.Scatter(
            x=[],
            y=[],
            mode='lines',
            line=dict(width=0.5, color='#888'),
            hoverinfo='none'
        )
        
        # 构建图布局
        G = nx.Graph()
        for node in nodes:
            G.add_node(node.node_id, importance=node.importance)
        
        for relation in relations:
            G.add_edge(relation.source_node, relation.target_node, strength=relation.strength)
        
        pos = nx.spring_layout(G)
        
        # 添加节点位置和属性
        for node in nodes:
            if node.node_id in pos:
                x, y = pos[node.node_id]
                node_trace['x'] += tuple([x])
                node_trace['y'] += tuple([y])
                node_trace['text'] += tuple([node.content[:20] + "..." if len(node.content) > 20 else node.content])
                node_trace['marker']['size'] += tuple([10 + node.importance * 20])
                node_trace['marker']['color'] += tuple([node.importance])
        
        # 添加边
        for relation in relations:
            if relation.source_node in pos and relation.target_node in pos:
                x0, y0 = pos[relation.source_node]
                x1, y1 = pos[relation.target_node]
                edge_trace['x'] += tuple([x0, x1, None])
                edge_trace['y'] += tuple([y0, y1, None])
        
        # 创建图形
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=f'Knowledge Graph: {query.query_text}',
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Knowledge Graph Visualization",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(color="#888", size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))
        
        return {
            "visualization_type": "knowledge_graph",
            "plotly_json": fig.to_json(),
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(relations),
                "query": query.query_text
            }
        }
    
    async def create_interactive_map(self, 
                                   nodes_data: List[Dict],
                                   edges_data: List[Dict],
                                   layout_algorithm: str) -> Dict[str, Any]:
        """创建交互式地图"""
        # 使用Plotly创建交互式网络图
        fig = go.Figure()
        
        # 添加边
        for edge in edges_data:
            source_node = next(n for n in nodes_data if n["id"] == edge["source"])
            target_node = next(n for n in nodes_data if n["id"] == edge["target"])
            
            fig.add_trace(go.Scatter(
                x=[source_node["x"], target_node["x"]],
                y=[source_node["y"], target_node["y"]],
                mode='lines',
                line=dict(width=edge["width"], color='rgba(125,125,125,0.5)'),
                hoverinfo='none',
                showlegend=False
            ))
        
        # 添加节点
        fig.add_trace(go.Scatter(
            x=[node["x"] for node in nodes_data],
            y=[node["y"] for node in nodes_data],
            mode='markers+text',
            marker=dict(
                size=[node["size"] for node in nodes_data],
                color=[node["color"] for node in nodes_data],
                line=dict(width=2, color='white')
            ),
            text=[node["label"] for node in nodes_data],
            textposition="middle center",
            hovertemplate='<b>%{text}</b><br>' +
                         'Type: %{customdata[0]}<br>' +
                         'Importance: %{customdata[1]}<br>' +
                         'Quality: %{customdata[2]}<extra></extra>',
            customdata=[[node["type"], node["importance"], node["quality"]] for node in nodes_data],
            showlegend=False
        ))
        
        fig.update_layout(
            title=f"Interactive Knowledge Map ({layout_algorithm} layout)",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        return {
            "interactive_map": fig.to_json(),
            "nodes_count": len(nodes_data),
            "edges_count": len(edges_data),
            "layout_algorithm": layout_algorithm
        }

class KnowledgeQualityAssessor:
    """知识质量评估器"""
    
    def __init__(self):
        self.quality_criteria = {
            "relevance": 0.3,
            "accuracy": 0.25,
            "freshness": 0.2,
            "completeness": 0.15,
            "authority": 0.1
        }
    
    async def assess_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """评估检索结果质量"""
        nodes = results["nodes"]
        scores = results["scores"]
        
        quality_scores = []
        for i, node in enumerate(nodes):
            relevance_score = scores[i] if i < len(scores) else 0.5
            
            # 计算各项质量指标
            accuracy_score = await self._assess_accuracy(node)
            freshness_score = await self._assess_freshness(node)
            completeness_score = await self._assess_completeness(node)
            authority_score = await self._assess_authority(node)
            
            # 加权平均
            overall_quality = (
                relevance_score * self.quality_criteria["relevance"] +
                accuracy_score * self.quality_criteria["accuracy"] +
                freshness_score * self.quality_criteria["freshness"] +
                completeness_score * self.quality_criteria["completeness"] +
                authority_score * self.quality_criteria["authority"]
            )
            
            quality_scores.append({
                "node_id": node.node_id,
                "overall_quality": overall_quality,
                "relevance": relevance_score,
                "accuracy": accuracy_score,
                "freshness": freshness_score,
                "completeness": completeness_score,
                "authority": authority_score
            })
        
        # 整体质量评估
        avg_quality = sum(q["overall_quality"] for q in quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "individual_quality_scores": quality_scores,
            "average_quality": avg_quality,
            "quality_distribution": self._calculate_quality_distribution(quality_scores),
            "quality_recommendations": await self._generate_quality_recommendations(quality_scores)
        }
    
    async def _assess_accuracy(self, node: KnowledgeNode) -> float:
        """评估准确性"""
        # 基于节点的质量标记
        quality_scores = {
            KnowledgeQuality.HIGH: 0.9,
            KnowledgeQuality.MEDIUM: 0.7,
            KnowledgeQuality.LOW: 0.4,
            KnowledgeQuality.UNCERTAIN: 0.2
        }
        return quality_scores.get(node.quality, 0.5)
    
    async def _assess_freshness(self, node: KnowledgeNode) -> float:
        """评估时效性"""
        days_old = (datetime.now() - node.created_at).days
        # 7天内为最新，超过1年为陈旧
        if days_old <= 7:
            return 1.0
        elif days_old <= 30:
            return 0.8
        elif days_old <= 90:
            return 0.6
        elif days_old <= 365:
            return 0.4
        else:
            return 0.2
    
    async def _assess_completeness(self, node: KnowledgeNode) -> float:
        """评估完整性"""
        # 基于内容长度和元数据丰富度
        content_score = min(len(node.content) / 500, 1.0)  # 500字符为满分
        metadata_score = min(len(node.metadata) / 10, 1.0)  # 10个元数据字段为满分
        
        return (content_score + metadata_score) / 2
    
    async def _assess_authority(self, node: KnowledgeNode) -> float:
        """评估权威性"""
        # 基于访问次数和重要性
        access_score = min(node.access_count / 100, 1.0)  # 100次访问为满分
        importance_score = node.importance
        
        return (access_score + importance_score) / 2

# 创建全局实例函数
def create_knowledge_retrieval_engine(mem_agent: MemAgent, 
                                    sskg_manager: EnhancedSSKGManager,
                                    role_manager: RoleManager) -> KnowledgeRetrievalEngine:
    """创建知识检索引擎实例"""
    return KnowledgeRetrievalEngine(mem_agent, sskg_manager, role_manager)