import asyncio
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.config import ConfigManager
from daip_live.core.models import ProviderConfig
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.persistence.database import DatabaseManager
from daip_live.tui import DAIP_TUI


# Create a mock tool manager class
class MockToolManager:
    def execute_tool(self, tool_name, args, session_context=None, confirmation_granted=False):
        # Simple mock implementation that just returns a string with the tool name and args
        return f"Mock tool '{tool_name}' executed with args: {args}"

async def main():
    # Initialize components
    config_manager = ConfigManager()
    config = config_manager.get_config()

    db_manager = DatabaseManager(config.database.path)

    # Create session manager
    session_manager = SessionManager()

    # Create memory service
    memory_service = MemoryService()

    # Create model provider
    provider_config = ProviderConfig(model=config.llm_provider.default_model)
    model_provider = LiteLLMProvider(provider_config)

    # Create a simple knowledge manager placeholder
    knowledge_manager = None

    # Create a mock tool manager
    tool_manager = MockToolManager()

    role_manager = RoleManager(config.role_manager.roles_dir)

    debate_manager = DebateManager(session_manager, role_manager, model_provider)

    # Create user input queue
    user_input_queue = asyncio.Queue()

    # Create executor with all required components
    executor = AgentExecutor(
        session_manager=session_manager,
        memory_service=memory_service,
        knowledge_manager=knowledge_manager,
        model_provider=model_provider,
        tool_manager=tool_manager,
        user_input_queue=user_input_queue
    )

    # Create and run TUI
    app = DAIP_TUI(
        executor,
        goal=None,
        session_manager=session_manager,
        role_manager=role_manager,
        knowledge_manager=knowledge_manager,
        debate_manager=debate_manager,
        model_provider=model_provider,
        db_manager=db_manager,
        config_manager=config_manager
    )
    await app.run_async()

if __name__ == '__main__':
    asyncio.run(main())
