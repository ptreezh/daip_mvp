#!/usr/bin/env python3
"""后端连接器服务 - 简化版本

负责与现有DAIP-LIVE后端服务的API集成
提供统一的服务接口供前端组件使用
"""

import logging
from dataclasses import dataclass
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BackendConfig:
    """后端服务配置"""

    base_url: str = "http://localhost:8000"
    websocket_url: str = "ws://localhost:8000/ws"
    timeout: int = 120
    max_retries: int = 3

# Import the actual services from src/core_services
# Alias them to avoid naming conflicts with the mock classes that will be removed.
from src.core_services.consensus_algorithm_selector import ConsensusAlgorithmSelector
from src.core_services.intent_analysis_service import BasicIntentAnalysisService
from src.core_services.role_manager import RoleManager
from src.core_services.task_manager import TaskManager as RealTaskManager
from src.core_services.user_profile_service import UserProfileService
from src.core_services.wiki_service import WikiService as RealWikiService
from src.core_services.workflow_knowledge_integrator import WorkflowKnowledgeIntegrator


class BackendConnector:
    """后端连接器主类"""

    def __init__(self, config: Optional[BackendConfig] = None):
        self.config = config or BackendConfig()





        # Initialize services using the actual implementations from src/core_services
        # Note: The real services use directory paths, not base_url.
        self.wiki_service = RealWikiService(wiki_directory="daip_mvp_project/memory_bank/wiki/")
        # TaskManager is used where TaskService was expected. Alias it.
        self.task_service = RealTaskManager(task_directory="daip_mvp_project/memory_bank/tasks/")

        # Initialize WorkflowKnowledgeIntegrator and ConsensusAlgorithmSelector
        from src.core_services.sskg_manager import SSKGManager  # Import here to avoid circular dependency
        sskg_manager = SSKGManager() # Assuming default constructor is sufficient
        self.workflow_integrator = WorkflowKnowledgeIntegrator(sskg_manager=sskg_manager, wiki_service=self.wiki_service)
        self.consensus_selector = ConsensusAlgorithmSelector()

        # Initialize UserProfileService and IntentAnalysisService
        self.user_profile_service = UserProfileService()
        self.intent_analysis_service = BasicIntentAnalysisService(user_profile_service=self.user_profile_service)

        # Initialize RoleManager
        self.role_manager = RoleManager()

        # WebSocket connection status
        self.is_connected = False



        logger.info("BackendConnector initialized. Using actual services from src/core_services.")

    async def health_check(self) -> bool:
        """Health check for backend services."""
        # This might need to be updated to check the health of the actual services
        logger.info("Performing health check (mocked for now).")
        # In a real implementation, this would check the health of the actual services
        return True

    async def close(self):
        """Close connections."""
        logger.info("BackendConnector closed.")
