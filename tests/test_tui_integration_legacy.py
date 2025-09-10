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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
            config={"knowledge_dir": self.knowledge_dir}
        )
        self.debate_manager = DebateManager(
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            model_provider=LiteLLMProvider(config_manager.get_config().llm_provider)
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
            debate_manager=self.debate_manager
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
        print("\n=== Testing Role Commands ===")

        # Test /role add
        print("Testing /role add...")
        self.tui._handle_role_add_command("test_role A test role persona", "", self.mock_log_view)

        # Test /role list
        print("Testing /role list...")
        self.tui._handle_role_list_command("", self.mock_log_view)

        # Test /role view
        print("Testing /role view...")
        self.tui._handle_role_view_command("test_role", "", self.mock_log_view)

        print("✓ Role commands tested")

    def test_session_commands(self):
        """Test session management commands."""
        print("\n=== Testing Session Commands ===")

        # Create a test session
        session = self.session_manager.create_session(
            goal="Test session",
            session_type="chat",
            participant_ids=["user", "assistant"]
        )
        self.tui._current_session_id = session.session_id

        # Test /l (list sessions)
        print("Testing /l...")
        self.tui._handle_session_list_command("", self.mock_log_view)

        # Test /v (search sessions)
        print("Testing /v...")
        self.tui._handle_session_search_command("Test", "", self.mock_log_view)

        # Test /t (session tree)
        print("Testing /t...")
        self.tui._handle_session_tree_command("", self.mock_log_view)

        # Test /c (abort)
        print("Testing /c...")
        self.tui._handle_session_abort_command("", self.mock_log_view)

        # Test /p (pause)
        print("Testing /p...")
        self.tui._handle_session_pause_command("", self.mock_log_view)

        # Test /g (continue)
        print("Testing /g...")
        self.tui._handle_session_continue_command("", self.mock_log_view)

        print("✓ Session commands tested")

    def test_knowledge_commands(self):
        """Test knowledge base commands."""
        print("\n=== Testing Knowledge Commands ===")

        # Test /0 with search
        print("Testing /0 with search...")
        self.tui._handle_knowledge_command("test query", "", self.mock_log_view)

        # Test /0 without search (sync)
        print("Testing /0 sync...")
        self.tui._handle_knowledge_command("", self.mock_log_view)

        print("✓ Knowledge commands tested")

    def test_debate_commands(self):
        """Test debate commands."""
        print("\n=== Testing Debate Commands ===")

        # Test /debate
        print("Testing /debate...")
        self.tui._handle_debate_command("AI ethics debate", "", self.mock_log_view)

        print("✓ Debate commands tested")

    def test_pa_command(self):
        """Test personal assistant command."""
        print("\n=== Testing Personal Assistant Command ===")

        # Test /pa
        print("Testing /pa...")
        self.tui._handle_pa_command("Create a project plan", "", self.mock_log_view)

        print("✓ Personal assistant command tested")

    def test_permission_system(self):
        """Test permission dialog system."""
        print("\n=== Testing Permission System ===")

        # Test permission response handling
        print("Testing permission response...")
        self.tui._handle_permission_response(True)
        self.tui._handle_permission_response(False)

        print("✓ Permission system tested")

    def test_escape_functionality(self):
        """Test ESC key functionality."""
        print("\n=== Testing ESC Functionality ===")

        # Test ESC key
        print("Testing ESC key...")
        self.tui._handle_escape_key()

        print("✓ ESC functionality tested")

    def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting TUI Integration Tests")
        print("=" * 50)

        try:
            self.test_role_commands()
            self.test_session_commands()
            self.test_knowledge_commands()
            self.test_debate_commands()
            self.test_pa_command()
            self.test_permission_system()
            self.test_escape_functionality()

            print("\n" + "=" * 50)
            print("✅ All TUI integration tests completed successfully!")

        except Exception as e:
            print(f"\n❌ Integration test failed: {e}")
            raise
        finally:
            self.cleanup()


async def main():
    """Main test runner."""
    tester = TUIIntegrationTester()
    tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
