"""Institutional Primitives System.

This package implements the Institutional Primitives System, which provides
standardized workflow nodes that encapsulate atomic capabilities and serve
as the fundamental building blocks for complex social institutions within
AI collaboration systems.
"""

from .base import (
    ExecutionContext,
    ExecutionStep,
    ExecutionTrace,
    InstitutionalPrimitive,
    PrimitiveInfo,
    ValidationResult,
)
from .parallel_execution import ParallelExecutionGroup, ParallelExecutionManager
from .registry import PrimitiveRegistry
from .workflow_engine import (
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowEngine,
    WorkflowNode,
    WorkflowResult,
    WorkflowStatus,
)

__all__ = [
    # Base classes
    "ExecutionContext",
    "ExecutionStep",
    "ExecutionTrace",
    "InstitutionalPrimitive",
    "PrimitiveInfo",
    "ValidationResult",
    
    # Registry
    "PrimitiveRegistry",
    
    # Workflow Engine
    "WorkflowDefinition",
    "WorkflowEdge",
    "WorkflowEngine",
    "WorkflowNode",
    "WorkflowResult",
    "WorkflowStatus",
    
    # Parallel Execution
    "ParallelExecutionGroup",
    "ParallelExecutionManager"
]