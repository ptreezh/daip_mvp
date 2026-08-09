"""
通用记忆系统
支持所有角色应用场景的分层记忆管理
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class MemoryType(Enum):
    """记忆类型枚举"""

    SHARED_FACT = "shared_fact"
    PERSONAL_ARGUMENT = "personal_argument"
    ROUND_SUMMARY = "round_summary"
    STANCE_EVOLUTION = "stance_evolution"
    USER_PREFERENCE = "user_preference"
    SESSION_CONTEXT = "session_context"
    KNOWLEDGE_FACT = "knowledge_fact"


@dataclass
class MemoryEntry:
    """记忆条目"""

    content: str
    memory_type: MemoryType
    source: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[str] = None


@dataclass
class UniversalMemorySystem:
    """通用记忆系统 - 适用于所有应用场景"""

    # 分层记忆存储
    shared_factual_history: list[MemoryEntry] = field(default_factory=list)
    role_personal_memories: dict[str, dict[MemoryType, list[MemoryEntry]]] = field(
        default_factory=dict
    )
    session_memories: dict[str, dict[MemoryType, list[MemoryEntry]]] = field(
        default_factory=dict
    )
    knowledge_base: list[MemoryEntry] = field(default_factory=list)

    # 记忆索引
    memory_index: dict[str, list[MemoryEntry]] = field(default_factory=dict)
    tag_index: dict[str, list[MemoryEntry]] = field(default_factory=dict)

    # 配置
    max_memory_entries: int = 10000
    memory_ttl: int = 86400  # 24小时
    compression_threshold: int = 1000  # 压缩阈值

    def add_memory(
        self,
        content: str,
        memory_type: MemoryType,
        source: str,
        confidence: float = 1.0,
        role_name: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: list[str] = None,
        metadata: dict[str, Any] = None,
        expires_in: Optional[int] = None,
    ) -> str:
        """添加记忆条目"""
        memory_entry = MemoryEntry(
            content=content,
            memory_type=memory_type,
            source=source,
            confidence=confidence,
            metadata=metadata or {},
            expires_at=self._calculate_expiry(expires_in) if expires_in else None,
        )

        # 添加标签
        if tags:
            memory_entry.metadata["tags"] = tags
            for tag in tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                self.tag_index[tag].append(memory_entry)

        # 存储到相应位置
        if memory_type == MemoryType.SHARED_FACT:
            self.shared_factual_history.append(memory_entry)
        elif role_name:
            if role_name not in self.role_personal_memories:
                self.role_personal_memories[role_name] = {}
            if memory_type not in self.role_personal_memories[role_name]:
                self.role_personal_memories[role_name][memory_type] = []
            self.role_personal_memories[role_name][memory_type].append(memory_entry)
        elif session_id:
            if session_id not in self.session_memories:
                self.session_memories[session_id] = {}
            if memory_type not in self.session_memories[session_id]:
                self.session_memories[session_id][memory_type] = []
            self.session_memories[session_id][memory_type].append(memory_entry)
        elif memory_type == MemoryType.KNOWLEDGE_FACT:
            self.knowledge_base.append(memory_entry)

        # 更新索引
        self._update_index(memory_entry)

        # 清理过期记忆
        self._cleanup_expired_memories()

        return memory_entry.timestamp

    def get_context(
        self,
        role_name: Optional[str] = None,
        session_id: Optional[str] = None,
        current_round: int = 1,
        memory_types: list[MemoryType] = None,
        max_entries: int = 10,
        keywords: list[str] = None,
    ) -> str:
        """获取上下文"""
        if memory_types is None:
            memory_types = [MemoryType.SHARED_FACT, MemoryType.PERSONAL_ARGUMENT]

        context_parts = []
        relevant_memories = []

        # 收集相关记忆
        for memory_type in memory_types:
            # 共享事实
            if memory_type == MemoryType.SHARED_FACT:
                relevant_memories.extend(self.shared_factual_history)

            # 角色个人记忆
            if role_name and role_name in self.role_personal_memories:
                if memory_type in self.role_personal_memories[role_name]:
                    relevant_memories.extend(
                        self.role_personal_memories[role_name][memory_type]
                    )

            # 会话记忆
            if session_id and session_id in self.session_memories:
                if memory_type in self.session_memories[session_id]:
                    relevant_memories.extend(
                        self.session_memories[session_id][memory_type]
                    )

        # 按关键词过滤
        if keywords:
            relevant_memories = [
                mem
                for mem in relevant_memories
                if any(keyword.lower() in mem.content.lower() for keyword in keywords)
            ]

        # 按置信度和时间排序
        relevant_memories.sort(key=lambda x: (x.confidence, x.timestamp), reverse=True)

        # 限制数量
        relevant_memories = relevant_memories[:max_entries]

        # 格式化上下文
        for memory in relevant_memories:
            context_parts.append(f"[{memory.memory_type.value}] {memory.content}")
            if memory.confidence < 1.0:
                context_parts.append(f"  Confidence: {memory.confidence}")
            if memory.metadata.get("tags"):
                context_parts.append(f"  Tags: {', '.join(memory.metadata['tags'])}")

        return (
            "\n".join(context_parts) if context_parts else "No relevant memories found."
        )

    def get_compressed_context(
        self,
        role_name: Optional[str] = None,
        session_id: Optional[str] = None,
        current_round: int = 1,
        max_length: int = 2000,
    ) -> str:
        """获取压缩上下文"""
        full_context = self.get_context(role_name, session_id, current_round)

        if len(full_context) <= max_length:
            return full_context

        # 简单的压缩策略：保留最重要的记忆
        lines = full_context.split("\n")
        compressed_lines = []

        for line in lines:
            if len("\n".join(compressed_lines + [line])) > max_length:
                break
            compressed_lines.append(line)

        return "\n".join(compressed_lines) + "\n... (context truncated)"

    def search_memories(
        self,
        query: str,
        memory_types: list[MemoryType] = None,
        role_name: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 20,
    ) -> list[MemoryEntry]:
        """搜索记忆"""
        results = []

        # 使用索引搜索
        query_lower = query.lower()
        for keyword, memories in self.memory_index.items():
            if keyword in query_lower:
                results.extend(memories)

        # 去重并排序
        unique_results = list({id(mem): mem for mem in results}.values())
        unique_results.sort(key=lambda x: (x.confidence, x.timestamp), reverse=True)

        # 过滤
        if memory_types:
            unique_results = [
                mem for mem in unique_results if mem.memory_type in memory_types
            ]
        if role_name:
            unique_results = [
                mem
                for mem in unique_results
                if mem
                in getattr(self.role_personal_memories.get(role_name, {}).values(), [])
            ]
        if session_id:
            unique_results = [
                mem
                for mem in unique_results
                if mem
                in getattr(self.session_memories.get(session_id, {}).values(), [])
            ]

        return unique_results[:limit]

    def update_memory_confidence(self, memory_timestamp: str, new_confidence: float):
        """更新记忆置信度"""
        all_memories = (
            self.shared_factual_history
            + sum(
                [
                    memories
                    for role_memories in self.role_personal_memories.values()
                    for memories in role_memories.values()
                ],
                [],
            )
            + sum(
                [
                    memories
                    for session_memories in self.session_memories.values()
                    for memories in session_memories.values()
                ],
                [],
            )
            + self.knowledge_base
        )

        for memory in all_memories:
            if memory.timestamp == memory_timestamp:
                memory.confidence = new_confidence
                break

    def get_memory_statistics(self) -> dict[str, Any]:
        """获取记忆统计"""
        return {
            "total_shared_facts": len(self.shared_factual_history),
            "total_role_memories": sum(
                len(memories)
                for role_memories in self.role_personal_memories.values()
                for memories in role_memories.values()
            ),
            "total_session_memories": sum(
                len(memories)
                for session_memories in self.session_memories.values()
                for memories in session_memories.values()
            ),
            "total_knowledge_entries": len(self.knowledge_base),
            "total_roles": len(self.role_personal_memories),
            "total_sessions": len(self.session_memories),
            "memory_index_size": len(self.memory_index),
            "tag_index_size": len(self.tag_index),
            "memory_types_used": list(
                {
                    mem.memory_type
                    for mem in self.shared_factual_history + self.knowledge_base
                }
            ),
        }

    def check_memory_consistency(self) -> list[dict[str, Any]]:
        """检查记忆一致性"""
        conflicts = []

        # 检查共享事实的一致性
        for i, fact1 in enumerate(self.shared_factual_history):
            for fact2 in self.shared_factual_history[i + 1 :]:
                if self._are_contradictory(fact1.content, fact2.content):
                    conflicts.append(
                        {
                            "type": "contradictory_facts",
                            "fact1": fact1.content,
                            "fact2": fact2.content,
                            "confidence1": fact1.confidence,
                            "confidence2": fact2.confidence,
                        }
                    )

        return conflicts

    def export_memory(self) -> dict[str, Any]:
        """导出记忆数据"""
        return {
            "shared_factual_history": [
                {
                    "content": mem.content,
                    "memory_type": mem.memory_type.value,
                    "source": mem.source,
                    "confidence": mem.confidence,
                    "timestamp": mem.timestamp,
                    "metadata": mem.metadata,
                }
                for mem in self.shared_factual_history
            ],
            "role_personal_memories": {
                role: {
                    mem_type.value: [
                        {
                            "content": mem.content,
                            "memory_type": mem.memory_type.value,
                            "source": mem.source,
                            "confidence": mem.confidence,
                            "timestamp": mem.timestamp,
                            "metadata": mem.metadata,
                        }
                        for mem in memories
                    ]
                    for mem_type, memories in role_memories.items()
                }
                for role, role_memories in self.role_personal_memories.items()
            },
            "knowledge_base": [
                {
                    "content": mem.content,
                    "memory_type": mem.memory_type.value,
                    "source": mem.source,
                    "confidence": mem.confidence,
                    "timestamp": mem.timestamp,
                    "metadata": mem.metadata,
                }
                for mem in self.knowledge_base
            ],
            "export_timestamp": datetime.now().isoformat(),
        }

    def import_memory(self, memory_data: dict[str, Any]):
        """导入记忆数据"""
        # 导入共享事实
        for fact_data in memory_data.get("shared_factual_history", []):
            self.add_memory(
                content=fact_data["content"],
                memory_type=MemoryType(fact_data["memory_type"]),
                source=fact_data["source"],
                confidence=fact_data["confidence"],
                metadata=fact_data.get("metadata", {}),
            )

        # 导入角色个人记忆
        for role, role_memories in memory_data.get(
            "role_personal_memories", {}
        ).items():
            for mem_type_str, memories in role_memories.items():
                mem_type = MemoryType(mem_type_str)
                for mem_data in memories:
                    self.add_memory(
                        content=mem_data["content"],
                        memory_type=mem_type,
                        source=mem_data["source"],
                        confidence=mem_data["confidence"],
                        role_name=role,
                        metadata=mem_data.get("metadata", {}),
                    )

        # 导入知识库
        for knowledge_data in memory_data.get("knowledge_base", []):
            self.add_memory(
                content=knowledge_data["content"],
                memory_type=MemoryType(knowledge_data["memory_type"]),
                source=knowledge_data["source"],
                confidence=knowledge_data["confidence"],
                metadata=knowledge_data.get("metadata", {}),
            )

    def clear_all_memories(self):
        """清除所有记忆"""
        self.shared_factual_history.clear()
        self.role_personal_memories.clear()
        self.session_memories.clear()
        self.knowledge_base.clear()
        self.memory_index.clear()
        self.tag_index.clear()

    def _update_index(self, memory_entry: MemoryEntry):
        """更新索引"""
        # 简单的关键词索引
        words = re.findall(r"\b\w+\b", memory_entry.content.lower())
        for word in words:
            if len(word) > 3:  # 只索引长度大于3的词
                if word not in self.memory_index:
                    self.memory_index[word] = []
                self.memory_index[word].append(memory_entry)

    def _calculate_expiry(self, expires_in: int) -> str:
        """计算过期时间"""
        expiry_time = datetime.now() + timedelta(seconds=expires_in)
        return expiry_time.isoformat()

    def _cleanup_expired_memories(self):
        """清理过期记忆"""
        current_time = datetime.now()

        def is_expired(memory_entry: MemoryEntry) -> bool:
            if not memory_entry.expires_at:
                return False
            expiry_time = datetime.fromisoformat(memory_entry.expires_at)
            return current_time > expiry_time

        # 清理各个存储区域
        self.shared_factual_history = [
            mem for mem in self.shared_factual_history if not is_expired(mem)
        ]
        for role_memories in self.role_personal_memories.values():
            for mem_type in role_memories:
                role_memories[mem_type] = [
                    mem for mem in role_memories[mem_type] if not is_expired(mem)
                ]
        for session_memories in self.session_memories.values():
            for mem_type in session_memories:
                session_memories[mem_type] = [
                    mem for mem in session_memories[mem_type] if not is_expired(mem)
                ]
        self.knowledge_base = [
            mem for mem in self.knowledge_base if not is_expired(mem)
        ]

    def _are_contradictory(self, fact1: str, fact2: str) -> bool:
        """检查两个事实是否矛盾"""
        contradictory_pairs = [
            (r"is safe", r"is not safe"),
            (r"is beneficial", r"is harmful"),
            (r"will improve", r"will worsen"),
            (r"supports", r"opposes"),
            (r"increases", r"decreases"),
        ]

        fact1_lower = fact1.lower()
        fact2_lower = fact2.lower()

        for pattern1, pattern2 in contradictory_pairs:
            if (
                re.search(pattern1, fact1_lower) and re.search(pattern2, fact2_lower)
            ) or (
                re.search(pattern2, fact1_lower) and re.search(pattern1, fact2_lower)
            ):
                return True

        return False

    def __str__(self) -> str:
        stats = self.get_memory_statistics()
        return f"UniversalMemorySystem(facts={stats['total_shared_facts']}, roles={stats['total_roles']}, sessions={stats['total_sessions']})"  # noqa: E501

    def __repr__(self) -> str:
        return (
            f"UniversalMemorySystem("
            f"shared_facts={len(self.shared_factual_history)}, "
            f"roles={list(self.role_personal_memories.keys())}, "
            f"sessions={list(self.session_memories.keys())}, "
            f"knowledge={len(self.knowledge_base)})"
        )


# 为了向后兼容，保留原有的LayeredMemorySystem作为别名
class LayeredMemorySystem(UniversalMemorySystem):
    """向后兼容的分层记忆系统"""

    pass
