# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : value_objects.py
@Description:
    Value objects for the Personal Intelligence Hub domain.
    These are immutable objects that represent descriptive aspects of the domain.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime


class EntranceType(Enum):
    """入口类型枚举"""
    SECRETARIAT = "secretariat"
    FORUM = "forum"
    
    def __str__(self):
        return self.value


class IntentType(Enum):
    """意图类型枚举"""
    ANALYSIS = "analysis"
    DISCUSSION = "discussion"
    QUESTION = "question"
    SUGGESTION = "suggestion"
    CORRECTION = "correction"
    COMMENT = "comment"
    EVALUATION = "evaluation"
    SUMMARIZATION = "summarization"
    
    def __str__(self):
        return self.value


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
    def __str__(self):
        return self.value


class SessionStatus(Enum):
    """会话状态枚举"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"
    
    def __str__(self):
        return self.value


class MessageIntent(Enum):
    """消息意图枚举"""
    COMMENT = "comment"
    QUESTION = "question"
    SUGGESTION = "suggestion"
    CORRECTION = "correction"
    AGREEMENT = "agreement"
    DISAGREEMENT = "disagreement"
    
    def __str__(self):
        return self.value


@dataclass(frozen=True)
class ConsensusLevel:
    """共识水平值对象"""
    value: float
    
    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Consensus level must be between 0.0 and 1.0, got {self.value}")
    
    def is_high(self) -> bool:
        """判断是否为高共识"""
        return self.value >= 0.7
    
    def is_medium(self) -> bool:
        """判断是否为中等共识"""
        return 0.4 <= self.value < 0.7
    
    def is_low(self) -> bool:
        """判断是否为低共识"""
        return self.value < 0.4
    
    def description(self) -> str:
        """获取共识水平描述"""
        if self.is_high():
            return "高共识"
        elif self.is_medium():
            return "中等共识"
        else:
            return "低共识"
    
    def __str__(self):
        return f"{self.value:.2f}"


@dataclass(frozen=True)
class TimeInterval:
    """时间间隔值对象"""
    start_time: datetime
    end_time: datetime
    
    def __post_init__(self):
        if self.start_time > self.end_time:
            raise ValueError("Start time must be before end time")
    
    @property
    def duration(self) -> float:
        """获取持续时间（秒）"""
        return (self.end_time - self.start_time).total_seconds()
    
    def contains(self, time: datetime) -> bool:
        """检查时间是否在间隔内"""
        return self.start_time <= time <= self.end_time


@dataclass(frozen=True)
class UserPreference:
    """用户偏好值对象"""
    preferred_entrance: EntranceType
    language: str = "zh-CN"
    theme: str = "light"
    notification_enabled: bool = True
    auto_transparency: bool = False
    detail_level: str = "comprehensive"
    
    def __str__(self):
        return f"UserPreference(entrance={self.preferred_entrance}, language={self.language})"


@dataclass(frozen=True)
class TaskPriority:
    """任务优先级值对象"""
    value: str
    
    def __post_init__(self):
        if self.value not in ["low", "normal", "high", "urgent"]:
            raise ValueError(f"Invalid priority: {self.value}")
    
    def is_higher_than(self, other: 'TaskPriority') -> bool:
        """判断是否比另一个优先级更高"""
        priority_order = {"low": 0, "normal": 1, "high": 2, "urgent": 3}
        return priority_order[self.value] > priority_order[other.value]
    
    def __str__(self):
        return self.value


@dataclass(frozen=True)
class ResourceUsage:
    """资源使用情况值对象"""
    memory_mb: float
    cpu_percent: float
    network_mb: float
    tokens_used: int
    
    def __post_init__(self):
        if self.memory_mb < 0:
            raise ValueError("Memory usage cannot be negative")
        if not 0.0 <= self.cpu_percent <= 100.0:
            raise ValueError("CPU percentage must be between 0 and 100")
        if self.network_mb < 0:
            raise ValueError("Network usage cannot be negative")
        if self.tokens_used < 0:
            raise ValueError("Tokens used cannot be negative")
    
    @property
    def is_high_usage(self) -> bool:
        """判断是否为高资源使用"""
        return (self.memory_mb > 1000 or 
                self.cpu_percent > 80 or 
                self.network_mb > 100)
    
    def __str__(self):
        return f"ResourceUsage(memory={self.memory_mb}MB, cpu={self.cpu_percent}%, network={self.network_mb}MB, tokens={self.tokens_used})"