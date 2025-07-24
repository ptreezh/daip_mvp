# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 10:00:00
@Author  : DAIP-LIVE Team
@File    : __init__.py
@Description:
    Package initialization for workflow implementations.
"""

from .critical_review_workflow import CriticalReviewWorkflow
from .multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow

__all__ = ["CriticalReviewWorkflow", "MultiPerspectiveSynthesisWorkflow"]