"""@Time: 2025-08-03
@Author: DAIP-LIVE
@File: knowledge_visualization_engine.py
@Description: V0.3.4 知识可视化引擎 - 交互式知识图谱和可视化组件
"""

import asyncio
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

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

def _get_networkx():
    global _networkx
    if _networkx is None:
        try:
            import networkx as nx
            _networkx = nx
        except ImportError:
            raise ImportError("networkx is required for knowledge visualization. Please install it with 'pip install networkx'")
    return _networkx

def _get_plotly_go():
    global _plotly_go
    if _plotly_go is None:
        try:
            import plotly.graph_objects as go
            _plotly_go = go
        except ImportError:
            raise ImportError("plotly is required for interactive visualizations. Please install it with 'pip install plotly'")
    return _plotly_go

def _get_plotly_px():
    global _plotly_px
    if _plotly_px is None:
        try:
            import plotly.express as px
            _plotly_px = px
        except ImportError:
            raise ImportError("plotly is required for interactive visualizations. Please install it with 'pip install plotly'")
    return _plotly_px

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
            import matplotlib.figure as figure
            _matplotlib_figure = figure
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
            raise ImportError("seaborn is required for visualization. Please install it with 'pip install seaborn'")
    return _seaborn

def _get_pandas():
    global _pandas
    if _pandas is None:
        try:
            import pandas as pd
            _pandas = pd
        except ImportError:
            raise ImportError("pandas is required for data processing. Please install it with 'pip install pandas'")
    return _pandas

def _get_numpy():
    global _numpy
    if _numpy is None:
        try:
            import numpy as np
            _numpy = np
        except ImportError:
            raise ImportError("numpy is required for numerical computations. Please install it with 'pip install numpy'")
    return _numpy

