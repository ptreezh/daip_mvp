"""Main visualizer class for multi-perspective synthesis.
"""

import logging
from typing import Any

from .generators import (
    create_conflict_network,
    create_consensus_treemap,
    create_insight_wordcloud,
    create_performance_timeline,
    create_perspective_radar,
    create_quality_heatmap,
    create_synthesis_dashboard,
    create_weight_distribution,
)
from .models import VisualizationType
from .utils import initialize_templates

logger = logging.getLogger(__name__)


class MultiPerspectiveVisualizer:
    """多视角可视化器 - Advanced visualization for multi-perspective synthesis.
    
    Creates interactive visualizations for synthesis results, quality metrics,
    performance trends, and perspective analysis.
    """
    
    def __init__(self, config: dict[str, Any] = None):
        """Initialize the Multi-Perspective Visualizer.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or {}
        
        # Default visualization settings
        self.default_settings = {
            "width": 800,
            "height": 600,
            "colors": [
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
            ],
            "interactive": True,
            "show_legend": True,
            "font_size": 12,
            "animation_duration": 1000
        }
        
        # Merge with provided config
        self.settings = {**self.default_settings, **self.config}
        
        # Visualization templates
        self.templates = initialize_templates()
        
        # Cache for generated visualizations
        self.visualization_cache = {}
        
    async def create_visualization(
        self,
        visualization_type: VisualizationType,
        data: dict[str, Any],
        config: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Create a visualization of the specified type.
        
        Args:
            visualization_type: Type of visualization to create
            data: Data to visualize
            config: Configuration overrides
            
        Returns:
            Visualization result
        """
        try:
            logger.info(f"Creating {visualization_type.value} visualization")
            
            # Merge configuration
            viz_config = {**self.settings, **(config or {})}
            
            # Select visualization method
            viz_methods = {
                VisualizationType.PERSPECTIVE_RADAR: create_perspective_radar,
                VisualizationType.QUALITY_HEATMAP: create_quality_heatmap,
                VisualizationType.CONSENSUS_TREEMAP: create_consensus_treemap,
                VisualizationType.PERFORMANCE_TIMELINE: create_performance_timeline,
                VisualizationType.CONFLICT_NETWORK: create_conflict_network,
                VisualizationType.INSIGHT_WORDCLOUD: create_insight_wordcloud,
                VisualizationType.WEIGHT_DISTRIBUTION: create_weight_distribution,
                VisualizationType.SYNTHESIS_DASHBOARD: create_synthesis_dashboard
            }
            
            if visualization_type in viz_methods:
                result = await viz_methods[visualization_type](data, viz_config)
            else:
                raise ValueError(f"Unknown visualization type: {visualization_type}")
            
            # Cache result
            cache_key = f"{visualization_type.value}_{hash(json.dumps(data, sort_keys=True))}"
            self.visualization_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create visualization: {e}")
            return {"success": False, "error": str(e)}
    
    def get_available_visualizations(self) -> list[dict[str, Any]]:
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
    
    def get_visualization_cache(self) -> dict[str, Any]:
        """Get visualization cache."""
        return self.visualization_cache.copy()
    
    def clear_cache(self):
        """Clear visualization cache."""
        self.visualization_cache.clear()
        logger.info("Visualization cache cleared")
    
    def export_visualization(self, visualization_id: str, format: str = "json") -> dict[str, Any]:
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