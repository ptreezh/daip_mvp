"""Data models for the perspective visualizer.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class VisualizationType(Enum):
    """Types of visualizations available."""
    PERSPECTIVE_RADAR = "perspective_radar"
    QUALITY_HEATMAP = "quality_heatmap"
    CONSENSUS_TREEMAP = "consensus_treemap"
    PERFORMANCE_TIMELINE = "performance_timeline"
    CONFLICT_NETWORK = "conflict_network"
    INSIGHT_WORDCLOUD = "insight_wordcloud"
    WEIGHT_DISTRIBUTION = "weight_distribution"
    SYNTHESIS_DASHBOARD = "synthesis_dashboard"


@dataclass
class VisualizationData:
    """Data structure for visualization."""
    type: VisualizationType
    title: str
    data: dict[str, Any]
    metadata: dict[str, Any]
    config: dict[str, Any]


@dataclass
class ChartConfig:
    """Configuration for chart rendering."""
    chart_type: str
    width: int
    height: int
    colors: list[str]
    interactive: bool
    show_legend: bool
    title: str
    subtitle: str = ""