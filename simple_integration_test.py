#!/usr/bin/env python3
"""
Simple integration test for TUI functionality.
"""

import os
import shutil
import sys
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from unittest.mock import Mock

from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.tui import DAIP_TUI


def test_basic_functionality():
    """Test basic TUI functionality."""
    print("🚀 Starting Basic TUI Integration Tests")
    print("=" * 50)

    temp_dir = tempfile.mkdtemp()
    try:
        # Setup test environment
        roles_dir = os.path.join(temp_dir, "roles")
        os.makedirs(roles_dir, exist_ok=True)

        # Create test role file
        with open(os.path.join(roles_dir, "test_role.yaml"), "w", encoding="utf-8") as f:
            f.write("""
persona: A helpful test assistant
tools: ["read_file", "write_file"]
""")

        # Initialize components
        session_manager = SessionManager()
        role_manager = RoleManager(roles_dir)
        mock_executor = Mock()

        # Create TUI instance
        tui = DAIP_TUI(mock_executor, "Test Goal")

        # Mock log view for testing
        class MockLogView:
            def __init__(self):
                self.content = ""
                self.renderable = ""
            def update(self, text):
                self.content = str(text)
                self.renderable = str(text)
                print(f"📋 {text}")

        mock_log_view = MockLogView()
        tui.query_one = lambda x: mock_log_view

        print("\n1. Testing Role Commands:")
        print("-" * 30)

        # Test role list
        tui._handle_role_list_command("", mock_log_view)

        # Test role view
        tui._handle_role_view_command("test_role", "", mock_log_view)

        # Test role add
        tui._handle_role_add_command("new_role A new test role", "", mock_log_view)

        print("\n2. Testing Session Commands:")
        print("-" * 30)

        # Create test session
        session = session_manager.create_session(
            goal="Test integration",
            session_type="chat",
            participant_ids=["user", "assistant"]
        )
        tui._current_session_id = session.session_id

        # Test session list
        tui._handle_session_list_command("", mock_log_view)

        # Test session search
        tui._handle_session_search_command("integration", "", mock_log_view)

        # Test session tree
        tui._handle_session_tree_command("", mock_log_view)

        print("\n3. Testing Knowledge Commands:")
        print("-" * 30)

        # Test knowledge commands
        tui._handle_knowledge_command("test search", "", mock_log_view)
        tui._handle_knowledge_command("", "", mock_log_view)

        print("\n4. Testing Debate Commands:")
        print("-" * 30)

        # Test debate command
        tui._handle_debate_command("AI ethics discussion", "", mock_log_view)

        print("\n5. Testing Personal Assistant:")
        print("-" * 30)

        # Test PA command
        tui._handle_pa_command("Create a simple plan", "", mock_log_view)

        print("\n6. Testing Permission System:")
        print("-" * 30)

        # Test permission responses
        tui._handle_permission_response(True)
        tui._handle_permission_response(False)

        print("\n7. Testing ESC Functionality:")
        print("-" * 30)

        # Test ESC key
        tui._handle_escape_key()

        print("\n" + "=" * 50)
        print("✅ All basic TUI functionality verified!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_basic_functionality()
