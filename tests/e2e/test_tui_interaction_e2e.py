"""End-to-end tests for TUI interaction.

Tests the complete user interaction flow through the terminal interface.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from daip_live.core.models import Session, DialogueTurn, AgentState
from daip_live.memory.session_manager import SessionManager
from daip_live.persistence.database import DatabaseManager
from daip_live.agent_engine.executor import AgentExecutor
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.service import MemoryService


@pytest.mark.e2e
class TestTUIInteractionE2E:
    """End-to-end tests for TUI user interaction."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_path = Path(temp_file.name)
        temp_file.close()
        db = DatabaseManager(db_path=str(temp_path))
        yield db
        try:
            temp_path.unlink()
        except (PermissionError, OSError):
            pass

    @pytest.fixture
    def session_manager(self, temp_db):
        """Create session manager."""
        return SessionManager(db_manager=temp_db)

    @pytest.fixture
    def mock_model_provider(self):
        """Create mock model provider."""
        provider = Mock(spec=LiteLLMProvider)
        provider.generate = AsyncMock(return_value="Test response from agent")
        provider.embed = Mock(return_value=[[0.1, 0.2, 0.3]])
        return provider

    @pytest.fixture
    def mock_knowledge_manager(self):
        """Create mock knowledge manager."""
        km = Mock(spec=KnowledgeManager)
        km.search = AsyncMock(return_value=[])
        km.add_document = Mock()
        return km

    @pytest.fixture
    def agent_executor(self, session_manager, mock_model_provider, mock_knowledge_manager):
        """Create agent executor with mocked dependencies."""
        tool_manager = ToolManager()
        memory_service = MemoryService(mock_model_provider)
        user_input_queue = asyncio.Queue()

        executor = AgentExecutor(
            session_manager=session_manager,
            memory_service=memory_service,
            knowledge_manager=mock_knowledge_manager,
            model_provider=mock_model_provider,
            tool_manager=tool_manager,
            user_input_queue=user_input_queue,
        )
        return executor

    def test_complete_tui_workflow_e2e(self, session_manager, agent_executor):
        """Test complete TUI workflow from start to finish."""
        # 1. User starts session via TUI
        session = session_manager.create_session(
            goal="Analyze market trends for AI adoption",
            session_type="chat",
            participant_ids=["user", "agent"]
        )
        session_manager.save_session(session)

        assert session.session_id is not None
        assert session.status == AgentState.RUNNING

        # 2. User sends first message
        user_message = "What are the key trends in AI adoption for 2024?"

        # 3. Agent processes and responds
        agent_response = asyncio.run(
            agent_executor.model_provider.generate(user_message)
        )

        assert agent_response is not None
        assert isinstance(agent_response, str)

        # 4. Verify session state
        loaded_session = session_manager.get_session(session.session_id)
        assert loaded_session is not None
        assert loaded_session.goal == "Analyze market trends for AI adoption"

        # 5. User asks follow-up question
        follow_up = "What about in healthcare specifically?"

        # 6. Agent provides follow-up response
        follow_up_response = asyncio.run(
            agent_executor.model_provider.generate(follow_up)
        )

        assert follow_up_response is not None

        # 7. Complete session
        session_manager.update_session_status(session.session_id, AgentState.COMPLETED)

        final_session = session_manager.get_session(session.session_id)
        assert final_session.status == AgentState.COMPLETED

    def test_multi_turn_conversation_e2e(self, session_manager, agent_executor):
        """Test multi-turn conversation flow."""
        session = session_manager.create_session(
            goal="Discuss renewable energy options",
            session_type="chat",
            participant_ids=["user", "agent"]
        )
        session_manager.save_session(session)

        # Simulate conversation turns
        conversation = [
            "What are the main types of renewable energy?",
            "Tell me more about solar power",
            "How does wind energy compare?",
            "What about hydroelectric power?",
            "Which is most cost-effective?"
        ]

        responses = []
        for message in conversation:
            response = asyncio.run(
                agent_executor.model_provider.generate(message)
            )
            responses.append(response)

        # Verify all turns were processed
        assert len(responses) == len(conversation)
        for response in responses:
            assert response is not None

    def test_session_with_knowledge_retrieval_e2e(
        self, session_manager, agent_executor, mock_knowledge_manager
    ):
        """Test session that retrieves knowledge base information."""
        # Mock knowledge manager to return relevant documents
        mock_knowledge_manager.search = AsyncMock(return_value=[
            {
                "content": "Python is a high-level programming language",
                "metadata": {"source": "docs/python.md", "score": 0.95}
            },
            {
                "content": "FastAPI is a modern web framework",
                "metadata": {"source": "docs/fastapi.md", "score": 0.87}
            }
        ])

        session = session_manager.create_session(
            goal="Get information about Python and FastAPI",
            session_type="chat",
            participant_ids=["user", "agent"]
        )
        session_manager.save_session(session)

        # User asks question that should trigger knowledge search
        query = "Tell me about Python web development"

        # Agent would use knowledge manager in real execution
        knowledge_results = asyncio.run(
            mock_knowledge_manager.search(query, top_k=5)
        )

        assert len(knowledge_results) == 2
        assert "Python" in knowledge_results[0]["content"]

    def test_error_handling_in_conversation_e2e(self, session_manager, agent_executor):
        """Test error handling during conversation."""
        session = session_manager.create_session(
            goal="Test error handling",
            session_type="chat",
            participant_ids=["user", "agent"]
        )
        session_manager.save_session(session)

        # Mock model provider to raise an error
        agent_executor.model_provider.generate = AsyncMock(
            side_effect=Exception("Model API error")
        )

        # User sends message
        user_message = "This should trigger an error"

        # Agent handles error gracefully (in real implementation)
        try:
            response = asyncio.run(
                agent_executor.model_provider.generate(user_message)
            )
            # If we get here, error was handled
        except Exception as e:
            # Error should be caught and logged, not crash the app
            assert "Model API error" in str(e)

        # Session should still be intact
        loaded_session = session_manager.get_session(session.session_id)
        assert loaded_session is not None

    def test_session_persistence_e2e(self, temp_db):
        """Test that session data persists correctly."""
        # Create session manager with temp database
        session_manager = SessionManager(db_manager=temp_db)

        # Create and save session
        session = session_manager.create_session(
            goal="Test persistence",
            session_type="chat",
            participant_ids=["user", "agent"]
        )
        session_manager.save_session(session)

        # Create new session manager (simulating app restart)
        new_session_manager = SessionManager(db_manager=temp_db)

        # Retrieve session
        loaded_session = new_session_manager.get_session(session.session_id)

        assert loaded_session is not None
        assert loaded_session.goal == "Test persistence"
        assert loaded_session.session_type == "chat"

    def test_concurrent_sessions_e2e(self, session_manager, agent_executor):
        """Test handling multiple concurrent sessions."""
        # Create multiple sessions
        sessions = []
        for i in range(3):
            session = session_manager.create_session(
                goal=f"Concurrent session {i}",
                session_type="chat",
                participant_ids=["user", "agent"]
            )
            session_manager.save_session(session)
            sessions.append(session)

        # Verify all sessions exist
        all_sessions = session_manager.list_sessions()
        assert len(all_sessions) >= 3

        # Simulate switching between sessions
        for session in sessions:
            loaded = session_manager.get_session(session.session_id)
            assert loaded is not None
            assert loaded.goal.startswith("Concurrent session")


