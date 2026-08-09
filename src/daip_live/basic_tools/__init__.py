"""Basic tools package: academic paper search and download utilities."""

from .core import (
    DependencyError,
    PermissionError,
    ToolError,
    ValidationError,
    download_paper,
    fetch_paper,
    markdown_to_md,
    search_academic_papers,
)

__version__ = "1.0.0"
__author__ = "DAIP-LIVE Team"

__all__ = [
    "search_academic_papers",
    "download_paper",
    "markdown_to_md",
    "fetch_paper",
    "ToolError",
    "PermissionError",
    "ValidationError",
    "DependencyError",
]
