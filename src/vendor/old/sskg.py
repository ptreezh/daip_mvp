import json
import os  # 添加 os 导入
import sqlite3
from threading import Lock
from typing import Any, Optional

import chromadb
import ollama
from chromadb.api.types import EmbeddingFunction

from src.config import (
    CHROMA_PATH,  # 导入正确的变量名
    CHROMADB_COLLECTION_NAME,
    CHROMADB_TOOLS_COLLECTION_NAME,  # 新增：导入工具集合名称
    DATABASE_PATH,  # 导入正确的变量名
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
                # 调用 Ollama 模型的 embedding 端点
                response = self.client.embeddings(model=self.model_name, prompt=text)
                embeddings_list.append(response["embedding"])
            except Exception as e:
                print(f"Error generating embedding for text '{text[:50]}...': {e}")
                # 重新抛出异常，让上层知道嵌入失败
                raise  # 这里需要一个 except 块来捕获异常
        return embeddings_list


class SSKG:
    def __init__(self, db_path: str, chroma_path: str):
        self.db_path = db_path
        self.chroma_path = chroma_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.db_lock = Lock()  # 用于多线程/异步环境下的数据库操作同步

        # ChromaDB 客户端和集合
        self.chroma_client: Optional[chromadb.PersistentClient] = None
        self.summaries_collection: Optional[
            chromadb.api.models.Collection.Collection
        ] = None
        self.tools_collection: Optional[
            chromadb.api.models.Collection.Collection
        ] = None  # 新增：工具集合

        # 初始化 embedding function
        self.embedding_function = OllamaEmbeddingFunction(
            ollama_base_url=OLLAMA_BASE_URL,
            model_name=EMBEDDING_MODEL_NAME,
        )

    def init_db(self):
        """初始化 SQLite 数据库和 ChromaDB 客户端。"""
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.chroma_path, exist_ok=True)

        try:
            # 初始化 SQLite
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self._create_tables()

            # 初始化 ChromaDB
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)

            # 尝试获取现有集合，如果存在则使用现有集合
            try:
                self.summaries_collection = self.chroma_client.get_collection(
                    name=CHROMADB_COLLECTION_NAME,
                )
                print(f"ChromaDB collection '{CHROMADB_COLLECTION_NAME}' loaded.")
            except:
                # 如果集合不存在，创建新集合
                self.summaries_collection = self.chroma_client.create_collection(
                    name=CHROMADB_COLLECTION_NAME,
                    embedding_function=self.embedding_function,
                )
                print(f"ChromaDB collection '{CHROMADB_COLLECTION_NAME}' created.")

            # 初始化工具集合
            try:
                self.tools_collection = self.chroma_client.get_collection(
                    name=CHROMADB_TOOLS_COLLECTION_NAME,
                )
                print(f"ChromaDB collection '{CHROMADB_TOOLS_COLLECTION_NAME}' loaded.")
            except:
                # 如果集合不存在，创建新集合
                self.tools_collection = self.chroma_client.create_collection(
                    name=CHROMADB_TOOLS_COLLECTION_NAME,
                    embedding_function=self.embedding_function,
                )
                print(
                    f"ChromaDB collection '{CHROMADB_TOOLS_COLLECTION_NAME}' created.",
                )

        except Exception as e:
            print(f"数据库初始化失败: {e}")
            # 不重新抛出异常，让系统继续运行
            # 如果ChromaDB有问题，至少SQLite还能工作

    def _create_tables(self):
        """创建 SQLite 数据库表。"""
        if not self.cursor:
            raise RuntimeError("Database cursor not initialized.")

        try:  # 修复：try 块必须有 except 或 finally
            # 对话消息表
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS dialogue_messages (
                    message_id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    content TEXT,
                    tool_calls_json TEXT,
                    tool_call_id TEXT
                )
            """,
            )

            # LLM 总结表
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_summaries (
                    summary_id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    summarized_message_ids TEXT,
                    embedding_present INTEGER NOT NULL
                )
            """,
            )
            self.conn.commit()
            print("SQLite tables created or already exist.")
        except Exception as e:  # 修复：try 块必须有 except 或 finally
            print(f"创建 SQLite 表失败: {e}")
            raise

    def save_dialogue_message(self, message: DialogueMessage):
        """保存 DialogueMessage 到 SQLite。"""
        if not self.conn or not self.cursor:
            raise RuntimeError("Database connection not established.")

        with self.db_lock:
            try:  # 修复：try 块必须有 except 或 finally
                self.cursor.execute(
                    """
                    INSERT INTO dialogue_messages (message_id, role, timestamp, content, tool_calls_json, tool_call_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        message.message_id,
                        message.role,
                        message.timestamp,
                        message.content,
                        message.tool_calls_json,
                        message.tool_call_id,
                    ),
                )
                self.conn.commit()
            except Exception as e:  # 修复：try 块必须有 except 或 finally
                print(f"保存对话消息失败: {e}")
                raise

    def get_all_dialogue_messages(self) -> list[DialogueMessage]:
        """从 SQLite 获取所有 DialogueMessage。"""
        if not self.conn or not self.cursor:
            return []

        with self.db_lock:
            try:  # 修复：try 块必须有 except 或 finally
                self.cursor.execute(
                    "SELECT message_id, role, timestamp, content, tool_calls_json, tool_call_id FROM dialogue_messages ORDER BY timestamp ASC",
                )
                rows = self.cursor.fetchall()
            except Exception as e:  # 修复：try 块必须有 except 或 finally
                print(f"获取所有对话消息失败: {e}")
                raise

        messages = []
        for row in rows:
            messages.append(
                DialogueMessage(
                    message_id=row[0],
                    role=row[1],
                    timestamp=row[2],
                    content=row[3],
                    tool_calls_json=row[4],
                    tool_call_id=row[5],
                ),
            )
        return messages

    def save_summary(self, summary: LLMSummary):
        """保存 LLMSummary 到 SQLite 和 ChromaDB。"""
        if not self.conn or not self.cursor or not self.summaries_collection:
            raise RuntimeError(
                "Database connection or ChromaDB collection not established.",
            )

        with self.db_lock:
            try:  # 修复：try 块必须有 except 或 finally
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

            # 无论嵌入是否成功，都尝试保存到 SQLite
            try:  # 修复：try 块必须有 except 或 finally
                self.cursor.execute(
                    """
                    INSERT OR REPLACE INTO llm_summaries (summary_id, text, timestamp, summarized_message_ids, embedding_present)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        summary.summary_id,
                        summary.text,
                        summary.timestamp,
                        json.dumps(summary.summarized_message_ids),
                        int(summary.embedding_present),
                    ),
                )
                self.conn.commit()
                print(f"Saved summary: {summary.summary_id}")
            except Exception as e:  # 修复：try 块必须有 except 或 finally
                print(f"保存总结到 SQLite 失败: {e}")
                raise

    def get_all_summaries(self) -> list[LLMSummary]:
        """从 SQLite 获取所有 LLM 总结。"""
        if not self.conn or not self.cursor:
            return []

        with self.db_lock:
            try:  # 修复：try 块必须有 except 或 finally
                self.cursor.execute(
                    "SELECT summary_id, text, timestamp, summarized_message_ids, embedding_present FROM llm_summaries ORDER BY timestamp ASC",
                )
                rows = self.cursor.fetchall()
            except Exception as e:  # 修复：try 块必须有 except 或 finally
                print(f"获取所有总结失败: {e}")
                raise

        summaries = []
        for row in rows:
            summaries.append(
                LLMSummary(
                    summary_id=row[0],
                    text=row[1],
                    timestamp=row[2],
                    summarized_message_ids=json.loads(row[3]),
                    embedding_present=bool(row[4]),
                ),
            )
        return summaries

    def search_vector(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """在 ChromaDB 中进行向量相似性搜索。
        :param query: 搜索查询文本。
        :param k: 返回最相似结果的数量。
        :return: 包含文档和距离的字典列表。
        """
        if not self.summaries_collection:
            print(
                "ChromaDB collection is not initialized. Cannot perform vector search.",
            )
            return []

        try:
            results = self.summaries_collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "distances"],
            )

            if results and results["documents"] and results["documents"][0]:
                formatted_results = []
                for i in range(len(results["documents"][0])):
                    formatted_results.append(
                        {
                            "document": results["documents"][0][i],
                            "distance": results["distances"][0][i],
                        },
                    )
                print(f"Querying ChromaDB for: '{query[:20]}...' (top {k} results)")
                print(f"Found {len(formatted_results)} results.")
                return formatted_results
            else:
                print(f"Found 0 results for query: '{query[:20]}...'.")
                return []
        except Exception as e:
            print(f"ERROR: Failed to query data from ChromaDB for '{query[:20]}': {e}")
            return []

    def save_tool_definition_to_vector_db(self, tool_def: dict[str, Any]):
        """将工具定义（特别是其描述）添加到 ChromaDB 的工具集合中。
        我们将工具的名称作为 ID，描述作为 document。
        """
        if not self.tools_collection:
            raise RuntimeError("ChromaDB tools collection not initialized.")

        tool_name = tool_def["function"]["name"]
        tool_description = tool_def["function"]["description"]

        try:
            self.tools_collection.add(
                documents=[tool_description],
                metadatas=[{"tool_name": tool_name}],
                ids=[tool_name],  # 使用工具名称作为ID，确保唯一性
            )
            print(
                f"Tool '{tool_name}' embedded and added to ChromaDB tools collection.",
            )
        except Exception as e:
            print(
                f"WARNING: Could not add tool '{tool_name}' to ChromaDB tools collection: {e}",
            )

    def search_tools_by_query(self, query: str, k: int = 3) -> list[str]:
        """根据查询文本在 ChromaDB 的工具集合中搜索最相关的工具名称。
        :param query: 用户查询文本。
        :param k: 返回最相似工具的数量。
        :return: 最相关的工具名称列表。
        """
        if not self.tools_collection:
            print(
                "ChromaDB tools collection is not initialized. Cannot perform tool search.",
            )
            return []

        try:
            results = self.tools_collection.query(
                query_texts=[query],
                n_results=k,
                include=["metadatas"],  # 只包含元数据，因为我们只需要工具名称
            )

            relevant_tool_names = []
            if results and results["metadatas"] and results["metadatas"][0]:
                for metadata_item in results["metadatas"][0]:
                    if "tool_name" in metadata_item:
                        relevant_tool_names.append(metadata_item["tool_name"])

            print(
                f"Searched for tools with query '{query[:50]}...'. Found {len(relevant_tool_names)} relevant tools: {relevant_tool_names}",
            )
            return relevant_tool_names

        except Exception as e:
            print(f"ERROR: Failed to query tools from ChromaDB for '{query[:20]}': {e}")
            return []

    def close(self):
        """关闭数据库连接。"""
        if self.conn:
            try:  # 修复：try 块必须有 except 或 finally
                self.conn.close()
                self.conn = None
                self.cursor = None
                print("SQLite connection closed.")
            except Exception as e:  # 修复：try 块必须有 except 或 finally
                print(f"关闭 SQLite 连接失败: {e}")
        print("ChromaDB client does not require explicit closing for PersistentClient.")

    def get_tasks_by_description(self, description: str) -> list:
        """根据任务描述查询任务表，返回所有匹配的行。"""
        if not self.conn or not self.cursor:
            return []
        with self.db_lock:
            try:
                self.cursor.execute(
                    "SELECT * FROM tasks WHERE description=?",
                    (description,),
                )
                rows = self.cursor.fetchall()
            except Exception as e:
                print(f"获取任务失败: {e}")
                return []
        return rows


# 单例实例，供外部直接使用
sskg_instance = SSKG(db_path=DATABASE_PATH, chroma_path=CHROMA_PATH)
