#!/usr/bin/env python3
"""Personal Intelligence Hub - Transparency Models

透明度监控相关的数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentStatus(Enum):
    """代理状态枚举"""

    IDLE = "idle"
    THINKING = "thinking"
    RESPONDING = "responding"
    WAITING = "waiting"


class MemoryOperationType(Enum):
    """记忆操作类型"""

    RETRIEVE = "retrieve"
    STORE = "store"
    CONSOLIDATE = "consolidate"


class MemoryType(Enum):
    """记忆类型"""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


@dataclass
class AgentStatusInfo:
    """代理状态信息"""

    agent_id: str
    name: str
    status: AgentStatus
    current_task: Optional[str] = None
    reasoning_framework: Optional[str] = None
    epistemology: Optional[str] = None
    last_activity: datetime = None

    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.now()


@dataclass
class LLMCall:
    """LLM调用记录"""

    id: str
    model_id: str
    input_tokens: int
    output_tokens: int
    cost: float
    latency: float
    timestamp: datetime
    success: bool = True


@dataclass
class MemoryOperation:
    """记忆操作记录"""

    operation_type: MemoryOperationType
    agent_id: str
    memory_type: MemoryType
    item_count: int
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TokenUsage:
    """Token使用统计"""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class OperationLog:
    """操作日志"""

    id: str
    timestamp: datetime
    operation: str
    component: str
    details: Dict[str, Any]
    duration: float
    success: bool


@dataclass
class SystemStatus:
    """系统状态"""

    active_agents: List[AgentStatusInfo]
    current_workflow: Optional[Dict[str, Any]] = None
    memory_operations: List[MemoryOperation] = None
    llm_calls: List[LLMCall] = None
    token_usage: Optional[TokenUsage] = None

    def __post_init__(self):
        if self.memory_operations is None:
            self.memory_operations = []
        if self.llm_calls is None:
            self.llm_calls = []


@dataclass
class PerformanceMetrics:
    """性能指标"""

    average_response_time: float
    total_tokens_used: int
    total_cost: float
    success_rate: float
    active_users: int
    workflows_completed: int
