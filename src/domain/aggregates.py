"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : aggregates.py
@Description:
    Domain aggregates for the Personal Intelligence Hub.
    Aggregates are clusters of domain objects that can be treated as a single unit.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from .entities import Debate, Message, Session, Task
from .value_objects import (
    ConsensusLevel,
    EntranceType,
    IntentType,
    SessionStatus,
    TaskPriority,
    TaskStatus,
)


class SessionAggregate:
    """会话聚合根"""
    
    def __init__(self, user_id: str, entrance_type: EntranceType, session_id: str = None):
        self.session_id = session_id or str(uuid4())
        self.user_id = user_id
        self.entrance_type = entrance_type
        self.status = SessionStatus.ACTIVE
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.metadata = {}
        
        # 聚合内的实体
        self._session = Session(
            session_id=self.session_id,
            user_id=self.user_id,
            entrance_type=self.entrance_type,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            metadata=self.metadata
        )
        
        self._tasks: list[Task] = []
        self._messages: list[Message] = []
        self._debate: Optional[Debate] = None
    
    @property
    def session(self) -> Session:
        """获取会话实体"""
        return self._session
    
    @property
    def tasks(self) -> list[Task]:
        """获取任务列表"""
        return self._tasks.copy()
    
    @property
    def messages(self) -> list[Message]:
        """获取消息列表"""
        return self._messages.copy()
    
    @property
    def debate(self) -> Optional[Debate]:
        """获取辩论实体"""
        return self._debate
    
    def add_task(self, task: Task) -> bool:
        """添加任务"""
        if task.session_id != self.session_id:
            raise ValueError("Task does not belong to this session")
        
        if not self._session.is_active():
            raise ValueError("Cannot add task to inactive session")
        
        self._tasks.append(task)
        self._update_timestamp()
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        for task in self._tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def get_active_task(self) -> Optional[Task]:
        """获取活跃任务"""
        for task in self._tasks:
            if task.status == TaskStatus.RUNNING:
                return task
        return None
    
    def get_completed_tasks(self) -> list[Task]:
        """获取已完成的任务"""
        return [task for task in self._tasks if task.status == TaskStatus.COMPLETED]
    
    def get_task_count(self) -> int:
        """获取任务数量"""
        return len(self._tasks)
    
    def add_message(self, message: Message) -> bool:
        """添加消息"""
        if message.session_id != self.session_id:
            raise ValueError("Message does not belong to this session")
        
        self._messages.append(message)
        self._update_timestamp()
        return True
    
    def get_messages_by_sender(self, sender: str) -> list[Message]:
        """根据发送者获取消息"""
        return [msg for msg in self._messages if msg.sender == sender]
    
    def get_recent_messages(self, count: int = 10) -> list[Message]:
        """获取最近的消息"""
        return sorted(self._messages, key=lambda x: x.timestamp, reverse=True)[:count]
    
    def create_debate(self, topic: str, participants: list[str]) -> Debate:
        """创建辩论"""
        if self.entrance_type != EntranceType.FORUM:
            raise ValueError("Debates can only be created in Forum sessions")
        
        if self._debate and self._debate.status == "active":
            raise ValueError("Active debate already exists")
        
        debate = Debate(
            debate_id=str(uuid4()),
            session_id=self.session_id,
            topic=topic,
            participants=participants,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._debate = debate
        self._update_timestamp()
        return debate
    
    def get_debate(self) -> Optional[Debate]:
        """获取辩论"""
        return self._debate
    
    def pause(self):
        """暂停会话"""
        self._session.pause()
        if self._debate:
            self._debate.pause()
        self._update_timestamp()
    
    def resume(self):
        """恢复会话"""
        self._session.resume()
        if self._debate:
            self._debate.resume()
        self._update_timestamp()
    
    def complete(self):
        """完成会话"""
        self._session.complete()
        if self._debate:
            self._debate.complete()
        self._update_timestamp()
    
    def update_metadata(self, key: str, value: Any):
        """更新元数据"""
        self.metadata[key] = value
        self._session.update_metadata(key, value)
        self._update_timestamp()
    
    def get_duration(self) -> float:
        """获取会话持续时间"""
        return (self.updated_at - self.created_at).total_seconds()
    
    def can_add_task(self) -> bool:
        """检查是否可以添加任务"""
        return self._session.is_active()
    
    def _update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.now()
        self._session.updated_at = self.updated_at
    
    def __str__(self):
        return f"SessionAggregate(id={self.session_id}, user={self.user_id}, type={self.entrance_type}, tasks={len(self._tasks)})"

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """从字典重建SessionAggregate"""
        session_id = data.get("session_id")
        user_id = data.get("user_id")
        entrance_type = EntranceType(data.get("entrance_type"))
        
        if not all([session_id, user_id, entrance_type]):
            raise ValueError("Missing essential data for SessionAggregate reconstruction")

        instance = cls(user_id=user_id, entrance_type=entrance_type, session_id=session_id)
        instance.status = SessionStatus(data.get("status", SessionStatus.ACTIVE.value))
        instance.created_at = datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        instance.updated_at = datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        instance.metadata = data.get("metadata", {})

        # Reconstruct nested entities
        if "tasks" in data:
            instance._tasks = [Task.from_dict(t) for t in data["tasks"]]
        if "messages" in data:
            instance._messages = [Message.from_dict(m) for m in data["messages"]]
        if "debate" in data and data["debate"] is not None:
            instance._debate = Debate.from_dict(data["debate"])
        
        return instance

    def to_dict(self) -> dict[str, Any]:
        """将SessionAggregate转换为字典"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "entrance_type": self.entrance_type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "tasks": [t.to_dict() for t in self._tasks],
            "messages": [m.to_dict() for m in self._messages],
            "debate": self._debate.to_dict() if self._debate else None,
        }


class TaskAggregate:
    """任务聚合根"""
    
    def __init__(self, task_id: str = None):
        self.task_id = task_id or str(uuid4())
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.execution_history = []
        
        # 聚合内的实体
        self._task = Task(
            task_id=self.task_id,
            session_id="",  # 将在设置会话时更新
            content="",     # 将在设置内容时更新
            intent_type=IntentType.ANALYSIS,  # 默认值
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    @property
    def task(self) -> Task:
        """获取任务实体"""
        return self._task
    
    def set_session(self, session_id: str):
        """设置会话ID"""
        self._task.session_id = session_id
        self._update_timestamp()
    
    def set_content(self, content: str, intent_type: IntentType):
        """设置任务内容和意图类型"""
        if self._task.status != TaskStatus.PENDING:
            raise ValueError("Cannot modify task content after execution starts")
        
        self._task.content = content
        self._task.intent_type = intent_type
        self._update_timestamp()
    
    def set_priority(self, priority: TaskPriority):
        """设置任务优先级"""
        self._task.priority = priority
        self._update_timestamp()
    
    def start_execution(self):
        """开始执行任务"""
        if self._task.status != TaskStatus.PENDING:
            raise ValueError("Task is not in pending status")
        
        self._task.start_execution()
        self.execution_history.append({
            "event": "started",
            "timestamp": datetime.now()
        })
        self._update_timestamp()
    
    def record_step(self, step_name: str, step_data: dict[str, Any]):
        """记录执行步骤"""
        if self._task.status != TaskStatus.RUNNING:
            raise ValueError("Task is not running")
        
        step_record = {
            "step": step_name,
            "data": step_data,
            "timestamp": datetime.now()
        }
        self.execution_history.append(step_record)
        self._update_timestamp()
    
    def complete_execution(self, result: str):
        """完成任务执行"""
        if self._task.status != TaskStatus.RUNNING:
            raise ValueError("Task is not running")
        
        self._task.complete_execution(result)
        self.execution_history.append({
            "event": "completed",
            "result": result,
            "timestamp": datetime.now()
        })
        self._update_timestamp()
    
    def fail_execution(self, error: str):
        """任务执行失败"""
        if self._task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            raise ValueError("Task cannot be failed in current status")
        
        self._task.fail_execution(error)
        self.execution_history.append({
            "event": "failed",
            "error": error,
            "timestamp": datetime.now()
        })
        self._update_timestamp()
    
    def cancel_execution(self):
        """取消任务执行"""
        if self._task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            raise ValueError("Task cannot be cancelled in current status")
        
        self._task.cancel_execution()
        self.execution_history.append({
            "event": "cancelled",
            "timestamp": datetime.now()
        })
        self._update_timestamp()
    
    def get_execution_history(self) -> list[dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history.copy()
    
    def get_execution_steps(self) -> list[dict[str, Any]]:
        """获取执行步骤"""
        return [step for step in self.execution_history if step.get("event") != "started"]
    
    def get_execution_time(self) -> Optional[float]:
        """获取执行时间"""
        return self._task.get_execution_time()
    
    def can_start_execution(self) -> bool:
        """检查是否可以开始执行"""
        return self._task.status == TaskStatus.PENDING
    
    def is_completed(self) -> bool:
        """检查是否已完成"""
        return self._task.status == TaskStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """检查是否失败"""
        return self._task.status == TaskStatus.FAILED
    
    def is_cancelled(self) -> bool:
        """检查是否已取消"""
        return self._task.status == TaskStatus.CANCELLED
    
    def _update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.now()
        self._task.updated_at = self.updated_at
    
    def __str__(self):
        return f"TaskAggregate(id={self.task_id}, status={self.status}, steps={len(self.execution_history)})"


class DebateAggregate:
    """辩论聚合根"""
    
    def __init__(self, debate_id: str = None):
        self.debate_id = debate_id or str(uuid4())
        self.status = "active"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.participant_activities = {}
        self.consensus_history = []
        
        # 聚合内的实体
        self._debate = Debate(
            debate_id=self.debate_id,
            session_id="",  # 将在设置会话时更新
            topic="",      # 将在设置主题时更新
            participants=[],
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    @property
    def debate(self) -> Debate:
        """获取辩论实体"""
        return self._debate
    
    def set_session(self, session_id: str):
        """设置会话ID"""
        self._debate.session_id = session_id
        self._update_timestamp()
    
    def set_topic(self, topic: str):
        """设置辩论主题"""
        if self.status != "active":
            raise ValueError("Cannot change topic when debate is not active")
        
        self._debate.topic = topic
        self._update_timestamp()
    
    def add_participant(self, participant_id: str, role: str = ""):
        """添加参与者"""
        if participant_id not in self._debate.participants:
            self._debate.add_participant(participant_id)
            self.participant_activities[participant_id] = {
                "role": role,
                "message_count": 0,
                "last_activity": None
            }
            self._update_timestamp()
    
    def add_message(self, message: Message):
        """添加消息"""
        if message.session_id != self._debate.session_id:
            raise ValueError("Message does not belong to this debate session")
        
        self._debate.add_message(message)
        
        # 更新参与者活动记录
        if message.sender in self.participant_activities:
            self.participant_activities[message.sender]["message_count"] += 1
            self.participant_activities[message.sender]["last_activity"] = message.timestamp
        
        self._update_timestamp()
    
    def update_consensus(self, consensus_level: ConsensusLevel):
        """更新共识水平"""
        self._debate.update_consensus(consensus_level)
        self.consensus_history.append({
            "consensus_level": consensus_level,
            "timestamp": datetime.now()
        })
        self._update_timestamp()
    
    def get_participant_activity(self, participant_id: str) -> Optional[dict[str, Any]]:
        """获取参与者活动记录"""
        return self.participant_activities.get(participant_id)
    
    def get_most_active_participant(self) -> Optional[str]:
        """获取最活跃的参与者"""
        if not self.participant_activities:
            return None
        
        return max(
            self.participant_activities.keys(),
            key=lambda x: self.participant_activities[x]["message_count"]
        )
    
    def get_consensus_trend(self) -> list[dict[str, Any]]:
        """获取共识趋势"""
        return self.consensus_history.copy()
    
    def pause(self):
        """暂停辩论"""
        if self.status == "active":
            self.status = "paused"
            self._debate.pause()
            self._update_timestamp()
    
    def resume(self):
        """恢复辩论"""
        if self.status == "paused":
            self.status = "active"
            self._debate.resume()
            self._update_timestamp()
    
    def complete(self):
        """完成辩论"""
        self.status = "completed"
        self._debate.complete()
        self._update_timestamp()
    
    def get_duration(self) -> float:
        """获取辩论持续时间"""
        return (self.updated_at - self.created_at).total_seconds()
    
    def get_message_count(self) -> int:
        """获取消息数量"""
        return self._debate.get_message_count()
    
    def get_participant_count(self) -> int:
        """获取参与者数量"""
        return len(self._debate.participants)
    
    def _update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.now()
        self._debate.updated_at = self.updated_at
    
    def __str__(self):
        return f"DebateAggregate(id={self.debate_id}, topic={self._debate.topic}, participants={len(self._debate.participants)}, messages={len(self._debate.messages)})"