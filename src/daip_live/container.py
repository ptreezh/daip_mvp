# src/daip_live/container.py

import asyncio
from dependency_injector import containers, providers

from daip_live.config import ConfigManager
from daip_live.config_bridge import config_bridge
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.persistence.database import DatabaseManager
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.p4_role_manager_tools.intelligent_role_manager_wrapper import IntelligentRoleManagerWrapper
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import KnowledgeBaseConfig, ProviderConfig
from daip_live.permission.permission_manager import PermissionManager
from daip_live.permission.tui_interface import PermissionTUIInterface
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
# 延迟导入TUI以避免初始化副作用
def get_daip_tui():
    try:
        from daip_live.tui import DAIP_TUI
    except ImportError:
        from daip_live.tui_modular import DAIP_TUI
    return DAIP_TUI
from daip_live.skills.manager import SkillManager
# Note: Context managers moved to different locations - using available alternatives


class Container(containers.DeclarativeContainer):
    """Main application dependency injection container."""

    # 移除了CLI模块的自动绑定以防止TUI初始化
    # wiring_config = containers.WiringConfiguration(modules=["daip_live.tui_modular", "daip_live.cli"])
    # 仅绑定需要的服务组件，而不绑定CLI应用本身

    # 延迟配置初始化 - 确保ConfigManager先初始化
    config_manager = providers.Singleton(ConfigManager)

    # 通过ConfigManager获取配置数据，避免直接的配置访问冲突
    config_data = providers.Singleton(
        lambda cm=config_manager: cm().get_config().model_dump()
    )

    # 数据库管理器 - 使用安全配置访问
    db_manager = providers.Singleton(
        DatabaseManager,
        db_path=providers.Callable(
            lambda cm=config_manager: cm().get_config().model_dump()['database']['path']
        )
    )

    # 模型提供者 - 使用延迟工厂确保配置已加载
    model_provider = providers.Singleton(
        LiteLLMProvider,
        config=providers.Factory(
            ProviderConfig,
            model=providers.Callable(
                lambda cm=config_manager: cm().get_config().model_dump()['llm_provider']['default_model']
            )
        )
    )

    # 嵌入模型提供者
    embed_provider = providers.Singleton(
        LiteLLMProvider,
        config=providers.Factory(
            ProviderConfig,
            model=providers.Callable(
                lambda cm=config_manager: cm().get_config().model_dump()['llm_provider']['default_model']
            ),
            embedding_model=providers.Callable(
                lambda cm=config_manager: cm().get_config().model_dump()['llm_provider']['embedding_model']
            )
        )
    )

    # 知识库配置
    knowledge_base_config = providers.Factory(
        KnowledgeBaseConfig,
        directory=providers.Callable(
            lambda cm=config_manager: cm().get_config().model_dump()['knowledge_base']['directory']
        ),
    )

    knowledge_manager = providers.Singleton(
        KnowledgeManager,
        db_manager=db_manager,
        model_provider=embed_provider,
        config=knowledge_base_config,
    )

    tool_manager = providers.Singleton(ToolManager)

    session_manager = providers.Singleton(
        SessionManager,
        db_manager=db_manager
    )

    memory_service = providers.Singleton(
        MemoryService,
        model_provider=model_provider
    )

    role_model_manager = providers.Singleton(
        RoleModelManager,
        roles_dir_path=providers.Callable(
            lambda cm=config_manager: cm().get_config().model_dump()['role_manager']['roles_dir']
        )
    )

    role_manager = providers.Singleton(
        IntelligentRoleManagerWrapper,
        roles_dir_path=providers.Callable(
            lambda cm=config_manager: cm().get_config().model_dump()['role_manager']['roles_dir']
        ),
        model_provider=model_provider
    )

    debate_history_tracker = providers.Singleton(
        DebateHistoryTracker,
        db_path=providers.Callable(
            lambda cm=config_manager: cm().get_config().model_dump()['database']['path']
        )
    )

    enhanced_debate_manager = providers.Singleton(
        EnhancedDebateManager,
        session_manager=session_manager,
        role_manager=role_manager,
        role_model_manager=role_model_manager,
        model_provider=model_provider
    )

    debate_manager = providers.Singleton(
        DebateManager,
        session_manager=session_manager,
        role_manager=role_manager,
        model_provider=model_provider
    )

    user_input_queue = providers.Singleton(asyncio.Queue)

    permission_manager = providers.Singleton(
        PermissionManager,
        user_input_queue=user_input_queue,
        tui_interface=providers.Factory(PermissionTUIInterface, user_input_queue)
    )

    agent_executor = providers.Factory(
        AgentExecutor,
        session_manager=session_manager,
        memory_service=memory_service,
        knowledge_manager=knowledge_manager,
        model_provider=model_provider,
        tool_manager=tool_manager,
        user_input_queue=user_input_queue,
        permission_manager=permission_manager
    )

    skill_manager = providers.Singleton(SkillManager)

    intent_recognizer = providers.Singleton(EnhancedIntentRecognizer)

    # context_manager = providers.Singleton(HistoryAwareContextManager)  # Temporarily disabled

    # 添加Wiki目录配置
    wiki_pages_directory = providers.Callable(
        lambda cm=config_manager: cm().get_config().model_dump()['wiki']['pages_directory']
    )

    # 添加论文下载目录配置
    paper_download_directory = providers.Callable(
        lambda cm=config_manager: cm().get_config().model_dump()['paper']['download_directory']
    )