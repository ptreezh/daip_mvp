"""
Debate System Module for newP6 TUI

Provides multi-AI role debate functionality with structured argument management.
"""

from .argument import Argument
from .debate import Debate
from .debate_manager import DebateManager
from .participant import DebateParticipant
from .roles import DebateRole, RoleType
from .round import DebateRound

# Export main classes
__all__ = [
    "Debate",
    "DebateManager",
    "DebateParticipant",
    "Argument",
    "DebateRound",
    "DebateRole",
    "RoleType",
]
