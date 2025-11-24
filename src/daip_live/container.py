# src/daip_live/container.py

import asyncio
from dependency_injector import containers, providers

from daip_live.config import ConfigManager
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.persistence.database import DatabaseManager
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import KnowledgeBaseConfig, ProviderConfig
from daip_live.permission.permission_manager import PermissionManager
from daip_live.permission.tui_interface import PermissionTUIInterface
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from src.intent_recognition.context_manager import ContextManager
from src.intent_recognition.history_aware_context_manager import HistoryAwareContextManager
from src.intent_recognition.context_aware_intent_recognizer import ContextAwareIntentRecognizer


class Container(containers.DeclarativeContainer):
    """Main application dependency injection container."""

    wiring_config = containers.WiringConfiguration(modules=["daip_live.tui", "daip_live.cli"])

    config = providers.Configuration()

    db_manager = providers.Singleton(
        DatabaseManager,
        db_path=config.database.path
    )

    model_provider = providers.Singleton(
        LiteLLMProvider,
        config=providers.Factory(
            ProviderConfig,
            model=config.llm_provider.default_model
        )
    )

    embed_provider = providers.Singleton(
        LiteLLMProvider,
        config=providers.Factory(
            ProviderConfig,
            model=config.llm_provider.embedding_model,
            embedding_model=config.llm_provider.embedding_model
        )
    )

    knowledge_base_config = providers.Factory(
        KnowledgeBaseConfig,
        directory=config.knowledge_base.directory,
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
        roles_dir_path=config.role_manager.roles_dir
    )
    
    role_manager = providers.Singleton(
        RoleManager,
        roles_dir_path=config.role_manager.roles_dir
    )
    
    debate_history_tracker = providers.Singleton(
        DebateHistoryTracker,
        db_path=config.database.path
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
    
    intent_recognizer = providers.Singleton(EnhancedIntentRecognizer)

    context_manager = providers.Singleton(HistoryAwareContextManager)

    # 添加Wiki目录配置
    wiki_pages_directory = providers.Factory(
        lambda config: config.wiki.pages_directory,
        config
    )

    # 添加论文下载目录配置
    paper_download_directory = providers.Factory(
        lambda config: config.paper.download_directory,
        config
    )

    # 添加辩论日志目录配置
    debate_logs_directory = providers.Factory(
        lambda config: config.debate.logs_directory,
        config
    )

    context_aware_intent_recognizer = providers.Singleton(
        ContextAwareIntentRecognizer,
        context_manager=context_manager,
        base_intent_recognizer=intent_recognizer
    )

    tui_app = providers.Factory("daip_live.tui.DAIP_TUI")
