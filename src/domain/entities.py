"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : entities.py
@Description:
    Domain entities for the Personal Intelligence Hub.
    These are objects with unique identities that represent core business concepts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from .value_objects import (
    ConsensusLevel,
    EntranceType,
    IntentType,
    MessageIntent,
    SessionStatus,
    TaskPriority,
    TaskStatus,
    UserPreference,
)


@dataclass
class User:
    """用户实体"""
    user_id: str
    username: str
    email: str
    preferred_entrance: EntranceType
    preferences: UserPreference
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def __post_init__(self):
        if not self.user_id:
            self.user_id = str(uuid4())
    
    def update_preference(self, preference: UserPreference):
        """更新用户偏好"""
        self.preferences = preference
        self.updated_at = datetime.now()
    
    def deactivate(self):
        """停用用户"""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def activate(self):
        """激活用户"""
        self.is_active = True
        self.updated_at = datetime.now()
    
    def is_eligible_for_entrance(self, entrance_type: EntranceType) -> bool:
        """检查用户是否有资格使用特定入口"""
        return self.is_active and self.preferred_entrance == entrance_type
    
    def __str__(self):
        return f"User(id={self.user_id}, username={self.username}, entrance={self.preferred_entrance})"


@dataclass
class Session:
    """会话实体"""
    session_id: str
    user_id: str
    entrance_type: EntranceType
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid4())
    
    def is_active(self) -> bool:
        """检查会话是否活跃"""
        return self.status == SessionStatus.ACTIVE
    
    def is_expired(self, timeout_hours: int = 24) -> bool:
        """检查会话是否已过期"""
        expiry_time = self.updated_at.timestamp() + (timeout_hours * 3600)
        return datetime.now().timestamp() > expiry_time
    
    def pause(self):
        """暂停会话"""
        self.status = SessionStatus.PAUSED
        self.updated_at = datetime.now()
    
    def resume(self):
        """恢复会话"""
        if self.status == SessionStatus.PAUSED:
            self.status = SessionStatus.ACTIVE
            self.updated_at = datetime.now()
    
    def complete(self):
        """完成会话"""
        self.status = SessionStatus.COMPLETED
        self.updated_at = datetime.now()
    
    def update_metadata(self, key: str, value: Any):
        """更新元数据"""
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def get_duration(self) -> float:
        """获取会话持续时间（秒）"""
        return (self.updated_at - self.created_at).total_seconds()
    
    def __str__(self):
        return f"Session(id={self.session_id}, user={self.user_id}, type={self.entrance_type}, status={self.status})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "entrance_type": self.entrance_type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            entrance_type=EntranceType(data["entrance_type"]),
            status=SessionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Task:
    """任务实体"""
    task_id: str
    session_id: str
    content: str
    intent_type: IntentType
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = field(default_factory=lambda: TaskPriority("normal"))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid4())
    
    def can_execute(self) -> bool:
        """检查任务是否可以执行"""
        return self.status == TaskStatus.PENDING
    
    def start_execution(self):
        """开始执行任务"""
        if self.can_execute():
            self.status = TaskStatus.RUNNING
            self.updated_at = datetime.now()
    
    def complete_execution(self, result: str):
        """完成任务执行"""
        if self.status == TaskStatus.RUNNING:
            self.status = TaskStatus.COMPLETED
            self.result = result
            self.completed_at = datetime.now()
            self.updated_at = datetime.now()
    
    def fail_execution(self, error: str):
        """任务执行失败"""
        if self.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            self.status = TaskStatus.FAILED
            self.metadata["error"] = error
            self.updated_at = datetime.now()
    
    def cancel_execution(self):
        """取消任务执行"""
        if self.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            self.status = TaskStatus.CANCELLED
            self.updated_at = datetime.now()
    
    def get_execution_time(self) -> Optional[float]:
        """获取任务执行时间（秒）"""
        if self.completed_at and self.updated_at > self.created_at:
            return (self.completed_at - self.created_at).total_seconds()
        return None
    
    def __str__(self):
        return f"Task(id={self.task_id}, session={self.session_id}, intent={self.intent_type}, status={self.status})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "session_id": self.session_id,
            "content": self.content,
            "intent_type": self.intent_type.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            task_id=data["task_id"],
            session_id=data["session_id"],
            content=data["content"],
            intent_type=IntentType(data["intent_type"]),
            status=TaskStatus(data["status"]),
            priority=TaskPriority(data["priority"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data["completed_at"] else None,
            result=data["result"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class Message:
    """消息实体"""
    message_id: str
    session_id: str
    content: str
    sender: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid4())
    
    def is_system_message(self) -> bool:
        """是否为系统消息"""
        return self.sender == "system"
    
    def is_user_message(self) -> bool:
        """是否为用户消息"""
        return self.sender.startswith("user_")
    
    def is_agent_message(self) -> bool:
        """是否为Agent消息"""
        return self.sender.startswith("agent_")
    
    def add_metadata(self, key: str, value: Any):
        """添加元数据"""
        self.metadata[key] = value
    
    def __str__(self):
        return f"Message(id={self.message_id}, session={self.session_id}, sender={self.sender})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "content": self.content,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class UserMessage(Message):
    """用户消息实体"""
    intent: MessageIntent = MessageIntent.COMMENT
    is_optimized: bool = False
    target_agent: Optional[str] = None
    
    def __post_init__(self):
        if not self.sender.startswith("user_"):
            self.sender = f"user_{self.sender}"
    
    def optimize(self, optimized_content: str):
        """优化消息内容"""
        self.content = optimized_content
        self.is_optimized = True
        self.metadata["optimized_at"] = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "intent": self.intent.value,
            "is_optimized": self.is_optimized,
            "target_agent": self.target_agent,
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            message_id=data["message_id"],
            session_id=data["session_id"],
            content=data["content"],
            sender=data["sender"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            intent=MessageIntent(data["intent"]),
            is_optimized=data["is_optimized"],
            target_agent=data["target_agent"],
        )


@dataclass
class AgentMessage(Message):
    """Agent消息实体"""
    agent_role: str = ""
    confidence: float = 0.0
    target_message_id: Optional[str] = None
    message_type: str = "response"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.sender.startswith("agent_"):
            self.sender = f"agent_{self.sender}"
    
    def set_confidence(self, confidence: float):
        """设置置信度"""
        if 0.0 <= confidence <= 1.0:
            self.confidence = confidence
        else:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    def is_high_confidence(self) -> bool:
        """检查是否为高置信度"""
        return self.confidence >= 0.8

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "agent_role": self.agent_role,
            "confidence": self.confidence,
            "target_message_id": self.target_message_id,
            "message_type": self.message_type,
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            message_id=data["message_id"],
            session_id=data["session_id"],
            content=data["content"],
            sender=data["sender"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            agent_role=data["agent_role"],
            confidence=data["confidence"],
            target_message_id=data["target_message_id"],
            message_type=data["message_type"],
        )


@dataclass
class SystemMessage(Message):
    """系统消息实体"""
    system_event: str = ""
    severity: str = "info"
    
    def __init__(self, **kwargs):
        kwargs["sender"] = "system"
        super().__init__(**kwargs)
    
    def is_error(self) -> bool:
        """是否为错误消息"""
        return self.severity == "error"
    
    def is_warning(self) -> bool:
        """是否为警告消息"""
        return self.severity == "warning"

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "system_event": self.system_event,
            "severity": self.severity,
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            message_id=data["message_id"],
            session_id=data["session_id"],
            content=data["content"],
            sender=data["sender"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            system_event=data["system_event"],
            severity=data["severity"],
        )


@dataclass
class Debate:
    """辩论实体"""
    debate_id: str
    session_id: str
    topic: str
    participants: list[str]
    messages: list[Message] = field(default_factory=list)
    consensus_level: ConsensusLevel = field(default_factory=lambda: ConsensusLevel(0.0))
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.debate_id:
            self.debate_id = str(uuid4())
    
    def add_message(self, message: Message):
        """添加消息"""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def add_participant(self, participant_id: str):
        """添加参与者"""
        if participant_id not in self.participants:
            self.participants.append(participant_id)
            self.updated_at = datetime.now()
    
    def update_consensus(self, consensus_level: ConsensusLevel):
        """更新共识水平"""
        self.consensus_level = consensus_level
        self.updated_at = datetime.now()
    
    def pause(self):
        """暂停辩论"""
        self.status = "paused"
        self.updated_at = datetime.now()
    
    def resume(self):
        """恢复辩论"""
        if self.status == "paused":
            self.status = "active"
            self.updated_at = datetime.now()
    
    def complete(self):
        """完成辩论"""
        self.status = "completed"
        self.updated_at = datetime.now()
    
    def get_duration(self) -> float:
        """获取辩论持续时间（秒）"""
        return (self.updated_at - self.created_at).total_seconds()
    
    def get_message_count(self) -> int:
        """获取消息数量"""
        return len(self.messages)
    
    def __str__(self):
        return f"Debate(id={self.debate_id}, topic={self.topic}, participants={len(self.participants)}, consensus={self.consensus_level})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "debate_id": self.debate_id,
            "session_id": self.session_id,
            "topic": self.topic,
            "participants": self.participants,
            "messages": [m.to_dict() for m in self.messages],
            "consensus_level": self.consensus_level.value,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            debate_id=data["debate_id"],
            session_id=data["session_id"],
            topic=data["topic"],
            participants=data["participants"],
            messages=[Message.from_dict(m) for m in data["messages"]], # Assuming Message.from_dict handles subclasses
            consensus_level=ConsensusLevel(data["consensus_level"]),
            status=data["status"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )