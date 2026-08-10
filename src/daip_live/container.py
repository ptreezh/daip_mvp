# src/daip_live/container.py

from __future__ import annotations

import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dependency_injector import containers, providers


def _resolve_db_path(cm) -> str:
    """解析数据库路径：DAIP_DB_PATH 环境变量优先（测试隔离，S3-2 同款机制）。"""
    return (
        os.environ.get("DAIP_DB_PATH")
        or cm.get_config().model_dump()["database"]["path"]
    )


def setup_logging(config_dict: dict = None) -> None:
    """Configure logging system with rotating file handler.

    Args:
        config_dict: Configuration dictionary containing logging settings.
                     If None, uses default settings.
    """
    if config_dict is None:
        config_dict = {}

    log_config = config_dict.get("logging", {})

    # Log directory
    log_dir = Path(log_config.get("dir", "data/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log level
    level_str = log_config.get("level", "INFO")
    level = getattr(logging, level_str.upper(), logging.INFO)

    # Log format
    format_str = log_config.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler with rotation
    max_bytes = log_config.get("max_bytes", 10 * 1024 * 1024)  # 10MB
    backup_count = log_config.get("backup_count", 5)

    file_handler = RotatingFileHandler(
        log_dir / "daip_live.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(format_str))
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format_str))
    console_handler.setLevel(level)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


from daip_live.agent_engine.enhanced_intent_recognizer import (  # noqa: E402
    EnhancedIntentRecognizer,  # noqa: E402
)
from daip_live.agent_engine.executor import AgentExecutor  # noqa: E402
from daip_live.config import ConfigManager  # noqa: E402
from daip_live.core.models import KnowledgeBaseConfig, ProviderConfig  # noqa: E402
from daip_live.knowledge.manager import KnowledgeManager  # noqa: E402
from daip_live.memory.service import MemoryService  # noqa: E402
from daip_live.memory.session_manager import SessionManager  # noqa: E402
from daip_live.p4_role_manager_tools.intelligent_role_manager_wrapper import (  # noqa: E402
    IntelligentRoleManagerWrapper,
)
from daip_live.p4_role_manager_tools.role_model_manager import (  # noqa: E402
    RoleModelManager,  # noqa: E402
)
from daip_live.p4_role_manager_tools.tool_manager import ToolManager  # noqa: E402
from daip_live.p8_debate_system.enhanced_debate_manager import (  # noqa: E402
    EnhancedDebateManager,  # noqa: E402
)
from daip_live.p8_debate_system.history_tracker import (  # noqa: E402
    DebateHistoryTracker,  # noqa: E402
)
from daip_live.p8_debate_system.manager import DebateManager  # noqa: E402
from daip_live.permission.permission_manager import PermissionManager  # noqa: E402
from daip_live.permission.tui_interface import PermissionTUIInterface  # noqa: E402
from daip_live.persistence.database import DatabaseManager  # noqa: E402


# 延迟导入TUI以避免初始化副作用
def get_daip_tui():
    try:
        from daip_live.tui import DAIP_TUI
    except ImportError:
        from daip_live.tui_modular import DAIP_TUI
    return DAIP_TUI


from daip_live.skills.manager import SkillManager  # noqa: E402

# Note: Context managers moved to different locations - using available alternatives


class Container(containers.DeclarativeContainer):
    """Main application dependency injection container."""

    @staticmethod
    def _make_llm_provider(config) -> LiteLLMProvider:  # noqa: F821
        """延迟创建 LiteLLMProvider（首次调用时才 import litellm，加速 CLI 冷启动）。"""  # noqa: E501
        from daip_live.model_provider.provider import LiteLLMProvider

        return LiteLLMProvider(config)

    # 移除了CLI模块的自动绑定以防止TUI初始化
    # wiring_config = containers.WiringConfiguration(modules=["daip_live.tui_modular", "daip_live.cli"])  # noqa: E501
    # 仅绑定需要的服务组件，而不绑定CLI应用本身

    # 延迟配置初始化 - 确保ConfigManager先初始化
    config_manager = providers.Singleton(ConfigManager)

    # 通过ConfigManager获取配置数据，避免直接的配置访问冲突
    config_data = providers.Singleton(
        lambda cm=config_manager: cm().get_config().model_dump()
    )

    # 数据库管理器 - 使用安全配置访问
    # DAIP_DB_PATH 环境变量覆盖（测试隔离，S3-2 同款机制）：测试用临时 DB，
    # 避免测试写入项目根 daip_live.db
    db_manager = providers.Singleton(
        DatabaseManager,
        db_path=providers.Callable(lambda cm=config_manager: _resolve_db_path(cm())),
    )

    # 模型提供者 - 使用延迟工厂确保配置已加载（LiteLLMProvider 延迟 import）
    model_provider = providers.Singleton(
        _make_llm_provider,
        config=providers.Factory(
            ProviderConfig,
            model=providers.Callable(
                lambda cm=config_manager: cm()
                .get_config()
                .model_dump()["llm_provider"]["default_model"]
            ),
        ),
    )

    # 嵌入模型提供者
    embed_provider = providers.Singleton(
        _make_llm_provider,
        config=providers.Factory(
            ProviderConfig,
            model=providers.Callable(
                lambda cm=config_manager: cm()
                .get_config()
                .model_dump()["llm_provider"]["default_model"]
            ),
            embedding_model=providers.Callable(
                lambda cm=config_manager: cm()
                .get_config()
                .model_dump()["llm_provider"]["embedding_model"]
            ),
        ),
    )

    # 知识库配置
    knowledge_base_config = providers.Factory(
        KnowledgeBaseConfig,
        directory=providers.Callable(
            lambda cm=config_manager: cm()
            .get_config()
            .model_dump()["knowledge_base"]["directory"]
        ),
    )

    knowledge_manager = providers.Singleton(
        KnowledgeManager,
        db_manager=db_manager,
        model_provider=embed_provider,
        config=knowledge_base_config,
    )

    tool_manager = providers.Singleton(ToolManager)

    session_manager = providers.Singleton(SessionManager, db_manager=db_manager)

    memory_service = providers.Singleton(MemoryService, model_provider=model_provider)

    role_model_manager = providers.Singleton(
        RoleModelManager,
        roles_dir_path=providers.Callable(
            lambda cm=config_manager: cm()
            .get_config()
            .model_dump()["role_manager"]["roles_dir"]
        ),
    )

    role_manager = providers.Singleton(
        IntelligentRoleManagerWrapper,
        roles_dir_path=providers.Callable(
            lambda cm=config_manager: cm()
            .get_config()
            .model_dump()["role_manager"]["roles_dir"]
        ),
        model_provider=model_provider,
    )

    debate_history_tracker = providers.Singleton(
        DebateHistoryTracker,
        db_path=providers.Callable(
            lambda cm: _resolve_db_path(cm),
            cm=config_manager,
        ),
    )

    enhanced_debate_manager = providers.Singleton(
        EnhancedDebateManager,
        session_manager=session_manager,
        role_manager=role_manager,
        role_model_manager=role_model_manager,
        model_provider=model_provider,
    )

    debate_manager = providers.Singleton(
        DebateManager,
        session_manager=session_manager,
        role_manager=role_manager,
        model_provider=model_provider,
    )

    user_input_queue = providers.Singleton(asyncio.Queue)

    permission_manager = providers.Singleton(
        PermissionManager,
        user_input_queue=user_input_queue,
        tui_interface=providers.Factory(PermissionTUIInterface, user_input_queue),
    )

    agent_executor = providers.Factory(
        AgentExecutor,
        session_manager=session_manager,
        memory_service=memory_service,
        knowledge_manager=knowledge_manager,
        model_provider=model_provider,
        tool_manager=tool_manager,
        user_input_queue=user_input_queue,
        permission_manager=permission_manager,
    )

    skill_manager = providers.Singleton(SkillManager)

    intent_recognizer = providers.Singleton(EnhancedIntentRecognizer)

    # context_manager = providers.Singleton(HistoryAwareContextManager)  # Temporarily disabled  # noqa: E501

    # 添加Wiki目录配置
    wiki_pages_directory = providers.Callable(
        lambda cm=config_manager: cm()
        .get_config()
        .model_dump()["wiki"]["pages_directory"]
    )

    # 添加论文下载目录配置
    paper_download_directory = providers.Callable(
        lambda cm=config_manager: cm()
        .get_config()
        .model_dump()["paper"]["download_directory"]
    )


# Initialize logging on module import
# This ensures logging is configured before any application code runs
_logging_initialized = False


def _ensure_logging():
    global _logging_initialized
    if not _logging_initialized:
        try:
            cfg = ConfigManager()
            setup_logging(cfg.get_config().model_dump())
            _logging_initialized = True
        except Exception:
            # If config loading fails, use defaults
            setup_logging()
            _logging_initialized = True


# Auto-initialize on import
_ensure_logging()
