"""
DAIP-LIVE newP6 TUI Entry Point

This module provides the main entry point for the DAIP-LIVE TUI application
using the newP6 componentized architecture.

This replaces the original monolithic TUI with a modular, component-based
approach while maintaining full backwards compatibility.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from textual.app import App

# Import DAIP services
from daip_live.agent_engine.executor import AgentExecutor
from daip_live.memory.session_manager import SessionManager
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.persistence.database import DatabaseManager
from daip_live.config import (
    config_manager,
    create_config_yaml_if_not_exists,
)

# Import newP6 TUI application
from daip_live.tui_v1.app import create_daip_newp6_app


class DAIP_TUI_NEWP6:
    """
    DAIP-LIVE TUI using newP6 componentized architecture.

    This class provides the same interface as the original DAIP_TUI but uses
    the new component-based architecture internally.
    """

    def __init__(
        self,
        executor: Optional[AgentExecutor] = None,
        session_manager: Optional[SessionManager] = None,
        role_manager: Optional[RoleManager] = None,
        knowledge_manager: Optional[KnowledgeManager] = None,
        debate_manager: Optional[DebateManager] = None,
        model_provider: Optional[LiteLLMProvider] = None,
        db_manager: Optional[DatabaseManager] = None,
        config_manager=None,
        role_model_manager: Optional[RoleModelManager] = None,
        goal: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the DAIP-LIVE TUI application.

        Args:
            executor: Agent executor service
            session_manager: Session manager service
            role_manager: Role manager service
            knowledge_manager: Knowledge manager service
            debate_manager: Debate manager service
            model_provider: Model provider service
            db_manager: Database manager
            config_manager: Configuration manager
            role_model_manager: Role model manager
            goal: User goal for the session
            **kwargs: Additional parameters
        """
        self.goal = goal
        self.daip_services = {
            'executor': executor,
            'session_manager': session_manager,
            'role_manager': role_manager,
            'knowledge_manager': knowledge_manager,
            'debate_manager': debate_manager,
            'model_provider': model_provider,
            'db_manager': db_manager,
            'config_manager': config_manager,
            'role_model_manager': role_model_manager,
            'goal': goal,
            **kwargs
        }

        # Create the newP6 TUI application
        self.app = create_daip_newp6_app(**self.daip_services)

    async def run_async(self) -> None:
        """Run the TUI application asynchronously."""
        try:
            await self.app.run_async()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Error running TUI: {e}")
            raise

    def run(self) -> None:
        """Run the TUI application."""
        try:
            self.app.run()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Error running TUI: {e}")
            raise


def create_tui_from_container(container) -> DAIP_TUI_NEWP6:
    """
    Create a TUI instance from a dependency injection container.

    Args:
        container: DI container with DAIP services

    Returns:
        DAIP_TUI_NEWP6: Configured TUI instance
    """
    return DAIP_TUI_NEWP6(
        executor=container.agent_executor(),
        session_manager=container.session_manager(),
        role_manager=container.role_manager(),
        knowledge_manager=container.knowledge_manager(),
        debate_manager=container.debate_manager(),
        model_provider=container.model_provider(),
        db_manager=container.db_manager(),
        config_manager=container.config_manager(),
        role_model_manager=RoleModelManager()
    )


# Backwards compatibility alias
DAIP_TUI = DAIP_TUI_NEWP6


if __name__ == "__main__":
    """Direct execution entry point for testing."""
    print("🚀 Starting DAIP-LIVE newP6 TUI...")

    # Initialize configuration
    create_config_yaml_if_not_exists()

    # Create minimal services for testing
    try:
        tui = DAIP_TUI_NEWP6()
        tui.run()
    except Exception as e:
        print(f"❌ Failed to start TUI: {e}")
        sys.exit(1)