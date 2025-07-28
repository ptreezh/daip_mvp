"""
核心数据模型定义
定义系统中所有核心数据结构和业务模型
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal, Tuple
from pydantic import BaseModel, Field
from enum import Enum


class ReasoningStyle(str, Enum):
    """推理风格枚举"""
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    PRAGMATIC = "pragmatic"
    REFLECTIVE = "reflective"


class MemoryType(str, Enum):
    """记忆类型枚举"""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class WorkflowStatus(str, Enum):
    """工作流状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


# ============================================================================
# 认知代理相关模型
# ============================================================================

class CognitiveProfile(BaseModel):
    """认知档案模型"""
    agent_id: str
    name: str
    avatar: str = "🤖"
    reasoning_style: ReasoningStyle
    core_values: Dict[str, float] = Field(default_factory=dict)
    personality_traits: List[str] = Field(default_factory=list)
    expertise_domains: Dict[str, float] = Field(default_factory=dict)
    cognitive_biases: List[str] = Field(default_factory=list)
    thinking_pattern: str = ""
    prompt_template: str = ""
    
    class Config:
        use_enum_values = True


class AgentMessage(BaseModel):
    """代理消息模型"""
    agent_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    message_type: Literal["analysis", "argument", "question", "summary"] = "analysis"
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 工作流相关模型
# ============================================================================

class WorkflowNode(BaseModel):
    """工作流节点模型"""
    id: str
    type: str  # 原语类型
    name: str
    config: Dict[str, Any] = Field(default_factory=dict)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)


class WorkflowEdge(BaseModel):
    """工作流边模型"""
    from_node: str
    to_node: str
    condition: Optional[str] = None


class WorkflowDefinition(BaseModel):
    """工作流定义模型"""
    id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    parameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class ExecutionStep(BaseModel):
    """执行步骤模型"""
    step_id: str
    node_id: str
    status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


class ExecutionMetrics(BaseModel):
    """执行指标模型"""
    total_duration: float  # 秒
    node_count: int
    success_rate: float
    token_consumption: int
    cost_estimate: float


class WorkflowResult(BaseModel):
    """工作流结果模型"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    outputs: Dict[str, Any] = Field(default_factory=dict)
    execution_trace: List[ExecutionStep] = Field(default_factory=list)
    metrics: ExecutionMetrics
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# 记忆和知识相关模型
# ============================================================================

class Memory(BaseModel):
    """记忆模型"""
    id: Optional[str] = None
    content: str
    source_role: str
    memory_type: MemoryType
    importance: float = Field(ge=0.0, le=1.0, default=0.5)
    recency: float = Field(ge=0.0, le=1.0, default=1.0)
    creation_time: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    related_memories: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeRelation(BaseModel):
    """知识关系模型"""
    relation_type: str  # "supports", "contradicts", "elaborates"
    target_fact_id: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeFact(BaseModel):
    """知识事实模型"""
    id: Optional[str] = None
    content: str
    source: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relations: List[KnowledgeRelation] = Field(default_factory=list)
    version: int = 1


class WikiPage(BaseModel):
    """Wiki页面模型"""
    id: str
    title: str
    content: str
    version: int = 1
    last_updated: datetime = Field(default_factory=datetime.now)
    contributors: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    quality_score: float = Field(ge=0.0, le=1.0, default=0.5)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 集体智慧涌现相关模型
# ============================================================================

class EmergentInsight(BaseModel):
    """涌现洞察模型"""
    insight_id: str
    title: str
    content: str
    novelty_score: float = Field(ge=0.0, le=1.0)
    emergence_score: float = Field(ge=0.0, le=1.0)
    contributing_agents: List[str] = Field(default_factory=list)
    evidence_support: List[str] = Field(default_factory=list)
    applications: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    impact_level: Literal["low", "medium", "high", "breakthrough"] = "medium"


class ConsensusResult(BaseModel):
    """共识结果模型"""
    consensus_id: str
    topic: str
    participants: List[str]
    consensus_strength: float = Field(ge=0.0, le=1.0)
    agreement_points: List[str] = Field(default_factory=list)
    disagreement_points: List[str] = Field(default_factory=list)
    final_position: str
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# 辩论相关模型
# ============================================================================

class Argument(BaseModel):
    """论证模型"""
    argument_id: str
    agent_id: str
    position: Literal["pro", "con", "neutral"]
    content: str
    evidence: List[str] = Field(default_factory=list)
    logical_strength: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence_quality: float = Field(ge=0.0, le=1.0, default=0.5)
    timestamp: datetime = Field(default_factory=datetime.now)


class DebateRound(BaseModel):
    """辩论轮次模型"""
    round_id: str
    round_number: int
    arguments: List[Argument] = Field(default_factory=list)
    summary: Optional[str] = None
    consensus_shift: float = 0.0


class DebateState(BaseModel):
    """辩论状态模型"""
    debate_id: str
    topic: str
    participants: List[str]
    rounds: List[DebateRound] = Field(default_factory=list)
    current_consensus: Optional[ConsensusResult] = None
    status: Literal["preparing", "active", "concluded"] = "preparing"
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# 任务管理相关模型
# ============================================================================

class Task(BaseModel):
    """任务模型"""
    task_id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.NOT_STARTED
    assigned_agent: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    estimated_duration: Optional[int] = None  # 分钟
    actual_duration: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Project(BaseModel):
    """项目模型"""
    project_id: str
    name: str
    description: str
    tasks: List[Task] = Field(default_factory=list)
    participants: List[str] = Field(default_factory=list)
    status: Literal["planning", "active", "completed", "cancelled"] = "planning"
    created_at: datetime = Field(default_factory=datetime.now)
    deadline: Optional[datetime] = None


# ============================================================================
# 系统监控和分析相关模型
# ============================================================================

class SystemEvent(BaseModel):
    """系统事件模型"""
    event_id: str
    event_type: str
    source: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    severity: Literal["info", "warning", "error", "critical"] = "info"


class SessionMetrics(BaseModel):
    """会话指标模型"""
    session_id: str
    message_count: int
    average_response_time: float
    topic_coherence: float = Field(ge=0.0, le=1.0)
    engagement_distribution: Dict[str, float] = Field(default_factory=dict)
    quality_score: float = Field(ge=0.0, le=1.0)


class RolePerformance(BaseModel):
    """角色表现模型"""
    role_id: str
    session_id: str
    message_count: int
    average_response_length: int
    topic_relevance: float = Field(ge=0.0, le=1.0)
    influence_score: float = Field(ge=0.0, le=1.0)
    contribution_quality: float = Field(ge=0.0, le=1.0)


# ============================================================================
# 配置和设置相关模型
# ============================================================================

class SystemConfig(BaseModel):
    """系统配置模型"""
    llm_provider: str = "openai"
    default_model: str = "gpt-4"
    max_context_length: int = 8000
    memory_retention_days: int = 30
    auto_save_interval: int = 300  # 秒
    transparency_level: Literal["minimal", "moderate", "detailed"] = "moderate"
    enable_analytics: bool = True


class UserPreferences(BaseModel):
    """用户偏好模型"""
    user_id: str
    preferred_agents: List[str] = Field(default_factory=list)
    notification_settings: Dict[str, bool] = Field(default_factory=dict)
    ui_theme: str = "default"
    language: str = "zh-CN"
    timezone: str = "Asia/Shanghai"