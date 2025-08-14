"""Task Context Optimizer module for the Virtual Role Chat System.

This module implements task-focused context optimization that is integrated
at the lowest level of LLM interactions, automatically optimizing context
preparation for all AI communications.
"""

from .dynamic_adapter import (
    AdaptationAction,
    AdaptationEvent,
    AdaptationTrigger,
    CoherenceMonitor,
    DynamicContextAdapter,
    TaskBoundaryDetector,
)
from .models import ContextElement, OptimizedContext, TaskDetectionResult, TaskRequirement
from .optimizer import TaskContextOptimizer
from .strategies import (
    ContextBlendingStrategy,
    ContextCompressionStrategy,
    ContextPrioritizationStrategy,
    TaskDetectionStrategy,
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
