"""
Semantic Structured Knowledge Graph (SSKG) module.

This module implements a unified knowledge representation system that serves
as the central memory interface for all components in the virtual role chat system.
"""

from .models import (
    KnowledgeFact,
    KnowledgeRelation,
    KnowledgeQuery,
    ConflictResolution,
    Memory,
    MemoryQuery,
    WikiPage
)
from .manager import SSKGManager
from .storage import SSKGStorage
from .adapters import (
    RoleMemoryAdapter,
    WikiAdapter,
    SessionAdapter,
    ProjectAdapter,
    MemoryBankAdapter
)

__all__ = [
    'KnowledgeFact',
    'KnowledgeRelation', 
    'KnowledgeQuery',
    'ConflictResolution',
    'Memory',
    'MemoryQuery',
    'WikiPage',
    'SSKGManager',
    'SSKGStorage',
    'RoleMemoryAdapter',
    'WikiAdapter',
    'SessionAdapter',
    'ProjectAdapter',
    'MemoryBankAdapter',
]