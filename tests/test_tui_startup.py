"""Tests for TUI startup behavior."""

import os
import tempfile
from unittest.mock import Mock

import pytest
from daip_live.tui import DAIP_TUI

from src.daip_live.config import ConfigManager
from src.daip_live.core.models import (
    AppConfig,
    DatabaseConfig,
    KnowledgeBaseConfig,
    LLMProviderConfig,
    RoleManagerConfig,
)
from src.daip_live.knowledge.manager import KnowledgeManager
from src.daip_live.memory.session_manager import SessionManager
from src.daip_live.model_provider.provider import LiteLLMProvider
from src.daip_live.p4_role_manager_tools.role_manager import RoleManager
from src.daip_live.p8_debate_system.manager import DebateManager
from src.daip_live.persistence.database import DatabaseManager


@pytest.fixture(scope="class")
def test_env(request):
    """Set up a test environment for the TUI startup tests."""
    with tempfile.TemporaryDirectory() as test_dir:
        db_path = os.path.join(test_dir, "test.db")
        roles_dir = os.path.join(test_dir, "roles")
        os.makedirs(roles_dir)

        mock_config = AppConfig(
            database=DatabaseConfig(path=db_path),
            llm_provider=LLMProviderConfig(default_model="mock-model", embedding_model="mock-embedding"),
            knowledge_base=KnowledgeBaseConfig(directory=test_dir),
            role_manager=RoleManagerConfig(roles_dir=roles_dir)
        )

        config_manager = ConfigManager()
        config_manager._config = mock_config

        db_manager = DatabaseManager(db_path=db_path)
        # Dependencies for DAIP_TUI
        session_manager = SessionManager()
        role_manager = RoleManager()
        model_provider = LiteLLMProvider(config=mock_config.llm_provider)
        knowledge_manager = KnowledgeManager(
            db_manager=db_manager,
            model_provider=model_provider,
            config={"knowledge_dir": test_dir}
        )
        debate_manager = DebateManager(
            session_manager=session_manager,
            role_manager=role_manager,
            model_provider=model_provider
        )

        request.cls.db_manager = db_manager
        request.cls.session_manager = session_manager
        request.cls.role_manager = role_manager
        request.cls.model_provider = model_provider
        request.cls.knowledge_manager = knowledge_manager
        request.cls.debate_manager = debate_manager
        request.cls.config_manager = config_manager

        yield

        db_manager.engine.dispose()


@pytest.mark.usefixtures("test_env")
class TestTUIStartup:
    """Test suite for TUI startup behaviors."""

    @pytest.mark.asyncio
    async def test_welcome_message_on_cold_start(self):
        """Test that a welcome message is displayed on cold start."""
        tui = DAIP_TUI(
            executor=Mock(),
            goal=None,  # Explicitly set goal to None for cold start
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            knowledge_manager=self.knowledge_manager,
            debate_manager=self.debate_manager,
            model_provider=self.model_provider,
            db_manager=self.db_manager,
            config_manager=self.config_manager
        )

        async with tui.run_test() as pilot:
            # On startup, without any action, check the status bar.
            # We need to find the StatusBar widget. Let's assume it has an ID.
            # If not, we might need to query by class.
            await pilot.pause(0.1) # Allow UI to settle

            status_bar = pilot.app.query_one("#status_bar")
            status_text = str(status_bar.renderable)

            assert "Welcome" in status_text or "Ready" in status_text, \
                f"Expected 'Welcome' or 'Ready' in status bar, but got '{status_text}'"

