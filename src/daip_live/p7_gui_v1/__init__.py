"""
DAIP-LIVE P7 GUI Package

This package implements the newP7 GUI specification using MVVM architecture
and CustomTkinter for cross-platform compatibility. It integrates with the
existing FastAPI backend services.
"""

__version__ = "1.0.0"
__author__ = "DAIP-LIVE Development Team"

# Do not import main here to avoid circular dependencies
# Main imports views which don't exist yet
# from .main import P7GUIApp

__all__ = []  # Empty for now to avoid import issues