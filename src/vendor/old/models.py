"""DAIP Insight Engine - 核心数据模型定义模块

本模块定义了项目核心数据结构，包括任务（LegacyTask）、对话消息（DialogueMessage）、LLM摘要（LLMSummary）等。
所有SQLModel表结构、属性、方法均具备类型注解和详细文档，支持自动化API文档工具提取。
"""

import json
import uuid
from datetime import datetime
from typing import Any, ClassVar, Optional

from sqlmodel import Field as SQLField
from sqlmodel import SQLModel

# SQLModel 模型定义


class LegacyTask(SQLModel, table=True):
    """兼容旧版的任务表结构（Legacy Task）。
    用于向后兼容历史数据，主线任务模型请见sskg_new.py。
    """

    __tablename__: ClassVar[str] = "legacy_tasks"

    task_id: str = SQLField(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    description: str
    due_date: Optional[str] = None  # ISO 8601 格式: YYYY-MM-DD
    status: str = "pending"  # 例如: 'pending', 'completed'
    created_at: str = SQLField(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = SQLField(default_factory=lambda: datetime.now().isoformat())

    def to_db_row(self) -> tuple[str, str, Optional[str], str, str, str]:
        """转换为适用于 SQLite 插入的元组（向后兼容）。
        Returns:
            tuple: (task_id, description, due_date, status, created_at, updated_at)
        """
        return (
            self.task_id,
            self.description,
            self.due_date,
            self.status,
            self.created_at,
            self.updated_at,
        )

    @classmethod
    def from_db_row(cls, row: Optional[tuple[Any, ...]]) -> Optional["LegacyTask"]:
        """从 SQLite 行创建 Task 实例（向后兼容）。
        Args:
            row (tuple): 数据库行元组。
        Returns:
            Optional[LegacyTask]: 实例或None。
        """
        if row is None:
            return None
        return cls(
            task_id=row[0],
            description=row[1],
            due_date=row[2],
            status=row[3],
            created_at=row[4],
            updated_at=row[5],
        )


# Note: Main Task class is now defined in sskg_new.py to avoid conflicts
# Use LegacyTask for backward compatibility or import Task from sskg_new when needed


class DialogueMessage(SQLModel, table=True):
    """对话消息表结构，支持多角色、工具调用、溯源等。
    """

    __tablename__: ClassVar[str] = "dialogue_messages"

    message_id: str = SQLField(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    role: str  # 'user', 'assistant', 'tool'
    content: Optional[str] = None  # 文本内容，或工具输出的 JSON 字符串
    timestamp: str = SQLField(default_factory=lambda: datetime.now().isoformat())
    # 对于 role='tool' 的消息，此字段关联其回复的 assistant tool_call_id
    tool_call_id: Optional[str] = None
    # 对于 role='assistant' 的消息，如果包含工具调用，存储 tool_calls 列表的 JSON 字符串
    tool_calls_json: Optional[str] = None
    # 新增字段，存储溯源片段ID列表（存储为JSON字符串）
    source_chunks_json: Optional[str] = None

    def to_db_row(
        self,
    ) -> tuple[
        str, str, Optional[str], str, Optional[str], Optional[str], Optional[str]
    ]:
        """转换为适用于 SQLite 插入的元组（向后兼容）。
        Returns:
            tuple: (message_id, role, content, timestamp, tool_call_id, tool_calls_json, source_chunks_json)
        """
        return (
            self.message_id,
            self.role,
            self.content,
            self.timestamp,
            self.tool_call_id,
            self.tool_calls_json,
            self.source_chunks_json,
        )

    @classmethod
    def from_db_row(cls, row: Optional[tuple[Any, ...]]) -> Optional["DialogueMessage"]:
        """从 SQLite 行创建 DialogueMessage 实例（向后兼容）。
        Args:
            row (tuple): 数据库行元组。
        Returns:
            Optional[DialogueMessage]: 实例或None。
        """
        if row is None:
            return None
        return cls(
            message_id=row[0],
            role=row[1],
            content=row[2],
            timestamp=row[3],
            tool_call_id=row[4],
            tool_calls_json=row[5],
            source_chunks_json=row[6],
        )

    @property
    def source_chunks(self) -> Optional[list[str]]:
        """获取溯源片段ID列表。
        Returns:
            Optional[List[str]]: 溯源片段ID列表。
        """
        if self.source_chunks_json:
            return json.loads(self.source_chunks_json)
        return None

    @source_chunks.setter
    def source_chunks(self, value: Optional[list[str]]):
        """设置溯源片段ID列表。
        Args:
            value (Optional[List[str]]): 溯源片段ID列表。
        """
        if value is not None:
            self.source_chunks_json = json.dumps(value)
        else:
            self.source_chunks_json = None


class LLMSummary(SQLModel, table=True):
    """LLM摘要表结构，支持消息ID列表、嵌入标志等。
    """

    __tablename__: ClassVar[str] = "llm_summaries"

    summary_id: str = SQLField(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    text: str
    timestamp: str = SQLField(default_factory=lambda: datetime.now().isoformat())
    # 被此次总结所包含的消息的 ID 列表
    summarized_message_ids: str = SQLField(default="[]")  # 存储为 JSON 字符串
    embedding_present: bool = False  # 标志 ChromaDB 中是否存在嵌入

    def to_db_row(self) -> tuple[str, str, str, str, int]:
        """转换为适用于 SQLite 插入的元组（向后兼容）。
        Returns:
            tuple: (summary_id, text, timestamp, summarized_message_ids, embedding_present)
        """
        return (
            self.summary_id,
            self.text,
            self.timestamp,
            self.summarized_message_ids,
            1 if self.embedding_present else 0,
        )

    @classmethod
    def from_db_row(cls, row: Optional[tuple[Any, ...]]) -> Optional["LLMSummary"]:
        """从 SQLite 行创建 LLMSummary 实例（向后兼容）。
        Args:
            row (tuple): 数据库行元组。
        Returns:
            Optional[LLMSummary]: 实例或None。
        """
        if row is None:
            return None
        return cls(
            summary_id=row[0],
            text=row[1],
            timestamp=row[2],
            summarized_message_ids=row[3],
            embedding_present=bool(row[4]),
        )

    @property
    def summarized_message_ids_list(self) -> list[str]:
        """获取消息ID列表。
        Returns:
            List[str]: 消息ID列表。
        """
        if isinstance(self.summarized_message_ids, str):
            return json.loads(self.summarized_message_ids)
        elif isinstance(self.summarized_message_ids, list):
            return self.summarized_message_ids
        else:
            return []

    @summarized_message_ids_list.setter
    def summarized_message_ids_list(self, value: list[str]):
        """设置消息ID列表。
        Args:
            value (List[str]): 消息ID列表。
        """
        if isinstance(value, list):
            self.summarized_message_ids = json.dumps(value)
        else:
            self.summarized_message_ids = "[]"
