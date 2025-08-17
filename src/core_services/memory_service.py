"""@Time    : 2025-07-04 10:00:00
@Author  : DAIP-LIVE Team
@File    : memory_service.py
@Description:
    Manages the memory for virtual roles, including identity, dialogue, and knowledge.
    This is the core memory service for the DAIP-LIVE MVP.
"""

import hashlib
import json
import logging
import sqlite3
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from src.models import PendingFact  # Assuming PendingFact model exists

from .sskg_manager import SSKGManager

try:
    import chromadb
    from chromadb.config import Settings

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available, using fallback memory storage")


@dataclass
class MemoryEntry:
    """A single entry in the memory bank."""

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
    """Defines the core identity of a role."""

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
    """Defines the context of a project."""

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


class MemoryService:
    """Role Memory Bank Service for the DAIP-MVP."""

    def __init__(self, data_dir: str = "data/memory_banks"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Thread-safe lock for database and graph operations
        self.lock = threading.Lock()

        # Database connection
        self.db_path = self.data_dir / "memory_bank.db"
        self.conn = None
        self._init_database()

        # Semantic Knowledge Graph
        self.sskg_path = self.data_dir / "sskg.graphml"
        self.sskg_manager = SSKGManager(graph_path=self.sskg_path)

        # Vector store
        self.vector_store = None
        if CHROMADB_AVAILABLE:
            self._init_vector_store()

        # In-memory cache
        self.memory_cache: dict[str, list[MemoryEntry]] = defaultdict(list)
        self.identity_cache: dict[str, RoleIdentity] = {}
        self.project_cache: dict[str, ProjectContext] = {}


        self.logger = logging.getLogger(__name__)
        self.logger.info(f"MemoryService initialized. DB: {self.db_path}, SSKG: {self.sskg_path}")
        # Load caches
        self._load_caches()

    def _init_database(self):
        """Initializes the SQLite database."""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # Create tables
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
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS pending_facts (
                id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                source_metadata TEXT,
                status TEXT NOT NULL DEFAULT 'pending', -- pending, approved, rejected
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_pending_facts_status ON pending_facts(status);
            """
        )
        self.conn.commit()

    def _init_vector_store(self):
        """Initializes the ChromaDB vector store."""
        try:
            chroma_path = self.data_dir / "chroma_db"
            self.vector_store = chromadb.PersistentClient(
                path=str(chroma_path),
                settings=Settings(anonymized_telemetry=False),
            )

            # Create collection
            try:
                self.memory_collection = self.vector_store.get_collection(
                    "role_memories",
                )
            except Exception:
                self.memory_collection = self.vector_store.create_collection(
                    name="role_memories",
                    metadata={"description": "Role memory embeddings"},
                )

        except Exception as e:
            self.logger.error(f"Failed to initialize vector store: {e}")
            self.vector_store = None

    def _load_caches(self):
        """Loads identities and projects into the in-memory cache."""
        with self.lock:
            # Load identity cache
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

            # Load project cache
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
        """Creates or updates a role's identity."""
        role_id = role_data.get("id") or role_data.get("role_id")
        if not role_id:
            raise ValueError("Role ID is required")

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
            self.identity_cache[role_id] = identity

        self.add_memory(
            role_id=role_id,
            content=f"我是{identity.name}，{identity.title}。{identity.background}",
            memory_type="identity",
            importance=1.0,
            tags=["身份", "基础信息"],
        )

        return identity

    def _extract_personality(self, role_data: dict[str, Any]) -> dict[str, Any]:
        """Infers personality traits from role data."""
        personality = {}
        description = role_data.get("description", "") + " " + role_data.get("bio", "")
        traits = {
            "analytical": ["分析", "数据", "逻辑", "研究", "analysis", "data", "research"],
            "creative": ["创意", "设计", "艺术", "创新", "creative", "design", "innovation"],
            "leadership": ["领导", "管理", "团队", "项目", "leadership", "management", "team"],
            "technical": ["技术", "开发", "工程", "编程", "technical", "development", "programming"],
            "communicative": ["沟通", "交流", "演讲", "表达", "communication", "speaking"],
        }
        for trait, keywords in traits.items():
            score = sum(1 for keyword in keywords if keyword.lower() in description.lower())
            if score > 0:
                personality[trait] = min(score / len(keywords), 1.0)
        return personality

    def _infer_speaking_style(self, role_data: dict[str, Any]) -> str:
        """Infers a speaking style from role data."""
        category = role_data.get("category", "").lower()
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
        """Generates a default prompt template for a role."""
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
        template += """

请以{name}的身份回应，保持角色的专业性和个性特点。在回答时：
1. 运用你的专业知识和经验
2. 保持角色的说话风格和思维方式
3. 结合相关的项目记忆和对话历史
4. 如果涉及你不熟悉的领域，诚实说明并提供可能的建议

当前对话上下文：{context}
相关记忆：{memories}
用户问题：{question}"""
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
        """Adds a memory entry to the bank."""
        memory_id = hashlib.md5(f"{role_id}_{content}_{time.time()}".encode()).hexdigest()
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

        with self.lock:
            self.conn.execute(
                """
                INSERT INTO memories
                (id, role_id, content, memory_type, importance, timestamp,
                 project_id, session_id, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    memory.id, memory.role_id, memory.content, memory.memory_type,
                    memory.importance, memory.timestamp, memory.project_id,
                    memory.session_id, json.dumps(memory.tags, ensure_ascii=False),
                    json.dumps(memory.metadata, ensure_ascii=False),
                ),
            )
            self.conn.commit()
            self.memory_cache[role_id].append(memory)
            if len(self.memory_cache[role_id]) > 100:
                self.memory_cache[role_id] = sorted(
                    self.memory_cache[role_id],
                    key=lambda x: (x.importance, x.timestamp),
                    reverse=True,
                )[:100]

        if self.vector_store and CHROMADB_AVAILABLE:
            try:
                self.memory_collection.add(
                    documents=[content],
                    metadatas=[{
                        "role_id": role_id, "memory_type": memory_type,
                        "importance": importance, "timestamp": memory.timestamp,
                        "project_id": project_id or "", "session_id": session_id or "",
                    }],
                    ids=[memory_id],
                )
            except Exception as e:
                self.logger.error(f"Failed to add memory to vector store: {e}")

        self.logger.info(f"Added memory for role {role_id}: {memory_type}")
        return memory_id

    def add_token_usage_memory(
        self,
        role_id: str,
        token_usage_info: dict[str, Any],
        session_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> str:
        """Adds token usage information as a memory entry for conversation tracking.
        
        Args:
            role_id: The role that used the tokens
            token_usage_info: Dictionary containing token usage details
            session_id: Optional session identifier
            project_id: Optional project identifier
            
        Returns:
            Memory ID of the stored token usage entry

        """
        content = f"Token usage: {token_usage_info.get('total_tokens', 0)} tokens " \
                 f"(input: {token_usage_info.get('input_tokens', 0)}, " \
                 f"output: {token_usage_info.get('output_tokens', 0)}) " \
                 f"for model {token_usage_info.get('model', 'unknown')}"

        metadata = {
            "token_usage": token_usage_info,
            "cost_estimate": token_usage_info.get("estimated_cost", 0.0),
            "model": token_usage_info.get("model", "unknown")
        }

        return self.add_memory(
            role_id=role_id,
            content=content,
            memory_type="token_usage",
            importance=0.1,  # Low importance for token tracking
            project_id=project_id,
            session_id=session_id,
            tags=["token_usage", "conversation_tracking"],
            metadata=metadata
        )

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
        """Retrieves memories based on various filters."""
        memories = []
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
                memories.append(MemoryEntry(
                    id=row["id"], role_id=row["role_id"], content=row["content"],
                    memory_type=row["memory_type"], importance=row["importance"],
                    timestamp=row["timestamp"], project_id=row["project_id"],
                    session_id=row["session_id"], tags=json.loads(row["tags"] or "[]"),
                    metadata=json.loads(row["metadata"] or "{}"),
                ))

        if query and self.vector_store and CHROMADB_AVAILABLE:
            try:
                results = self.memory_collection.query(
                    query_texts=[query], n_results=min(limit * 2, 50),
                    where={"role_id": role_id},
                )
                if results["ids"] and results["ids"][0]:
                    vector_memory_ids = results["ids"][0]
                    memory_dict = {m.id: m for m in memories}
                    reordered_memories = [memory_dict[mem_id] for mem_id in vector_memory_ids if mem_id in memory_dict]
                    for memory in memories:
                        if memory.id not in vector_memory_ids:
                            reordered_memories.append(memory)
                    memories = reordered_memories[:limit]
            except Exception as e:
                self.logger.error(f"Vector search failed: {e}")

        return memories

    def add_fact_to_sskg(self, subject: str, predicate: str, obj: str, metadata: Optional[dict[str, Any]] = None):
        """Adds a structured fact to the Semantic Structured Knowledge Graph.

        This is a direct interface to the underlying SSKGManager. It is thread-safe.
        """
        with self.lock:
            self.sskg_manager.add_fact(subject, predicate, obj, metadata)

    def query_sskg(self, subject: str, predicate: Optional[str] = None) -> list[dict[str, Any]]:
        """Queries the SSKG for facts related to a subject. It is thread-safe.
        """
        with self.lock:
            return self.sskg_manager.query(subject, predicate)

    def add_fact_to_staging(
        self, subject: str, predicate: str, obj: str, confidence: float, status: str, metadata: Optional[dict[str, Any]] = None
    ) -> str:
        """Adds a fact to the staging table with a specific status ('pending' or 'rejected').
        """
        if status not in ["pending", "rejected"]:
            raise ValueError("Status must be 'pending' or 'rejected'.")

        with self.lock:
            fact_id = hashlib.md5(f"{subject}_{predicate}_{obj}_{time.time()}".encode()).hexdigest()
            self.conn.execute(
                """
                INSERT INTO pending_facts (id, subject, predicate, object, source_metadata, status, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (fact_id, subject, predicate, obj, json.dumps(metadata or {}), status, confidence),
            )
            self.conn.commit()
            self.logger.info(f"Added fact '{fact_id}' to staging with status '{status}'.")
            return fact_id

    def get_pending_facts(self, limit: int = 50, offset: int = 0) -> list[PendingFact]:
        """Retrieves a list of facts with 'pending' status."""
        with self.lock:
            cursor = self.conn.execute(
                "SELECT * FROM pending_facts WHERE status = 'pending' ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = cursor.fetchall()
            return [PendingFact(**dict(row)) for row in rows]

    def get_pending_fact_by_id(self, fact_id: str) -> Optional[PendingFact]:
        """Retrieves a single pending fact by its ID."""
        with self.lock:
            cursor = self.conn.execute("SELECT * FROM pending_facts WHERE id = ?", (fact_id,))
            row = cursor.fetchone()
            return PendingFact(**dict(row)) if row else None

    def update_pending_fact_status(self, fact_id: str, status: str) -> bool:
        """Updates the status of a pending fact (e.g., to 'approved' or 'rejected').
        Returns True if a row was updated, False otherwise.
        """
        if status not in ["approved", "rejected"]:
            raise ValueError("Status must be 'approved' or 'rejected'.")

        with self.lock:
            cursor = self.conn.execute(
                "UPDATE pending_facts SET status = ?, updated_at = ? WHERE id = ?",
                (status, datetime.now().isoformat(), fact_id)
            )
            self.conn.commit()
            return cursor.rowcount > 0

    def approve_fact(self, fact_id: str) -> bool:
        """Approves a fact: moves it to the SSKG and updates its status.
        """
        pending_fact = self.get_pending_fact_by_id(fact_id)
        if not pending_fact or pending_fact.status != 'pending':
            self.logger.warning(f"Could not approve fact '{fact_id}': not found or not in pending state.")
            return False

        with self.lock:
            # Add to permanent SSKG
            self.add_fact_to_sskg(
                subject=pending_fact.subject,
                predicate=pending_fact.predicate,
                obj=pending_fact.object,
                metadata=pending_fact.source_metadata
            )
            # Update status in pending table
            self.update_pending_fact_status(fact_id, "approved")
            self.logger.info(f"Approved fact '{fact_id}' and added to SSKG.")
            return True

    def close(self):
        """Closes the database connection and saves the knowledge graph."""
        self.logger.info("Closing MemoryService: saving SSKG and closing DB connection.")
        with self.lock:
            if self.sskg_manager:
                self.sskg_manager.save_graph()

        if self.conn:
            self.conn.close()
