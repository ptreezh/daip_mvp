"""Unified Storage Adapters for the Semantic Structured Knowledge Graph (SSKG).

This package implements domain-specific adapters that map different memory types
to SSKG representations while maintaining semantic integrity and consistent access patterns.
"""

from .base import StorageAdapter, StorageAdapterManager
from .role_adapter import RoleMemoryAdapter
from .session_adapter import SessionAdapter
from .wiki_adapter import WikiAdapter

__all__ = [
    'StorageAdapter',
    'StorageAdapterManager',
    'RoleMemoryAdapter',
    'WikiAdapter',
    'SessionAdapter',
]
