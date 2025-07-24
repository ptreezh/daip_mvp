"""
Institutional Primitives System

This module implements the core institutional primitives system that provides
standardized workflow nodes for composing complex social institutions within
AI collaboration systems.
"""

from .base import InstitutionalPrimitive, ExecutionContext, PrimitiveInfo
from .registry import PrimitiveRegistry, get_global_registry, register_primitive

__all__ = [
    'InstitutionalPrimitive',
    'ExecutionContext', 
    'PrimitiveInfo',
    'PrimitiveRegistry',
    'get_global_registry',
    'register_primitive'
]