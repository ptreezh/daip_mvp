"""Personal Intelligence Hub - Workflow Models

工作流相关的数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class StepType(Enum):
    """步骤类型枚举"""

    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    CRITIQUE = "critique"
    VALIDATION = "validation"
    DOCUMENTATION = "documentation"
    COLLABORATION = "collaboration"
    ITERATION = "iteration"


class WorkflowStatus(Enum):
    """工作流状态枚举"""

    DRAFT = "draft"
    VALIDATED = "validated"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowStep:
    """工作流步骤"""

    id: str
    name: str
    type: StepType
    description: str
    agent_roles: List[str]
    dependencies: List[str]
    parameters: Dict[str, Any]
    validation_criteria: Dict[str, Any]
    timeout: Optional[int] = 300
    retry_count: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WorkflowDefinition:
    """工作流定义"""

    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    parameters: Dict[str, Any]
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WorkflowValidationResult:
    """工作流验证结果"""

    is_valid: bool
    issues: List[str]
    suggestions: List[str]
    confidence: float = 0.8
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.suggestions is None:
            self.suggestions = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WorkflowPreview:
    """工作流预览"""

    name: str
    description: str
    total_steps: int
    estimated_duration: int
    agent_roles: List[str]
    complexity: str
    confidence: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WorkflowExecution:
    """工作流执行"""

    id: str
    workflow_id: str
    status: str
    current_step: Optional[str]
    progress: float
    started_at: datetime
    completed_at: Optional[datetime]
    results: Dict[str, Any]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()
        if self.results is None:
            self.results = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WorkflowTemplate:
    """工作流模板"""

    id: str
    name: str
    description: str
    definition: WorkflowDefinition
    tags: List[str]
    usage_count: int
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
