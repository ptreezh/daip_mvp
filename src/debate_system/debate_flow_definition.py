#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多轮辩论系统流程定义

定义辩论的各个阶段、流程控制和状态管理。
支持灵活的辩论格式和自定义规则。
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid


class DebatePhase(Enum):
    """辩论阶段枚举"""
    PREPARATION = "preparation"
    OPENING_STATEMENTS = "opening_statements"
    MAIN_ARGUMENTS = "main_arguments"
    CROSS_EXAMINATION = "cross_examination"
    REBUTTAL = "rebuttal"
    CLOSING_STATEMENTS = "closing_statements"
    CONSENSUS_BUILDING = "consensus_building"
    EVALUATION = "evaluation"
    COMPLETED = "completed"


class ParticipantRole(Enum):
    """参与者角色枚举"""
    PROPONENT = "proponent"
    OPPONENT = "opponent"
    MODERATOR = "moderator"
    OBSERVER = "observer"
    EXPERT = "expert"
    JUDGE = "judge"


class DebateStatus(Enum):
    """辩论状态枚举"""
    CREATED = "created"
    PREPARING = "preparing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class DebateFormat(Enum):
    """辩论格式枚举"""
    TRADITIONAL = "traditional"
    OXFORD = "oxford"
    PARLIAMENTARY = "parliamentary"
    FISHBOWL = "fishbowl"
    SOCRATIC = "socratic"
    CONSENSUS_BUILDING = "consensus_building"
    CUSTOM = "custom"


@dataclass
class DebateRules:
    """辩论规则配置"""
    format: DebateFormat = DebateFormat.TRADITIONAL
    max_rounds: int = 3
    round_duration_minutes: Optional[int] = 60
    total_duration_minutes: Optional[int] = 180
    min_participants: int = 2
    max_participants: int = 10
    require_balanced_sides: bool = True
    allow_audience_participation: bool = False
    consensus_threshold: float = 0.7
    evidence_required: bool = True
    fact_checking_enabled: bool = True
    real_time_feedback: bool = True


@dataclass
class DebateParticipant:
    """辩论参与者"""
    participant_id: str
    name: str
    role: ParticipantRole
    side: Optional[str] = None
    expertise_areas: List[str] = field(default_factory=list)
    credibility_score: float = 0.5
    participation_history: List[str] = field(default_factory=list)
    is_active: bool = True
    joined_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebateContribution:
    """辩论贡献（发言、论证等）"""
    contribution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    participant_id: str = ""
    round_number: int = 1
    phase: DebatePhase = DebatePhase.MAIN_ARGUMENTS
    content: str = ""
    contribution_type: str = "statement"
    timestamp: datetime = field(default_factory=datetime.now)
    references: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    quality_score: Optional[float] = None
    relevance_score: Optional[float] = None
    impact_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebateRound:
    """辩论轮次"""
    round_number: int
    current_phase: DebatePhase = DebatePhase.PREPARATION
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    contributions: List[DebateContribution] = field(default_factory=list)
    phase_history: List[Dict[str, Any]] = field(default_factory=list)
    consensus_attempts: List[Dict[str, Any]] = field(default_factory=list)
    round_summary: Optional[str] = None
    key_points: List[str] = field(default_factory=list)
    unresolved_issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebateSession:
    """辩论会话"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    topic: str = ""
    description: str = ""
    rules: DebateRules = field(default_factory=DebateRules)
    status: DebateStatus = DebateStatus.CREATED
    participants: List[DebateParticipant] = field(default_factory=list)
    rounds: List[DebateRound] = field(default_factory=list)
    current_round: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    moderator_id: Optional[str] = None
    final_consensus: Optional[Dict[str, Any]] = None
    debate_metrics: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)