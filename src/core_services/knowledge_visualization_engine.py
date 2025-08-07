"""
@Time: 2025-08-03
@Author: DAIP-LIVE
@File: knowledge_visualization_engine.py
@Description: V0.3.4 知识可视化引擎 - 交互式知识图谱和可视化组件
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
# 延迟加载的可视化库
_matplotlib_plt = None
_matplotlib_mdates = None
_matplotlib_figure = None
_seaborn = None
_plotly_go = None
_plotly_px = None
_plotly_subplots = None
_pandas = None
_numpy = None
_networkx = None

def _get_matplotlib_plt():
    global _matplotlib_plt
    if _matplotlib_plt is None:
        try:
            import matplotlib.pyplot as plt
            _matplotlib_plt = plt
        except ImportError:
            raise ImportError("matplotlib.pyplot is required for visualization")
    return _matplotlib_plt

def _get_matplotlib_mdates():
    global _matplotlib_mdates
    if _matplotlib_mdates is None:
        try:
            import matplotlib.dates as mdates
            _matplotlib_mdates = mdates
        except ImportError:
            raise ImportError("matplotlib.dates is required for visualization")
    return _matplotlib_mdates

def _get_matplotlib_figure():
    global _matplotlib_figure
    if _matplotlib_figure is None:
        try:
            from matplotlib.figure import Figure
            _matplotlib_figure = Figure
        except ImportError:
            raise ImportError("matplotlib.figure is required for visualization")
    return _matplotlib_figure

def _get_seaborn():
    global _seaborn
    if _seaborn is None:
        try:
            import seaborn as sns
            _seaborn = sns
        except ImportError:
            raise ImportError("seaborn is required for visualization")
    return _seaborn

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

def _get_pandas():
    global _pandas
    if _pandas is None:
        try:
            import pandas as pd
            _pandas = pd
        except ImportError:
            raise ImportError("pandas is required for data analysis")
    return _pandas

def _get_numpy():
    global _numpy
    if _numpy is None:
        try:
            import numpy as np
            _numpy = np
        except ImportError:
            raise ImportError("numpy is required for data analysis")
    return _numpy

def _get_networkx():
    global _networkx
    if _networkx is None:
        try:
            import networkx as nx
            _networkx = nx
        except ImportError:
            raise ImportError("networkx is required for graph analysis")
    return _networkx
from collections import defaultdict, Counter

from ..core_services.knowledge_retrieval_service import KnowledgeRetrievalService
from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
from ..core_services.memory_agent import MemAgent
from ..virtual_role_chat.sskg.models import KnowledgeFact, KnowledgeRelation, RelationType


class VisualizationType(Enum):
    """可视化类型枚举"""
    KNOWLEDGE_GRAPH = "knowledge_graph"  # 知识图谱
    TIMELINE = "timeline"  # 时间线
    CLUSTER_VIEW = "cluster_view"  # 聚类视图
    NETWORK_DIAGRAM = "network_diagram"  # 网络关系图
    HEATMAP = "heatmap"  # 热力图
    TREE_MAP = "tree_map"  # 树状图
    SANKEY_DIAGRAM = "sankey_diagram"  # 桑基图


@dataclass
class VisualizationConfig:
    """可视化配置"""
    width: int = 800
    height: int = 600
    theme: str = "plotly_white"
    color_scheme: str = "viridis"
    font_size: int = 12
    show_labels: bool = True
    interactive: bool = True
    export_format: str = "html"


@dataclass
class GraphNode:
    """图谱节点"""
    id: str
    label: str
    type: str
    confidence: float
    domain: str
    size: float = 1.0
    color: str = "#1f77b4"
    x: float = 0.0
    y: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass
class GraphEdge:
    """图谱边"""
    source: str
    target: str
    relation_type: str
    weight: float = 1.0
    color: str = "#999999"
    metadata: Dict[str, Any] = None


@dataclass
class TimelineEvent:
    """时间线事件"""
    id: str
    title: str
    description: str
    timestamp: datetime
    category: str
    importance: float
    metadata: Dict[str, Any] = None


@dataclass
class ClusterInfo:
    """聚类信息"""
    id: str
    label: str
    size: int
    centrality: float
    members: List[str]
    domain: str
    metadata: Dict[str, Any] = None


class KnowledgeVisualizationEngine:
    """知识可视化引擎"""
    
    def __init__(self, sskg_manager: EnhancedSSKGManager, 
                 knowledge_retrieval: KnowledgeRetrievalService):
        self.sskg_manager = sskg_manager
        self.knowledge_retrieval = knowledge_retrieval
        self.logger = logging.getLogger(__name__)
        
        # 布局算法
        self.layout_algorithms = {
            "spring": nx.spring_layout,
            "circular": nx.circular_layout,
            "random": nx.random_layout,
            "shell": nx.shell_layout
        }
        
        # 颜色方案
        self.color_schemes = {
            "viridis": px.colors.sequential.Viridis,
            "plasma": px.colors.sequential.Plasma,
            "blues": px.colors.sequential.Blues,
            "reds": px.colors.sequential.Reds,
            "category10": px.colors.qualitative.Set3
        }
    
    async def generate_knowledge_graph(self, 
                                    query: str = "",
                                    max_nodes: int = 100,
                                    config: VisualizationConfig = None) -> Dict[str, Any]:
        """生成交互式知识图谱"""
        try:
            if config is None:
                config = VisualizationConfig()
            
            # 获取知识数据
            knowledge_facts = await self._get_knowledge_facts(query, max_nodes)
            
            # 构建网络图
            G = await self._build_knowledge_network(knowledge_facts)
            
            # 应用布局算法
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            # 准备可视化数据
            nodes = []
            edges = []
            
            for node_id, node_data in G.nodes(data=True):
                x, y = pos[node_id]
                node = GraphNode(
                    id=node_id,
                    label=node_data.get('label', node_id),
                    type=node_data.get('type', 'unknown'),
                    confidence=node_data.get('confidence', 0.5),
                    domain=node_data.get('domain', 'general'),
                    size=max(10, node_data.get('confidence', 0.5) * 30),
                    color=self._get_node_color(node_data.get('type', 'unknown')),
                    x=x,
                    y=y,
                    metadata=node_data
                )
                nodes.append(asdict(node))
            
            for source, target, edge_data in G.edges(data=True):
                edge = GraphEdge(
                    source=source,
                    target=target,
                    relation_type=edge_data.get('relation_type', 'related'),
                    weight=edge_data.get('weight', 1.0),
                    color=self._get_edge_color(edge_data.get('relation_type', 'related')),
                    metadata=edge_data
                )
                edges.append(asdict(edge))
            
            # 生成Plotly图表
            fig = self._create_interactive_graph(nodes, edges, config)
            
            return {
                "visualization_type": "knowledge_graph",
                "figure": fig.to_dict(),
                "nodes": nodes,
                "edges": edges,
                "stats": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "average_degree": sum(dict(G.degree()).values()) / len(G.nodes()),
                    "network_density": nx.density(G)
                },
                "config": asdict(config)
            }
            
        except Exception as e:
            self.logger.error(f"生成知识图谱失败: {e}")
            return {"error": str(e)}
    
    async def generate_timeline(self, 
                             start_date: datetime = None,
                             end_date: datetime = None,
                             category_filter: List[str] = None,
                             config: VisualizationConfig = None) -> Dict[str, Any]:
        """生成时间线可视化"""
        try:
            if config is None:
                config = VisualizationConfig()
            
            # 获取时间序列数据
            events = await self._get_timeline_events(start_date, end_date, category_filter)
            
            if not events:
                return {"error": "没有找到时间序列数据"}
            
            # 创建时间线图表
            fig = self._create_timeline_chart(events, config)
            
            return {
                "visualization_type": "timeline",
                "figure": fig.to_dict(),
                "events": [asdict(event) for event in events],
                "stats": {
                    "total_events": len(events),
                    "date_range": {
                        "start": min(event.timestamp for event in events).isoformat(),
                        "end": max(event.timestamp for event in events).isoformat()
                    },
                    "categories": list(set(event.category for event in events))
                },
                "config": asdict(config)
            }
            
        except Exception as e:
            self.logger.error(f"生成时间线失败: {e}")
            return {"error": str(e)}
    
    async def generate_cluster_view(self, 
                                  query: str = "",
                                  algorithm: str = "louvain",
                                  config: VisualizationConfig = None) -> Dict[str, Any]:
        """生成聚类视图"""
        try:
            if config is None:
                config = VisualizationConfig()
            
            # 获取知识数据
            knowledge_facts = await self._get_knowledge_facts(query, 200)
            
            # 构建网络图
            G = await self._build_knowledge_network(knowledge_facts)
            
            # 应用聚类算法
            clusters = self._apply_clustering_algorithm(G, algorithm)
            
            # 创建聚类可视化
            fig = self._create_cluster_visualization(G, clusters, config)
            
            return {
                "visualization_type": "cluster_view",
                "figure": fig.to_dict(),
                "clusters": [asdict(cluster) for cluster in clusters],
                "stats": {
                    "total_clusters": len(clusters),
                    "largest_cluster_size": max(cluster.size for cluster in clusters),
                    "average_cluster_size": sum(cluster.size for cluster in clusters) / len(clusters),
                    "modularity": self._calculate_modularity(G, clusters)
                },
                "config": asdict(config)
            }
            
        except Exception as e:
            self.logger.error(f"生成聚类视图失败: {e}")
            return {"error": str(e)}
    
    async def generate_network_diagram(self, 
                                    focus_node: str = "",
                                    depth: int = 2,
                                    config: VisualizationConfig = None) -> Dict[str, Any]:
        """生成网络关系图"""
        try:
            if config is None:
                config = VisualizationConfig()
            
            # 获取以焦点节点为中心的子网络
            subgraph = await self._get_subgraph_around_node(focus_node, depth)
            
            # 创建网络图
            fig = self._create_network_diagram(subgraph, config)
            
            return {
                "visualization_type": "network_diagram",
                "figure": fig.to_dict(),
                "focus_node": focus_node,
                "depth": depth,
                "stats": {
                    "nodes_in_view": len(subgraph.nodes()),
                    "edges_in_view": len(subgraph.edges()),
                    "average_path_length": nx.average_shortest_path_length(subgraph) if nx.is_connected(subgraph) else 0
                },
                "config": asdict(config)
            }
            
        except Exception as e:
            self.logger.error(f"生成网络关系图失败: {e}")
            return {"error": str(e)}
    
    async def generate_heatmap(self, 
                            dimension1: str = "domain",
                            dimension2: str = "confidence",
                            config: VisualizationConfig = None) -> Dict[str, Any]:
        """生成热力图"""
        try:
            if config is None:
                config = VisualizationConfig()
            
            # 获取知识统计数据
            stats = await self._get_knowledge_statistics()
            
            # 创建热力图数据
            heatmap_data = self._prepare_heatmap_data(stats, dimension1, dimension2)
            
            # 生成热力图
            fig = self._create_heatmap(heatmap_data, config)
            
            return {
                "visualization_type": "heatmap",
                "figure": fig.to_dict(),
                "dimensions": [dimension1, dimension2],
                "data_summary": {
                    "rows": len(heatmap_data),
                    "columns": len(heatmap_data[0]) if heatmap_data else 0,
                    "max_value": max(max(row) for row in heatmap_data) if heatmap_data else 0,
                    "min_value": min(min(row) for row in heatmap_data) if heatmap_data else 0
                },
                "config": asdict(config)
            }
            
        except Exception as e:
            self.logger.error(f"生成热力图失败: {e}")
            return {"error": str(e)}
    
    def export_visualization(self, 
                           visualization_data: Dict[str, Any], 
                           format: str = "html",
                           filename: str = None) -> str:
        """导出可视化结果"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"knowledge_visualization_{timestamp}"
            
            fig_dict = visualization_data.get("figure", {})
            fig = go.Figure(fig_dict)
            
            if format == "html":
                output_file = f"{filename}.html"
                fig.write_html(output_file)
            elif format == "png":
                output_file = f"{filename}.png"
                fig.write_image(output_file)
            elif format == "pdf":
                output_file = f"{filename}.pdf"
                fig.write_image(output_file)
            else:
                raise ValueError(f"不支持的导出格式: {format}")
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"导出可视化失败: {e}")
            return ""
    
    async def _get_knowledge_facts(self, query: str, max_count: int) -> List[KnowledgeFact]:
        """获取知识事实"""
        try:
            if query:
                # 基于查询搜索
                search_results = await self.knowledge_retrieval.semantic_search(
                    query=query, limit=max_count
                )
                return search_results
            else:
                # 获取最新知识
                return await self.knowledge_retrieval.get_recent_knowledge(max_count)
        except Exception as e:
            self.logger.error(f"获取知识事实失败: {e}")
            return []
    
    async def _build_knowledge_network(self, knowledge_facts: List[KnowledgeFact]) -> nx.Graph:
        """构建知识网络"""
        G = nx.Graph()
        
        for fact in knowledge_facts:
            # 添加节点
            G.add_node(
                fact.id,
                label=fact.content[:50] + "..." if len(fact.content) > 50 else fact.content,
                type=fact.metadata.get('type', 'fact'),
                confidence=fact.confidence,
                domain=fact.domain or 'general',
                content=fact.content,
                timestamp=fact.timestamp.isoformat()
            )
            
            # 添加关系边
            for relation in fact.relations:
                G.add_edge(
                    fact.id,
                    relation.target_fact_id,
                    relation_type=relation.relation_type.value,
                    weight=relation.confidence,
                    evidence=relation.evidence
                )
        
        return G
    
    def _create_interactive_graph(self, nodes: List[Dict], edges: List[Dict], config: VisualizationConfig) -> go.Figure:
        """创建交互式图谱"""
        # 准备节点轨迹
        node_trace = go.Scatter(
            x=[node['x'] for node in nodes],
            y=[node['y'] for node in nodes],
            mode='markers+text' if config.show_labels else 'markers',
            text=[node['label'] for node in nodes] if config.show_labels else None,
            textposition="middle center",
            hovertext=[f"ID: {node['id']}<br>Type: {node['type']}<br>Confidence: {node['confidence']:.2f}" for node in nodes],
            hoverinfo='text',
            marker=dict(
                size=[node['size'] for node in nodes],
                color=[node['color'] for node in nodes],
                line=dict(width=1, color='black')
            ),
            name='Knowledge Nodes'
        )
        
        # 准备边轨迹
        edge_trace = go.Scatter(
            x=[], y=[],
            mode='lines',
            line=dict(width=1, color='gray'),
            hoverinfo='none',
            name='Relations'
        )
        
        for edge in edges:
            x0 = next((node['x'] for node in nodes if node['id'] == edge['source']), 0)
            y0 = next((node['y'] for node in nodes if node['id'] == edge['source']), 0)
            x1 = next((node['x'] for node in nodes if node['id'] == edge['target']), 0)
            y1 = next((node['y'] for node in nodes if node['id'] == edge['target']), 0)
            
            edge_trace['x'] += [x0, x1, None]
            edge_trace['y'] += [y0, y1, None]
        
        # 创建图表
        fig = go.Figure(data=[edge_trace, node_trace])
        
        fig.update_layout(
            title="Interactive Knowledge Graph",
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[
                dict(
                    text="",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color="black", size=12)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            template=config.theme,
            width=config.width,
            height=config.height
        )
        
        return fig
    
    async def _get_timeline_events(self, start_date: datetime, end_date: datetime, 
                                 category_filter: List[str]) -> List[TimelineEvent]:
        """获取时间线事件"""
        try:
            # 从SSKG获取时间序列数据
            events = []
            
            # 这里简化实现，实际应该从数据库查询
            # 模拟一些事件数据
            sample_events = [
                TimelineEvent(
                    id="event_1",
                    title="系统启动",
                    description="DAIP-LIVE系统正式启动",
                    timestamp=datetime.now() - timedelta(days=30),
                    category="system",
                    importance=0.9
                ),
                TimelineEvent(
                    id="event_2",
                    title="知识图谱构建",
                    description="完成初始知识图谱构建",
                    timestamp=datetime.now() - timedelta(days=25),
                    category="knowledge",
                    importance=0.8
                ),
                TimelineEvent(
                    id="event_3",
                    title="V0.3.4开发",
                    description="开始V0.3.4版本开发",
                    timestamp=datetime.now() - timedelta(days=10),
                    category="development",
                    importance=0.7
                )
            ]
            
            # 应用过滤器
            filtered_events = sample_events
            if start_date:
                filtered_events = [e for e in filtered_events if e.timestamp >= start_date]
            if end_date:
                filtered_events = [e for e in filtered_events if e.timestamp <= end_date]
            if category_filter:
                filtered_events = [e for e in filtered_events if e.category in category_filter]
            
            return filtered_events
            
        except Exception as e:
            self.logger.error(f"获取时间线事件失败: {e}")
            return []
    
    def _create_timeline_chart(self, events: List[TimelineEvent], config: VisualizationConfig) -> go.Figure:
        """创建时间线图表"""
        # 准备数据
        df = pd.DataFrame([{
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'timestamp': event.timestamp,
            'category': event.category,
            'importance': event.importance
        } for event in events])
        
        # 创建时间线图
        fig = px.timeline(
            df,
            x_start="timestamp",
            x_end="timestamp",
            y="title",
            color="category",
            hover_data=["description", "importance"],
            title="Knowledge Timeline",
            width=config.width,
            height=config.height
        )
        
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Events",
            template=config.theme
        )
        
        return fig
    
    def _apply_clustering_algorithm(self, G: nx.Graph, algorithm: str) -> List[ClusterInfo]:
        """应用聚类算法"""
        try:
            if algorithm == "louvain":
                import community as community_louvain
                partition = community_louvain.best_partition(G)
            else:
                # 默认使用连通分量
                partition = {}
                for i, component in enumerate(nx.connected_components(G)):
                    for node in component:
                        partition[node] = i
            
            # 构建聚类信息
            clusters = {}
            for node, cluster_id in partition.items():
                if cluster_id not in clusters:
                    clusters[cluster_id] = {
                        'nodes': [],
                        'domain': G.nodes[node].get('domain', 'general')
                    }
                clusters[cluster_id]['nodes'].append(node)
            
            cluster_infos = []
            for cluster_id, cluster_data in clusters.items():
                cluster = ClusterInfo(
                    id=f"cluster_{cluster_id}",
                    label=f"Cluster {cluster_id}",
                    size=len(cluster_data['nodes']),
                    centrality=self._calculate_cluster_centrality(G, cluster_data['nodes']),
                    members=cluster_data['nodes'],
                    domain=cluster_data['domain']
                )
                cluster_infos.append(cluster)
            
            return cluster_infos
            
        except Exception as e:
            self.logger.error(f"应用聚类算法失败: {e}")
            return []
    
    def _calculate_cluster_centrality(self, G: nx.Graph, nodes: List[str]) -> float:
        """计算聚类中心性"""
        try:
            subgraph = G.subgraph(nodes)
            centrality_scores = nx.degree_centrality(subgraph)
            return sum(centrality_scores.values()) / len(centrality_scores)
        except Exception:
            return 0.0
    
    def _calculate_modularity(self, G: nx.Graph, clusters: List[ClusterInfo]) -> float:
        """计算模块度"""
        try:
            import community as community_louvain
            partition = {}
            for cluster in clusters:
                for node in cluster.members:
                    partition[node] = int(cluster.id.split('_')[1])
            
            return community_louvain.modularity(partition, G)
        except Exception:
            return 0.0
    
    def _create_cluster_visualization(self, G: nx.Graph, clusters: List[ClusterInfo], 
                                    config: VisualizationConfig) -> go.Figure:
        """创建聚类可视化"""
        # 为每个聚类分配颜色
        colors = px.colors.qualitative.Set3
        
        # 准备节点数据
        node_colors = []
        node_sizes = []
        cluster_labels = []
        
        for node in G.nodes():
            cluster_id = None
            for cluster in clusters:
                if node in cluster.members:
                    cluster_id = cluster.id
                    break
            
            if cluster_id:
                cluster_index = int(cluster_id.split('_')[1])
                node_colors.append(colors[cluster_index % len(colors)])
                node_sizes.append(20)
                cluster_labels.append(cluster_id)
            else:
                node_colors.append('gray')
                node_sizes.append(10)
                cluster_labels.append('unclustered')
        
        # 获取节点位置
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 创建图表
        fig = go.Figure()
        
        # 添加边
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            fig.add_trace(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=1, color='lightgray'),
                showlegend=False
            ))
        
        # 添加节点
        fig.add_trace(go.Scatter(
            x=[pos[node][0] for node in G.nodes()],
            y=[pos[node][1] for node in G.nodes()],
            mode='markers',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=1, color='black')
            ),
            text=[G.nodes[node].get('label', node) for node in G.nodes()],
            hovertemplate='<b>%{text}</b><br>Cluster: %{customdata}<extra></extra>',
            customdata=cluster_labels,
            name='Knowledge Nodes'
        ))
        
        fig.update_layout(
            title="Knowledge Clusters",
            showlegend=False,
            width=config.width,
            height=config.height,
            template=config.theme
        )
        
        return fig
    
    async def _get_subgraph_around_node(self, focus_node: str, depth: int) -> nx.Graph:
        """获取以焦点节点为中心的子网络"""
        try:
            # 获取焦点节点的邻居
            neighbors = await self.sskg_manager.find_related_nodes(
                focus_node, max_depth=depth
            )
            
            # 构建子网络
            G = nx.Graph()
            G.add_node(focus_node, label=focus_node, type='focus')
            
            for neighbor in neighbors:
                G.add_node(
                    neighbor.id,
                    label=neighbor.properties.get('title', neighbor.id),
                    type=neighbor.properties.get('type', 'related')
                )
                G.add_edge(focus_node, neighbor.id)
            
            return G
            
        except Exception as e:
            self.logger.error(f"获取子网络失败: {e}")
            return nx.Graph()
    
    def _create_network_diagram(self, G: nx.Graph, config: VisualizationConfig) -> go.Figure:
        """创建网络关系图"""
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 创建边的轨迹
        edge_trace = go.Scatter(
            x=[], y=[],
            mode='lines',
            line=dict(width=2, color='lightblue'),
            hoverinfo='none',
            name='Connections'
        )
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += [x0, x1, None]
            edge_trace['y'] += [y0, y1, None]
        
        # 创建节点的轨迹
        node_trace = go.Scatter(
            x=[pos[node][0] for node in G.nodes()],
            y=[pos[node][1] for node in G.nodes()],
            mode='markers+text',
            text=[G.nodes[node].get('label', node) for node in G.nodes()],
            textposition="middle center",
            textfont=dict(size=10),
            marker=dict(
                size=15,
                color='lightcoral',
                line=dict(width=2, color='black')
            ),
            name='Nodes',
            hovertemplate='<b>%{text}</b><extra></extra>'
        )
        
        fig = go.Figure(data=[edge_trace, node_trace])
        
        fig.update_layout(
            title="Network Relationship Diagram",
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            template=config.theme,
            width=config.width,
            height=config.height
        )
        
        return fig
    
    async def _get_knowledge_statistics(self) -> Dict[str, Any]:
        """获取知识统计数据"""
        try:
            # 这里应该从实际数据库获取统计数据
            # 简化实现，返回模拟数据
            return {
                "domain_distribution": {
                    "technology": 45,
                    "science": 32,
                    "business": 28,
                    "education": 19,
                    "health": 15
                },
                "confidence_distribution": {
                    "0.0-0.2": 5,
                    "0.2-0.4": 12,
                    "0.4-0.6": 23,
                    "0.6-0.8": 41,
                    "0.8-1.0": 58
                },
                "temporal_distribution": {
                    "2024-01": 10,
                    "2024-02": 15,
                    "2024-03": 22,
                    "2024-04": 18,
                    "2024-05": 25
                }
            }
        except Exception as e:
            self.logger.error(f"获取知识统计数据失败: {e}")
            return {}
    
    def _prepare_heatmap_data(self, stats: Dict[str, Any], dim1: str, dim2: str) -> List[List[float]]:
        """准备热力图数据"""
        try:
            if dim1 == "domain" and dim2 == "confidence":
                # 创建领域vs置信度的热力图
                domains = list(stats["domain_distribution"].keys())
                confidence_ranges = list(stats["confidence_distribution"].keys())
                
                data = []
                for domain in domains:
                    row = []
                    for conf_range in confidence_ranges:
                        # 简化：随机生成数据
                        row.append(np.random.random() * 100)
                    data.append(row)
                
                return data
            else:
                # 默认返回随机数据
                return [[np.random.random() * 100 for _ in range(5)] for _ in range(5)]
        except Exception as e:
            self.logger.error(f"准备热力图数据失败: {e}")
            return [[0 for _ in range(5)] for _ in range(5)]
    
    def _create_heatmap(self, data: List[List[float]], config: VisualizationConfig) -> go.Figure:
        """创建热力图"""
        fig = go.Figure(data=go.Heatmap(
            z=data,
            colorscale='Viridis',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Knowledge Heatmap",
            xaxis_title="Dimension 1",
            yaxis_title="Dimension 2",
            template=config.theme,
            width=config.width,
            height=config.height
        )
        
        return fig
    
    def _get_node_color(self, node_type: str) -> str:
        """获取节点颜色"""
        color_map = {
            'fact': '#1f77b4',
            'concept': '#ff7f0e',
            'memory': '#2ca02c',
            'wiki': '#d62728',
            'rule': '#9467bd',
            'unknown': '#7f7f7f'
        }
        return color_map.get(node_type, '#7f7f7f')
    
    def _get_edge_color(self, relation_type: str) -> str:
        """获取边颜色"""
        color_map = {
            'supports': '#2ca02c',
            'contradicts': '#d62728',
            'elaborates': '#ff7f0e',
            'implies': '#1f77b4',
            'related': '#7f7f7f'
        }
        return color_map.get(relation_type, '#7f7f7f')


# 使用示例
async def example_usage():
    """使用示例"""
    # 初始化组件
    sskg_manager = EnhancedSSKGManager()
    knowledge_retrieval = KnowledgeRetrievalService()
    
    # 创建可视化引擎
    viz_engine = KnowledgeVisualizationEngine(sskg_manager, knowledge_retrieval)
    
    # 生成知识图谱
    graph_result = await viz_engine.generate_knowledge_graph(
        query="机器学习",
        max_nodes=50
    )
    
    print(f"知识图谱节点数: {graph_result.get('stats', {}).get('total_nodes', 0)}")
    
    # 生成时间线
    timeline_result = await viz_engine.generate_timeline()
    
    print(f"时间线事件数: {timeline_result.get('stats', {}).get('total_events', 0)}")
    
    # 生成聚类视图
    cluster_result = await viz_engine.generate_cluster_view(
        query="AI技术",
        algorithm="louvain"
    )
    
    print(f"聚类数量: {cluster_result.get('stats', {}).get('total_clusters', 0)}")
    
    # 导出可视化
    if 'figure' in graph_result:
        output_file = viz_engine.export_visualization(
            graph_result, 
            format="html",
            filename="knowledge_graph_demo"
        )
        print(f"可视化已导出到: {output_file}")


if __name__ == "__main__":
    asyncio.run(example_usage())