"""Logging infrastructure test for Phase 0-3."""
import os
import logging
from pathlib import Path


def test_log_directory_created():
    """Test that log directory is created."""
    from daip_live.container import Container

    # Initialize container should set up logging
    container = Container()

    # Verify log directory exists
    log_dir = Path("data/logs")
    assert log_dir.exists() or Path("../data/logs").exists() or Path("../../data/logs").exists()


def test_log_handlers_configured():
    """Test that root logger has handlers configured."""
    # Check if handlers are configured
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0, "Root logger should have handlers"


def test_rotating_file_handler():
    """Test that RotatingFileHandler is configured."""
    from logging.handlers import RotatingFileHandler

    root_logger = logging.getLogger()
    has_rotating_handler = any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers)
    assert has_rotating_handler, "Should have RotatingFileHandler"
