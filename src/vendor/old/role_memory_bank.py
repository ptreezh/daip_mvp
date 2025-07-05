"""虚拟角色记忆银行系统
支持独立记忆存储、跨对话记忆、身份恢复和多模型适配
"""

import hashlib
import json
import logging
import sqlite3
import threading
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

try:
    import chromadb
    from chromadb.config import Settings

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available, using fallback memory storage")


@dataclass
class MemoryEntry:
    """记忆条目"""

    id: str
    role_id: str
    content: str
    memory_type: str  # identity, project, dialogue, experience, knowledge
    importance: float  # 0.0-1.0
    timestamp: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: list[str] = None
    metadata: dict[str, Any] = None
    embedding: Optional[list[float]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RoleIdentity:
    """角色身份信息"""

    role_id: str
    name: str
    title: str
    personality: dict[str, Any]
    background: str
    core_traits: list[str]
    speaking_style: str
    knowledge_domains: list[str]
    prompt_template: str
    created_at: str
    updated_at: str


@dataclass
class ProjectContext:
    """项目上下文"""

    project_id: str
    project_name: str
    description: str
    participants: list[str]
    start_date: str
    status: str
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RoleMemoryBank:
    """角色记忆银行"""

    def __init__(self, data_dir: str = "data/memory_banks"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 数据库连接
        self.db_path = self.data_dir / "memory_bank.db"
        self.conn = None
        self._init_database()

        # 向量存储
        self.vector_store = None
        if CHROMADB_AVAILABLE:
            self._init_vector_store()

        # 内存缓存
        self.memory_cache: dict[str, list[MemoryEntry]] = defaultdict(list)
        self.identity_cache: dict[str, RoleIdentity] = {}
        self.project_cache: dict[str, ProjectContext] = {}

        # 线程锁
        self.lock = threading.RLock()

        self.logger = logging.getLogger(__name__)

        # 加载缓存
        self._load_caches()

    def _init_database(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # 创建表
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS memories (
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

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
            );

            CREATE TABLE IF NOT EXISTS project_contexts (
                project_id TEXT PRIMARY KEY,
                project_name TEXT NOT NULL,
                description TEXT,
                participants TEXT,
                start_date TEXT,
                status TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_memories_role_id ON memories(role_id);
            CREATE INDEX IF NOT EXISTS idx_memories_project_id ON memories(project_id);
            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
            CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp);
        """,
        )
        self.conn.commit()

    def _init_vector_store(self):
        """初始化向量存储"""
        try:
            chroma_path = self.data_dir / "chroma_db"
            self.vector_store = chromadb.PersistentClient(
                path=str(chroma_path),
                settings=Settings(anonymized_telemetry=False),
            )

            # 创建集合
            try:
                self.memory_collection = self.vector_store.get_collection(
                    "role_memories",
                )
            except:
                self.memory_collection = self.vector_store.create_collection(
                    name="role_memories",
                    metadata={"description": "Role memory embeddings"},
                )

        except Exception as e:
            self.logger.error(f"Failed to initialize vector store: {e}")
            self.vector_store = None

    def _load_caches(self):
        """加载缓存"""
        with self.lock:
            # 加载身份缓存
            cursor = self.conn.execute("SELECT * FROM role_identities")
            for row in cursor.fetchall():
                identity = RoleIdentity(
                    role_id=row["role_id"],
                    name=row["name"],
                    title=row["title"] or "",
                    personality=json.loads(row["personality"] or "{}"),
                    background=row["background"] or "",
                    core_traits=json.loads(row["core_traits"] or "[]"),
                    speaking_style=row["speaking_style"] or "",
                    knowledge_domains=json.loads(row["knowledge_domains"] or "[]"),
                    prompt_template=row["prompt_template"] or "",
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                self.identity_cache[row["role_id"]] = identity

            # 加载项目缓存
            cursor = self.conn.execute("SELECT * FROM project_contexts")
            for row in cursor.fetchall():
                project = ProjectContext(
                    project_id=row["project_id"],
                    project_name=row["project_name"],
                    description=row["description"] or "",
                    participants=json.loads(row["participants"] or "[]"),
                    start_date=row["start_date"],
                    status=row["status"],
                    metadata=json.loads(row["metadata"] or "{}"),
                )
                self.project_cache[row["project_id"]] = project

    def create_role_identity(self, role_data: dict[str, Any]) -> RoleIdentity:
        """创建角色身份"""
        role_id = role_data.get("id") or role_data.get("role_id")
        if not role_id:
            raise ValueError("Role ID is required")

        # 从角色数据提取身份信息
        identity = RoleIdentity(
            role_id=role_id,
            name=role_data.get("name", ""),
            title=role_data.get("title", ""),
            personality=self._extract_personality(role_data),
            background=role_data.get("description", "")
            + " "
            + role_data.get("bio", ""),
            core_traits=role_data.get("specialties", []) + role_data.get("skills", []),
            speaking_style=self._infer_speaking_style(role_data),
            knowledge_domains=role_data.get("specialties", []),
            prompt_template=self._generate_prompt_template(role_data),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        # 保存到数据库
        with self.lock:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO role_identities
                (role_id, name, title, personality, background, core_traits,
                 speaking_style, knowledge_domains, prompt_template, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    identity.role_id,
                    identity.name,
                    identity.title,
                    json.dumps(identity.personality, ensure_ascii=False),
                    identity.background,
                    json.dumps(identity.core_traits, ensure_ascii=False),
                    identity.speaking_style,
                    json.dumps(identity.knowledge_domains, ensure_ascii=False),
                    identity.prompt_template,
                    identity.updated_at,
                ),
            )
            self.conn.commit()

            # 更新缓存
            self.identity_cache[role_id] = identity

        # 添加身份记忆
        self.add_memory(
            role_id=role_id,
            content=f"我是{identity.name}，{identity.title}。{identity.background}",
            memory_type="identity",
            importance=1.0,
            tags=["身份", "基础信息"],
        )

        return identity

    def _extract_personality(self, role_data: dict[str, Any]) -> dict[str, Any]:
        """从角色数据提取性格特征"""
        personality = {}

        # 从描述中推断性格
        description = role_data.get("description", "") + " " + role_data.get("bio", "")

        # 简单的性格特征映射
        traits = {
            "analytical": ["分析", "数据", "逻辑", "研究", "analysis", "data", "research"],
            "creative": ["创意", "设计", "艺术", "创新", "creative", "design", "innovation"],
            "leadership": ["领导", "管理", "团队", "项目", "leadership", "management", "team"],
            "technical": [
                "技术",
                "开发",
                "工程",
                "编程",
                "technical",
                "development",
                "programming",
            ],
            "communicative": ["沟通", "交流", "演讲", "表达", "communication", "speaking"],
        }

        for trait, keywords in traits.items():
            score = sum(
                1 for keyword in keywords if keyword.lower() in description.lower()
            )
            if score > 0:
                personality[trait] = min(score / len(keywords), 1.0)

        return personality

    def _infer_speaking_style(self, role_data: dict[str, Any]) -> str:
        """推断说话风格"""
        category = role_data.get("category", "").lower()
        specialties = " ".join(role_data.get("specialties", [])).lower()

        if "学术" in category or "academic" in category:
            return "严谨专业，逻辑清晰，善用专业术语"
        elif "技术" in category or "tech" in category:
            return "简洁明了，注重实用性，喜欢用具体例子说明"
        elif "管理" in category or "business" in category:
            return "条理清晰，目标导向，善于总结要点"
        elif "创意" in category or "creative" in category:
            return "富有想象力，表达生动，善用比喻和形象化语言"
        else:
            return "友好专业，表达清晰，乐于分享经验"

    def _generate_prompt_template(self, role_data: dict[str, Any]) -> str:
        """生成角色提示词模板"""
        name = role_data.get("name", "专家")
        title = role_data.get("title", "")
        specialties = role_data.get("specialties", [])
        background = role_data.get("description", "") + " " + role_data.get("bio", "")

        template = f"""你是{name}"""
        if title:
            template += f"，{title}"

        if specialties:
            template += f"，专长领域包括：{', '.join(specialties[:3])}"

        if background:
            template += f"。\n\n背景信息：{background[:200]}..."

        template += f"""

请以{name}的身份回应，保持角色的专业性和个性特点。在回答时：
1. 运用你的专业知识和经验
2. 保持角色的说话风格和思维方式
3. 结合相关的项目记忆和对话历史
4. 如果涉及你不熟悉的领域，诚实说明并提供可能的建议

当前对话上下文：{{context}}
相关记忆：{{memories}}
用户问题：{{question}}"""

        return template

    def add_memory(
        self,
        role_id: str,
        content: str,
        memory_type: str,
        importance: float = 0.5,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """添加记忆"""
        memory_id = hashlib.md5(
            f"{role_id}_{content}_{time.time()}".encode(),
        ).hexdigest()

        memory = MemoryEntry(
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
        )

        # 保存到数据库
        with self.lock:
            self.conn.execute(
                """
                INSERT INTO memories
                (id, role_id, content, memory_type, importance, timestamp,
                 project_id, session_id, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    json.dumps(memory.tags, ensure_ascii=False),
                    json.dumps(memory.metadata, ensure_ascii=False),
                ),
            )
            self.conn.commit()

            # 更新缓存
            self.memory_cache[role_id].append(memory)

            # 限制缓存大小
            if len(self.memory_cache[role_id]) > 100:
                self.memory_cache[role_id] = sorted(
                    self.memory_cache[role_id],
                    key=lambda x: (x.importance, x.timestamp),
                    reverse=True,
                )[:100]

        # 添加到向量存储
        if self.vector_store and CHROMADB_AVAILABLE:
            try:
                self.memory_collection.add(
                    documents=[content],
                    metadatas=[
                        {
                            "role_id": role_id,
                            "memory_type": memory_type,
                            "importance": importance,
                            "timestamp": memory.timestamp,
                            "project_id": project_id or "",
                            "session_id": session_id or "",
                        },
                    ],
                    ids=[memory_id],
                )
            except Exception as e:
                self.logger.error(f"Failed to add memory to vector store: {e}")

        self.logger.info(f"Added memory for role {role_id}: {memory_type}")
        return memory_id

    def retrieve_memories(
        self,
        role_id: str,
        query: Optional[str] = None,
        memory_types: Optional[list[str]] = None,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> list[MemoryEntry]:
        """检索记忆"""
        memories = []

        # 构建SQL查询
        sql = "SELECT * FROM memories WHERE role_id = ?"
        params = [role_id]

        if memory_types:
            placeholders = ",".join(["?" for _ in memory_types])
            sql += f" AND memory_type IN ({placeholders})"
            params.extend(memory_types)

        if project_id:
            sql += " AND project_id = ?"
            params.append(project_id)

        if session_id:
            sql += " AND session_id = ?"
            params.append(session_id)

        if min_importance > 0:
            sql += " AND importance >= ?"
            params.append(min_importance)

        sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)

        with self.lock:
            cursor = self.conn.execute(sql, params)
            for row in cursor.fetchall():
                memory = MemoryEntry(
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
                )
                memories.append(memory)

        # 如果有查询文本，使用向量搜索重新排序
        if query and self.vector_store and CHROMADB_AVAILABLE:
            try:
                results = self.memory_collection.query(
                    query_texts=[query],
                    n_results=min(limit * 2, 50),
                    where={"role_id": role_id},
                )

                if results["ids"] and results["ids"][0]:
                    # 重新排序记忆
                    vector_memory_ids = results["ids"][0]
                    memory_dict = {m.id: m for m in memories}

                    # 按向量相似度重新排序
                    reordered_memories = []
                    for mem_id in vector_memory_ids:
                        if mem_id in memory_dict:
                            reordered_memories.append(memory_dict[mem_id])

                    # 添加未在向量搜索中的记忆
                    for memory in memories:
                        if memory.id not in vector_memory_ids:
                            reordered_memories.append(memory)

                    memories = reordered_memories[:limit]

            except Exception as e:
                self.logger.error(f"Vector search failed: {e}")

        return memories

    def get_role_identity(self, role_id: str) -> Optional[RoleIdentity]:
        """获取角色身份"""
        return self.identity_cache.get(role_id)

    def build_context_for_conversation(
        self,
        role_id: str,
        current_question: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        """为对话构建上下文"""
        context = {
            "role_identity": None,
            "relevant_memories": [],
            "project_context": None,
            "conversation_summary": "",
            "prompt": "",
        }

        # 获取角色身份
        identity = self.get_role_identity(role_id)
        if identity:
            context["role_identity"] = asdict(identity)

        # 检索相关记忆
        relevant_memories = []

        # 身份记忆（最重要）
        identity_memories = self.retrieve_memories(
            role_id=role_id,
            memory_types=["identity"],
            limit=3,
            min_importance=0.8,
        )
        relevant_memories.extend(identity_memories)

        # 项目相关记忆
        if project_id:
            project_memories = self.retrieve_memories(
                role_id=role_id,
                query=current_question,
                memory_types=["project", "experience"],
                project_id=project_id,
                limit=5,
                min_importance=0.3,
            )
            relevant_memories.extend(project_memories)

            # 获取项目上下文
            project_context = self.project_cache.get(project_id)
            if project_context:
                context["project_context"] = asdict(project_context)

        # 知识和经验记忆
        knowledge_memories = self.retrieve_memories(
            role_id=role_id,
            query=current_question,
            memory_types=["knowledge", "experience"],
            limit=5,
            min_importance=0.4,
        )
        relevant_memories.extend(knowledge_memories)

        # 最近的对话记忆
        recent_memories = self.retrieve_memories(
            role_id=role_id,
            memory_types=["dialogue"],
            session_id=session_id,
            limit=3,
        )
        relevant_memories.extend(recent_memories)

        # 去重并按重要性排序
        unique_memories = {}
        for memory in relevant_memories:
            if memory.id not in unique_memories:
                unique_memories[memory.id] = memory

        sorted_memories = sorted(
            unique_memories.values(),
            key=lambda x: (x.importance, x.timestamp),
            reverse=True,
        )[:10]

        context["relevant_memories"] = [asdict(m) for m in sorted_memories]

        # 构建对话摘要
        if conversation_history:
            context["conversation_summary"] = self._summarize_conversation(
                conversation_history,
            )

        # 生成完整提示词
        if identity:
            context["prompt"] = self._build_prompt(identity, context, current_question)

        return context

    def _summarize_conversation(
        self,
        conversation_history: list[dict[str, str]],
    ) -> str:
        """总结对话历史"""
        if not conversation_history:
            return ""

        # 简单的对话摘要
        summary_parts = []
        for msg in conversation_history[-5:]:  # 最近5条消息
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:100]  # 截取前100字符
            summary_parts.append(f"{role}: {content}")

        return " | ".join(summary_parts)

    def _build_prompt(
        self,
        identity: RoleIdentity,
        context: dict[str, Any],
        question: str,
    ) -> str:
        """构建完整提示词"""
        # 格式化记忆
        memories_text = ""
        if context["relevant_memories"]:
            memory_items = []
            for memory in context["relevant_memories"][:5]:  # 最多5条记忆
                memory_items.append(f"- {memory['content'][:200]}")
            memories_text = "\n".join(memory_items)

        # 格式化项目上下文
        project_text = ""
        if context["project_context"]:
            project = context["project_context"]
            project_text = f"当前项目：{project['project_name']} - {project['description']}"

        # 格式化对话历史
        conversation_text = context.get("conversation_summary", "")

        # 使用模板生成提示词
        prompt = identity.prompt_template.format(
            context=f"{project_text}\n{conversation_text}".strip(),
            memories=memories_text,
            question=question,
        )

        return prompt

    def create_project_context(
        self,
        project_name: str,
        description: str,
        participants: list[str],
    ) -> str:
        """创建项目上下文"""
        project_id = hashlib.md5(f"{project_name}_{time.time()}".encode()).hexdigest()[
            :16
        ]

        project = ProjectContext(
            project_id=project_id,
            project_name=project_name,
            description=description,
            participants=participants,
            start_date=datetime.now().isoformat(),
            status="active",
        )

        # 保存到数据库
        with self.lock:
            self.conn.execute(
                """
                INSERT INTO project_contexts
                (project_id, project_name, description, participants, start_date, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    project.project_id,
                    project.project_name,
                    project.description,
                    json.dumps(project.participants, ensure_ascii=False),
                    project.start_date,
                    project.status,
                    json.dumps(project.metadata, ensure_ascii=False),
                ),
            )
            self.conn.commit()

            # 更新缓存
            self.project_cache[project_id] = project

        # 为所有参与者添加项目记忆
        for role_id in participants:
            self.add_memory(
                role_id=role_id,
                content=f"开始参与项目：{project_name}。项目描述：{description}",
                memory_type="project",
                importance=0.8,
                project_id=project_id,
                tags=["项目开始", project_name],
            )

        self.logger.info(f"Created project context: {project_id} - {project_name}")
        return project_id

    def add_dialogue_memory(
        self,
        role_id: str,
        user_message: str,
        role_response: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """添加对话记忆"""
        # 添加用户消息记忆
        self.add_memory(
            role_id=role_id,
            content=f"用户说：{user_message}",
            memory_type="dialogue",
            importance=0.3,
            project_id=project_id,
            session_id=session_id,
            tags=["对话", "用户输入"],
        )

        # 添加角色回应记忆
        self.add_memory(
            role_id=role_id,
            content=f"我回应：{role_response}",
            memory_type="dialogue",
            importance=0.4,
            project_id=project_id,
            session_id=session_id,
            tags=["对话", "我的回应"],
        )

    def add_experience_memory(
        self,
        role_id: str,
        experience: str,
        project_id: Optional[str] = None,
        importance: float = 0.6,
    ):
        """添加经验记忆"""
        self.add_memory(
            role_id=role_id,
            content=experience,
            memory_type="experience",
            importance=importance,
            project_id=project_id,
            tags=["经验", "学习"],
        )

    def update_role_identity(self, role_id: str, updates: dict[str, Any]) -> bool:
        """更新角色身份"""
        identity = self.identity_cache.get(role_id)
        if not identity:
            return False

        # 更新字段
        for field, value in updates.items():
            if hasattr(identity, field):
                setattr(identity, field, value)

        identity.updated_at = datetime.now().isoformat()

        # 保存到数据库
        with self.lock:
            self.conn.execute(
                """
                UPDATE role_identities SET
                name=?, title=?, personality=?, background=?, core_traits=?,
                speaking_style=?, knowledge_domains=?, prompt_template=?, updated_at=?
                WHERE role_id=?
            """,
                (
                    identity.name,
                    identity.title,
                    json.dumps(identity.personality, ensure_ascii=False),
                    identity.background,
                    json.dumps(identity.core_traits, ensure_ascii=False),
                    identity.speaking_style,
                    json.dumps(identity.knowledge_domains, ensure_ascii=False),
                    identity.prompt_template,
                    identity.updated_at,
                    role_id,
                ),
            )
            self.conn.commit()

        return True

    def get_cross_dialogue_memories(
        self,
        role_id: str,
        project_id: str,
        days_back: int = 30,
    ) -> list[MemoryEntry]:
        """获取跨对话的项目相关记忆"""
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        sql = """
            SELECT * FROM memories
            WHERE role_id = ? AND project_id = ? AND timestamp >= ?
            AND memory_type IN ('project', 'experience', 'knowledge')
            ORDER BY importance DESC, timestamp DESC
            LIMIT 20
        """

        memories = []
        with self.lock:
            cursor = self.conn.execute(sql, [role_id, project_id, cutoff_date])
            for row in cursor.fetchall():
                memory = MemoryEntry(
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
                )
                memories.append(memory)

        return memories

    def cleanup_old_memories(self, days_to_keep: int = 90, min_importance: float = 0.5):
        """清理旧记忆"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()

        with self.lock:
            # 删除低重要性的旧记忆
            cursor = self.conn.execute(
                """
                DELETE FROM memories
                WHERE timestamp < ? AND importance < ? AND memory_type != 'identity'
            """,
                [cutoff_date, min_importance],
            )

            deleted_count = cursor.rowcount
            self.conn.commit()

            # 清理向量存储中的对应记忆
            if self.vector_store and CHROMADB_AVAILABLE:
                try:
                    # 获取所有记忆ID
                    cursor = self.conn.execute("SELECT id FROM memories")
                    valid_ids = {row[0] for row in cursor.fetchall()}

                    # 获取向量存储中的所有ID
                    collection_data = self.memory_collection.get()
                    if collection_data["ids"]:
                        invalid_ids = [
                            id for id in collection_data["ids"] if id not in valid_ids
                        ]
                        if invalid_ids:
                            self.memory_collection.delete(ids=invalid_ids)

                except Exception as e:
                    self.logger.error(f"Failed to cleanup vector store: {e}")

        self.logger.info(f"Cleaned up {deleted_count} old memories")
        return deleted_count

    def export_role_memories(
        self,
        role_id: str,
        file_path: Optional[str] = None,
    ) -> str:
        """导出角色记忆"""
        if not file_path:
            file_path = self.data_dir / f"export_{role_id}_{int(time.time())}.json"

        # 获取角色的所有数据
        identity = self.get_role_identity(role_id)
        memories = self.retrieve_memories(role_id, limit=1000)

        export_data = {
            "role_id": role_id,
            "identity": asdict(identity) if identity else None,
            "memories": [asdict(m) for m in memories],
            "export_timestamp": datetime.now().isoformat(),
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Exported memories for role {role_id} to {file_path}")
        return str(file_path)

    def import_role_memories(self, file_path: str) -> bool:
        """导入角色记忆"""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            role_id = data["role_id"]

            # 导入身份
            if data["identity"]:
                identity_data = data["identity"]
                identity = RoleIdentity(**identity_data)

                with self.lock:
                    self.conn.execute(
                        """
                        INSERT OR REPLACE INTO role_identities
                        (role_id, name, title, personality, background, core_traits,
                         speaking_style, knowledge_domains, prompt_template, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            identity.role_id,
                            identity.name,
                            identity.title,
                            json.dumps(identity.personality, ensure_ascii=False),
                            identity.background,
                            json.dumps(identity.core_traits, ensure_ascii=False),
                            identity.speaking_style,
                            json.dumps(identity.knowledge_domains, ensure_ascii=False),
                            identity.prompt_template,
                            identity.created_at,
                            identity.updated_at,
                        ),
                    )

                    self.identity_cache[role_id] = identity

            # 导入记忆
            for memory_data in data["memories"]:
                memory = MemoryEntry(**memory_data)

                with self.lock:
                    self.conn.execute(
                        """
                        INSERT OR REPLACE INTO memories
                        (id, role_id, content, memory_type, importance, timestamp,
                         project_id, session_id, tags, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                            json.dumps(memory.tags, ensure_ascii=False),
                            json.dumps(memory.metadata, ensure_ascii=False),
                        ),
                    )

            self.conn.commit()
            self.logger.info(f"Imported memories for role {role_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import memories: {e}")
            return False

    def get_memory_statistics(self, role_id: Optional[str] = None) -> dict[str, Any]:
        """获取记忆统计信息"""
        stats = {}

        with self.lock:
            if role_id:
                # 单个角色统计
                cursor = self.conn.execute(
                    """
                    SELECT memory_type, COUNT(*) as count, AVG(importance) as avg_importance
                    FROM memories WHERE role_id = ?
                    GROUP BY memory_type
                """,
                    [role_id],
                )

                stats["role_id"] = role_id
                stats["memory_types"] = {}
                total_memories = 0

                for row in cursor.fetchall():
                    memory_type = row["memory_type"]
                    count = row["count"]
                    avg_importance = row["avg_importance"]

                    stats["memory_types"][memory_type] = {
                        "count": count,
                        "avg_importance": round(avg_importance, 2),
                    }
                    total_memories += count

                stats["total_memories"] = total_memories

            else:
                # 全局统计
                cursor = self.conn.execute(
                    """
                    SELECT COUNT(DISTINCT role_id) as role_count,
                           COUNT(*) as total_memories,
                           AVG(importance) as avg_importance
                    FROM memories
                """,
                )

                row = cursor.fetchone()
                stats["total_roles"] = row["role_count"]
                stats["total_memories"] = row["total_memories"]
                stats["avg_importance"] = round(row["avg_importance"] or 0, 2)

                # 按类型统计
                cursor = self.conn.execute(
                    """
                    SELECT memory_type, COUNT(*) as count
                    FROM memories
                    GROUP BY memory_type
                """,
                )

                stats["memory_types"] = {}
                for row in cursor.fetchall():
                    stats["memory_types"][row["memory_type"]] = row["count"]

        return stats

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


from src.constants import *
