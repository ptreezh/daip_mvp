"""
模块化辩论系统
避免复杂依赖，提供简化的辩论功能
"""

from .core import DebateCore
from .events import DebateEvents
from .simple_debate import SimpleDebateEngine

__version__ = "1.0.0"
__all__ = [
    "DebateCore",
    "DebateEventTypes",
    "SimpleDebateEngine"
]