# 读取原始文件的其余部分﻿            # 鑾峰彇鐭ヨ瘑鏁版嵁
            knowledge_facts = await self._get_knowledge_facts(query, max_nodes)
            
            # 鏋勫缓缃戠粶鍥?            G = await self._build_knowledge_network(knowledge_facts)
            
            # 搴旂敤甯冨眬绠楁硶
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            # 鍑嗗鍙鍖栨暟鎹?            nodes = []
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
            
            # 鐢熸垚Plotly鍥捐〃
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
            self.logger.error(f"鐢熸垚鐭ヨ瘑鍥捐氨澶辫触: {e}")
            return {"error": str(e)}
    
    async def generate_timeline(self, 
                             start_date: datetime = None,
                             end_date: datetime = None,
                             category_filter: list[str] = None,
                             config: VisualizationConfig = None) -> dict[str, Any]:
        """鐢熸垚鏃堕棿绾垮彲瑙嗗寲"""
        try:
            if config is None:
                config = VisualizationConfig()
            
            # 鑾峰彇鏃堕棿搴忓垪鏁版嵁
            events = await self._get_timeline_events(start_date, end_date, category_filter)
            
            if not events:
                return {"error": "娌℃湁鎵惧埌鏃堕棿搴忓垪鏁版嵁"}
            
            # 鍒涘缓鏃堕棿绾垮浘琛?            fig = self._create_timeline_chart(events, config)
            
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
            self.logger.error(f"鐢熸垚鏃堕棿绾垮け璐? {e}")
            return {"error": str(e)}
    
    async def generate_cluster_view(self, 
                                  query: str = "",
                                  algorithm: str = "louvain",
                                  config: VisualizationConfig = None) -> dict[str, Any]:
        """鐢熸垚鑱氱被瑙嗗浘"""
        try:
            if config is None:
                config = VisualizationConfig()
            
            # 鑾峰彇鐭ヨ瘑鏁版嵁
            knowledge_facts = await self._get_knowledge_facts(query, 200)
            
            # 鏋勫缓缃戠粶鍥?            G = await self._build_knowledge_network(knowledge_facts)
            
            # 搴旂敤鑱氱被绠楁硶
            clusters = self._apply_clustering_algorithm(G, algorithm)
            
            # 鍒涘缓鑱氱被鍙鍖?            fig = self._create_cluster_visualization(G, clusters, config)
            
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
            self.logger.error(f"鐢熸垚鑱氱被瑙嗗浘澶辫触: {e}")
            return {"error": str(e)}
    
    async def generate_network_diagram(self, 
                                    focus_node: str = "",
                                    depth: int = 2,
                                    config: VisualizationConfig = None) -> dict[str, Any]:
        """鐢熸垚缃戠粶鍏崇郴鍥?""
        try:
            if config is None:
                config = VisualizationConfig()
            
            # 鑾峰彇浠ョ劍鐐硅妭鐐逛负涓績鐨勫瓙缃戠粶
            subgraph = await self._get_subgraph_around_node(focus_node, depth)
            
            # 鍒涘缓缃戠粶鍥?            fig = self._create_network_diagram(subgraph, config)
            
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
            self.logger.error(f"鐢熸垚缃戠粶鍏崇郴鍥惧け璐? {e}")
            return {"error": str(e)}
    
    async def generate_heatmap(self, 
                            dimension1: str = "domain",
                            dimension2: str = "confidence",
                            config: VisualizationConfig = None) -> dict[str, Any]:
        """鐢熸垚鐑姏鍥?""
        try:
            if config is None:
                config = VisualizationConfig()
            
            # 鑾峰彇鐭ヨ瘑缁熻鏁版嵁
            stats = await self._get_knowledge_statistics()
            
            # 鍒涘缓鐑姏鍥炬暟鎹?            heatmap_data = self._prepare_heatmap_data(stats, dimension1, dimension2)
            
            # 鐢熸垚鐑姏鍥?            fig = self._create_heatmap(heatmap_data, config)
            
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
            self.logger.error(f"鐢熸垚鐑姏鍥惧け璐? {e}")
            return {"error": str(e)}
    
    def export_visualization(self, 
                           visualization_data: dict[str, Any], 
                           format: str = "html",
                           filename: str = None) -> str:
        """瀵煎嚭鍙鍖栫粨鏋?""
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
                raise ValueError(f"涓嶆敮鎸佺殑瀵煎嚭鏍煎紡: {format}")
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"瀵煎嚭鍙鍖栧け璐? {e}")
            return ""
    
    async def _get_knowledge_facts(self, query: str, max_count: int) -> list[KnowledgeFact]:
        """鑾峰彇鐭ヨ瘑浜嬪疄"""
        try:
            if query:
                # 鍩轰簬鏌ヨ鎼滅储
                search_results = await self.knowledge_retrieval.semantic_search(
                    query=query, limit=max_count
                )
                return search_results
            else:
                # 鑾峰彇鏈€鏂扮煡璇?                return await self.knowledge_retrieval.get_recent_knowledge(max_count)
        except Exception as e:
            self.logger.error(f"鑾峰彇鐭ヨ瘑浜嬪疄澶辫触: {e}")
            return []
    
    async def _build_knowledge_network(self, knowledge_facts: list[KnowledgeFact]) -> "nx.Graph":
        """鏋勫缓鐭ヨ瘑缃戠粶"""
        nx = _get_networkx()
        G = nx.Graph()
        
        for fact in knowledge_facts:
            # 娣诲姞鑺傜偣
            G.add_node(
                fact.id,
                label=fact.content[:50] + "..." if len(fact.content) > 50 else fact.content,
                type=fact.metadata.get('type', 'fact'),
                confidence=fact.confidence,
                domain=fact.domain or 'general',
                content=fact.content,
                timestamp=fact.timestamp.isoformat()
            )
            
            # 娣诲姞鍏崇郴杈?            for relation in fact.relations:
                G.add_edge(
                    fact.id,
                    relation.target_fact_id,
                    relation_type=relation.relation_type.value,
                    weight=relation.confidence,
                    evidence=relation.evidence
                )
        
        return G
    
    def _create_interactive_graph(self, nodes: list[dict], edges: list[dict], config: VisualizationConfig) -> "_get_plotly_go()".Figure:
        """鍒涘缓浜や簰寮忓浘璋?""
        go = _get_plotly_go()
        # 鍑嗗鑺傜偣杞ㄨ抗
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
        
        # 鍑嗗杈硅建杩?        edge_trace = go.Scatter(
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
        
        # 鍒涘缓鍥捐〃
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
                                 category_filter: list[str]) -> list[TimelineEvent]:
        """鑾峰彇鏃堕棿绾夸簨浠?""
        try:
            # 浠嶴SKG鑾峰彇鏃堕棿搴忓垪鏁版嵁
            events = []
            
            # 杩欓噷绠€鍖栧疄鐜帮紝瀹為檯搴旇浠庢暟鎹簱鏌ヨ
            # 妯℃嫙涓€浜涗簨浠舵暟鎹?            sample_events = [
                TimelineEvent(
                    id="event_1",
                    title="绯荤粺鍚姩",
                    description="DAIP-LIVE绯荤粺姝ｅ紡鍚姩",
                    timestamp=datetime.now() - timedelta(days=30),
                    category="system",
                    importance=0.9
                ),
                TimelineEvent(
                    id="event_2",
                    title="鐭ヨ瘑鍥捐氨鏋勫缓",
                    description="瀹屾垚鍒濆鐭ヨ瘑鍥捐氨鏋勫缓",
                    timestamp=datetime.now() - timedelta(days=25),
                    category="knowledge",
                    importance=0.8
                ),
                TimelineEvent(
                    id="event_3",
                    title="V0.3.4寮€鍙?,
                    description="寮€濮媀0.3.4鐗堟湰寮€鍙?,
                    timestamp=datetime.now() - timedelta(days=10),
                    category="development",
                    importance=0.7
                )
            ]
            
            # 搴旂敤杩囨护鍣?            filtered_events = sample_events
            if start_date:
                filtered_events = [e for e in filtered_events if e.timestamp >= start_date]
            if end_date:
                filtered_events = [e for e in filtered_events if e.timestamp <= end_date]
            if category_filter:
                filtered_events = [e for e in filtered_events if e.category in category_filter]
            
            return filtered_events
            
        except Exception as e:
            self.logger.error(f"鑾峰彇鏃堕棿绾夸簨浠跺け璐? {e}")
            return []
    
    def _create_timeline_chart(self, events: list[TimelineEvent], config: VisualizationConfig) -> "_get_plotly_go()".Figure:
        """鍒涘缓鏃堕棿绾垮浘琛?""
        px = _get_plotly_px()
        # 鍑嗗鏁版嵁
        df = pd.DataFrame([{
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'timestamp': event.timestamp,
            'category': event.category,
            'importance': event.importance
        } for event in events])
        
        # 鍒涘缓鏃堕棿绾垮浘
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
    
    def _apply_clustering_algorithm(self, G: nx.Graph, algorithm: str) -> list[ClusterInfo]:
        """搴旂敤鑱氱被绠楁硶"""
        try:
            if algorithm == "louvain":
                import community as community_louvain
                partition = community_louvain.best_partition(G)
            else:
                # 榛樿浣跨敤杩為€氬垎閲?                partition = {}
                for i, component in enumerate(nx.connected_components(G)):
                    for node in component:
                        partition[node] = i
            
            # 鏋勫缓鑱氱被淇℃伅
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
            self.logger.error(f"搴旂敤鑱氱被绠楁硶澶辫触: {e}")
            return []
    
    def _calculate_cluster_centrality(self, G: nx.Graph, nodes: list[str]) -> float:
        """璁＄畻鑱氱被涓績鎬?""
        try:
            subgraph = G.subgraph(nodes)
            centrality_scores = nx.degree_centrality(subgraph)
            return sum(centrality_scores.values()) / len(centrality_scores)
        except Exception:
            return 0.0
    
    def _calculate_modularity(self, G: nx.Graph, clusters: list[ClusterInfo]) -> float:
        """璁＄畻妯″潡搴?""
        try:
            import community as community_louvain
            partition = {}
            for cluster in clusters:
                for node in cluster.members:
                    partition[node] = int(cluster.id.split('_')[1])
            
            return community_louvain.modularity(partition, G)
        except Exception:
            return 0.0
    
    def _create_cluster_visualization(self, G: nx.Graph, clusters: list[ClusterInfo], 
                                    config: VisualizationConfig) -> "_get_plotly_go()".Figure:
        """鍒涘缓鑱氱被鍙鍖?""
        px = _get_plotly_px()
        # 涓烘瘡涓仛绫诲垎閰嶉鑹?        colors = px.colors.qualitative.Set3
        
        # 鍑嗗鑺傜偣鏁版嵁
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
        
        # 鑾峰彇鑺傜偣浣嶇疆
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 鍒涘缓鍥捐〃
        fig = go.Figure()
        
        # 娣诲姞杈?        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            fig.add_trace(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=1, color='lightgray'),
                showlegend=False
            ))
        
        # 娣诲姞鑺傜偣
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
        """鑾峰彇浠ョ劍鐐硅妭鐐逛负涓績鐨勫瓙缃戠粶"""
        try:
            # 鑾峰彇鐒︾偣鑺傜偣鐨勯偦灞?            neighbors = await self.sskg_manager.find_related_nodes(
                focus_node, max_depth=depth
            )
            
            # 鏋勫缓瀛愮綉缁?            G = nx.Graph()
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
            self.logger.error(f"鑾峰彇瀛愮綉缁滃け璐? {e}")
            return nx.Graph()
    
    def _create_network_diagram(self, G: nx.Graph, config: VisualizationConfig) -> "_get_plotly_go()".Figure:
        """鍒涘缓缃戠粶鍏崇郴鍥?""
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 鍒涘缓杈圭殑杞ㄨ抗
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
        
        # 鍒涘缓鑺傜偣鐨勮建杩?        node_trace = go.Scatter(
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
    
    async def _get_knowledge_statistics(self) -> dict[str, Any]:
        """鑾峰彇鐭ヨ瘑缁熻鏁版嵁"""
        try:
            # 杩欓噷搴旇浠庡疄闄呮暟鎹簱鑾峰彇缁熻鏁版嵁
            # 绠€鍖栧疄鐜帮紝杩斿洖妯℃嫙鏁版嵁
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
            self.logger.error(f"鑾峰彇鐭ヨ瘑缁熻鏁版嵁澶辫触: {e}")
            return {}
    
    def _prepare_heatmap_data(self, stats: dict[str, Any], dim1: str, dim2: str) -> list[list[float]]:
        """鍑嗗鐑姏鍥炬暟鎹?""
        try:
            if dim1 == "domain" and dim2 == "confidence":
                # 鍒涘缓棰嗗煙vs缃俊搴︾殑鐑姏鍥?                domains = list(stats["domain_distribution"].keys())
                confidence_ranges = list(stats["confidence_distribution"].keys())
                
                data = []
                for domain in domains:
                    row = []
                    for conf_range in confidence_ranges:
                        # 绠€鍖栵細闅忔満鐢熸垚鏁版嵁
                        row.append(np.random.random() * 100)
                    data.append(row)
                
                return data
            else:
                # 榛樿杩斿洖闅忔満鏁版嵁
                return [[np.random.random() * 100 for _ in range(5)] for _ in range(5)]
        except Exception as e:
            self.logger.error(f"鍑嗗鐑姏鍥炬暟鎹け璐? {e}")
            return [[0 for _ in range(5)] for _ in range(5)]
    
    def _create_heatmap(self, data: list[list[float]], config: VisualizationConfig) -> "_get_plotly_go()".Figure:
        """鍒涘缓鐑姏鍥?""
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
        """鑾峰彇鑺傜偣棰滆壊"""
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
        """鑾峰彇杈归鑹?""
        color_map = {
            'supports': '#2ca02c',
            'contradicts': '#d62728',
            'elaborates': '#ff7f0e',
            'implies': '#1f77b4',
            'related': '#7f7f7f'
        }
        return color_map.get(relation_type, '#7f7f7f')


# 浣跨敤绀轰緥
async def example_usage():
    """浣跨敤绀轰緥"""
    # 鍒濆鍖栫粍浠?    sskg_manager = EnhancedSSKGManager()
    knowledge_retrieval = KnowledgeRetrievalService()
    
    # 鍒涘缓鍙鍖栧紩鎿?    viz_engine = KnowledgeVisualizationEngine(sskg_manager, knowledge_retrieval)
    
    # 鐢熸垚鐭ヨ瘑鍥捐氨
    graph_result = await viz_engine.generate_knowledge_graph(
        query="鏈哄櫒瀛︿範",
        max_nodes=50
    )
    
    print(f"鐭ヨ瘑鍥捐氨鑺傜偣鏁? {graph_result.get('stats', {}).get('total_nodes', 0)}")
    
    # 鐢熸垚鏃堕棿绾?    timeline_result = await viz_engine.generate_timeline()
    
    print(f"鏃堕棿绾夸簨浠舵暟: {timeline_result.get('stats', {}).get('total_events', 0)}")
    
    # 鐢熸垚鑱氱被瑙嗗浘
    cluster_result = await viz_engine.generate_cluster_view(
        query="AI鎶€鏈?,
        algorithm="louvain"
    )
    
    print(f"鑱氱被鏁伴噺: {cluster_result.get('stats', {}).get('total_clusters', 0)}")
    
    # 瀵煎嚭鍙鍖?    if 'figure' in graph_result:
        output_file = viz_engine.export_visualization(
            graph_result, 
            format="html",
            filename="knowledge_graph_demo"
        )
        print(f"鍙鍖栧凡瀵煎嚭鍒? {output_file}")


if __name__ == "__main__":
    asyncio.run(example_usage())
