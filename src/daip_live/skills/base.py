"""
Skill interface and base classes for the Skills system.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


@dataclass
class SkillInput:
    """Standard input format for skills."""
    data: str
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillOutput:
    """Standard output format for skills."""
    result: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    execution_time: float = 0.0


@dataclass
class SkillMetadata:
    """Metadata describing a skill."""
    name: str
    description: str
    version: str
    author: str
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class Skill(ABC):
    """Abstract base class for all skills."""
    
    def __init__(self, metadata: SkillMetadata):
        self.metadata = metadata
        self.is_enabled = True
    
    @abstractmethod
    def execute(self, input: SkillInput) -> SkillOutput:
        """
        Execute the skill with the provided input.
        
        Args:
            input: SkillInput containing the data and context
            
        Returns:
            SkillOutput containing the result
        """
        pass
    
    def validate_input(self, input: SkillInput) -> bool:
        """
        Validate the input for this skill.
        
        Args:
            input: SkillInput to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        return True
    
    def enable(self) -> None:
        """Enable the skill."""
        self.is_enabled = True
    
    def disable(self) -> None:
        """Disable the skill."""
        self.is_enabled = False