"""Observability module for system monitoring.

This module provides:
- JSON structured logging
- Health check endpoints
- Graceful shutdown handling
"""

from daip_live.observability.logging import (
    JsonFormatter,
    StructuredLogger,
    get_logger,
    LogLevel
)
from daip_live.observability.health import (
    HealthCheck,
    HealthStatus,
    ComponentHealth,
    HealthCheckRegistry
)
from daip_live.observability.shutdown import (
    GracefulShutdown,
    ShutdownHandler,
    ShutdownSignal
)

__all__ = [
    # Logging
    "JsonFormatter",
    "StructuredLogger",
    "get_logger",
    "LogLevel",
    # Health
    "HealthCheck",
    "HealthStatus",
    "ComponentHealth",
    "HealthCheckRegistry",
    # Shutdown
    "GracefulShutdown",
    "ShutdownHandler",
    "ShutdownSignal",
]
