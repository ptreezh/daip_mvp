"""Semantic Structured Knowledge Graph (SSKG) module.

This module implements a unified knowledge representation system that serves
as the central memory interface for all components in the virtual role chat system.
"""

from .manager import SSKGManager
from .models import ConflictResolution, KnowledgeFact, KnowledgeQuery, KnowledgeRelation, Memory, MemoryQuery, WikiPage
from .storage import SSKGStorage

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
]
