#!/usr/bin/env python3
"""知识图谱可视化器

提供知识图谱的可视化和交互功能
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class KnowledgeGraphVisualizer:
    """知识图谱可视化器"""

    def __init__(self):
        """初始化知识图谱可视化器"""
        self.layout_algorithms = {
            "force_directed": "力导向布局",
            "hierarchical": "层次布局",
            "circular": "环形布局",
            "grid": "网格布局"
        }

        self.visualization_styles = {
            "default": {
                "node_size_range": (10, 50),
                "edge_width_range": (1, 5),
                "color_scheme": "category",
                "label_display": "hover"
            },
            "compact": {
                "node_size_range": (5, 25),
                "edge_width_range": (1, 3),
                "color_scheme": "monochrome",
                "label_display": "none"
            },
            "detailed": {
                "node_size_range": (20, 80),
                "edge_width_range": (2, 8),
                "color_scheme": "importance",
                "label_display": "always"
            }
        }

        logger.info("知识图谱可视化器初始化完成")

    def create_graph_visualization(
        self,
        graph_data: Dict[str, Any],
        layout: str = "force_directed",
        style: str = "default",
        interactive: bool = True
    ) -> Dict[str, Any]:
        """创建图谱可视化"""
        try:
            visualization_id = str(uuid.uuid4())

            # 处理节点数据
            processed_nodes = self._process_nodes(
                graph_data.get("nodes", []),
                style
            )

            # 处理边数据
            processed_edges = self._process_edges(
                graph_data.get("edges", []),
                style
            )

            # 生成布局配置
            layout_config = self._generate_layout_config(layout, processed_nodes)

            # 生成交互功能配置
            interactive_features = self._generate_interactive_features(interactive)

            # 生成可视化配置
            visualization_config = {
                "visualization_id": visualization_id,
                "creation_time": datetime.now().isoformat(),
                "layout_config": layout_config,
                "style_config": self.visualization_styles[style],
                "interactive_features": interactive_features,
                "data": {
                    "nodes": processed_nodes,
                    "edges": processed_edges
                },
                "metadata": {
                    "node_count": len(processed_nodes),
                    "edge_count": len(processed_edges),
                    "layout_algorithm": layout,
                    "style_theme": style,
                    "is_interactive": interactive
                }
            }

            logger.info(f"图谱可视化创建完成: {visualization_id}, {len(processed_nodes)}个节点")
            return visualization_config

        except Exception as e:
            logger.error(f"创建图谱可视化失败: {e}")
            return {
                "error": str(e),
                "visualization_id": None,
                "layout_config": {},
                "interactive_features": {}
            }

    def generate_interactive_view(
        self,
        visualization_config: Dict[str, Any],
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成交互式视图"""
        try:
            # 应用用户偏好
            if user_preferences:
                visualization_config = self._apply_user_preferences(
                    visualization_config,
                    user_preferences
                )

            # 生成交互式HTML/JavaScript代码
            interactive_code = self._generate_interactive_code(visualization_config)

            # 生成控制面板配置
            control_panel = self._generate_control_panel(visualization_config)

            # 生成事件处理器
            event_handlers = self._generate_event_handlers(visualization_config)

            interactive_view = {
                "view_id": str(uuid.uuid4()),
                "visualization_id": visualization_config.get("visualization_id"),
                "interactive_code": interactive_code,
                "control_panel": control_panel,
                "event_handlers": event_handlers,
                "view_metadata": {
                    "supports_zoom": True,
                    "supports_pan": True,
                    "supports_selection": True,
                    "supports_filtering": True,
                    "supports_search": True
                }
            }

            logger.info("交互式视图生成完成")
            return interactive_view

        except Exception as e:
            logger.error(f"生成交互式视图失败: {e}")
            return {"error": str(e)}

    def export_graph_data(
        self,
        visualization_config: Dict[str, Any],
        export_format: str = "json",
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """导出图谱数据"""
        try:
            export_data = {}

            if export_format == "json":
                export_data = self._export_to_json(visualization_config, include_metadata)
            elif export_format == "graphml":
                export_data = self._export_to_graphml(visualization_config, include_metadata)
            elif export_format == "csv":
                export_data = self._export_to_csv(visualization_config, include_metadata)
            elif export_format == "svg":
                export_data = self._export_to_svg(visualization_config)
            else:
                raise ValueError(f"不支持的导出格式: {export_format}")

            export_result = {
                "export_id": str(uuid.uuid4()),
                "export_time": datetime.now().isoformat(),
                "format": export_format,
                "data": export_data,
                "metadata": {
                    "source_visualization": visualization_config.get("visualization_id"),
                    "include_metadata": include_metadata,
                    "data_size": len(str(export_data))
                }
            }

            logger.info(f"图谱数据导出完成: {export_format}格式")
            return export_result

        except Exception as e:
            logger.error(f"导出图谱数据失败: {e}")
            return {"error": str(e)}

    def _process_nodes(self, nodes: List[Dict[str, Any]], style: str) -> List[Dict[str, Any]]:
        """处理节点数据"""
        processed_nodes = []
        style_config = self.visualization_styles[style]

        for node in nodes:
            # 计算节点大小
            importance = node.get("importance", 0.5)
            size_range = style_config["node_size_range"]
            node_size = size_range[0] + (size_range[1] - size_range[0]) * importance

            # 确定节点颜色
            node_color = self._determine_node_color(node, style_config["color_scheme"])

            # 生成节点标签
            node_label = self._generate_node_label(node, style_config["label_display"])

            processed_node = {
                "id": node.get("id"),
                "label": node_label,
                "type": node.get("type", "default"),
                "size": node_size,
                "color": node_color,
                "position": node.get("position", {"x": 0, "y": 0}),
                "properties": node.get("properties", {}),
                "metadata": {
                    "original_importance": importance,
                    "display_label": node.get("label", ""),
                    "tooltip": self._generate_node_tooltip(node)
                }
            }

            processed_nodes.append(processed_node)

        return processed_nodes

    def _process_edges(self, edges: List[Dict[str, Any]], style: str) -> List[Dict[str, Any]]:
        """处理边数据"""
        processed_edges = []
        style_config = self.visualization_styles[style]

        for edge in edges:
            # 计算边宽度
            weight = edge.get("weight", 0.5)
            width_range = style_config["edge_width_range"]
            edge_width = width_range[0] + (width_range[1] - width_range[0]) * weight

            # 确定边颜色
            edge_color = self._determine_edge_color(edge, style_config["color_scheme"])

            # 生成边标签
            edge_label = self._generate_edge_label(edge, style_config["label_display"])

            processed_edge = {
                "id": edge.get("id"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "type": edge.get("type", "default"),
                "width": edge_width,
                "color": edge_color,
                "label": edge_label,
                "properties": edge.get("properties", {}),
                "metadata": {
                    "original_weight": weight,
                    "relation_type": edge.get("type", ""),
                    "tooltip": self._generate_edge_tooltip(edge)
                }
            }

            processed_edges.append(processed_edge)

        return processed_edges

    def _generate_layout_config(self, layout: str, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成布局配置"""
        base_config = {
            "algorithm": layout,
            "iterations": 100,
            "node_repulsion": 50,
            "edge_attraction": 10,
            "center_gravity": 0.1
        }

        if layout == "force_directed":
            base_config.update({
                "spring_length": 100,
                "spring_strength": 0.1,
                "damping": 0.9
            })
        elif layout == "hierarchical":
            base_config.update({
                "level_separation": 150,
                "node_separation": 100,
                "direction": "vertical"
            })
        elif layout == "circular":
            base_config.update({
                "radius": max(100, len(nodes) * 10),
                "start_angle": 0
            })
        elif layout == "grid":
            base_config.update({
                "grid_size": max(3, int(len(nodes) ** 0.5) + 1),
                "cell_size": 100
            })

        return base_config

    def _generate_interactive_features(self, interactive: bool) -> Dict[str, Any]:
        """生成交互功能配置"""
        if not interactive:
            return {"enabled": False}

        return {
            "enabled": True,
            "zoom": {
                "enabled": True,
                "min_scale": 0.1,
                "max_scale": 10.0,
                "wheel_sensitivity": 0.1
            },
            "pan": {
                "enabled": True,
                "boundary_check": True
            },
            "selection": {
                "enabled": True,
                "multi_select": True,
                "select_on_click": True
            },
            "hover": {
                "enabled": True,
                "highlight_neighbors": True,
                "show_tooltip": True
            },
            "drag": {
                "enabled": True,
                "drag_nodes": True,
                "drag_edges": False
            },
            "search": {
                "enabled": True,
                "search_fields": ["label", "type", "properties"],
                "highlight_results": True
            },
            "filter": {
                "enabled": True,
                "filter_by_type": True,
                "filter_by_properties": True,
                "dynamic_filtering": True
            }
        }

    def _determine_node_color(self, node: Dict[str, Any], color_scheme: str) -> str:
        """确定节点颜色"""
        if color_scheme == "category":
            color_map = {
                "concept": "#3498db",
                "technology": "#e74c3c",
                "principle": "#2ecc71",
                "domain": "#f39c12",
                "default": "#95a5a6"
            }
            return color_map.get(node.get("type", "default"), color_map["default"])

        elif color_scheme == "importance":
            importance = node.get("importance", 0.5)
            # 从蓝色到红色的渐变
            red = int(255 * importance)
            blue = int(255 * (1 - importance))
            return f"rgb({red}, 100, {blue})"

        elif color_scheme == "monochrome":
            return "#666666"

        else:
            return "#3498db"

    def _determine_edge_color(self, edge: Dict[str, Any], color_scheme: str) -> str:
        """确定边颜色"""
        if color_scheme == "category":
            color_map = {
                "is_a": "#3498db",
                "includes": "#2ecc71",
                "affects": "#e74c3c",
                "related_to": "#f39c12",
                "based_on": "#9b59b6",
                "default": "#bdc3c7"
            }
            return color_map.get(edge.get("type", "default"), color_map["default"])

        else:
            return "#bdc3c7"

    def _generate_node_label(self, node: Dict[str, Any], label_display: str) -> str:
        """生成节点标签"""
        if label_display == "none":
            return ""
        elif label_display == "always":
            return node.get("label", node.get("id", ""))
        elif label_display == "hover":
            return ""  # 悬停时显示
        else:
            return node.get("label", "")

    def _generate_edge_label(self, edge: Dict[str, Any], label_display: str) -> str:
        """生成边标签"""
        if label_display == "none":
            return ""
        elif label_display == "always":
            return edge.get("type", "")
        else:
            return ""

    def _generate_node_tooltip(self, node: Dict[str, Any]) -> str:
        """生成节点提示信息"""
        tooltip_parts = [
            f"标签: {node.get('label', 'N/A')}",
            f"类型: {node.get('type', 'N/A')}",
            f"重要性: {node.get('importance', 0.5):.2f}"
        ]

        properties = node.get("properties", {})
        if properties:
            tooltip_parts.append("属性:")
            for key, value in properties.items():
                tooltip_parts.append(f"  {key}: {value}")

        return "\\n".join(tooltip_parts)

    def _generate_edge_tooltip(self, edge: Dict[str, Any]) -> str:
        """生成边提示信息"""
        tooltip_parts = [
            f"关系类型: {edge.get('type', 'N/A')}",
            f"权重: {edge.get('weight', 0.5):.2f}",
            f"源节点: {edge.get('source', 'N/A')}",
            f"目标节点: {edge.get('target', 'N/A')}"
        ]

        return "\\n".join(tooltip_parts)

    def _generate_interactive_code(self, visualization_config: Dict[str, Any]) -> str:
        """生成交互式代码"""
        # 简化的JavaScript代码生成
        code_template = f"""
        // 知识图谱可视化代码
        const graphData = {json.dumps(visualization_config.get('data', {}), indent=2)};
        const layoutConfig = {json.dumps(visualization_config.get('layout_config', {}), indent=2)};
        const interactiveFeatures = {json.dumps(visualization_config.get('interactive_features', {}), indent=2)};
        
        // 初始化图谱可视化
        function initializeGraph() {{
            // 图谱初始化逻辑
            console.log('初始化知识图谱可视化');
            console.log('节点数量:', graphData.nodes.length);
            console.log('边数量:', graphData.edges.length);
        }}
        
        // 事件处理函数
        function handleNodeClick(nodeId) {{
            console.log('节点点击:', nodeId);
        }}
        
        function handleEdgeClick(edgeId) {{
            console.log('边点击:', edgeId);
        }}
        
        // 启动可视化
        initializeGraph();
        """

        return code_template

    def _generate_control_panel(self, visualization_config: Dict[str, Any]) -> Dict[str, Any]:
        """生成控制面板配置"""
        return {
            "layout_controls": {
                "algorithm_selector": list(self.layout_algorithms.keys()),
                "force_parameters": ["node_repulsion", "edge_attraction", "center_gravity"],
                "animation_controls": ["play", "pause", "reset"]
            },
            "style_controls": {
                "theme_selector": list(self.visualization_styles.keys()),
                "color_scheme": ["category", "importance", "monochrome"],
                "size_adjustment": {"min": 5, "max": 100}
            },
            "filter_controls": {
                "node_type_filter": True,
                "importance_range": {"min": 0.0, "max": 1.0},
                "search_box": True
            },
            "export_controls": {
                "formats": ["json", "graphml", "csv", "svg"],
                "include_metadata": True
            }
        }

    def _generate_event_handlers(self, visualization_config: Dict[str, Any]) -> Dict[str, str]:
        """生成事件处理器"""
        return {
            "node_click": "handleNodeClick",
            "node_hover": "handleNodeHover",
            "edge_click": "handleEdgeClick",
            "background_click": "handleBackgroundClick",
            "zoom_change": "handleZoomChange",
            "selection_change": "handleSelectionChange"
        }

    def _apply_user_preferences(
        self,
        visualization_config: Dict[str, Any],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用用户偏好"""
        # 应用布局偏好
        if "preferred_layout" in user_preferences:
            visualization_config["layout_config"]["algorithm"] = user_preferences["preferred_layout"]

        # 应用样式偏好
        if "preferred_style" in user_preferences:
            style = user_preferences["preferred_style"]
            if style in self.visualization_styles:
                visualization_config["style_config"] = self.visualization_styles[style]

        # 应用颜色偏好
        if "color_scheme" in user_preferences:
            visualization_config["style_config"]["color_scheme"] = user_preferences["color_scheme"]

        return visualization_config

    def _export_to_json(self, visualization_config: Dict[str, Any], include_metadata: bool) -> Dict[str, Any]:
        """导出为JSON格式"""
        export_data = {
            "nodes": visualization_config.get("data", {}).get("nodes", []),
            "edges": visualization_config.get("data", {}).get("edges", [])
        }

        if include_metadata:
            export_data["metadata"] = visualization_config.get("metadata", {})
            export_data["layout_config"] = visualization_config.get("layout_config", {})

        return export_data

    def _export_to_graphml(self, visualization_config: Dict[str, Any], include_metadata: bool) -> str:
        """导出为GraphML格式"""
        # 简化的GraphML生成
        nodes = visualization_config.get("data", {}).get("nodes", [])
        edges = visualization_config.get("data", {}).get("edges", [])

        graphml_content = '<?xml version="1.0" encoding="UTF-8"?>\\n'
        graphml_content += '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\\n'
        graphml_content += '  <graph id="knowledge_graph" edgedefault="undirected">\\n'

        # 添加节点
        for node in nodes:
            graphml_content += f'    <node id="{node.get("id")}">\\n'
            graphml_content += f'      <data key="label">{node.get("label", "")}</data>\\n'
            graphml_content += f'      <data key="type">{node.get("type", "")}</data>\\n'
            graphml_content += '    </node>\\n'

        # 添加边
        for edge in edges:
            graphml_content += f'    <edge source="{edge.get("source")}" target="{edge.get("target")}">\\n'
            graphml_content += f'      <data key="type">{edge.get("type", "")}</data>\\n'
            graphml_content += '    </edge>\\n'

        graphml_content += '  </graph>\\n'
        graphml_content += '</graphml>'

        return graphml_content

    def _export_to_csv(self, visualization_config: Dict[str, Any], include_metadata: bool) -> Dict[str, str]:
        """导出为CSV格式"""
        nodes = visualization_config.get("data", {}).get("nodes", [])
        edges = visualization_config.get("data", {}).get("edges", [])

        # 节点CSV
        nodes_csv = "id,label,type,size,color\\n"
        for node in nodes:
            nodes_csv += f'"{node.get("id")}","{node.get("label", "")}","{node.get("type", "")}",{node.get("size", 0)},"{node.get("color", "")}"\\n'

        # 边CSV
        edges_csv = "id,source,target,type,width,color\\n"
        for edge in edges:
            edges_csv += f'"{edge.get("id")}","{edge.get("source")}","{edge.get("target")}","{edge.get("type", "")}",{edge.get("width", 0)},"{edge.get("color", "")}"\\n'

        return {
            "nodes.csv": nodes_csv,
            "edges.csv": edges_csv
        }

    def _export_to_svg(self, visualization_config: Dict[str, Any]) -> str:
        """导出为SVG格式"""
        # 简化的SVG生成
        nodes = visualization_config.get("data", {}).get("nodes", [])
        edges = visualization_config.get("data", {}).get("edges", [])

        svg_content = '<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">\\n'

        # 添加边
        for edge in edges:
            svg_content += f'  <line x1="100" y1="100" x2="200" y2="200" stroke="{edge.get("color", "#ccc")}" stroke-width="{edge.get("width", 1)}"/>\\n'

        # 添加节点
        for i, node in enumerate(nodes):
            x = 100 + (i % 10) * 60
            y = 100 + (i // 10) * 60
            svg_content += f'  <circle cx="{x}" cy="{y}" r="{node.get("size", 10)}" fill="{node.get("color", "#3498db")}"/>\\n'
            svg_content += f'  <text x="{x}" y="{y+5}" text-anchor="middle" font-size="12">{node.get("label", "")}</text>\\n'

        svg_content += '</svg>'

        return svg_content
