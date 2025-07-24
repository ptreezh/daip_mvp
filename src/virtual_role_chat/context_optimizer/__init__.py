"""
Task Context Optimizer module for the Virtual Role Chat System.

This module implements task-focused context optimization that is integrated
at the lowest level of LLM interactions, automatically optimizing context
preparation for all AI communications.
"""

from .optimizer import TaskContextOptimizer
from .models import (
    TaskRequirement,
    ContextElement,
    OptimizedContext,
    TaskDetectionResult
)
from .strategies import (
    TaskDetectionStrategy,
    ContextPrioritizationStrategy,
    ContextCompressionStrategy,
    ContextBlendingStrategy
)
from .dynamic_adapter import (
    DynamicContextAdapter,
    TaskBoundaryDetector,
    CoherenceMonitor,
    AdaptationTrigger,
    AdaptationAction,
    AdaptationEvent
)

__all__ = [
    'TaskContextOptimizer',
    'TaskRequirement',
    'ContextElement', 
    'OptimizedContext',
    'TaskDetectionResult',
    'TaskDetectionStrategy',
    'ContextPrioritizationStrategy',
    'ContextCompressionStrategy',
    'ContextBlendingStrategy',
    'DynamicContextAdapter',
    'TaskBoundaryDetector',
    'CoherenceMonitor',
    'AdaptationTrigger',
    'AdaptationAction',
    'AdaptationEvent',
]