"""
Chart generation functions for the perspective visualizer.
"""

import logging
import asyncio
import json
import statistics
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import asdict

from .models import ChartConfig, VisualizationType
from .utils import generate_heatmap_colors

logger = logging.getLogger(__name__)


async def create_perspective_radar(data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Create perspective radar chart."""
    try:
        perspectives = data.get("perspectives", [])
        quality_scores = data.get("quality_scores", {})
        
        if not perspectives:
            raise ValueError("No perspectives data provided")
        
        # Prepare radar data
        radar_data = []
        for perspective in perspectives:
            score = quality_scores.get(perspective, 0.0)
            radar_data.append({
                "axis": perspective,
                "value": score * 100  # Convert to percentage
            })
        
        # Create chart configuration
        chart_config = ChartConfig(
            chart_type="radar",
            width=config.get("width", 800),
            height=config.get("height", 600),
            colors=config.get("colors", ["#1f77b4"]),
            interactive=config.get("interactive", True),
            show_legend=config.get("show_legend", True),
            title="多视角质量雷达图",
            subtitle="各视角的综合质量评估"
        )
        
        # Generate visualization
        visualization = {
            "type": "radar",
            "data": {
                "datasets": [{
                    "label": "质量评分",
                    "data": radar_data,
                    "fill": True,
                    "backgroundColor": "rgba(31, 119, 180, 0.2)",
                    "borderColor": "rgb(31, 119, 180)",
                    "pointBackgroundColor": "rgb(31, 119, 180)",
                    "pointBorderColor": "#fff",
                    "pointHoverBackgroundColor": "#fff",
                    "pointHoverBorderColor": "rgb(31, 119, 180)"
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": chart_config.title,
                        "subtitle": chart_config.subtitle
                    },
                    "legend": {
                        "display": chart_config.show_legend
                    }
                },
                "scales": {
                    "r": {
                        "angleLines": {"display": True},
                        "suggestedMin": 0,
                        "suggestedMax": 100
                    }
                }
            }
        }
        
        return {
            "success": True,
            "visualization": visualization,
            "config": asdict(chart_config),
            "metadata": {
                "perspective_count": len(perspectives),
                "average_score": statistics.mean(quality_scores.values()) if quality_scores else 0.0,
                "created_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create perspective radar: {e}")
        return {"success": False, "error": str(e)}


async def create_quality_heatmap(data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Create quality heatmap visualization."""
    try:
        quality_dimensions = data.get("quality_dimensions", {})
        synthesis_results = data.get("synthesis_results", [])
        
        if not quality_dimensions:
            raise ValueError("No quality dimensions data provided")
        
        # Prepare heatmap data
        dimensions = list(quality_dimensions.keys())
        results = synthesis_results if synthesis_results else ["latest"]
        
        heatmap_data = []
        for result in results:
            row = []
            for dimension in dimensions:
                score = quality_dimensions.get(dimension, {}).get("score", 0.0)
                row.append(score * 100)
            heatmap_data.append(row)
        
        # Create chart configuration
        chart_config = ChartConfig(
            chart_type="heatmap",
            width=config.get("width", 800),
            height=config.get("height", 600),
            colors=config.get("colors", ["#1f77b4", "#ff7f0e"]),
            interactive=config.get("interactive", True),
            show_legend=config.get("show_legend", True),
            title="质量维度热力图",
            subtitle="不同维度的质量表现分布"
        )
        
        # Generate visualization
        visualization = {
            "type": "heatmap",
            "data": {
                "labels": dimensions,
                "datasets": [{
                    "label": "质量评分",
                    "data": heatmap_data,
                    "backgroundColor": generate_heatmap_colors(heatmap_data)
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": chart_config.title,
                        "subtitle": chart_config.subtitle
                    },
                    "legend": {
                        "display": chart_config.show_legend
                    }
                },
                "scales": {
                    "x": {"title": {"display": True, "text": "质量维度"}},
                    "y": {"title": {"display": True, "text": "综合结果"}}
                }
            }
        }
        
        return {
            "success": True,
            "visualization": visualization,
            "config": asdict(chart_config),
            "metadata": {
                "dimension_count": len(dimensions),
                "result_count": len(results),
                "created_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create quality heatmap: {e}")
        return {"success": False, "error": str(e)}


async def create_consensus_treemap(data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Create consensus treemap visualization."""
    try:
        consensus_areas = data.get("consensus_areas", [])
        conflicts = data.get("conflicts", [])
        
        if not consensus_areas and not conflicts:
            raise ValueError("No consensus areas or conflicts data provided")
        
        # Prepare treemap data
        treemap_data = []
        
        # Add consensus areas
        for i, area in enumerate(consensus_areas):
            treemap_data.append({
                "name": f"共识 {i+1}",
                "value": len(area) * 10,  # Size based on content length
                "color": "#2ca02c",
                "type": "consensus",
                "content": area
            })
        
        # Add conflicts
        for i, conflict in enumerate(conflicts):
            treemap_data.append({
                "name": f"冲突 {i+1}",
                "value": conflict.get("conflict_score", 0.5) * 20,
                "color": "#d62728",
                "type": "conflict",
                "description": conflict.get("description", "")
            })
        
        # Create chart configuration
        chart_config = ChartConfig(
            chart_type="treemap",
            width=config.get("width", 800),
            height=config.get("height", 600),
            colors=config.get("colors", ["#2ca02c", "#d62728"]),
            interactive=config.get("interactive", True),
            show_legend=config.get("show_legend", True),
            title="共识与冲突树图",
            subtitle="共识领域和冲突点的相对重要性"
        )
        
        # Generate visualization
        visualization = {
            "type": "treemap",
            "data": {
                "datasets": [{
                    "tree": treemap_data,
                    "key": "value",
                    "groups": ["name"],
                    "spacing": 2,
                    "backgroundColor": "function(ctx) { const item = ctx.raw; return item.color; }"
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": chart_config.title,
                        "subtitle": chart_config.subtitle
                    },
                    "legend": {
                        "display": chart_config.show_legend
                    },
                    "tooltip": {
                        "callbacks": {
                            "title": "function(context) { return context[0].raw.name; }",
                            "label": "function(context) { const item = context.raw; return [`类型: ${item.type}`, `内容: ${item.content || item.description || ''}`]; }"
                        }
                    }
                }
            }
        }
        
        return {
            "success": True,
            "visualization": visualization,
            "config": asdict(chart_config),
            "metadata": {
                "consensus_count": len(consensus_areas),
                "conflict_count": len(conflicts),
                "created_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create consensus treemap: {e}")
        return {"success": False, "error": str(e)}


async def create_performance_timeline(data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Create performance timeline visualization."""
    try:
        performance_data = data.get("performance_data", [])
        metrics = data.get("metrics", ["quality_score", "synthesis_speed"])
        
        if not performance_data:
            raise ValueError("No performance data provided")
        
        # Prepare timeline data
        timeline_data = {}
        for metric in metrics:
            timeline_data[metric] = []
        
        for point in performance_data:
            timestamp = point.get("timestamp", "")
            for metric in metrics:
                value = point.get(metric, 0.0)
                timeline_data[metric].append({
                    "x": timestamp,
                    "y": value
                })
        
        # Create datasets
        datasets = []
        colors = config.get("colors", ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
        
        for i, metric in enumerate(metrics):
            datasets.append({
                "label": metric,
                "data": timeline_data[metric],
                "borderColor": colors[i % len(colors)],
                "backgroundColor": colors[i % len(colors)] + "20",
                "fill": False,
                "tension": 0.1
            })
        
        # Create chart configuration
        chart_config = ChartConfig(
            chart_type="line",
            width=config.get("width", 800),
            height=config.get("height", 600),
            colors=config.get("colors", ["#1f77b4", "#ff7f0e"]),
            interactive=config.get("interactive", True),
            show_legend=config.get("show_legend", True),
            title="性能时间线",
            subtitle="关键性能指标的历史变化趋势"
        )
        
        # Generate visualization
        visualization = {
            "type": "line",
            "data": {
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": chart_config.title,
                        "subtitle": chart_config.subtitle
                    }
                }
            }
        }
        
        return {
            "success": True,
            "visualization": visualization,
            "config": asdict(chart_config),
            "metadata": {
                "metric_count": len(metrics),
                "data_points": len(performance_data),
                "time_range": {
                    "start": performance_data[0].get("timestamp") if performance_data else None,
                    "end": performance_data[-1].get("timestamp") if performance_data else None
                },
                "created_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create performance timeline: {e}")
        return {"success": False, "error": str(e)}
    
    async def _create_conflict_network(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create conflict network visualization."""
        try:
            conflicts = data.get("conflicts", [])
            perspectives = data.get("perspectives", [])
            
            if not conflicts:
                raise ValueError("No conflict data provided")
            
            # Prepare network data
            nodes = []
            edges = []
            
            # Add perspective nodes
            for i, perspective in enumerate(perspectives):
                nodes.append({
                    "id": f"perspective_{i}",
                    "label": perspective,
                    "type": "perspective",
                    "size": 20,
                    "color": "#1f77b4"
                })
            
            # Add conflict nodes and edges
            for i, conflict in enumerate(conflicts):
                conflict_id = f"conflict_{i}"
                nodes.append({
                    "id": conflict_id,
                    "label": f"冲突 {i+1}",
                    "type": "conflict",
                    "size": conflict.get("conflict_score", 0.5) * 30,
                    "color": "#d62728"
                })
                
                # Connect to involved perspectives (simplified)
                involved_perspectives = conflict.get("involved_perspectives", [])
                for perspective_idx in involved_perspectives:
                    if perspective_idx < len(perspectives):
                        edges.append({
                            "from": f"perspective_{perspective_idx}",
                            "to": conflict_id,
                            "width": 2,
                            "color": "#ff7f0e"
                        })
            
            # Create chart configuration
            chart_config = ChartConfig(
                chart_type="network",
                width=config.get("width", 800),
                height=config.get("height", 600),
                colors=config.get("colors", ["#1f77b4", "#d62728", "#ff7f0e"]),
                interactive=config.get("interactive", True),
                show_legend=config.get("show_legend", True),
                title="冲突网络图",
                subtitle="视角间的冲突关系网络"
            )
            
            # Generate visualization
            visualization = {
                "type": "network",
                "data": {
                    "nodes": nodes,
                    "edges": edges
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": chart_config.title,
                            "subtitle": chart_config.subtitle
                        },
                        "legend": {
                            "display": chart_config.show_legend
                        }
                    },
                    "physics": {
                        "enabled": True,
                        "stabilization": {"iterations": 100}
                    }
                }
            }
            
            return {
                "success": True,
                "visualization": visualization,
                "config": asdict(chart_config),
                "metadata": {
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "conflict_count": len(conflicts),
                    "created_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create conflict network: {e}")
            return {"success": False, "error": str(e)}


async def create_insight_wordcloud(data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Create insight word cloud visualization."""
    try:
        insights = data.get("insights", [])
        synthesis_content = data.get("synthesis_content", "")
        
        # Extract keywords from insights and content
        all_text = " ".join(insights) + " " + synthesis_content
        
        # Simple word frequency analysis
        words = all_text.split()
        word_freq = {}
        
        # Filter common words and count frequencies
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        
        for word in words:
            word = word.strip(".,!?;:()[]{}'" + '。！？；：（）【】"'')
            if len(word) > 1 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Convert to word cloud format
        wordcloud_data = [
            {"text": word, "value": freq}
            for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]
        ]
        
        # Create chart configuration
        chart_config = ChartConfig(
            chart_type="wordcloud",
            width=config.get("width", 800),
            height=config.get("height", 600),
            colors=config.get("colors", ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]),
            interactive=config.get("interactive", True),
            show_legend=config.get("show_legend", False),
            title="洞察词云图",
            subtitle="综合分析中的关键词分布"
        )
        
        # Generate visualization
        visualization = {
            "type": "wordcloud",
            "data": {
                "words": wordcloud_data
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": chart_config.title,
                        "subtitle": chart_config.subtitle
                    }
                }
            }
        }
        
        return {
            "success": True,
            "visualization": visualization,
            "config": asdict(chart_config),
            "metadata": {
                "word_count": len(wordcloud_data),
                "total_words": len(words),
                "unique_words": len(word_freq),
                "created_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create insight wordcloud: {e}")
        return {"success": False, "error": str(e)}
    
    async def _create_weight_distribution(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create weight distribution visualization."""
        try:
            weights = data.get("weights", {})
            weight_history = data.get("weight_history", [])
            
            if not weights:
                raise ValueError("No weight data provided")
            
            # Prepare bar chart data
            labels = list(weights.keys())
            values = list(weights.values())
            
            # Create chart configuration
            chart_config = ChartConfig(
                chart_type="bar",
                width=config.get("width", 800),
                height=config.get("height", 600),
                colors=config.get("colors", ["#1f77b4"]),
                interactive=config.get("interactive", True),
                show_legend=config.get("show_legend", True),
                title="权重分布图",
                subtitle="各维度的当前权重分配"
            )
            
            # Generate visualization
            visualization = {
                "type": "bar",
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "label": "权重值",
                        "data": values,
                        "backgroundColor": config.get("colors", ["#1f77b4"]),
                        "borderColor": config.get("colors", ["#1f77b4"]),
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": chart_config.title,
                            "subtitle": chart_config.subtitle
                        },
                        "legend": {
                            "display": chart_config.show_legend
                        }
                    },
                    "scales": {
                        "x": {"title": {"display": True, "text": "维度"}},
                        "y": {
                            "title": {"display": True, "text": "权重"},
                            "beginAtZero": True,
                            "max": 1.0
                        }
                    }
                }
            }
            
            return {
                "success": True,
                "visualization": visualization,
                "config": asdict(chart_config),
                "metadata": {
                    "dimension_count": len(labels),
                    "total_weight": sum(values),
                    "max_weight": max(values) if values else 0.0,
                    "min_weight": min(values) if values else 0.0,
                    "created_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create weight distribution: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_synthesis_dashboard(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive synthesis dashboard."""
        try:
            # Create multiple visualizations for dashboard
            dashboard_components = []
            
            # Quality overview
            if "quality_scores" in data:
                quality_viz = await self._create_perspective_radar(data, config)
                if quality_viz.get("success"):
                    dashboard_components.append({
                        "type": "quality_radar",
                        "title": "质量概览",
                        "visualization": quality_viz["visualization"],
                        "position": {"row": 0, "col": 0, "width": 6, "height": 4}
                    })
            
            # Performance timeline
            if "performance_data" in data:
                timeline_viz = await self._create_performance_timeline(data, config)
                if timeline_viz.get("success"):
                    dashboard_components.append({
                        "type": "performance_timeline",
                        "title": "性能趋势",
                        "visualization": timeline_viz["visualization"],
                        "position": {"row": 0, "col": 6, "width": 6, "height": 4}
                    })
            
            # Weight distribution
            if "weights" in data:
                weight_viz = await self._create_weight_distribution(data, config)
                if weight_viz.get("success"):
                    dashboard_components.append({
                        "type": "weight_distribution",
                        "title": "权重分配",
                        "visualization": weight_viz["visualization"],
                        "position": {"row": 4, "col": 0, "width": 6, "height": 4}
                    })
            
            # Insight wordcloud
            if "insights" in data or "synthesis_content" in data:
                wordcloud_viz = await self._create_insight_wordcloud(data, config)
                if wordcloud_viz.get("success"):
                    dashboard_components.append({
                        "type": "insight_wordcloud",
                        "title": "关键词云",
                        "visualization": wordcloud_viz["visualization"],
                        "position": {"row": 4, "col": 6, "width": 6, "height": 4}
                    })
            
            # Create dashboard configuration
            dashboard_config = {
                "title": "多视角综合分析仪表板",
                "subtitle": f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "layout": "grid",
                "components": dashboard_components,
                "refresh_interval": config.get("refresh_interval", 30000)  # 30 seconds
            }
            
            return {
                "success": True,
                "dashboard": dashboard_config,
                "metadata": {
                    "component_count": len(dashboard_components),
                    "created_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create synthesis dashboard: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_heatmap_colors(self, data: List[List[float]]) -> List[str]:
        """Generate colors for heatmap based on values."""
        colors = []
        for row in data:
            row_colors = []
            for value in row:
                if value >= 80:
                    color = "#2ca02c"  # Green
                elif value >= 60:
                    color = "#ff7f0e"  # Orange
                elif value >= 40:
                    color = "#ffbb78"  # Light orange
                else:
                    color = "#d62728"  # Red
                row_colors.append(color)
            colors.append(row_colors)
        return colors
    
    def _initialize_templates(self) -> Dict[str, Any]:
        """Initialize visualization templates."""
        return {
            "radar": {
                "suggestedMin": 0,
                "suggestedMax": 100,
                "beginAtZero": True
            },
            "line": {
                "tension": 0.1,
                "fill": False
            },
            "bar": {
                "beginAtZero": True
            },
            "heatmap": {
                "colorScale": "sequential"
            }
        }
    
    def get_available_visualizations(self) -> List[Dict[str, Any]]:
        """Get list of available visualization types."""
        return [
            {
                "type": viz_type.value,
                "name": viz_type.name.replace("_", " ").title(),
                "description": self._get_visualization_description(viz_type)
            }
            for viz_type in VisualizationType
        ]
    
    def _get_visualization_description(self, viz_type: VisualizationType) -> str:
        """Get description for visualization type."""
        descriptions = {
            VisualizationType.PERSPECTIVE_RADAR: "多视角质量雷达图，显示各视角的综合质量评估",
            VisualizationType.QUALITY_HEATMAP: "质量维度热力图，显示不同维度的质量表现分布",
            VisualizationType.CONSENSUS_TREEMAP: "共识与冲突树图，显示共识领域和冲突点的相对重要性",
            VisualizationType.PERFORMANCE_TIMELINE: "性能时间线，显示关键性能指标的历史变化趋势",
            VisualizationType.CONFLICT_NETWORK: "冲突网络图，显示视角间的冲突关系网络",
            VisualizationType.INSIGHT_WORDCLOUD: "洞察词云图，显示综合分析中的关键词分布",
            VisualizationType.WEIGHT_DISTRIBUTION: "权重分布图，显示各维度的当前权重分配",
            VisualizationType.SYNTHESIS_DASHBOARD: "综合分析仪表板，整合多个可视化组件"
        }
        return descriptions.get(viz_type, "Unknown visualization type")
    
    def get_visualization_cache(self) -> Dict[str, Any]:
        """Get visualization cache."""
        return self.visualization_cache.copy()
    
    def clear_cache(self):
        """Clear visualization cache."""
        self.visualization_cache.clear()
        logger.info("Visualization cache cleared")
    
    def export_visualization(self, visualization_id: str, format: str = "json") -> Dict[str, Any]:
        """Export visualization in specified format."""
        if visualization_id not in self.visualization_cache:
            return {"error": "Visualization not found"}
        
        visualization_data = self.visualization_cache[visualization_id]
        
        if format == "json":
            return {
                "format": "json",
                "data": visualization_data,
                "exported_at": datetime.now().isoformat()
            }
        else:
            return {"error": f"Unsupported format: {format}"}