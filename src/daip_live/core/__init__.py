"""
Core module for DAIP-LIVE system.
Provides foundational interfaces, models, and utilities.

This module is compilation-ready and has stable interfaces.
"""

from .models import *
from .interfaces import *
from .exceptions import *

__version__ = "0.2.0"
__all__ = [
    # Models
    "AgentState", "Session", "Role", "Tool", "Permission",
    "Debate", "Knowledge", "Memory",

    # Interfaces
    "ModelProviderInterface", "KnowledgeManagerInterface",
    "RoleManagerInterface", "ToolManagerInterface",
    "AgentExecutorInterface", "MemoryInterface",

    # Exceptions
    "DAIPLiveException", "ConfigurationError",
    "PermissionDenied", "ModelProviderError"
]