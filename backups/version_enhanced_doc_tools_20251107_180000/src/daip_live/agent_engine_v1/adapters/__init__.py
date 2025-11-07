"""
Compatibility Adapters Module

This module provides compatibility adapters that bridge the new agent_engine_v1 architecture
with existing legacy systems, ensuring smooth migration and backward compatibility.
"""

from .compatibility_adapter import (
    CompatibilityAdapter,
    AgentEngineV1ToLegacyAdapter,
    LegacyEventAdapter,
    MigrationHelper,
    LegacyRequest,
    LegacyResponse
)

__all__ = [
    "CompatibilityAdapter",
    "AgentEngineV1ToLegacyAdapter",
    "LegacyEventAdapter",
    "MigrationHelper",
    "LegacyRequest",
    "LegacyResponse"
]