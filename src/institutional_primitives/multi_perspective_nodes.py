# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 13:00:00
@Author  : DAIP-LIVE Team
@File    : multi_perspective_nodes.py
@Description:
    Legacy import file for Multi-perspective Synthesis Workflow nodes.
    This file now imports from the modularized multi_perspective package.
"""

# Import all components from the modularized package
from .multi_perspective import (
    SubProblem,
    ExpertViewpoint,
    ViewpointCollection,
    SynthesisQuality,
    SynthesisResult,
    TaskDecompositionNode,
    ParallelExplorationNode,
    ViewpointCollectionNode,
    EnhancedSynthesisNode,
    IterativeRefinementNode
)

# For backward compatibility, also export the original ViewpointSynthesisNode name
ViewpointSynthesisNode = EnhancedSynthesisNode

__all__ = [
    "SubProblem",
    "ExpertViewpoint",
    "ViewpointCollection", 
    "SynthesisQuality",
    "SynthesisResult",
    "TaskDecompositionNode",
    "ParallelExplorationNode",
    "ViewpointCollectionNode",
    "EnhancedSynthesisNode",
    "ViewpointSynthesisNode",  # Backward compatibility
    "IterativeRefinementNode"
]