"""
Personal Assistant System for newP6 TUI

This module provides comprehensive personal assistant capabilities including:
- Assistant profile management and personality customization
- Conversation management with context awareness
- Task management and execution tracking
- Memory management for personalized interactions
- Skill management for specialized capabilities
"""

from .assistant_profile import AssistantProfile
from .assistant_skills import SkillManager, SkillType
from .conversation_manager import ConversationManager
from .memory_manager import MemoryManager
from .personal_assistant import PersonalAssistant
from .task_manager import TaskManager, TaskStatus

__all__ = [
    "PersonalAssistant",
    "AssistantProfile",
    "ConversationManager",
    "TaskManager",
    "TaskStatus",
    "MemoryManager",
    "SkillManager",
    "SkillType",
]