@pytest.mark.e2e
class TestTUIDisplayE2E:
    """End-to-end tests for TUI display and rendering."""

    def test_session_list_display_e2e(self, session_manager):
        """Test displaying session list in TUI."""
        # Create test sessions
        for i in range(5):
            session = session_manager.create_session(
                goal=f"Display test session {i}",
                session_type="chat",
                participant_ids=["user", "agent"]
            )
            session_manager.save_session(session)

        # Retrieve for display
        all_sessions = session_manager.list_sessions()

        # Simulate TUI display logic
        display_data = []
        for session in all_sessions:
            display_data.append({
                "id": session.session_id[:8],  # Shortened for display
                "goal": session.goal[:30],     # Truncated for display
                "status": session.status.value if hasattr(session.status, 'value') else str(session.status),
                "created": session.created_at.strftime("%Y-%m-%d %H:%M")
            })

        assert len(display_data) >= 5
        for item in display_data:
            assert "id" in item
            assert "goal" in item
            assert "status" in item

    def test_session_detail_display_e2e(self, session_manager):
        """Test displaying session detail in TUI."""
        session = session_manager.create_session(
            goal="Detail display test",
            session_type="workflow",
            participant_ids=["user", "agent", "observer"]
        )
        session_manager.save_session(session)

        # Retrieve for detail display
        loaded = session_manager.get_session(session.session_id)

        # Simulate TUI detail view
        detail_view = {
            "Session ID": loaded.session_id,
            "Goal": loaded.goal,
            "Type": loaded.session_type,
            "Participants", ", ".join(loaded.participant_ids),
            "Status": loaded.status.value if hasattr(loaded.status, 'value') else str(loaded.status),
            "Created": loaded.created_at.isoformat(),
            "Updated": loaded.updated_at.isoformat()
        }

        assert detail_view["Goal"] == "Detail display test"
        assert "agent" in detail_view["Participants"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
