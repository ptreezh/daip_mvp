import json
import os
import uuid
from datetime import datetime
from threading import Lock
from typing import Any, Optional

import chromadb
import ollama
from chromadb.api.types import EmbeddingFunction
from sqlalchemy.orm import Session
from sqlmodel import Field as SQLField
from sqlmodel import SQLModel, select

from src.config import (
    CHROMADB_COLLECTION_NAME,
    CHROMADB_TOOLS_COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    OLLAMA_BASE_URL,
)
from src.models import DialogueMessage, LLMSummary


class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, ollama_base_url: str, model_name: str):
        self.ollama_base_url = ollama_base_url
        self.model_name = model_name
        self.client = ollama.Client(host=self.ollama_base_url)

    def __call__(self, input: list[str]) -> list[list[float]]:
        embeddings_list = []
        for text in input:
            try:
                response = self.client.embeddings(model=self.model_name, prompt=text)
                embeddings_list.append(response["embedding"])
            except Exception as e:
                print(f"Error generating embedding for text '{text[:50]}...': {e}")
                raise
        return embeddings_list


class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    task_id: str = SQLField(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    description: str = ""
    status: str = "not_started"  # 看板状态
    progress: int = 0
    assigned_to: Optional[str] = None
    parent_id: Optional[str] = None  # 支持递归分解
    children_ids: str = SQLField(default="[]")  # JSON string to store list
    related_knowledge: str = SQLField(default="[]")  # JSON string to store list
    related_tools: str = SQLField(default="[]")  # JSON string to store list
    comments: str = SQLField(default="[]")  # JSON string to store list
    signatures: str = SQLField(default="[]")  # JSON string to store list
    created_at: str = SQLField(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = SQLField(default_factory=lambda: datetime.now().isoformat())

    @property
    def children_ids_list(self) -> list[str]:
        """Get children_ids as a list"""
        try:
            return json.loads(self.children_ids) if self.children_ids else []
        except:
            return []

    @children_ids_list.setter
    def children_ids_list(self, value: list[str]):
        """Set children_ids from a list"""
        self.children_ids = json.dumps(value)

    @property
    def related_knowledge_list(self) -> list[str]:
        """Get related_knowledge as a list"""
        try:
            return json.loads(self.related_knowledge) if self.related_knowledge else []
        except:
            return []

    @related_knowledge_list.setter
    def related_knowledge_list(self, value: list[str]):
        """Set related_knowledge from a list"""
        self.related_knowledge = json.dumps(value)

    @property
    def related_tools_list(self) -> list[str]:
        """Get related_tools as a list"""
        try:
            return json.loads(self.related_tools) if self.related_tools else []
        except:
            return []

    @related_tools_list.setter
    def related_tools_list(self, value: list[str]):
        """Set related_tools from a list"""
        self.related_tools = json.dumps(value)

    @property
    def comments_list(self) -> list[dict]:
        """Get comments as a list"""
        try:
            return json.loads(self.comments) if self.comments else []
        except:
            return []

    @comments_list.setter
    def comments_list(self, value: list[dict]):
        """Set comments from a list"""
        self.comments = json.dumps(value)

    @property
    def signatures_list(self) -> list[dict]:
        """Get signatures as a list"""
        try:
            return json.loads(self.signatures) if self.signatures else []
        except:
            return []

    @signatures_list.setter
    def signatures_list(self, value: list[dict]):
        """Set signatures from a list"""
        self.signatures = json.dumps(value)


class SSKG:
    def __init__(self, db_path: str, chroma_path: str):
        self.db_path = db_path
        self.chroma_path = chroma_path
        self.db_lock = Lock()

        # ChromaDB 客户端和集合
        self.chroma_client: Optional[chromadb.PersistentClient] = None
        self.summaries_collection: Optional[
            chromadb.api.models.Collection.Collection
        ] = None
        self.tools_collection: Optional[
            chromadb.api.models.Collection.Collection
        ] = None

        # 初始化 embedding function
        self.embedding_function = OllamaEmbeddingFunction(
            ollama_base_url=OLLAMA_BASE_URL,
            model_name=EMBEDDING_MODEL_NAME,
        )

    def init_db(self):
        """初始化 ChromaDB 客户端。"""
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.chroma_path, exist_ok=True)

        try:
            # 初始化 ChromaDB
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            self.summaries_collection = self.chroma_client.get_or_create_collection(
                name=CHROMADB_COLLECTION_NAME,
                embedding_function=self.embedding_function,
            )
            print(f"ChromaDB collection '{CHROMADB_COLLECTION_NAME}' loaded/created.")

            # 初始化工具集合
            self.tools_collection = self.chroma_client.get_or_create_collection(
                name=CHROMADB_TOOLS_COLLECTION_NAME,
                embedding_function=self.embedding_function,
            )
            print(
                f"ChromaDB collection '{CHROMADB_TOOLS_COLLECTION_NAME}' loaded/created.",
            )

        except Exception as e:
            print(f"数据库初始化失败: {e}")
            raise

    def save_dialogue_message(self, message: DialogueMessage, db: Session):
        """保存 DialogueMessage 到数据库。"""
        with self.db_lock:
            try:
                db.add(message)
                db.commit()
                db.refresh(message)
            except Exception as e:
                print(f"保存对话消息失败: {e}")
                db.rollback()
                raise

    def get_all_dialogue_messages(self, db: Session = None) -> list[DialogueMessage]:
        """从数据库获取所有 DialogueMessage。"""
        if db is None:
            # 兼容无数据库环境（如集成测试）
            return []
        with self.db_lock:
            try:
                statement = select(DialogueMessage).order_by(DialogueMessage.timestamp)
                result = db.exec(statement)
                return result.all()
            except Exception as e:
                print(f"获取所有对话消息失败: {e}")
                raise

    def save_summary(self, summary: LLMSummary, db: Session):
        """保存 LLMSummary 到数据库和 ChromaDB。"""
        if not self.summaries_collection:
            raise RuntimeError("ChromaDB collection not established.")

        with self.db_lock:
            try:
                # 保存到 ChromaDB
                self.summaries_collection.add(
                    documents=[summary.text],
                    metadatas=[
                        {
                            "summary_id": summary.summary_id,
                            "timestamp": summary.timestamp,
                        },
                    ],
                    ids=[summary.summary_id],
                )
                summary.embedding_present = True
                print(f"Summary '{summary.summary_id}' embedded and added to ChromaDB.")
            except Exception as e:
                print(
                    f"警告: 无法为总结 '{summary.summary_id}' 生成或添加嵌入: {e}. 'embedding_present' 将为 False。",
                )
                summary.embedding_present = False

            # 保存到数据库
            try:
                db.add(summary)
                db.commit()
                db.refresh(summary)
            except Exception as e:
                print(f"保存总结到数据库失败: {e}")
                db.rollback()
                raise

    def get_all_summaries(self, db: Session = None) -> list[LLMSummary]:
        """从数据库获取所有 LLMSummary。"""
        if db is None:
            # 兼容无数据库环境（如集成测试）
            return []
        with self.db_lock:
            try:
                statement = select(LLMSummary).order_by(LLMSummary.timestamp)
                result = db.exec(statement)
                return result.all()
            except Exception as e:
                print(f"获取所有总结失败: {e}")
                raise

    def search_vector(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """在 ChromaDB 中搜索向量。"""
        if not self.summaries_collection:
            return []

        try:
            results = self.summaries_collection.query(query_texts=[query], n_results=k)

            search_results = []
            if results["ids"] and results["ids"][0]:
                for i, summary_id in enumerate(results["ids"][0]):
                    search_results.append(
                        {
                            "summary_id": summary_id,
                            "text": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "distance": results["distances"][0][i]
                            if "distances" in results
                            else None,
                        },
                    )

            return search_results
        except Exception as e:
            print(f"向量搜索失败: {e}")
            return []

    def save_tool_definition_to_vector_db(self, tool_def: dict[str, Any]):
        """将工具定义保存到 ChromaDB 工具集合。"""
        if not self.tools_collection:
            return

        try:
            tool_name = tool_def["function"]["name"]
            tool_description = tool_def["function"].get("description", "")

            # 使用工具名称和描述作为文档
            document = f"{tool_name}: {tool_description}"

            self.tools_collection.add(
                documents=[document],
                metadatas=[{"tool_name": tool_name, "tool_def": json.dumps(tool_def)}],
                ids=[tool_name],
            )
            print(f"Tool '{tool_name}' added to vector database.")
        except Exception as e:
            print(f"保存工具定义到向量数据库失败: {e}")

    def search_tools_by_query(self, query: str, k: int = 3) -> list[str]:
        """根据查询搜索相关工具。"""
        if not self.tools_collection:
            return []

        try:
            results = self.tools_collection.query(query_texts=[query], n_results=k)

            tool_names = []
            if results["ids"] and results["ids"][0]:
                tool_names = results["ids"][0]

            return tool_names
        except Exception as e:
            print(f"工具搜索失败: {e}")
            return []

    def close(self):
        """关闭数据库连接。"""
        if self.chroma_client:
            self.chroma_client = None
        print("SSKG connections closed.")

    def get_tasks_by_description(self, description: str, db: Session) -> list:
        """根据描述搜索任务（向后兼容）。"""
        with self.db_lock:
            try:
                # 这里需要实现任务搜索逻辑
                # 由于原代码中没有Task模型，这里返回空列表
                return []
            except Exception as e:
                print(f"搜索任务失败: {e}")
                return []

    def add_knowledge_block(self, content: str, meta: dict) -> str:
        """添加知识块到ChromaDB，返回block_id"""
        if not self.summaries_collection:
            raise RuntimeError("ChromaDB collection not established.")
        block_id = str(uuid.uuid4())
        metadata = meta.copy()
        metadata["block_id"] = block_id
        self.summaries_collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[block_id],
        )
        return block_id

    def get_knowledge_blocks_by_session(self, session_id: str) -> list:
        """获取指定session_id的所有知识块"""
        if not self.summaries_collection:
            return []
        results = self.summaries_collection.get(
            include=["metadatas", "documents", "ids"],
        )
        blocks = []
        for i, meta in enumerate(results["metadatas"]):
            if meta.get("session_id") == session_id:
                blocks.append(
                    {
                        "id": results["ids"][i],
                        "content": results["documents"][i],
                        "metadata": meta,
                    },
                )
        return blocks

    def delete_knowledge_block(self, block_id: str, session_id: str = None) -> bool:
        """删除指定block_id的知识块，若session_id给定则校验归属"""
        if not self.summaries_collection:
            return False
        # 校验归属
        try:
            results = self.summaries_collection.get(
                ids=[block_id],
                include=["metadatas"],
            )
            if not results["ids"] or not results["metadatas"]:
                return False
            meta = results["metadatas"][0]
            if session_id and meta.get("session_id") != session_id:
                return False
            self.summaries_collection.delete(ids=[block_id])
            return True
        except Exception as e:
            print(f"删除知识块失败: {e}")
            return False

    def create_task(
        self,
        db: Session,
        title: str,
        description: str = "",
        parent_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
    ) -> Task:
        """创建任务，支持递归分解（parent_id）"""
        with self.db_lock:
            task = Task(
                title=title,
                description=description,
                parent_id=parent_id,
                assigned_to=assigned_to,
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            # 更新父任务的children_ids
            if parent_id:
                parent = db.get(Task, parent_id)
                if parent:
                    children_list = parent.children_ids_list
                    children_list.append(task.task_id)
                    parent.children_ids_list = children_list
                    db.add(parent)
                    db.commit()
            return task

    def update_task(self, db: Session, task_id: str, **kwargs) -> Optional[Task]:
        """更新任务（状态、进度、分工、父子关系等）"""
        with self.db_lock:
            task = db.get(Task, task_id)
            if not task:
                return None
            for k, v in kwargs.items():
                if hasattr(task, k):
                    setattr(task, k, v)
            task.updated_at = datetime.now().isoformat()
            db.add(task)
            db.commit()
            db.refresh(task)
            return task

    def get_task_tree(self, db: Session, root_id: Optional[str] = None) -> list[Task]:
        """递归获取项目/任务树（可用于前端树状+看板视图）"""

        def _get_subtree(task: Task) -> dict:
            children = [
                db.get(Task, cid) for cid in task.children_ids_list if db.get(Task, cid)
            ]
            return {
                **task.dict(),
                "children": [_get_subtree(child) for child in children],
            }

        if root_id:
            root = db.get(Task, root_id)
            return [_get_subtree(root)] if root else []
        else:
            roots = db.exec(select(Task).where(Task.parent_id == None)).all()
            return [_get_subtree(r) for r in roots]

    def list_tasks(
        self,
        db: Session,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
    ) -> list[Task]:
        """按条件检索任务（支持看板分栏、分工筛选等）"""
        q = select(Task)
        if status:
            q = q.where(Task.status == status)
        if assigned_to:
            q = q.where(Task.assigned_to == assigned_to)
        return db.exec(q).all()

    def add_task_comment(self, db: Session, task_id: str, user: str, comment: str):
        with self.db_lock:
            task = db.get(Task, task_id)
            if not task:
                return False
            comments_list = task.comments_list
            comments_list.append(
                {"user": user, "content": comment, "time": datetime.now().isoformat()},
            )
            task.comments_list = comments_list
            db.add(task)
            db.commit()
            return True

    def sign_task(self, db: Session, task_id: str, expert: str):
        with self.db_lock:
            task = db.get(Task, task_id)
            if not task:
                return False
            signatures_list = task.signatures_list
            signatures_list.append(
                {"expert": expert, "time": datetime.now().isoformat()},
            )
            task.signatures_list = signatures_list
            db.add(task)
            db.commit()
            return True
