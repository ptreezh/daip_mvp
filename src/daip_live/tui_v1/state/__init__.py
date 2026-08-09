"""
State Management System for newP6 Architecture

This module provides the state management system as specified in the newP6
architecture requirements. The state management system provides:

- Reactive state updates
- Subscription mechanism for state changes
- State history and rollback
- Performance-optimized batch updates
"""

from .manager import TUIStateManager

__all__ = ["TUIStateManager"]
