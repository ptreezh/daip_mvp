"""
Cognitive Agent module for the Virtual Role Chat System.

This module implements the cognitive agent framework that enables true cognitive
independence for virtual roles, allowing them to function as autonomous cognitive
agents rather than mere role-playing simulations.
"""

from .agent import CognitiveAgent
from .reasoning import ReasoningFramework
from .belief import BeliefSystem
from .epistemology import Epistemology
from .metacognition import MetaCognition
from .memory import AgentMemory

__all__ = [
    'CognitiveAgent',
    'ReasoningFramework',
    'BeliefSystem',
    'Epistemology',
    'MetaCognition',
    'AgentMemory',
]