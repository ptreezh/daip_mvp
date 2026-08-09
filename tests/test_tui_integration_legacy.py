#!/usr/bin/env python3
"""
Integration test script for TUI functionality.
This script tests all TUI shortcut commands with real dependencies.
"""

import asyncio
import os
import shutil
import sys
import tempfile
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.config import config_manager
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.persistence.database import DatabaseManager
from daip_live.tui import DAIP_TUI


class TUIIntegrationTester:
    """Integration tester for TUI functionality."""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_integration.db")
        self.roles_dir = os.path.join(self.temp_dir, "roles")
        self.knowledge_dir = os.path.join(self.temp_dir, "knowledge")

        # Setup test environment
        os.makedirs(self.roles_dir, exist_ok=True)
        os.makedirs(self.knowledge_dir, exist_ok=True)

        # Override config for testing
        config_manager._config.database.path = self.db_path
        config_manager._config.knowledge_base.directory = self.knowledge_dir

        # Initialize real dependencies
        self.db_manager = DatabaseManager(self.db_path)
        self.session_manager = SessionManager()
        self.role_manager = RoleManager(self.roles_dir)
        self.knowledge_manager = KnowledgeManager(
            db_manager=self.db_manager,
            model_provider=LiteLLMProvider(config_manager.get_config().llm_provider),
            config={"knowledge_dir": self.knowledge_dir},
        )
        self.debate_manager = DebateManager(
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            model_provider=LiteLLMProvider(config_manager.get_config().llm_provider),
        )

        # Mock executor for testing
        self.mock_executor = Mock(spec=AgentExecutor)
        self.mock_executor.run = Mock()

        # Create TUI instance
        self.tui = DAIP_TUI(
            executor=self.mock_executor,
            goal="Integration Test",
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            knowledge_manager=self.knowledge_manager,
            debate_manager=self.debate_manager,
        )

        # Mock UI components
        self.mock_log_view = Mock()
        self.mock_log_view.renderable = ""
        self.tui.query_one = Mock(return_value=self.mock_log_view)

    def cleanup(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_role_commands(self):
        """Test role management commands."""

        # Test /role add
        self.tui._handle_role_add_command(
            "test_role A test role persona", "", self.mock_log_view
        )

        # Test /role list
        self.tui._handle_role_list_command("", self.mock_log_view)

        # Test /role view
        self.tui._handle_role_view_command("test_role", "", self.mock_log_view)

    def test_session_commands(self):
        """Test session management commands."""

        # Create a test session
        session = self.session_manager.create_session(
            goal="Test session",
            session_type="chat",
            participant_ids=["user", "assistant"],
        )
        self.tui._current_session_id = session.session_id

        # Test /l (list sessions)
        self.tui._handle_session_list_command("", self.mock_log_view)

        # Test /v (search sessions)
        self.tui._handle_session_search_command("Test", "", self.mock_log_view)

        # Test /t (session tree)
        self.tui._handle_session_tree_command("", self.mock_log_view)

        # Test /c (abort)
        self.tui._handle_session_abort_command("", self.mock_log_view)

        # Test /p (pause)
        self.tui._handle_session_pause_command("", self.mock_log_view)

        # Test /g (continue)
        self.tui._handle_session_continue_command("", self.mock_log_view)

    def test_knowledge_commands(self):
        """Test knowledge base commands."""

        # Test /0 with search
        self.tui._handle_knowledge_command("test query", "", self.mock_log_view)

        # Test /0 without search (sync)
        self.tui._handle_knowledge_command("", self.mock_log_view)

    def test_debate_commands(self):
        """Test debate commands."""

        # Test /debate
        self.tui._handle_debate_command("AI ethics debate", "", self.mock_log_view)

    def test_pa_command(self):
        """Test personal assistant command."""

        # Test /pa
        self.tui._handle_pa_command("Create a project plan", "", self.mock_log_view)

    def test_permission_system(self):
        """Test permission dialog system."""

        # Test permission response handling
        self.tui._handle_permission_response(True)
        self.tui._handle_permission_response(False)

    def test_escape_functionality(self):
        """Test ESC key functionality."""

        # Test ESC key
        self.tui._handle_escape_key()

    def run_all_tests(self):
        """Run all integration tests."""

        try:
            self.test_role_commands()
            self.test_session_commands()
            self.test_knowledge_commands()
            self.test_debate_commands()
            self.test_pa_command()
            self.test_permission_system()
            self.test_escape_functionality()

        except Exception:
            raise
        finally:
            self.cleanup()


async def main():
    """Main test runner."""
    tester = TUIIntegrationTester()
    tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
