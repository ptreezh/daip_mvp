"""@Time    : 2025-07-24 16:30:00
@Author  : DAIP-LIVE Team
@File    : models.py
@Description:
    Data models for Multi-perspective Synthesis Workflow.
"""
from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class SubProblem(BaseModel):
    """Model for a decomposed sub-problem."""

    id: str
    perspective: str  # e.g., "经济", "社会", "技术", "伦理"
    description: str
    questions: List[str] = Field(default_factory=list)
    expertise_required: List[str] = Field(default_factory=list)
    priority: int = 1  # 1 (highest) to 5 (lowest)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExpertViewpoint(BaseModel):
    """Model for an expert's viewpoint on a sub-problem."""

    expert_id: str
    expert_name: str
    expertise_areas: List[str] = Field(default_factory=list)
    sub_problem_id: str
    viewpoint: str
    supporting_evidence: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_process: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ViewpointCollection(BaseModel):
    """Model for collected viewpoints with analysis."""

    topic: str
    viewpoints: List[ExpertViewpoint] = Field(default_factory=list)
    conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    consensus_areas: List[str] = Field(default_factory=list)
    coverage_analysis: Dict[str, Any] = Field(default_factory=dict)
    quality_score: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SynthesisQuality(BaseModel):
    """Model for assessing synthesis quality."""

    depth_score: float = Field(ge=0.0, le=1.0)
    breadth_score: float = Field(ge=0.0, le=1.0)
    insight_score: float = Field(ge=0.0, le=1.0)
    coherence_score: float = Field(ge=0.0, le=1.0)
    overall_score: float = Field(ge=0.0, le=1.0)
    improvement_suggestions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SynthesisResult(BaseModel):
    """Model for the final synthesis result."""

    topic: str
    perspectives: List[str] = Field(default_factory=list)
    synthesis: str
    key_insights: List[str] = Field(default_factory=list)
    expert_contributions: Dict[str, List[str]] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    quality_assessment: SynthesisQuality = None
    refinement_iterations: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
