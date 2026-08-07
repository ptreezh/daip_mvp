"""Tests for observability shutdown module (TDD - RED phase)."""

import pytest
from daip_live.observability.shutdown import (
    GracefulShutdown,
    ShutdownHandler,
    ShutdownSignal
)


def test_shutdown_signal_enum():
    """Test ShutdownSignal enum values."""
    assert ShutdownSignal.SIGINT.value == "SIGINT"
    assert ShutdownSignal.SIGTERM.value == "SIGTERM"


def test_graceful_shutdown_creation():
    """Test creating a GracefulShutdown instance."""
    shutdown = GracefulShutdown(timeout=10)
    assert shutdown.timeout == 10
    assert shutdown.is_shutting_down is False


def test_graceful_shutdown_register_callback():
    """Test registering a shutdown callback."""
    shutdown = GracefulShutdown(timeout=10)
    called = False

    def callback():
        nonlocal called
        called = True

    shutdown.register(callback)
    assert len(shutdown.callbacks) == 1


def test_graceful_shutdown_trigger():
    """Test triggering shutdown."""
    shutdown = GracefulShutdown(timeout=10)
    called = False

    def callback():
        nonlocal called
        called = True

    shutdown.register(callback)
    shutdown.trigger()
    assert shutdown.is_shutting_down is True
    assert called is True


def test_graceful_shutdown_multiple_callbacks():
    """Test that multiple callbacks are executed."""
    shutdown = GracefulShutdown(timeout=10)
    call_order = []

    def callback1():
        call_order.append(1)

    def callback2():
        call_order.append(2)

    shutdown.register(callback1)
    shutdown.register(callback2)
    shutdown.trigger()
    assert call_order == [1, 2]


def test_shutdown_handler_creation():
    """Test creating a ShutdownHandler."""
    handler = ShutdownHandler(timeout=5)
    assert handler is not None
    assert handler.shutdown.timeout == 5
