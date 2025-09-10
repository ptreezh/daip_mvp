"""Tests for TUI command auto-completion feature."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from textual.widgets import Input, Label, ListItem, ListView

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from daip_live.config import ConfigManager
from daip_live.core.models import (
    AppConfig,
    DatabaseConfig,
    KnowledgeBaseConfig,
    LLMProviderConfig,
    RoleManagerConfig,
)
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.persistence.database import DatabaseManager
from daip_live.tui import DAIP_TUI


@pytest.fixture(scope="class")
def test_env(request):
    """Set up a test environment for the TUI tests."""
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
class TestTUIAutocompletion:
    """Test suite for TUI auto-completion features."""

    @pytest.mark.asyncio
    async def test_autocomplete_popup_appears_on_slash(self):
        """Test that the autocomplete popup appears when '/' is typed."""
        tui = DAIP_TUI(
            executor=Mock(),
            goal=None,
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            knowledge_manager=self.knowledge_manager,
            debate_manager=self.debate_manager,
            model_provider=self.model_provider,
            db_manager=self.db_manager,
            config_manager=self.config_manager
        )

        async with tui.run_test() as pilot:
            # Initially, the popup should not exist
            assert len(pilot.app.query("#autocomplete-popup")) == 0

            # Simulate user typing '/'
            await pilot.press("/")
            await pilot.pause(0.1) # Allow UI to react

            # Now, the popup should exist
            assert len(pilot.app.query("#autocomplete-popup")) == 1, \
                "Autocomplete popup did not appear after typing '/'."

    @pytest.mark.asyncio
    async def test_autocomplete_popup_shows_commands(self):
        """Test that the autocomplete popup is populated with commands."""
        tui = DAIP_TUI(
            executor=Mock(),
            goal=None,
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            knowledge_manager=self.knowledge_manager,
            debate_manager=self.debate_manager,
            model_provider=self.model_provider,
            db_manager=self.db_manager,
            config_manager=self.config_manager
        )

        async with tui.run_test() as pilot:
            await pilot.press("/")
            await pilot.pause(0.1)

            popup = pilot.app.query_one("#autocomplete-popup")
            list_view = popup.query_one("#autocomplete-list", ListView)
            items = list_view.query(ListItem)
            content = " ".join([str(item.query_one(Label).renderable) for item in items])

            # Check for a few known commands and their help text
            assert "/quit - Exit the application." in content, "Popup should contain commands with help text."

    @pytest.mark.asyncio
    async def test_autocomplete_filters_list(self):
        """Test that the autocomplete list filters as the user types."""
        tui = DAIP_TUI(
            executor=Mock(),
            goal=None,
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            knowledge_manager=self.knowledge_manager,
            debate_manager=self.debate_manager,
            model_provider=self.model_provider,
            db_manager=self.db_manager,
            config_manager=self.config_manager
        )

        async with tui.run_test() as pilot:
            await pilot.press("/")
            await pilot.press("p")
            await pilot.press("a")
            await pilot.pause(0.1)

            popup = pilot.app.query_one("#autocomplete-popup")
            list_view = popup.query_one("#autocomplete-list", ListView)
            items = list_view.query(ListItem)
            content = " ".join([str(item.query_one(Label).renderable) for item in items])

            assert "/pa" in content
            assert "/help" not in content
            assert "/quit" not in content, "Popup should only show filtered commands."

    @pytest.mark.asyncio
    async def test_autocomplete_selection_and_acceptance(self):
        """Test that an item can be selected and accepted."""
        tui = DAIP_TUI(
            executor=Mock(),
            goal=None,
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            knowledge_manager=self.knowledge_manager,
            debate_manager=self.debate_manager,
            model_provider=self.model_provider,
            db_manager=self.db_manager,
            config_manager=self.config_manager
        )

        async with tui.run_test() as pilot:
            await pilot.press("/")
            await pilot.pause(0.1)

            # Navigate down to the second item (index 1)
            await pilot.press("down")
            await pilot.pause(0.1)

            # Accept the selection
            await pilot.press("enter")
            await pilot.pause(0.1)

            # The input value should now be the selected command
            input_widget = pilot.app.query_one(Input)

            # Get the actual second command from the app's discovered list
            # to make the test robust against ordering changes.
            all_commands = sorted(tui._available_commands)
            expected_command_tuple = all_commands[1] # The second item after sorting
            expected_command = expected_command_tuple[0]

            assert input_widget.value == expected_command, f"Input value was not updated with selected command. Expected {expected_command} but got {input_widget.value}"

    @pytest.mark.asyncio
    async def test_autocomplete_accept_with_tab(self):
        """Test that an item can be accepted with the Tab key."""
        tui = DAIP_TUI(
            executor=Mock(),
            goal=None,
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            knowledge_manager=self.knowledge_manager,
            debate_manager=self.debate_manager,
            model_provider=self.model_provider,
            db_manager=self.db_manager,
            config_manager=self.config_manager
        )

        async with tui.run_test() as pilot:
            await pilot.press("/")
            await pilot.pause(0.1)

            # Navigate down to the second item (index 1)
            await pilot.press("down")
            await pilot.pause(0.1)

            # Accept the selection with Tab
            await pilot.press("tab")
            await pilot.pause(0.1)

            # The input value should now be the selected command
            input_widget = pilot.app.query_one(Input)
            all_commands = sorted(tui._available_commands)
            expected_command = all_commands[1][0]

            assert input_widget.value == expected_command, "Input value was not updated with selected command using Tab."

