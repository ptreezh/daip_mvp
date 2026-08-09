"""
Core module for DAIP-LIVE system.
Provides foundational interfaces, models, and utilities.

This module is compilation-ready and has stable interfaces.
"""
# ruff: noqa: F403, F405  # 核心模块标准 re-export 模式（__all__ 显式声明）

from .exceptions import *
from .interfaces import *
from .models import *

__version__ = "0.2.0"
__all__ = [
    # Models
    "AgentState",
    "Session",
    "Role",
    "Tool",
    "Permission",
    "Debate",
    "Knowledge",
    "Memory",
    # Interfaces
    "ModelProviderInterface",
    "KnowledgeManagerInterface",
    "RoleManagerInterface",
    "ToolManagerInterface",
    "AgentExecutorInterface",
    "MemoryInterface",
    # Exceptions
    "DAIPError",
    "ModelError",
    "ConfigurationError",
    "PermissionDenied",
    "ValidationError",
    "ToolError",
    "ErrorHandler",
    "ErrorContext",
    "get_error_handler",
    "handle_error",
]
