"""Utility functions for the perspective visualizer.
"""

from typing import Any


def generate_heatmap_colors(data: list[list[float]]) -> list[str]:
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


def initialize_templates() -> dict[str, Any]:
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