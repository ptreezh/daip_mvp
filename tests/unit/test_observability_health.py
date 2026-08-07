"""Tests for observability health check module (TDD - RED phase)."""

import pytest
from daip_live.observability.health import (
    HealthCheck,
    HealthStatus,
    ComponentHealth,
    HealthCheckRegistry
)


def test_health_status_enum():
    """Test HealthStatus enum values."""
    assert HealthStatus.HEALTHY.value == "healthy"
    assert HealthStatus.DEGRADED.value == "degraded"
    assert HealthStatus.UNHEALTHY.value == "unhealthy"


def test_component_health_creation():
    """Test creating a component health check."""
    component = ComponentHealth(
        name="database",
        status=HealthStatus.HEALTHY,
        message="Connected"
    )
    assert component.name == "database"
    assert component.status == HealthStatus.HEALTHY
    assert component.message == "Connected"


def test_health_check_creation():
    """Test creating a health check."""
    health = HealthCheck(
        status=HealthStatus.HEALTHY,
        components={}
    )
    assert health.status == HealthStatus.HEALTHY
    assert health.components == {}


def test_health_check_with_components():
    """Test health check with component details."""
    health = HealthCheck(
        status=HealthStatus.HEALTHY,
        components={
            "database": ComponentHealth(
                name="database",
                status=HealthStatus.HEALTHY,
                message="OK"
            )
        }
    )
    assert health.status == HealthStatus.HEALTHY
    assert "database" in health.components


def test_health_check_registry_creation():
    """Test creating a health check registry."""
    registry = HealthCheckRegistry()
    assert registry is not None


def test_health_check_registry_register():
    """Test registering a health check function."""
    registry = HealthCheckRegistry()

    def dummy_check():
        return ComponentHealth("test", HealthStatus.HEALTHY, "OK")

    registry.register("test", dummy_check)
    assert "test" in registry.checks


def test_health_check_registry_execute():
    """Test executing all registered health checks."""
    registry = HealthCheckRegistry()

    def dummy_check():
        return ComponentHealth("test", HealthStatus.HEALTHY, "OK")

    registry.register("test", dummy_check)
    health = registry.execute()
    assert health.status == HealthStatus.HEALTHY
    assert "test" in health.components


def test_health_check_registry_unhealthy_when_all_unhealthy():
    """Test registry is unhealthy when all checks fail."""
    registry = HealthCheckRegistry()

    def failing_check():
        return ComponentHealth("test", HealthStatus.UNHEALTHY, "Failed")

    registry.register("test", failing_check)
    health = registry.execute()
    assert health.status == HealthStatus.UNHEALTHY
