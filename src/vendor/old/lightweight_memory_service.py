"""轻量级记忆服务
高性能、低延迟、高可用性的记忆管理服务
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# 轻量级依赖
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import aiosqlite

    ASYNC_SQLITE_AVAILABLE = True
except ImportError:
    ASYNC_SQLITE_AVAILABLE = False


class MemoryPriority(Enum):
    """记忆优先级"""

    LOW = 1  # 低优先级，可延迟处理
    NORMAL = 2  # 正常优先级
    HIGH = 3  # 高优先级，立即处理
    CRITICAL = 4  # 关键优先级，必须立即处理


@dataclass
class LightweightMemory:
    """轻量级记忆条目"""

    id: str
    role_id: str
    content: str
    memory_type: str
    importance: float
    timestamp: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: list[str] = None
    metadata: dict[str, Any] = None
    priority: MemoryPriority = MemoryPriority.NORMAL
    ttl: Optional[int] = None  # 生存时间（秒）

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MemoryContext:
    """记忆上下文"""

    role_id: str
    relevant_memories: list[LightweightMemory]
    role_identity: Optional[dict[str, Any]] = None
    conversation_summary: Optional[str] = None
    project_context: Optional[dict[str, Any]] = None
    model_adaptation: Optional[dict[str, Any]] = None


class MemoryCache:
    """高性能内存缓存"""

    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: dict[str, tuple[Any, float]] = {}
        self.access_order = deque()
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    # 更新访问顺序
                    self.access_order.remove(key)
                    self.access_order.append(key)
                    return value
                else:
                    # 过期，删除
                    del self.cache[key]
                    self.access_order.remove(key)
        return None

    def set(self, key: str, value: Any):
        """设置缓存项"""
        with self.lock:
            # LRU淘汰
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = self.access_order.popleft()
                del self.cache[oldest_key]

            self.cache[key] = (value, time.time())
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)

    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()


class AsyncDatabaseManager:
    """异步数据库管理器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._init_database()

    def _init_database(self):
        """初始化数据库"""

        def init_db():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS lightweight_memories (
                        id TEXT PRIMARY KEY,
                        role_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        memory_type TEXT NOT NULL,
                        importance REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        project_id TEXT,
                        session_id TEXT,
                        tags TEXT,
                        metadata TEXT,
                        priority INTEGER DEFAULT 2,
                        ttl INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS role_identities (
                        role_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        title TEXT,
                        personality TEXT,
                        background TEXT,
                        core_traits TEXT,
                        speaking_style TEXT,
                        knowledge_domains TEXT,
                        prompt_template TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                )

                # 创建索引
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_memories_role_id ON lightweight_memories(role_id)",
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_memories_project_id ON lightweight_memories(project_id)",
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_memories_type ON lightweight_memories(memory_type)",
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_memories_importance ON lightweight_memories(importance)",
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON lightweight_memories(timestamp)",
                )

        self.executor.submit(init_db)

    async def save_memory(self, memory: LightweightMemory) -> bool:
        """异步保存记忆"""

        def save():
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO lightweight_memories
                        (id, role_id, content, memory_type, importance, timestamp,
                         project_id, session_id, tags, metadata, priority, ttl)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            memory.id,
                            memory.role_id,
                            memory.content,
                            memory.memory_type,
                            memory.importance,
                            memory.timestamp,
                            memory.project_id,
                            memory.session_id,
                            json.dumps(memory.tags),
                            json.dumps(memory.metadata),
                            memory.priority.value,
                            memory.ttl,
                        ),
                    )
                    return True
            except Exception as e:
                logging.error(f"保存记忆失败: {e}")
                return False

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, save)

    async def get_memories(
        self,
        role_id: str,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> list[LightweightMemory]:
        """异步获取记忆"""

        def fetch():
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        """
                        SELECT * FROM lightweight_memories
                        WHERE role_id = ? AND importance >= ?
                        ORDER BY importance DESC, timestamp DESC
                        LIMIT ?
                    """,
                        (role_id, min_importance, limit),
                    )

                    memories = []
                    for row in cursor.fetchall():
                        memory = LightweightMemory(
                            id=row["id"],
                            role_id=row["role_id"],
                            content=row["content"],
                            memory_type=row["memory_type"],
                            importance=row["importance"],
                            timestamp=row["timestamp"],
                            project_id=row["project_id"],
                            session_id=row["session_id"],
                            tags=json.loads(row["tags"] or "[]"),
                            metadata=json.loads(row["metadata"] or "{}"),
                            priority=MemoryPriority(row["priority"]),
                            ttl=row["ttl"],
                        )
                        memories.append(memory)
                    return memories
            except Exception as e:
                logging.error(f"获取记忆失败: {e}")
                return []

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, fetch)


