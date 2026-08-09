"""
P6 TUI Componentized Architecture v1

This package contains the componentized version of the DAIP-LIVE TUI system.
The implementation follows the newP6 specification requirements.

Architecture:
- components: Reusable UI components
- state: State management system
- theme: Theme management system
- events: Event-driven communication system
"""

__version__ = "1.0.0"
__author__ = "DAIP-LIVE Frontend Architecture Team"

from .main import DAIP_TUI_V1

__all__ = ["DAIP_TUI_V1"]
