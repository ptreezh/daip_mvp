# -*- coding: utf-8 -*-
"""@Time    : 2025-07-19 03:00:00
@Author  : DAIP-LIVE Team
@File    : service_utils.py
@Description: Service utility functions for CLI commands to avoid circular imports.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Service initialization with lazy loading
_services_initialized = False
_service_instances = {}

def _initialize_services():
    """Initialize services only when needed with lazy loading."""
    global _services_initialized, _service_instances
    
    if _services_initialized:
        return _service_instances
    
    # Lightweight services (initialize immediately)
    from src.core_services.user_profile_service import UserProfileService
    from src.core_services.intent_analysis_service import BasicIntentAnalysisService
    from src.core_services.role_manager import RoleManager
    from src.core_services.task_manager import TaskManager
    from src.institutional_primitives.registry import PrimitiveRegistry
    from src.institutional_primitives.workflow_engine import WorkflowEngine
    
    user_profile_service = UserProfileService()
    intent_analysis_service = BasicIntentAnalysisService(user_profile_service=user_profile_service)
    role_manager = RoleManager()
    task_manager = TaskManager()
    primitive_registry = PrimitiveRegistry()
    workflow_engine = WorkflowEngine(primitive_registry=primitive_registry)
    
    _service_instances.update({
        'user_profile_service': user_profile_service,
        'intent_analysis_service': intent_analysis_service,
        'role_manager': role_manager,
        'task_manager': task_manager,
        'primitive_registry': primitive_registry,
        'workflow_engine': workflow_engine
    })
    
    # Heavy services (initialize on demand)
    _service_instances.update({
        'enhanced_sskg_manager': lambda: EnhancedSSKGManager(
            graph_path=Path("data/sskg_graph.graphml"), 
            vector_store_path=Path("data/sskg_vector_store")
        ),
        'mem_agent': lambda: MemAgent(sskg_manager=_get_service('enhanced_sskg_manager')),
        'integrated_llm_manager': lambda: IntegratedLLMManager(),
        'chat_room_manager': lambda: ChatRoomManager(storage_path="data/chat_rooms.json"),
        'chat_session_service': lambda: ChatSessionService(
            chat_room_manager=_get_service('chat_room_manager'), 
            storage_path="data/chat_sessions.json"
        ),
        'wiki_service': lambda: WikiService(),
        'chat_coordinator': lambda: ChatCoordinator(
            chat_room_manager=_get_service('chat_room_manager'),
            chat_session_service=_get_service('chat_session_service'),
            role_manager=role_manager,
            primitive_registry=primitive_registry,
            wiki_service=_get_service('wiki_service')
        ),
        'personal_assistant_router': lambda: PersonalAssistantRouter(
            intent_analysis_service=intent_analysis_service,
            llm_manager=_get_service('integrated_llm_manager'),
            workflow_engine=workflow_engine,
            task_manager=task_manager
        )
    })
    
    _services_initialized = True
    return _service_instances

def _get_service(service_name):
    """Get a service instance with lazy initialization."""
    if not _services_initialized:
        _initialize_services()
    
    service = _service_instances.get(service_name)
    if callable(service):
        # Initialize the service if it's a lambda function
        service_instance = service()
        _service_instances[service_name] = service_instance
        return service_instance
    return service

def get_wiki_service():
    """Get the global wiki service instance."""
    return _get_service('wiki_service')

def get_role_manager():
    """Get the global role manager instance."""
    return _get_service('role_manager')

def get_primitive_registry():
    """Get the global primitive registry instance."""
    return _get_service('primitive_registry')

def get_personal_assistant_router():
    """Get the personal assistant router instance."""
    return _get_service('personal_assistant_router')

def get_chat_coordinator():
    """Get the global chat coordinator instance."""
    return _get_service('chat_coordinator')

def get_chat_room_manager():
    """Get the global chat room manager instance."""
    return _get_service('chat_room_manager')

def get_chat_session_service():
    """Get the global chat session service instance."""
    return _get_service('chat_session_service')

# Import heavy service classes only when needed
def EnhancedSSKGManager():
    from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
    return EnhancedSSKGManager

def MemAgent():
    from src.core_services.memory_agent import MemAgent
    return MemAgent

def IntegratedLLMManager():
    from src.core_services.integrated_llm_manager import IntegratedLLMManager
    return IntegratedLLMManager

def ChatRoomManager():
    from src.virtual_role_chat.chat_room_manager import ChatRoomManager
    return ChatRoomManager

def ChatSessionService():
    from src.virtual_role_chat.chat_session_service import ChatSessionService
    return ChatSessionService

def WikiService():
    from src.core_services.wiki_service import WikiService
    return WikiService

def ChatCoordinator():
    from src.virtual_role_chat.chat_coordinator import ChatCoordinator
    return ChatCoordinator

def PersonalAssistantRouter():
    from src.application.personal_assistant_router import PersonalAssistantRouter
    return PersonalAssistantRouter