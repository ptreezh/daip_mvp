"""
Personal Assistant System for newP6 TUI

This module provides comprehensive personal assistant capabilities including:
- Assistant profile management and personality customization
- Conversation management with context awareness
- Task management and execution tracking
- Memory management for personalized interactions
- Skill management for specialized capabilities
"""

from .personal_assistant import PersonalAssistant
from .assistant_profile import AssistantProfile
from .conversation_manager import ConversationManager
from .task_manager import TaskManager, TaskStatus
from .memory_manager import MemoryManager
from .assistant_skills import SkillManager, SkillType

__all__ = [
    "PersonalAssistant",
    "AssistantProfile",
    "ConversationManager",
    "TaskManager",
    "TaskStatus",
    "MemoryManager",
    "SkillManager",
    "SkillType"
]