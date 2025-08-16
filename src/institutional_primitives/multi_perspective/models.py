"""@Time    : 2025-07-24 16:30:00
@Author  : DAIP-LIVE Team
@File    : models.py
@Description:
    Data models for Multi-perspective Synthesis Workflow.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SubProblem(BaseModel):
    """Model for a decomposed sub-problem."""

    id: str
    perspective: str  # e.g., "经济", "社会", "技术", "伦理"
    description: str
    questions: list[str] = Field(default_factory=list)
    expertise_required: list[str] = Field(default_factory=list)
    priority: int = 1  # 1 (highest) to 5 (lowest)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExpertViewpoint(BaseModel):
    """Model for an expert's viewpoint on a sub-problem."""

    expert_id: str
    expert_name: str
    expertise_areas: list[str] = Field(default_factory=list)
    sub_problem_id: str
    viewpoint: str
    supporting_evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_process: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ViewpointCollection(BaseModel):
    """Model for collected viewpoints with analysis."""

    topic: str
    viewpoints: list[ExpertViewpoint] = Field(default_factory=list)
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    consensus_areas: list[str] = Field(default_factory=list)
    coverage_analysis: dict[str, Any] = Field(default_factory=dict)
    quality_score: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SynthesisQuality(BaseModel):
    """Model for assessing synthesis quality."""

    depth_score: float = Field(ge=0.0, le=1.0)
    breadth_score: float = Field(ge=0.0, le=1.0)
    insight_score: float = Field(ge=0.0, le=1.0)
    coherence_score: float = Field(ge=0.0, le=1.0)
    overall_score: float = Field(ge=0.0, le=1.0)
    improvement_suggestions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SynthesisResult(BaseModel):
    """Model for the final synthesis result."""

    topic: str
    perspectives: list[str] = Field(default_factory=list)
    synthesis: str
    key_insights: list[str] = Field(default_factory=list)
    expert_contributions: dict[str, list[str]] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    quality_assessment: SynthesisQuality = None
    refinement_iterations: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)
<<<<<<< HEAD
    metadata: Dict[str, Any] = Field(default_factory=dict)
=======
    metadata: dict[str, Any] = Field(default_factory=dict)
>>>>>>> feature/core-services-refactor
