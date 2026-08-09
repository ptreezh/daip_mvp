"""Health check endpoints for observability.

This module provides health check functionality for monitoring system status.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class HealthStatus(Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a single component."""

    name: str
    status: HealthStatus
    message: str
    details: Optional[dict] = None


@dataclass
class HealthCheck:
    """Overall health check result."""

    status: HealthStatus
    components: dict[str, ComponentHealth] = field(default_factory=dict)


class HealthCheckRegistry:
    """Registry for health check functions."""

    def __init__(self):
        self.checks: dict[str, Callable[[], ComponentHealth]] = {}

    def register(self, name: str, check_func: Callable[[], ComponentHealth]) -> None:
        """Register a health check function.

        Args:
            name: Component name
            check_func: Function that returns ComponentHealth
        """
        self.checks[name] = check_func

    def unregister(self, name: str) -> None:
        """Unregister a health check function.

        Args:
            name: Component name to remove
        """
        self.checks.pop(name, None)

    def execute(self) -> HealthCheck:
        """Execute all registered health checks.

        Returns:
            HealthCheck with overall status and component details
        """
        components = {}
        healthy_count = 0
        unhealthy_count = 0

        for name, check_func in self.checks.items():
            try:
                component = check_func()
                components[name] = component
                if component.status == HealthStatus.HEALTHY:
                    healthy_count += 1
                else:
                    unhealthy_count += 1
            except Exception as e:
                components[name] = ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {e}",
                )
                unhealthy_count += 1

        # Determine overall status
        if unhealthy_count == 0:
            overall_status = HealthStatus.HEALTHY
        elif healthy_count == 0:
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED

        return HealthCheck(status=overall_status, components=components)
