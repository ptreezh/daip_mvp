"""DAIP Insight Engine - 全局配置模块

本模块集中定义项目根目录、模型配置、数据库路径、工具配置等全局常量和配置项。
所有业务代码、测试代码、工具脚本均应引用本文件中的配置，避免硬编码。
支持自动化API文档工具提取。
"""

import os
from typing import Any, Optional

# 获取项目根目录
PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ollama配置
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 测试和日志目录
TEST_WORKSPACE_DIR: str = os.path.join(PROJECT_ROOT, "test_workspace")
LOG_DIR: str = os.path.join(PROJECT_ROOT, "logs")
REPORT_DIR: str = os.path.join(PROJECT_ROOT, "reports")

# 模型列表文件
MODELS_LIST_FILE: str = os.path.join(PROJECT_ROOT, "models_list.txt")

# 支持的模型配置（dict结构，便于扩展）
SUPPORTED_MODELS: dict[str, dict[str, Any]] = {
    "llama3:instruct": {
        "provider": "ollama",
        "model": "llama3:instruct",
        "description": "本地Llama3",
        "base_url": OLLAMA_BASE_URL,
        "temperature": 0.7,
    },
    "phi3:mini": {
        "provider": "ollama",
        "model": "phi3:mini",
        "description": "本地Phi3",
        "base_url": OLLAMA_BASE_URL,
        "temperature": 0.7,
    },
    "yi:6b": {
        "provider": "ollama",
        "model": "yi:6b",
        "description": "本地Yi",
        "base_url": OLLAMA_BASE_URL,
        "temperature": 0.7,
    },
    "gemma": {
        "provider": "ollama",
        "model": "gemma",
        "description": "本地Gemma",
        "base_url": OLLAMA_BASE_URL,
        "temperature": 0.7,
    },
    "granite-code:3b": {
        "provider": "ollama",
        "model": "granite-code:3b",
        "description": "本地Granite",
        "base_url": OLLAMA_BASE_URL,
        "temperature": 0.7,
    },
    "mistral-nemo:latest": {
        "provider": "ollama",
        "model": "mistral-nemo:latest",
        "description": "本地Mistral",
        "base_url": OLLAMA_BASE_URL,
        "temperature": 0.7,
    },
    "qwen3:30b-a3b": {
        "provider": "cloud",
        "model": "qwen3:30b-a3b",
        "description": "云端Qwen3-30B",
        "base_url": "https://api.together.ai/v1",
        "temperature": 0.7,
    },
}

# 函数调用模型
FUNCTION_CALLING_MODEL: str = os.getenv("FUNCTION_CALLING_MODEL", "llama3:instruct")

# 默认聊天模型
DEFAULT_CHAT_MODEL: str = os.getenv("DEFAULT_CHAT_MODEL", "llama3:instruct")


def get_tool_definitions_path(session_id: Optional[str] = None) -> str:
    """获取工具定义文件路径。
    Args:
        session_id (Optional[str]): 会话ID，若指定则返回对应会话的工具定义文件路径。
    Returns:
        str: 工具定义文件的绝对路径。
    """
    if session_id:
        return os.path.join(
            PROJECT_ROOT,
            "tools",
            f"tool_definitions_{session_id}.json",
        )
    return os.path.join(PROJECT_ROOT, "tools", "tool_definitions.json")


# 工具调用配置
TOOL_CALLING_CONFIG: dict[str, Any] = {
    "max_retries": 3,
    "timeout": 30,
    "enable_function_calling": True,
}

# 数据库配置
DATABASE_PATH: str = os.path.join(PROJECT_ROOT, "data", "sskg.db")
CHROMA_PATH: str = os.path.join(PROJECT_ROOT, "data", "chroma")
CHROMADB_COLLECTION_NAME: str = "sskg_summaries"
CHROMADB_TOOLS_COLLECTION_NAME: str = "sskg_tools"
EMBEDDING_MODEL_NAME: str = "llama3:instruct"
OLLAMA_MODEL_NAME: str = "llama3:instruct"

# Token阈值和RAG参数
TOKEN_COUNT_THRESHOLD: int = 2048
SUMMARY_RAG_K: int = 5

SQLITE_DB_PATH: str = os.path.join(PROJECT_ROOT, "data", "sqlite.db")

# 确保目录存在（工程健壮性）
for directory in [
    TEST_WORKSPACE_DIR,
    LOG_DIR,
    REPORT_DIR,
    os.path.dirname(DATABASE_PATH),
    CHROMA_PATH,
]:
    os.makedirs(directory, exist_ok=True)

# --- API文档片段 ---
# 本模块所有配置项均已补充类型注解和用途说明，支持Sphinx/自动化API文档工具提取。
