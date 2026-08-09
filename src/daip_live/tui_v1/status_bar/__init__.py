"""
Status Bar Module for newP6 TUI

Provides real-time status bar functionality with widgets and auto-updates.
"""

from .connection_widget import ConnectionStatusWidget

# Import specific widgets
from .model_widget import ModelStatusWidget
from .resource_widget import SystemResourceWidget
from .session_widget import SessionWidget
from .status_bar import StatusBar
from .status_updater import StatusUpdater
from .status_widget import StatusWidget

# Export main classes
__all__ = [
    "StatusBar",
    "StatusWidget",
    "StatusUpdater",
    "ModelStatusWidget",
    "SessionWidget",
    "ConnectionStatusWidget",
    "SystemResourceWidget",
]