class LightweightMemoryService:
    """轻量级记忆服务"""

    def __init__(
        self,
        data_dir: str = "data/lightweight_memory",
        enable_redis: bool = False,
        redis_url: str = "redis://localhost:6379",
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 核心组件
        self.db_manager = AsyncDatabaseManager(
            str(self.data_dir / "lightweight_memory.db"),
        )

        # 缓存系统
        self.memory_cache = MemoryCache(max_size=5000, ttl_seconds=1800)  # 30分钟TTL
        self.context_cache = MemoryCache(max_size=1000, ttl_seconds=300)  # 5分钟TTL

        # Redis缓存（可选）
        self.redis_client = None
        if enable_redis and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                logging.info("Redis缓存已启用")
            except Exception as e:
                logging.warning(f"Redis连接失败，使用内存缓存: {e}")

        # 异步任务队列
        self.task_queue = asyncio.Queue()
        self.background_tasks = set()

        # 性能监控
        self.performance_metrics = {
            "memory_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "db_operations": 0,
            "average_response_time": 0.0,
        }

        # 容错配置
        self.fallback_config = {
            "enable_fallback": True,
            "max_retries": 3,
            "retry_delay": 0.1,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_timeout": 60,
        }

        # 电路断路器
        self.circuit_breaker = {
            "failure_count": 0,
            "last_failure_time": 0,
            "state": "closed",  # closed, open, half_open
        }

        self.logger = logging.getLogger(__name__)

        # 启动后台任务
        asyncio.create_task(self._background_worker())
        asyncio.create_task(self._cleanup_expired_memories())

    async def add_memory(
        self,
        role_id: str,
        content: str,
        memory_type: str,
        importance: float = 0.5,
        priority: MemoryPriority = MemoryPriority.NORMAL,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        ttl: Optional[int] = None,
    ) -> str:
        """添加记忆（高性能版本）"""
        start_time = time.time()

        try:
            # 生成记忆ID
            memory_id = hashlib.md5(
                f"{role_id}_{content}_{time.time()}".encode(),
            ).hexdigest()[:16]

            # 创建记忆对象
            memory = LightweightMemory(
                id=memory_id,
                role_id=role_id,
                content=content,
                memory_type=memory_type,
                importance=importance,
                timestamp=datetime.now().isoformat(),
                project_id=project_id,
                session_id=session_id,
                tags=tags or [],
                metadata=metadata or {},
                priority=priority,
                ttl=ttl,
            )

            # 高优先级记忆立即处理
            if priority in [MemoryPriority.HIGH, MemoryPriority.CRITICAL]:
                await self._save_memory_immediate(memory)
            else:
                # 低优先级记忆异步处理
                await self.task_queue.put(memory)

            # 更新缓存
            cache_key = f"memory:{role_id}:{memory_id}"
            self.memory_cache.set(cache_key, memory)

            # 更新性能指标
            self.performance_metrics["memory_operations"] += 1
            self.performance_metrics["average_response_time"] = (
                self.performance_metrics["average_response_time"] * 0.9
                + (time.time() - start_time) * 0.1
            )

            return memory_id

        except Exception as e:
            self.logger.error(f"添加记忆失败: {e}")
            # 容错：返回临时ID
            return f"temp_{int(time.time())}"

    async def get_memories(
        self,
        role_id: str,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> list[LightweightMemory]:
        """获取记忆（高性能版本）"""
        start_time = time.time()

        try:
            # 检查缓存
            cache_key = f"memories:{role_id}:{limit}:{min_importance}"
            cached_memories = self.memory_cache.get(cache_key)

            if cached_memories:
                self.performance_metrics["cache_hits"] += 1
                return cached_memories

            self.performance_metrics["cache_misses"] += 1

            # 从数据库获取
            memories = await self.db_manager.get_memories(
                role_id,
                limit,
                min_importance,
            )

            # 更新缓存
            self.memory_cache.set(cache_key, memories)

            # 更新性能指标
            self.performance_metrics["db_operations"] += 1
            self.performance_metrics["average_response_time"] = (
                self.performance_metrics["average_response_time"] * 0.9
                + (time.time() - start_time) * 0.1
            )

            return memories

        except Exception as e:
            self.logger.error(f"获取记忆失败: {e}")
            # 容错：返回空列表
            return []

    async def build_context_for_conversation(
        self,
        role_id: str,
        current_question: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
        target_model: str = "ollama",
    ) -> MemoryContext:
        """构建对话上下文（高性能版本）"""
        start_time = time.time()

        try:
            # 检查上下文缓存
            cache_key = (
                f"context:{role_id}:{hash(current_question)}:{project_id}:{session_id}"
            )
            cached_context = self.context_cache.get(cache_key)

            if cached_context:
                return cached_context

            # 并行获取数据
            tasks = [
                self.get_memories(role_id, limit=5, min_importance=0.3),
                self._get_role_identity(role_id),
                self._summarize_conversation(conversation_history)
                if conversation_history
                else None,
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 处理结果
            memories = results[0] if not isinstance(results[0], Exception) else []
            role_identity = (
                results[1] if not isinstance(results[1], Exception) else None
            )
            conversation_summary = (
                results[2] if not isinstance(results[2], Exception) else None
            )

            # 构建上下文
            context = MemoryContext(
                role_id=role_id,
                relevant_memories=memories,
                role_identity=role_identity,
                conversation_summary=conversation_summary,
                project_context={"project_id": project_id, "session_id": session_id},
                model_adaptation=self._adapt_for_model(target_model),
            )

            # 更新缓存
            self.context_cache.set(cache_key, context)

            return context

        except Exception as e:
            self.logger.error(f"构建上下文失败: {e}")
            # 容错：返回最小上下文
            return MemoryContext(
                role_id=role_id,
                relevant_memories=[],
                project_context={"project_id": project_id, "session_id": session_id},
            )

    async def _save_memory_immediate(self, memory: LightweightMemory):
        """立即保存记忆"""
        try:
            await self.db_manager.save_memory(memory)
        except Exception as e:
            self.logger.error(f"立即保存记忆失败: {e}")

    async def _background_worker(self):
        """后台工作线程"""
        while True:
            try:
                # 批量处理任务
                batch = []
                batch_size = 10
                timeout = 1.0  # 1秒超时

                # 收集批量任务
                start_time = time.time()
                while len(batch) < batch_size and (time.time() - start_time) < timeout:
                    try:
                        memory = await asyncio.wait_for(
                            self.task_queue.get(),
                            timeout=0.1,
                        )
                        batch.append(memory)
                    except asyncio.TimeoutError:
                        break

                if batch:
                    # 批量保存
                    tasks = [self._save_memory_immediate(memory) for memory in batch]
                    await asyncio.gather(*tasks, return_exceptions=True)

                await asyncio.sleep(0.1)  # 避免过度占用CPU

            except Exception as e:
                self.logger.error(f"后台工作线程错误: {e}")
                await asyncio.sleep(1)

    async def _cleanup_expired_memories(self):
        """清理过期记忆"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时清理一次

                def cleanup():
                    with sqlite3.connect(self.db_manager.db_path) as conn:
                        current_time = time.time()
                        conn.execute(
                            """
                            DELETE FROM lightweight_memories
                            WHERE ttl IS NOT NULL AND
                                  (strftime('%s', timestamp) + ttl) < ?
                        """,
                            (current_time,),
                        )

                loop = asyncio.get_event_loop()
                await loop.run_in_executor(self.db_manager.executor, cleanup)

            except Exception as e:
                self.logger.error(f"清理过期记忆失败: {e}")

    async def _get_role_identity(self, role_id: str) -> Optional[dict[str, Any]]:
        """获取角色身份（简化版）"""
        # 这里可以集成现有的角色身份系统
        return None

    async def _summarize_conversation(
        self,
        conversation_history: list[dict[str, str]],
    ) -> Optional[str]:
        """总结对话历史（简化版）"""
        if not conversation_history:
            return None

        # 简单的总结：取最后几条消息
        recent_messages = conversation_history[-3:]
        summary = " ".join([msg.get("content", "") for msg in recent_messages])
        return summary[:200] + "..." if len(summary) > 200 else summary

    def _adapt_for_model(self, target_model: str) -> dict[str, Any]:
        """为模型适配（简化版）"""
        return {"model": target_model, "max_tokens": 1000, "temperature": 0.7}

    def get_performance_metrics(self) -> dict[str, Any]:
        """获取性能指标"""
        return {
            **self.performance_metrics,
            "cache_hit_rate": (
                self.performance_metrics["cache_hits"]
                / (
                    self.performance_metrics["cache_hits"]
                    + self.performance_metrics["cache_misses"]
                )
                if (
                    self.performance_metrics["cache_hits"]
                    + self.performance_metrics["cache_misses"]
                )
                > 0
                else 0
            ),
            "task_queue_size": self.task_queue.qsize(),
            "circuit_breaker_state": self.circuit_breaker["state"],
        }

    def clear_cache(self):
        """清空缓存"""
        self.memory_cache.clear()
        self.context_cache.clear()

    async def close(self):
        """关闭服务"""
        # 等待所有后台任务完成
        while not self.task_queue.empty():
            await asyncio.sleep(0.1)

        # 关闭数据库连接
        self.db_manager.executor.shutdown(wait=True)
