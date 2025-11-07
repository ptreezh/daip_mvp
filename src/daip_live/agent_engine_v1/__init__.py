"""P5 Agent Engine V1 - Refactored Architecture"""

# Version information
__version__ = "1.0.0"
__description__ = "Event-driven agent engine with decoupled services"

# Core exports
from .events.event_bus import EventBus
from .container import ServiceContainer
from .integration.service_integration import ServiceIntegrationManager
from .orchestration.agent_orchestrator import AgentOrchestrator
from .adapters.compatibility_adapter import (
    AgentEngineV1ToLegacyAdapter,
    LegacyRequest,
    LegacyResponse,
    MigrationHelper
)

__all__ = [
    "EventBus",
    "ServiceContainer",
    "ServiceIntegrationManager",
    "AgentOrchestrator",
    "AgentEngineV1ToLegacyAdapter",
    "LegacyRequest",
    "LegacyResponse",
    "MigrationHelper",
    "__version__",
    "__description__"
]