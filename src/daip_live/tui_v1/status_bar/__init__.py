"""
Status Bar Module for newP6 TUI

Provides real-time status bar functionality with widgets and auto-updates.
"""

from .status_bar import StatusBar
from .status_widget import StatusWidget
from .status_updater import StatusUpdater

# Import specific widgets
from .model_widget import ModelStatusWidget
from .session_widget import SessionWidget
from .connection_widget import ConnectionStatusWidget
from .resource_widget import SystemResourceWidget

# Export main classes
__all__ = [
    "StatusBar",
    "StatusWidget",
    "StatusUpdater",
    "ModelStatusWidget",
    "SessionWidget",
    "ConnectionStatusWidget",
    "SystemResourceWidget"
]