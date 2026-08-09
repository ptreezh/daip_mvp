"""
Services Module for newP6 TUI

Provides service adapters and container for DAIP service integration.
"""

from .base import BaseServiceAdapter
from .container import ServiceContainer
from .knowledge_service import KnowledgeServiceAdapter
from .model_service import ModelServiceAdapter
from .session_service import SessionServiceAdapter

# Export main classes
__all__ = [
    "BaseServiceAdapter",
    "ServiceContainer",
    "SessionServiceAdapter",
    "KnowledgeServiceAdapter",
    "ModelServiceAdapter",
]
