"""Observability module for system monitoring.

This module provides:
- JSON structured logging
- Health check endpoints
- Graceful shutdown handling
"""

from daip_live.observability.health import (
    ComponentHealth,
    HealthCheck,
    HealthCheckRegistry,
    HealthStatus,
)
from daip_live.observability.logging import (
    JsonFormatter,
    LogLevel,
    StructuredLogger,
    get_logger,
)
from daip_live.observability.shutdown import (
    GracefulShutdown,
    ShutdownHandler,
    ShutdownSignal,
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
