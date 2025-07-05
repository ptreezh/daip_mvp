"""DAIP Insight Engine - 通用工具函数模块

本模块提供配置加载、环境变量处理、日志设置、API密钥管理、依赖检查、目录结构初始化等通用工具函数。
所有函数均具备类型注解、异常处理、详细文档，适用于全项目范围的基础依赖。
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional


def load_config(config_file: str = "config/model_config.json") -> dict[str, Any]:
    """加载JSON格式的配置文件，并合并环境变量配置。

    Args:
    ----
        config_file (str): 配置文件路径，默认为config/model_config.json。
    Returns:
        dict[str, Any]: 合并后的配置字典，环境变量优先生效。
    """
    config_path = Path(config_file)
    config: dict[str, Any] = {}
    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load config file {config_file}: {e}")
    # 环境变量优先
    env_config = {
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "gemma3:latest"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest"),
        "qiniu_api_key": os.getenv("QINIU_API_KEY"),
        "qiniu_api_url": os.getenv(
            "QINIU_API_URL", "https://api.qnaigc.com/v1/chat/completions"
        ),
        "qiniu_model": os.getenv("QINIU_MODEL", "deepseek-chat"),
        "together_api_key": os.getenv("TOGETHER_API_KEY"),
        "together_api_url": os.getenv(
            "TOGETHER_API_URL", "https://api.together.xyz/v1/chat/completions"
        ),
        "together_model": os.getenv("TOGETHER_MODEL", "meta-llama/Llama-2-70b-chat-hf"),
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
        "openrouter_api_url": os.getenv(
            "OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions"
        ),
        "openrouter_model": os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
        "siliconflow_api_key": os.getenv("SILICONFLOW_API_KEY"),
        "siliconflow_api_url": os.getenv(
            "SILICONFLOW_API_URL", "https://api.siliconflow.cn/v1/chat/completions"
        ),
        "siliconflow_model": os.getenv(
            "SILICONFLOW_MODEL", "internlm/internlm2_5-7b-chat"
        ),
    }
    for key, value in env_config.items():
        if value is not None:
            config[key] = value
    return config


def save_config(
    config: dict[str, Any], config_file: str = "config/model_config.json"
) -> None:
    """保存配置字典为JSON文件。

    Args:
    ----
        config (dict[str, Any]): 配置字典。
        config_file (str): 保存路径。
    Raises:
        OSError: 文件写入失败时抛出。
    """
    config_path = Path(config_file)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to save config file {config_file}: {e}")
        raise


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """配置全局日志系统。

    Args:
    ----
        level (str): 日志级别，默认INFO。
        log_file (Optional[str]): 日志文件路径，若为None则仅输出到控制台。
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging_kwargs = {
        "level": log_level,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logging_kwargs["filename"] = log_file
        logging_kwargs["encoding"] = "utf-8"
    logging.basicConfig(**logging_kwargs)


def get_api_keys() -> dict[str, Optional[str]]:
    """获取所有支持平台的API密钥。

    Returns
    -------
        dict[str, Optional[str]]: 各平台API密钥，未配置为None。
    """
    return {
        "qiniu": os.getenv("QINIU_API_KEY"),
        "together": os.getenv("TOGETHER_API_KEY"),
        "openrouter": os.getenv("OPENROUTER_API_KEY"),
        "siliconflow": os.getenv("SILICONFLOW_API_KEY"),
    }


def check_api_keys() -> dict[str, bool]:
    """检查各平台API密钥是否已配置。

    Returns
    -------
        dict[str, bool]: 各平台密钥配置情况。
    """
    keys = get_api_keys()
    return {platform: bool(key) for platform, key in keys.items()}


def create_default_config() -> dict[str, Any]:
    """生成并保存默认配置文件和.env.example示例。

    Returns
    -------
        dict[str, Any]: 默认配置字典。
    """
    default_config = {
        "data_dir": "data",
        "memory_bank_dir": "data/memory_banks",
        "roles_dir": "roles",
        "default_model": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "ollama_model": "gemma3:latest",
        "embedding_model": "nomic-embed-text:latest",
        "qiniu_model": "deepseek-chat",
        "together_model": "meta-llama/Llama-2-70b-chat-hf",
        "openrouter_model": "openai/gpt-3.5-turbo",
        "siliconflow_model": "internlm/internlm2_5-7b-chat",
        "model_check_interval": 30,
        "auto_fallback": True,
        "enable_simulated_responses": True,
    }
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    save_config(default_config, "config/model_config.json")
    env_example = """# DAIP Insight Engine Environment Variables
# Copy this file to .env and fill in your API keys

# Ollama Configuration (Local Models)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:latest
EMBEDDING_MODEL=nomic-embed-text:latest

# 七牛云 Configuration
QINIU_API_KEY=your_qiniu_api_key_here
QINIU_API_URL=https://api.qnaigc.com/v1/chat/completions
QINIU_MODEL=deepseek-chat

# Together.ai Configuration
TOGETHER_API_KEY=your_together_api_key_here
TOGETHER_API_URL=https://api.together.xyz/v1/chat/completions
TOGETHER_MODEL=meta-llama/Llama-2-70b-chat-hf

# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_MODEL=openai/gpt-3.5-turbo

# SiliconFlow Configuration
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
SILICONFLOW_API_URL=https://api.siliconflow.cn/v1/chat/completions
SILICONFLOW_MODEL=internlm/internlm2_5-7b-chat

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/daip.log
"""
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_example)
    return default_config


def load_env_file(env_file: str = ".env") -> None:
    """加载.env环境变量文件，将内容写入os.environ。

    Args:
    ----
        env_file (str): .env文件路径，默认为.env。
    """
    env_path = Path(env_file)
    if env_path.exists():
        try:
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            logging.warning(f"Failed to load .env file: {e}")


def format_model_size(size_str: str) -> str:
    """格式化模型大小字符串，支持自动单位转换。

    Args:
    ----
        size_str (str): 原始大小字符串或数字。
    Returns:
        str: 格式化后的字符串。
    """
    if not size_str:
        return ""
    if any(unit in size_str.upper() for unit in ["B", "KB", "MB", "GB", "TB"]):
        return size_str
    try:
        size_bytes = float(size_str)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}PB"
    except Exception:
        return size_str


def get_system_info() -> dict[str, Any]:
    """获取主机系统信息（平台、CPU、内存、磁盘等）。

    Returns
    -------
        dict[str, Any]: 系统信息字典。
    """
    import platform

    import psutil

    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_usage": psutil.disk_usage(".").percent,
    }


def check_dependencies() -> dict[str, bool]:
    """检查常用依赖包是否已安装。

    Returns
    -------
        dict[str, bool]: 依赖包安装情况。
    """
    dependencies = {
        "aiohttp": False,
        "chromadb": False,
        "sqlite3": True,  # 内置模块
        "psutil": False,
        "openai": False,
        "anthropic": False,
    }
    for dep in dependencies:
        if dep == "sqlite3":
            continue
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    return dependencies


def create_directory_structure() -> list[str]:
    """自动创建项目所需的目录结构。

    Returns
    -------
        list[str]: 已创建的目录列表。
    """
    directories = ["data", "data/memory_banks", "config", "logs", "roles", "backup"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    return directories
