"""
Base classes and interfaces for the hierarchical architecture.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class AnalysisResult:
    """Standard result format for Subagent analyses."""
    content: str
    metadata: Dict[str, Any]
    confidence: float = 1.0
    subagent_name: str = ""
    

@dataclass
class SubagentCapabilities:
    """Describes the capabilities of a Subagent."""
    name: str
    description: str
    supported_domains: List[str]
    required_skills: List[str]
    version: str = "1.0"


class TheorySubagent(ABC):
    """Abstract base class for all theory-based Subagents."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.is_initialized = False
    
    @abstractmethod
    def analyze(self, data: str, context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        Perform analysis on the provided data.
        
        Args:
            data: The input data to analyze
            context: Additional context for the analysis
            
        Returns:
            AnalysisResult containing the analysis output
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> SubagentCapabilities:
        """
        Get the capabilities of this Subagent.
        
        Returns:
            SubagentCapabilities describing what this Subagent can do
        """
        pass
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the Subagent with specific settings.
        
        Args:
            config: Configuration dictionary
        """
        self.config.update(config)
    
    def initialize(self) -> None:
        """
        Initialize the Subagent. Override this method for custom initialization.
        """
        self.is_initialized = True
    
    def cleanup(self) -> None:
        """
        Cleanup resources. Override this method for custom cleanup.
        """
        pass