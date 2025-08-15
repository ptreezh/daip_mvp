"""Data models for the Task Context Optimizer.

This module defines the data models used by the task context optimization system,
including task requirements, context elements, and optimization results.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Enumeration of task types that can be detected."""
    INFORMATION_RETRIEVAL = "information_retrieval"
    EXPLANATION = "explanation"
    PROBLEM_SOLVING = "problem_solving"
    DECISION_SUPPORT = "decision_support"
    CREATIVE_IDEATION = "creative_ideation"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    EVALUATION = "evaluation"
    PLANNING = "planning"
    UNKNOWN = "unknown"


class RequirementType(str, Enum):
    """Types of requirements for task execution."""
    KNOWLEDGE = "knowledge"
    INSTRUCTION = "instruction"
    CONTEXT = "context"
    EXAMPLE = "example"
    CONSTRAINT = "constraint"
    GOAL = "goal"


class ElementType(str, Enum):
    """Types of context elements."""
    INSTRUCTION = "instruction"
    KNOWLEDGE = "knowledge"
    CONVERSATION = "conversation"
    EXAMPLE = "example"
    CONSTRAINT = "constraint"
    BACKGROUND = "background"
    METADATA = "metadata"


class TaskRequirement(BaseModel):
    """Representation of a requirement for task execution.
    """
    requirement_type: RequirementType
    content: str
    importance: float = Field(ge=0.0, le=1.0, description="Importance level (0.0-1.0)")
    domain: Optional[str] = None
    specificity: float = Field(ge=0.0, le=1.0, default=0.5, description="How specific this requirement is")
    urgency: float = Field(ge=0.0, le=1.0, default=0.5, description="How urgent this requirement is")
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContextElement(BaseModel):
    """Individual element within a context.
    """
    id: str
    content: str
    element_type: ElementType
    relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance to current task")
    importance: float = Field(ge=0.0, le=1.0, description="General importance")
    token_count: int = Field(ge=0, description="Estimated token count")
    source: str = Field(description="Source of this context element")
    timestamp: datetime = Field(default_factory=datetime.now)
    dependencies: list[str] = Field(default_factory=list, description="IDs of elements this depends on")
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    def get_priority_score(self) -> float:
        """Calculate priority score based on relevance, importance, and other factors.
        
        Returns:
            Priority score (0.0-1.0)
        """
        # Weighted combination of relevance and importance
        base_score = (self.relevance_score * 0.6) + (self.importance * 0.4)
        
        # Adjust based on element type
        type_weights = {
            ElementType.INSTRUCTION: 1.2,
            ElementType.CONSTRAINT: 1.1,
            ElementType.KNOWLEDGE: 1.0,
            ElementType.EXAMPLE: 0.9,
            ElementType.CONVERSATION: 0.8,
            ElementType.BACKGROUND: 0.7,
            ElementType.METADATA: 0.5
        }
        
        type_weight = type_weights.get(self.element_type, 0.8)
        return min(base_score * type_weight, 1.0)


class TaskDetectionResult(BaseModel):
    """Result of task detection analysis.
    """
    task_type: TaskType
    confidence: float = Field(ge=0.0, le=1.0)
    task_description: str
    detected_goals: list[str] = Field(default_factory=list)
    detected_constraints: list[str] = Field(default_factory=list)
    domain: Optional[str] = None
    complexity: float = Field(ge=0.0, le=1.0, default=0.5)
    urgency: float = Field(ge=0.0, le=1.0, default=0.5)
    requirements: list[TaskRequirement] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OptimizedContext(BaseModel):
    """Result of context optimization.
    """
    elements: list[ContextElement]
    total_tokens: int
    task_focus: str
    optimization_metrics: dict[str, float] = Field(default_factory=dict)
    excluded_elements: list[ContextElement] = Field(default_factory=list)
    compression_ratio: float = Field(ge=0.0, le=1.0, default=1.0)
    coherence_score: float = Field(ge=0.0, le=1.0, default=1.0)
    completeness_score: float = Field(ge=0.0, le=1.0, default=1.0)
    optimization_strategy: str = "default"
    processing_time_ms: float = 0.0
    
    def get_context_string(self) -> str:
        """Generate the optimized context as a string.
        
        Returns:
            Formatted context string
        """
        # Sort elements by priority
        sorted_elements = sorted(self.elements, key=lambda e: e.get_priority_score(), reverse=True)
        
        # Group by type for better organization
        grouped_elements = {}
        for element in sorted_elements:
            element_type = element.element_type
            if element_type not in grouped_elements:
                grouped_elements[element_type] = []
            grouped_elements[element_type].append(element)
        
        # Build context string
        context_parts = []
        
        # Add task focus if available
        if self.task_focus:
            context_parts.append(f"# Task Focus: {self.task_focus}\n")
        
        # Add elements by type in priority order
        type_order = [
            ElementType.INSTRUCTION,
            ElementType.CONSTRAINT,
            ElementType.KNOWLEDGE,
            ElementType.EXAMPLE,
            ElementType.CONVERSATION,
            ElementType.BACKGROUND,
            ElementType.METADATA
        ]
        
        for element_type in type_order:
            if element_type in grouped_elements:
                elements = grouped_elements[element_type]
                if elements:
                    context_parts.append(f"\n## {element_type.value.title()}:")
                    for element in elements:
                        context_parts.append(f"- {element.content}")
        
        return "\n".join(context_parts)


class ContextOptimizationConfig(BaseModel):
    """Configuration for context optimization.
    """
    max_tokens: int = 4000
    min_relevance_threshold: float = Field(ge=0.0, le=1.0, default=0.3)
    compression_target: float = Field(ge=0.0, le=1.0, default=0.8)
    preserve_dependencies: bool = True
    maintain_coherence: bool = True
    enable_smart_truncation: bool = True
    prioritize_recent: bool = True
    recency_weight: float = Field(ge=0.0, le=1.0, default=0.2)
    diversity_weight: float = Field(ge=0.0, le=1.0, default=0.1)
    
    # Task-specific settings
    task_specific_weights: dict[TaskType, dict[str, float]] = Field(default_factory=dict)
    
    # Element type priorities
    element_type_priorities: dict[ElementType, float] = Field(
        default_factory=lambda: {
            ElementType.INSTRUCTION: 1.0,
            ElementType.CONSTRAINT: 0.9,
            ElementType.KNOWLEDGE: 0.8,
            ElementType.EXAMPLE: 0.7,
            ElementType.CONVERSATION: 0.6,
            ElementType.BACKGROUND: 0.5,
            ElementType.METADATA: 0.3
        }
    )


class ContextAnalysisResult(BaseModel):
    """Result of context analysis before optimization.
    """
    total_elements: int
    total_tokens: int
    element_type_distribution: dict[ElementType, int]
    average_relevance: float
    average_importance: float
    complexity_score: float = Field(ge=0.0, le=1.0)
    coherence_score: float = Field(ge=0.0, le=1.0)
    redundancy_score: float = Field(ge=0.0, le=1.0)
    coverage_gaps: list[str] = Field(default_factory=list)
    optimization_recommendations: list[str] = Field(default_factory=list)