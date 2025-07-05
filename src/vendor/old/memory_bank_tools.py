"""记忆银行工具定义
为虚拟角色提供通过工具调用接口操作记忆银行的能力
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MemoryBankTools:
    """记忆银行工具集合"""

    def __init__(self, memory_bank_path: str = "memory_bank"):
        self.memory_bank_path = Path(memory_bank_path)
        self.shared_path = self.memory_bank_path / "shared"
        self.private_path = self.memory_bank_path / "private"

        # 确保目录存在
        self.shared_path.mkdir(parents=True, exist_ok=True)
        self.private_path.mkdir(parents=True, exist_ok=True)

    def get_shared_memory(self, filename: str) -> dict[str, Any]:
        """获取共享记忆银行文件内容

        Args:
        ----
            filename: 文件名（如 "project_brief.md"）

        Returns:
        -------
            包含文件内容和元数据的字典

        """
        try:
            file_path = self.shared_path / filename
            if not file_path.exists():
                return {
                    "status": "error",
                    "message": f"文件不存在: {filename}",
                    "content": None,
                    "metadata": {
                        "exists": False,
                        "path": str(file_path),
                        "timestamp": datetime.now().isoformat(),
                    },
                }

            content = file_path.read_text(encoding="utf-8")
            stat = file_path.stat()

            return {
                "status": "success",
                "content": content,
                "metadata": {
                    "exists": True,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "timestamp": datetime.now().isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"读取共享记忆文件失败: {e}")
            return {
                "status": "error",
                "message": f"读取文件失败: {e!s}",
                "content": None,
                "metadata": {
                    "exists": False,
                    "path": str(self.shared_path / filename),
                    "timestamp": datetime.now().isoformat(),
                },
            }

    def set_shared_memory(self, filename: str, content: str) -> dict[str, Any]:
        """设置共享记忆银行文件内容

        Args:
        ----
            filename: 文件名（如 "project_brief.md"）
            content: 文件内容

        Returns:
        -------
            操作结果字典

        """
        try:
            file_path = self.shared_path / filename

            # 创建备份
            if file_path.exists():
                backup_path = (
                    self.memory_bank_path
                    / "backup"
                    / f"{filename}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                backup_path.write_text(
                    file_path.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )

            # 写入新内容
            file_path.write_text(content, encoding="utf-8")

            return {
                "status": "success",
                "message": f"文件 {filename} 已更新",
                "metadata": {
                    "path": str(file_path),
                    "size": len(content),
                    "timestamp": datetime.now().isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"写入共享记忆文件失败: {e}")
            return {
                "status": "error",
                "message": f"写入文件失败: {e!s}",
                "metadata": {
                    "path": str(self.shared_path / filename),
                    "timestamp": datetime.now().isoformat(),
                },
            }

    def get_private_memory(self, role_id: str, filename: str) -> dict[str, Any]:
        """获取私有记忆银行文件内容

        Args:
        ----
            role_id: 角色ID（如 "project_coordinator_001"）
            filename: 文件名

        Returns:
        -------
            包含文件内容和元数据的字典

        """
        try:
            role_path = self.private_path / role_id
            file_path = role_path / filename

            if not file_path.exists():
                return {
                    "status": "error",
                    "message": f"私有文件不存在: {role_id}/{filename}",
                    "content": None,
                    "metadata": {
                        "exists": False,
                        "role_id": role_id,
                        "path": str(file_path),
                        "timestamp": datetime.now().isoformat(),
                    },
                }

            content = file_path.read_text(encoding="utf-8")
            stat = file_path.stat()

            return {
                "status": "success",
                "content": content,
                "metadata": {
                    "exists": True,
                    "role_id": role_id,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "timestamp": datetime.now().isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"读取私有记忆文件失败: {e}")
            return {
                "status": "error",
                "message": f"读取私有文件失败: {e!s}",
                "content": None,
                "metadata": {
                    "role_id": role_id,
                    "path": str(self.private_path / role_id / filename),
                    "timestamp": datetime.now().isoformat(),
                },
            }

    def set_private_memory(
        self,
        role_id: str,
        filename: str,
        content: str,
    ) -> dict[str, Any]:
        """设置私有记忆银行文件内容

        Args:
        ----
            role_id: 角色ID
            filename: 文件名
            content: 文件内容

        Returns:
        -------
            操作结果字典

        """
        try:
            role_path = self.private_path / role_id
            role_path.mkdir(parents=True, exist_ok=True)

            file_path = role_path / filename

            # 创建备份
            if file_path.exists():
                backup_path = (
                    self.memory_bank_path
                    / "backup"
                    / role_id
                    / f"{filename}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                backup_path.write_text(
                    file_path.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )

            # 写入新内容
            file_path.write_text(content, encoding="utf-8")

            return {
                "status": "success",
                "message": f"私有文件 {role_id}/{filename} 已更新",
                "metadata": {
                    "role_id": role_id,
                    "path": str(file_path),
                    "size": len(content),
                    "timestamp": datetime.now().isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"写入私有记忆文件失败: {e}")
            return {
                "status": "error",
                "message": f"写入私有文件失败: {e!s}",
                "metadata": {
                    "role_id": role_id,
                    "path": str(self.private_path / role_id / filename),
                    "timestamp": datetime.now().isoformat(),
                },
            }

    def search_memory_bank(
        self,
        query: str,
        role_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """搜索记忆银行内容

        Args:
        ----
            query: 搜索查询
            role_id: 可选的角色ID，限制搜索范围

        Returns:
        -------
            搜索结果字典

        """
        try:
            results = {
                "shared_memory": [],
                "private_memory": [],
                "query": query,
                "timestamp": datetime.now().isoformat(),
            }

            # 搜索共享记忆
            for file_path in self.shared_path.glob("*.md"):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if query.lower() in content.lower():
                        results["shared_memory"].append(
                            {
                                "filename": file_path.name,
                                "path": str(file_path),
                                "match_count": content.lower().count(query.lower()),
                            },
                        )
                except Exception as e:
                    logger.warning(f"搜索共享文件失败 {file_path}: {e}")

            # 搜索私有记忆
            if role_id:
                role_path = self.private_path / role_id
                if role_path.exists():
                    for file_path in role_path.glob("*.md"):
                        try:
                            content = file_path.read_text(encoding="utf-8")
                            if query.lower() in content.lower():
                                results["private_memory"].append(
                                    {
                                        "filename": file_path.name,
                                        "path": str(file_path),
                                        "match_count": content.lower().count(
                                            query.lower(),
                                        ),
                                    },
                                )
                        except Exception as e:
                            logger.warning(f"搜索私有文件失败 {file_path}: {e}")

            return {
                "status": "success",
                "results": results,
                "total_matches": len(results["shared_memory"])
                + len(results["private_memory"]),
            }
        except Exception as e:
            logger.error(f"搜索记忆银行失败: {e}")
            return {
                "status": "error",
                "message": f"搜索失败: {e!s}",
                "results": {"shared_memory": [], "private_memory": []},
                "total_matches": 0,
            }

    def list_memory_files(self, role_id: Optional[str] = None) -> dict[str, Any]:
        """列出记忆银行文件

        Args:
        ----
            role_id: 可选的角色ID，限制列表范围

        Returns:
        -------
            文件列表字典

        """
        try:
            files = {
                "shared_memory": [],
                "private_memory": [],
                "timestamp": datetime.now().isoformat(),
            }

            # 列出共享记忆文件
            for file_path in self.shared_path.glob("*.md"):
                stat = file_path.stat()
                files["shared_memory"].append(
                    {
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    },
                )

            # 列出私有记忆文件
            if role_id:
                role_path = self.private_path / role_id
                if role_path.exists():
                    for file_path in role_path.glob("*.md"):
                        stat = file_path.stat()
                        files["private_memory"].append(
                            {
                                "filename": file_path.name,
                                "path": str(file_path),
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(
                                    stat.st_mtime,
                                ).isoformat(),
                            },
                        )

            return {
                "status": "success",
                "files": files,
                "total_files": len(files["shared_memory"])
                + len(files["private_memory"]),
            }
        except Exception as e:
            logger.error(f"列出记忆文件失败: {e}")
            return {
                "status": "error",
                "message": f"列出文件失败: {e!s}",
                "files": {"shared_memory": [], "private_memory": []},
                "total_files": 0,
            }

    def build_context_for_conversation(
        self,
        role_id: str,
        current_question: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        """为对话构建完整上下文结构，集成记忆银行功能"""
        try:
            # 1. 获取角色身份信息
            role_identity = self._get_role_identity(role_id)

            # 2. 获取相关记忆
            relevant_memories = self._get_relevant_memories(
                role_id,
                current_question,
                project_id,
            )

            # 3. 获取项目上下文
            project_context = (
                self._get_project_context(project_id) if project_id else None
            )

            # 4. 构建对话摘要
            conversation_summary = (
                self._summarize_conversation(conversation_history)
                if conversation_history
                else ""
            )

            # 5. 生成完整提示词
            prompt = self._build_complete_prompt(
                role_identity,
                current_question,
                relevant_memories,
                project_context,
                conversation_summary,
            )

            return {
                "role_identity": role_identity,
                "relevant_memories": relevant_memories,
                "project_context": project_context,
                "conversation_summary": conversation_summary,
                "prompt": prompt,
                "current_question": current_question,
                "project_id": project_id,
                "session_id": session_id,
            }

        except Exception as e:
            logger.error(f"构建对话上下文失败: {e}")
            # 容错：返回最小上下文
            return {
                "role_identity": {"role_id": role_id},
                "relevant_memories": [],
                "project_context": {"project_id": project_id, "session_id": session_id},
                "conversation_summary": "",
                "prompt": current_question,
            }

    def _get_role_identity(self, role_id: str) -> dict[str, Any]:
        """获取角色身份信息"""
        try:
            # 尝试从角色文件获取身份信息
            role_file = self.private_path / role_id / "role_identity.json"
            if role_file.exists():
                return json.loads(role_file.read_text(encoding="utf-8"))

            # 从共享记忆获取角色信息
            shared_role_info = self.get_shared_memory("role_definitions.md")
            if shared_role_info.get("status") == "success":
                # 解析角色定义文件，查找对应角色
                content = shared_role_info.get("content", "")
                # 简单解析，实际可增强
                return {
                    "role_id": role_id,
                    "name": role_id.replace("_", " ").title(),
                    "description": f"AI角色: {role_id}",
                }

            return {
                "role_id": role_id,
                "name": role_id,
                "description": f"AI角色: {role_id}",
            }

        except Exception as e:
            logger.error(f"获取角色身份失败: {e}")
            return {
                "role_id": role_id,
                "name": role_id,
                "description": f"AI角色: {role_id}",
            }

    def _get_relevant_memories(
        self,
        role_id: str,
        current_question: str,
        project_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """获取相关记忆"""
        relevant_memories = []

        try:
            # 1. 获取角色私有记忆
            private_memories = self._search_private_memories(role_id, current_question)
            relevant_memories.extend(private_memories)

            # 2. 获取项目相关共享记忆
            if project_id:
                project_memories = self._search_project_memories(
                    project_id,
                    current_question,
                )
                relevant_memories.extend(project_memories)

            # 3. 获取通用共享记忆
            shared_memories = self._search_shared_memories(current_question)
            relevant_memories.extend(shared_memories)

            # 去重并按相关性排序
            unique_memories = {}
            for memory in relevant_memories:
                memory_id = memory.get("id", memory.get("content", "")[:50])
                if memory_id not in unique_memories:
                    unique_memories[memory_id] = memory

            return list(unique_memories.values())[:10]  # 限制数量

        except Exception as e:
            logger.error(f"获取相关记忆失败: {e}")
            return []

    def _search_private_memories(
        self,
        role_id: str,
        query: str,
    ) -> list[dict[str, Any]]:
        """搜索角色私有记忆"""
        memories = []
        try:
            role_path = self.private_path / role_id
            if role_path.exists():
                for file_path in role_path.glob("*.md"):
                    content = file_path.read_text(encoding="utf-8")
                    if any(
                        keyword.lower() in content.lower() for keyword in query.split()
                    ):
                        memories.append(
                            {
                                "id": f"private_{role_id}_{file_path.stem}",
                                "content": content[:200] + "..."
                                if len(content) > 200
                                else content,
                                "source": f"private/{role_id}/{file_path.name}",
                                "type": "private",
                                "relevance": 0.8,
                            },
                        )
        except Exception as e:
            logger.error(f"搜索私有记忆失败: {e}")
        return memories

    def _search_project_memories(
        self,
        project_id: str,
        query: str,
    ) -> list[dict[str, Any]]:
        """搜索项目相关记忆"""
        memories = []
        try:
            # 搜索项目相关的共享记忆文件
            project_files = [
                "project_brief.md",
                "task_assignments.md",
                "collaboration_log.md",
                "development_progress.md",
            ]
            for filename in project_files:
                result = self.get_shared_memory(filename)
                if result.get("status") == "success":
                    content = result.get("content", "")
                    if any(
                        keyword.lower() in content.lower() for keyword in query.split()
                    ):
                        memories.append(
                            {
                                "id": f"project_{project_id}_{filename}",
                                "content": content[:200] + "..."
                                if len(content) > 200
                                else content,
                                "source": f"shared/{filename}",
                                "type": "project",
                                "relevance": 0.7,
                            },
                        )
        except Exception as e:
            logger.error(f"搜索项目记忆失败: {e}")
        return memories

    def _search_shared_memories(self, query: str) -> list[dict[str, Any]]:
        """搜索通用共享记忆"""
        memories = []
        try:
            # 搜索所有共享记忆文件
            for file_path in self.shared_path.glob("*.md"):
                content = file_path.read_text(encoding="utf-8")
                if any(keyword.lower() in content.lower() for keyword in query.split()):
                    memories.append(
                        {
                            "id": f"shared_{file_path.stem}",
                            "content": content[:200] + "..."
                            if len(content) > 200
                            else content,
                            "source": f"shared/{file_path.name}",
                            "type": "shared",
                            "relevance": 0.6,
                        },
                    )
        except Exception as e:
            logger.error(f"搜索共享记忆失败: {e}")
        return memories

    def _get_project_context(self, project_id: str) -> Optional[dict[str, Any]]:
        """获取项目上下文"""
        try:
            # 获取项目简介
            project_brief = self.get_shared_memory("project_brief.md")
            if project_brief.get("status") == "success":
                return {
                    "project_id": project_id,
                    "project_brief": project_brief.get("content", ""),
                    "status": "active",
                }
        except Exception as e:
            logger.error(f"获取项目上下文失败: {e}")
        return None

    def _summarize_conversation(
        self,
        conversation_history: list[dict[str, str]],
    ) -> str:
        """总结对话历史"""
        if not conversation_history:
            return ""

        try:
            # 简单总结：提取最近几条消息的关键信息
            recent_messages = conversation_history[-5:]  # 最近5条
            summary_parts = []

            for msg in recent_messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:100]  # 截取前100字符
                summary_parts.append(f"{role}: {content}")

            return " | ".join(summary_parts)

        except Exception as e:
            logger.error(f"总结对话历史失败: {e}")
            return ""

    def _build_complete_prompt(
        self,
        role_identity: dict[str, Any],
        current_question: str,
        relevant_memories: list[dict[str, Any]],
        project_context: Optional[dict[str, Any]],
        conversation_summary: str,
    ) -> str:
        """构建完整提示词"""
        prompt_parts = []

        # 1. 角色身份
        role_name = role_identity.get("name", role_identity.get("role_id", "AI助手"))
        role_desc = role_identity.get("description", "")
        prompt_parts.append(f"你是 {role_name}，{role_desc}")

        # 2. 项目上下文
        if project_context:
            project_brief = project_context.get("project_brief", "")
            if project_brief:
                prompt_parts.append(f"当前项目背景：{project_brief[:300]}...")

        # 3. 相关记忆
        if relevant_memories:
            memory_text = "相关记忆：\n"
            for i, memory in enumerate(relevant_memories[:3]):  # 最多3条记忆
                memory_text += f"{i+1}. {memory.get('content', '')}\n"
            prompt_parts.append(memory_text)

        # 4. 对话历史
        if conversation_summary:
            prompt_parts.append(f"对话历史：{conversation_summary}")

        # 5. 当前问题
        prompt_parts.append(f"用户问题：{current_question}")

        # 6. 回答要求
        prompt_parts.append("请基于你的角色身份和相关记忆，提供专业、准确的回答。")

        return "\n\n".join(prompt_parts)


# 全局记忆银行工具实例
memory_bank_tools = MemoryBankTools()


# 工具函数定义（供UnifiedToolManager注册）
def get_shared_memory_tool(filename: str) -> dict[str, Any]:
    """获取共享记忆银行文件内容"""
    return memory_bank_tools.get_shared_memory(filename)


def set_shared_memory_tool(filename: str, content: str) -> dict[str, Any]:
    """设置共享记忆银行文件内容"""
    return memory_bank_tools.set_shared_memory(filename, content)


def get_private_memory_tool(role_id: str, filename: str) -> dict[str, Any]:
    """获取私有记忆银行文件内容"""
    return memory_bank_tools.get_private_memory(role_id, filename)


def set_private_memory_tool(
    role_id: str,
    filename: str,
    content: str,
) -> dict[str, Any]:
    """设置私有记忆银行文件内容"""
    return memory_bank_tools.set_private_memory(role_id, filename, content)


def search_memory_bank_tool(
    query: str,
    role_id: Optional[str] = None,
) -> dict[str, Any]:
    """搜索记忆银行内容"""
    return memory_bank_tools.search_memory_bank(query, role_id)


def list_memory_files_tool(role_id: Optional[str] = None) -> dict[str, Any]:
    """列出记忆银行文件"""
    return memory_bank_tools.list_memory_files(role_id)


# 工具定义（OpenAI Function Calling格式）
MEMORY_BANK_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_shared_memory",
            "description": "获取共享记忆银行文件内容，用于读取项目相关的共享信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "文件名，如 'project_brief.md', 'system_architecture.md' 等",
                    },
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_shared_memory",
            "description": "设置共享记忆银行文件内容，用于更新项目相关的共享信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "文件名，如 'project_brief.md', 'development_progress.md' 等",
                    },
                    "content": {"type": "string", "description": "文件内容（Markdown格式）"},
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_private_memory",
            "description": "获取私有记忆银行文件内容，用于读取角色专属的私有信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "role_id": {
                        "type": "string",
                        "description": "角色ID，如 'project_coordinator_001', 'system_architect_001' 等",
                    },
                    "filename": {
                        "type": "string",
                        "description": "文件名，如 'coordination_decisions.md', 'architectural_decisions.md' 等",
                    },
                },
                "required": ["role_id", "filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_private_memory",
            "description": "设置私有记忆银行文件内容，用于更新角色专属的私有信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "role_id": {"type": "string", "description": "角色ID"},
                    "filename": {"type": "string", "description": "文件名"},
                    "content": {"type": "string", "description": "文件内容（Markdown格式）"},
                },
                "required": ["role_id", "filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory_bank",
            "description": "搜索记忆银行内容，用于查找包含特定关键词的文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询关键词"},
                    "role_id": {
                        "type": "string",
                        "description": "可选的角色ID，限制搜索范围到该角色的私有记忆",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_memory_files",
            "description": "列出记忆银行文件，用于查看可用的记忆文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "role_id": {
                        "type": "string",
                        "description": "可选的角色ID，限制列表范围到该角色的私有记忆",
                    },
                },
                "required": [],
            },
        },
    },
]
